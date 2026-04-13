#!/usr/bin/env python3
"""Run previously missing Task 1 experiments and reorganize outputs by section."""

from __future__ import annotations

import csv
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import classification_report, f1_score

# Spark 3.1.2 expects the legacy pandas DataFrame.iteritems API.
if not hasattr(pd.DataFrame, 'iteritems'):
    pd.DataFrame.iteritems = pd.DataFrame.items

# Spark 3.1.2 in the CDS527 env must use Java 11, not the env-bundled Java 17.
os.environ['JAVA_HOME'] = '/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk/Contents/Home'
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from gensim import downloader as gensim_api
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression, MultilayerPerceptronClassifier
from pyspark.ml.feature import CountVectorizer, IDF, NGram, RegexTokenizer, StopWordsRemover, VectorAssembler, Word2Vec
from pyspark.ml.linalg import VectorUDT, Vectors
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace, trim, when
from pyspark.sql.types import DoubleType, StructField, StructType
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'smile-annotations-final.csv'
OUT_ROOT = ROOT / '输出'
FIG_DIR = OUT_ROOT / 'figures'
REPORT_DIR = OUT_ROOT / 'reports'
DATA_DIR = OUT_ROOT / 'data'
TABLE_DIR = OUT_ROOT / 'tables'
SECTION_DIR = OUT_ROOT / 'sections'

SEED = 42
LABEL_MAP = {0: 'surprise', 1: 'angry', 2: 'disgust', 3: 'happy', 4: 'sad'}
LABEL_ORDER = [0, 1, 2, 3, 4]
COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']


def ensure_dirs() -> None:
    for path in [FIG_DIR, REPORT_DIR, DATA_DIR, TABLE_DIR, SECTION_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    for sec in [
        'section1_baseline',
        'section2_model_comparison',
        'section3_representation',
        'section4_improvement',
    ]:
        (SECTION_DIR / sec).mkdir(parents=True, exist_ok=True)


def clean_text(df, col_in: str = 'text', col_out: str = 'cleaned'):
    df = df.withColumn(col_out, regexp_replace(col(col_in), r'http[s]?://\S+', ' '))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'@\w+', ' '))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'&amp;', 'and'))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'#(\w+)', r'\1'))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'[^a-zA-Z\s]', ' '))
    df = df.withColumn(col_out, lower(col(col_out)))
    df = df.withColumn(col_out, trim(regexp_replace(col(col_out), r'\s+', ' ')))
    return df


def light_clean_text(df, col_in: str = 'text', col_out: str = 'light_cleaned'):
    df = df.withColumn(col_out, lower(col(col_in)))
    df = df.withColumn(col_out, trim(regexp_replace(col(col_out), r'\s+', ' ')))
    return df


def evaluate_arrays(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, object]:
    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    accuracy = float((y_true == y_pred).mean())
    report_text = classification_report(
        y_true,
        y_pred,
        labels=LABEL_ORDER,
        target_names=[LABEL_MAP[i] for i in LABEL_ORDER],
        zero_division=0,
        digits=4,
    )
    report_dict = classification_report(
        y_true,
        y_pred,
        labels=LABEL_ORDER,
        target_names=[LABEL_MAP[i] for i in LABEL_ORDER],
        zero_division=0,
        output_dict=True,
    )
    return {
        'macro_f1': macro_f1,
        'weighted_f1': weighted_f1,
        'accuracy': accuracy,
        'report_text': report_text,
        'report_dict': report_dict,
    }


def evaluate_predictions(preds, experiment_name: str = '') -> Dict[str, object]:
    preds_pd = preds.select('label', 'prediction').toPandas()
    y_true = preds_pd['label'].astype(int).to_numpy()
    y_pred = preds_pd['prediction'].astype(int).to_numpy()
    metrics = evaluate_arrays(y_true, y_pred)
    if experiment_name:
        print(f'\n=== {experiment_name} ===')
        print(f'  macro-F1    : {metrics["macro_f1"]:.4f}')
        print(f'  weighted-F1 : {metrics["weighted_f1"]:.4f}')
        print(f'  accuracy    : {metrics["accuracy"]:.4f}')
    return metrics


def report_text(title: str, metrics: Dict[str, object], train_sec: float | None = None, extra: Iterable[str] = ()) -> str:
    lines = [f'=== {title} ===', '']
    lines.append(f'macro-F1    : {metrics["macro_f1"]:.4f}')
    lines.append(f'weighted-F1 : {metrics["weighted_f1"]:.4f}')
    lines.append(f'accuracy    : {metrics["accuracy"]:.4f}')
    if train_sec is not None:
        lines.append(f'train time  : {train_sec:.1f}s')
    if extra:
        lines.append('')
        lines.extend(extra)
    lines.extend(['', 'Per-class report:', metrics['report_text']])
    return '\n'.join(lines).rstrip() + '\n'


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def make_vector_df(spark: SparkSession, X: np.ndarray, y: np.ndarray):
    schema = StructType(
        [
            StructField('label', DoubleType(), False),
            StructField('features', VectorUDT(), False),
        ]
    )
    rows = [(float(lbl), Vectors.dense(vec.tolist())) for vec, lbl in zip(X, y)]
    return spark.createDataFrame(rows, schema)


def average_glove_embeddings(model, texts: List[str], dim: int) -> np.ndarray:
    vectors = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        toks = [tok for tok in text.split() if tok in model]
        if toks:
            vectors[i] = np.mean([model[t] for t in toks], axis=0)
    return vectors


def mean_pool_embeddings(model, tokenizer, texts: List[str], device: torch.device, batch_size: int = 32) -> np.ndarray:
    all_vecs: List[np.ndarray] = []
    model.eval()
    with torch.no_grad():
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=64,
                return_tensors='pt',
            )
            encoded = {k: v.to(device) for k, v in encoded.items()}
            out = model(**encoded)
            hidden = out.last_hidden_state
            mask = encoded['attention_mask'].unsqueeze(-1)
            pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            all_vecs.append(pooled.detach().cpu().numpy())
    return np.vstack(all_vecs).astype(np.float32)


def make_ablation_pipeline(
    *,
    text_col: str,
    remove_stopwords: bool,
    use_idf: bool,
    use_class_weight: bool,
    reg_param: float,
) -> Pipeline:
    stages = [RegexTokenizer(inputCol=text_col, outputCol='tokens', pattern='\\W', minTokenLength=2)]
    token_col = 'tokens'
    if remove_stopwords:
        stages.append(StopWordsRemover(inputCol='tokens', outputCol='filtered'))
        token_col = 'filtered'
    stages.append(CountVectorizer(inputCol=token_col, outputCol='raw_features', vocabSize=10000, minDF=2.0))
    feat_col = 'raw_features'
    if use_idf:
        stages.append(IDF(inputCol='raw_features', outputCol='features', minDocFreq=2))
        feat_col = 'features'
    lr_kwargs = dict(
        featuresCol=feat_col,
        labelCol='label',
        maxIter=200,
        regParam=reg_param,
        family='multinomial',
    )
    if use_class_weight:
        lr_kwargs['weightCol'] = 'class_weight'
    stages.append(LogisticRegression(**lr_kwargs))
    return Pipeline(stages=stages)


def parse_report_file(path: Path) -> Tuple[Dict[str, float], Dict[str, float]]:
    text = path.read_text(encoding='utf-8')
    metrics = {}
    for key, pattern in {
        'macro_f1': r'macro-F1\s*:\s*([0-9.]+)',
        'weighted_f1': r'weighted-F1\s*:\s*([0-9.]+)',
        'accuracy': r'accuracy\s*:\s*([0-9.]+)',
        'train_sec': r'train time\s*:\s*([0-9.]+)s',
    }.items():
        m = re.search(pattern, text)
        metrics[key] = float(m.group(1)) if m else np.nan
    per_class = {}
    for emo in LABEL_MAP.values():
        m = re.search(rf'^\s*{emo}\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+(\d+)\s*$', text, re.M)
        if m:
            per_class[emo] = float(m.group(3))
    return metrics, per_class


def copy_into_section(section_name: str, files: Iterable[Path]) -> None:
    target = SECTION_DIR / section_name
    target.mkdir(parents=True, exist_ok=True)
    for path in files:
        if path.exists():
            shutil.copy2(path, target / path.name)


def main() -> None:
    ensure_dirs()

    spark = (
        SparkSession.builder.master('local[*]')
        .appName('CDS527-Additional-Experiments')
        .config('spark.driver.memory', '4g')
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel('ERROR')

    df_raw = spark.read.csv(
        str(DATA_PATH),
        header=True,
        inferSchema=True,
        multiLine=True,
        quote='"',
        escape='"',
    )
    df_raw = df_raw.dropDuplicates(['text']).withColumnRenamed('emotions', 'label')
    df = clean_text(df_raw)
    df = light_clean_text(df)

    label_vals = [r['label'] for r in df.select('label').distinct().collect()]
    fractions = {v: 0.8 for v in label_vals}
    train = df.sampleBy('label', fractions=fractions, seed=SEED).cache()
    test = df.subtract(train).cache()

    label_counts_pd = train.groupBy('label').count().orderBy('label').toPandas()
    n_samp = int(label_counts_pd['count'].sum())
    n_cls = len(label_counts_pd)
    weight_dict = {
        int(row['label']): n_samp / (n_cls * int(row['count']))
        for _, row in label_counts_pd.iterrows()
    }
    w_expr = when(col('label') == 0, weight_dict[0])
    for lbl in range(1, n_cls):
        w_expr = w_expr.when(col('label') == lbl, weight_dict[lbl])
    train_w = train.withColumn('class_weight', w_expr.otherwise(1.0)).cache()

    # Section 3 Part B: GloVe and BERT embeddings under the same classifier.
    train_pd = train.select('cleaned', 'label').toPandas()
    test_pd = test.select('cleaned', 'label').toPandas()
    y_train = train_pd['label'].astype(int).to_numpy()
    y_test = test_pd['label'].astype(int).to_numpy()
    train_texts = train_pd['cleaned'].tolist()
    test_texts = test_pd['cleaned'].tolist()

    s3b_rows: List[Dict[str, object]] = []
    s3b_per_class: Dict[str, Dict[str, float]] = {}

    print('\nLoading GloVe vectors...')
    glove_model = gensim_api.load('glove-twitter-100')
    t0 = time.time()
    X_train_glove = average_glove_embeddings(glove_model, train_texts, 100)
    X_test_glove = average_glove_embeddings(glove_model, test_texts, 100)
    glove_train_df = make_vector_df(spark, X_train_glove, y_train)
    glove_test_df = make_vector_df(spark, X_test_glove, y_test)
    glove_lr = LogisticRegression(featuresCol='features', labelCol='label', maxIter=100, regParam=0.1, family='multinomial')
    glove_model_fit = glove_lr.fit(glove_train_df)
    glove_preds = glove_model_fit.transform(glove_test_df)
    glove_elapsed = round(time.time() - t0, 1)
    glove_metrics = evaluate_predictions(glove_preds, 'Section 3B — GloVe + LR')
    s3b_rows.append(
        {
            'short': 'R5',
            'display': 'GloVe (twitter-100d)',
            'macro_f1': glove_metrics['macro_f1'],
            'weighted_f1': glove_metrics['weighted_f1'],
            'accuracy': glove_metrics['accuracy'],
            'train_sec': glove_elapsed,
        }
    )
    s3b_per_class['GloVe (twitter-100d)'] = {
        emo: glove_metrics['report_dict'][emo]['f1-score'] for emo in LABEL_MAP.values()
    }
    write_text(
        REPORT_DIR / 'report_s3B_GloVe.txt',
        report_text('Section 3B — GloVe (twitter-100d) + LogisticRegression', glove_metrics, glove_elapsed),
    )

    print('\nLoading BERT model...')
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    bert_model = AutoModel.from_pretrained('bert-base-uncased').to(device)
    t0 = time.time()
    X_train_bert = mean_pool_embeddings(bert_model, tokenizer, train_texts, device)
    X_test_bert = mean_pool_embeddings(bert_model, tokenizer, test_texts, device)
    bert_train_df = make_vector_df(spark, X_train_bert, y_train)
    bert_test_df = make_vector_df(spark, X_test_bert, y_test)
    bert_lr = LogisticRegression(featuresCol='features', labelCol='label', maxIter=100, regParam=0.1, family='multinomial')
    bert_model_fit = bert_lr.fit(bert_train_df)
    bert_preds = bert_model_fit.transform(bert_test_df)
    bert_elapsed = round(time.time() - t0, 1)
    bert_metrics = evaluate_predictions(bert_preds, 'Section 3B — BERT embedding + LR')
    s3b_rows.append(
        {
            'short': 'R6',
            'display': 'BERT embedding (bert-base-uncased)',
            'macro_f1': bert_metrics['macro_f1'],
            'weighted_f1': bert_metrics['weighted_f1'],
            'accuracy': bert_metrics['accuracy'],
            'train_sec': bert_elapsed,
        }
    )
    s3b_per_class['BERT embedding (bert-base-uncased)'] = {
        emo: bert_metrics['report_dict'][emo]['f1-score'] for emo in LABEL_MAP.values()
    }
    write_text(
        REPORT_DIR / 'report_s3B_BERT.txt',
        report_text('Section 3B — BERT embedding (bert-base-uncased) + LogisticRegression', bert_metrics, bert_elapsed),
    )

    df_s3b = pd.DataFrame(s3b_rows).sort_values('macro_f1', ascending=False).reset_index(drop=True)
    df_s3b.to_csv(DATA_DIR / 'results_s3_partb_embeddings.csv', index=False)
    write_text(
        REPORT_DIR / 'report_s3B_summary.txt',
        'Section 3B — Embedding Comparison Summary\n'
        '=========================================\n'
        f'{df_s3b.to_string(index=False)}\n',
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df_s3b['display'], df_s3b['macro_f1'], color=['#8e44ad', '#16a085'])
    ax.axhline(0.2337, color='gray', linestyle='--', lw=1, label='S1 baseline')
    ax.set_title('Section 3B — GloVe vs BERT (macro-F1)')
    ax.set_ylabel('macro-F1')
    ax.tick_params(axis='x', rotation=15)
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'fig11_s3b_embeddings.png', bbox_inches='tight')
    plt.close(fig)

    # Section 4 optional: MLP + Word2Vec.
    t0 = time.time()
    w2v = Word2Vec(vectorSize=100, minCount=1, inputCol='filtered', outputCol='features', seed=SEED)
    mlp = MultilayerPerceptronClassifier(
        featuresCol='features',
        labelCol='label',
        layers=[100, 64, 5],
        maxIter=200,
        blockSize=64,
        seed=SEED,
    )
    mlp_pipe = Pipeline(
        stages=[
            RegexTokenizer(inputCol='cleaned', outputCol='tokens', pattern='\\W', minTokenLength=2),
            StopWordsRemover(inputCol='tokens', outputCol='filtered'),
            w2v,
            mlp,
        ]
    )
    mlp_model = mlp_pipe.fit(train)
    mlp_preds = mlp_model.transform(test)
    mlp_elapsed = round(time.time() - t0, 1)
    mlp_metrics = evaluate_predictions(mlp_preds, 'Section 4A — Optional MLP + Word2Vec')
    df_mlp = pd.DataFrame(
        [
            {
                'display': 'MLP + Word2Vec (dim=100)',
                'macro_f1': mlp_metrics['macro_f1'],
                'weighted_f1': mlp_metrics['weighted_f1'],
                'accuracy': mlp_metrics['accuracy'],
                'train_sec': mlp_elapsed,
            }
        ]
    )
    df_mlp.to_csv(DATA_DIR / 'results_s4_optional_mlp_word2vec.csv', index=False)
    write_text(
        REPORT_DIR / 'report_s4_MLP_word2vec.txt',
        report_text('Section 4A — Optional MLP + Word2Vec', mlp_metrics, mlp_elapsed),
    )

    # Section 4B: ablation study around the current best LR + class-weighted model.
    ablations = [
        ('A0', 'Full best (clean + stopwords + TF-IDF + class weight)', 'cleaned', True, True, True, 0.5),
        ('A1', 'No class weight', 'cleaned', True, True, False, 0.5),
        ('A2', 'No stopword removal', 'cleaned', False, True, True, 0.5),
        ('A3', 'No IDF', 'cleaned', True, False, True, 0.5),
        ('A4', 'Light cleaning only', 'light_cleaned', True, True, True, 0.5),
    ]
    ablation_rows = []
    for short, display, text_col, remove_stop, use_idf, use_weight, reg_param in ablations:
        t0 = time.time()
        pipe = make_ablation_pipeline(
            text_col=text_col,
            remove_stopwords=remove_stop,
            use_idf=use_idf,
            use_class_weight=use_weight,
            reg_param=reg_param,
        )
        train_src = train_w if use_weight else train
        model = pipe.fit(train_src)
        preds = model.transform(test)
        elapsed = round(time.time() - t0, 1)
        metrics = evaluate_predictions(preds, f'Section 4B — Ablation: {display}')
        ablation_rows.append(
            {
                'short': short,
                'display': display,
                'text_col': text_col,
                'remove_stopwords': remove_stop,
                'use_idf': use_idf,
                'use_class_weight': use_weight,
                'regParam': reg_param,
                'macro_f1': metrics['macro_f1'],
                'weighted_f1': metrics['weighted_f1'],
                'accuracy': metrics['accuracy'],
                'train_sec': elapsed,
            }
        )
        write_text(
            REPORT_DIR / f'report_s4_ablation_{short}.txt',
            report_text(f'Section 4B — Ablation: {display}', metrics, elapsed),
        )

    df_ablation = pd.DataFrame(ablation_rows).sort_values('macro_f1', ascending=False).reset_index(drop=True)
    df_ablation.to_csv(DATA_DIR / 'results_s4_ablation.csv', index=False)
    write_text(
        REPORT_DIR / 'report_s4_ablation_summary.txt',
        'Section 4B — Ablation Study Summary\n'
        '===================================\n'
        f'{df_ablation.to_string(index=False)}\n',
    )
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.bar(df_ablation['display'], df_ablation['macro_f1'], color=COLORS[: len(df_ablation)])
    ax.set_title('Section 4B — Ablation Study (macro-F1)')
    ax.set_ylabel('macro-F1')
    ax.tick_params(axis='x', rotation=20)
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'fig12_s4_ablation.png', bbox_inches='tight')
    plt.close(fig)

    # Consolidated tables.
    baseline_row = pd.DataFrame(
        [
            {
                'section': 'S1',
                'subsection': 'Baseline',
                'experiment': 'TF-IDF unigram + LR',
                'role': 'baseline',
                'macro_f1': 0.2337,
                'weighted_f1': 0.8590,
                'accuracy': 0.8985,
                'train_sec': 8.3,
            }
        ]
    )

    s2 = pd.read_csv(DATA_DIR / 'results_s2_model_comparison.csv')
    s2['experiment'] = s2['display'].str.replace('\n', ' ', regex=False)
    s2['section'] = 'S2'
    s2['subsection'] = 'Model Comparison'
    s2['role'] = np.where(s2['short'] == 'LR', 'baseline-reference', 'experiment')
    s2 = s2[['section', 'subsection', 'experiment', 'role', 'macro_f1', 'weighted_f1', 'accuracy', 'train_sec']]

    s3a = pd.read_csv(DATA_DIR / 'results_s3_repr_comparison.csv')
    s3a['experiment'] = s3a['display'].str.replace('\n', ' ', regex=False)
    s3a['section'] = 'S3'
    s3a['subsection'] = 'Representation Comparison Part A'
    s3a['role'] = np.where(s3a['short'] == 'R1', 'baseline-reference', 'experiment')
    s3a = s3a[['section', 'subsection', 'experiment', 'role', 'macro_f1', 'weighted_f1', 'accuracy', 'train_sec']]

    s3b_tbl = df_s3b.copy()
    s3b_tbl['section'] = 'S3'
    s3b_tbl['subsection'] = 'Representation Comparison Part B'
    s3b_tbl['role'] = 'experiment'
    s3b_tbl = s3b_tbl.rename(columns={'display': 'experiment'})
    s3b_tbl = s3b_tbl[['section', 'subsection', 'experiment', 'role', 'macro_f1', 'weighted_f1', 'accuracy', 'train_sec']]

    s4 = pd.read_csv(DATA_DIR / 'results_s4_improvement.csv')
    s4['experiment'] = s4['display']
    s4['section'] = 'S4'
    s4['subsection'] = 'Improvement Core'
    s4['role'] = np.where(s4['display'].str.contains('CNB'), 'reference', 'experiment')
    s4 = s4[['section', 'subsection', 'experiment', 'role', 'macro_f1', 'weighted_f1', 'accuracy', 'train_sec']]

    s4_mlp = df_mlp.copy()
    s4_mlp['section'] = 'S4'
    s4_mlp['subsection'] = 'Optional MLP + Word2Vec'
    s4_mlp['role'] = 'optional'
    s4_mlp = s4_mlp.rename(columns={'display': 'experiment'})
    s4_mlp = s4_mlp[['section', 'subsection', 'experiment', 'role', 'macro_f1', 'weighted_f1', 'accuracy', 'train_sec']]

    s4_ab = df_ablation.copy()
    s4_ab['section'] = 'S4'
    s4_ab['subsection'] = 'Ablation Study'
    s4_ab['role'] = 'analysis'
    s4_ab = s4_ab.rename(columns={'display': 'experiment'})
    s4_ab = s4_ab[['section', 'subsection', 'experiment', 'role', 'macro_f1', 'weighted_f1', 'accuracy', 'train_sec']]

    overall = pd.concat([baseline_row, s2, s3a, s3b_tbl, s4, s4_mlp, s4_ab], ignore_index=True)
    overall = overall.sort_values(['section', 'subsection', 'macro_f1'], ascending=[True, True, False]).reset_index(drop=True)
    overall.to_csv(TABLE_DIR / 'overall_experiment_metrics.csv', index=False)
    write_text(TABLE_DIR / 'overall_experiment_metrics.md', overall.to_markdown(index=False))

    ranking = overall[['section', 'subsection', 'experiment', 'role', 'macro_f1', 'weighted_f1', 'accuracy', 'train_sec']].sort_values(
        'macro_f1', ascending=False
    )
    ranking.to_csv(TABLE_DIR / 'macro_f1_ranking.csv', index=False)
    write_text(TABLE_DIR / 'macro_f1_ranking.md', ranking.to_markdown(index=False))

    roadmap = pd.DataFrame(
        [
            ['S1', 'LR + TF-IDF unigram', 'done', 'Section 1 baseline'],
            ['S2', 'LR', 'done', 'Section 2'],
            ['S2', 'Complement NaiveBayes', 'done', 'Section 2'],
            ['S2', 'Decision Tree', 'done', 'Section 2'],
            ['S2', 'Random Forest', 'done', 'Section 2'],
            ['S2', 'OneVsRest + LinearSVC', 'done', 'Section 2'],
            ['S3A', 'TF-IDF unigram + LR', 'done', 'Section 3 Part A'],
            ['S3A', 'TF-IDF (1,2-gram) + LR', 'done', 'Section 3 Part A'],
            ['S3A', 'CountVectorizer + LR', 'done', 'Section 3 Part A'],
            ['S3A', 'Word2Vec + LR', 'done', 'Section 3 Part A'],
            ['S3B', 'GloVe + LR', 'done', 'Section 3 Part B'],
            ['S3B', 'BERT embedding + LR', 'done', 'Section 3 Part B'],
            ['S4A', 'Fine-grained text cleaning', 'partial', '统一清洗已做；ablation 中补做 light-cleaning 对照'],
            ['S4A', 'Class weighting / imbalance handling', 'done', 'Section 4 core'],
            ['S4A', 'Hyperparameter tuning', 'done', 'Section 4 core'],
            ['S4A', 'Optional MLP + Word2Vec', 'done', '本脚本新增'],
            ['S4B', 'Confusion matrix', 'done', '原 Section 4 深度分析'],
            ['S4B', 'Per-class precision / recall / F1', 'done', '原 Section 4 深度分析'],
            ['S4B', 'Hardest class pairs', 'done', '原 Section 4 深度分析'],
            ['S4B', 'Ablation study', 'done', '本脚本新增'],
            ['S4B', 'Training time vs performance trade-off', 'done', '原 Section 4 深度分析'],
        ],
        columns=['section', 'item', 'status', 'note'],
    )
    roadmap.to_csv(TABLE_DIR / 'official_roadmap_status.csv', index=False)
    write_text(TABLE_DIR / 'official_roadmap_status.md', roadmap.to_markdown(index=False))

    # Per-class F1 table for selected models.
    selected_report_files = {
        'S1 Baseline': REPORT_DIR / 'report_s1_baseline.txt',
        'S2 Best CNB': REPORT_DIR / 'report_s2_CNB.txt',
        'S3A Word2Vec+LR': REPORT_DIR / 'report_s3_R4.txt',
        'S3B GloVe+LR': REPORT_DIR / 'report_s3B_GloVe.txt',
        'S3B BERT+LR': REPORT_DIR / 'report_s3B_BERT.txt',
        'S4 Best LR+Weight': REPORT_DIR / 'report_s4_LR_weight_rp0.5.txt',
        'S4 Optional MLP+W2V': REPORT_DIR / 'report_s4_MLP_word2vec.txt',
    }
    per_class_rows = []
    for model_name, path in selected_report_files.items():
        _, per_cls = parse_report_file(path)
        for emo in LABEL_MAP.values():
            per_class_rows.append({'model': model_name, 'emotion': emo, 'f1': per_cls.get(emo, np.nan)})
    per_class_df = pd.DataFrame(per_class_rows)
    per_class_pivot = per_class_df.pivot(index='model', columns='emotion', values='f1').reset_index()
    per_class_pivot.to_csv(TABLE_DIR / 'per_class_f1_selected_models.csv', index=False)
    write_text(TABLE_DIR / 'per_class_f1_selected_models.md', per_class_pivot.to_markdown(index=False))

    # Section-based organization (copy existing and new outputs into section folders).
    copy_into_section(
        'section1_baseline',
        [
            REPORT_DIR / 'report_s1_baseline.txt',
            TABLE_DIR / 'overall_experiment_metrics.csv',
        ],
    )
    copy_into_section(
        'section2_model_comparison',
        [
            FIG_DIR / 'fig6_s2_model_comparison.png',
            REPORT_DIR / 'report_s2_LR.txt',
            REPORT_DIR / 'report_s2_CNB.txt',
            REPORT_DIR / 'report_s2_DT.txt',
            REPORT_DIR / 'report_s2_RF.txt',
            REPORT_DIR / 'report_s2_OVR-SVC.txt',
            REPORT_DIR / 'report_s2_summary.txt',
            DATA_DIR / 'results_s2_model_comparison.csv',
        ],
    )
    copy_into_section(
        'section3_representation',
        [
            FIG_DIR / 'fig7_s3_repr_comparison.png',
            FIG_DIR / 'fig11_s3b_embeddings.png',
            REPORT_DIR / 'report_s3_R1.txt',
            REPORT_DIR / 'report_s3_R2.txt',
            REPORT_DIR / 'report_s3_R3.txt',
            REPORT_DIR / 'report_s3_R4.txt',
            REPORT_DIR / 'report_s3_summary.txt',
            REPORT_DIR / 'report_s3B_GloVe.txt',
            REPORT_DIR / 'report_s3B_BERT.txt',
            REPORT_DIR / 'report_s3B_summary.txt',
            DATA_DIR / 'results_s3_repr_comparison.csv',
            DATA_DIR / 'results_s3_partb_embeddings.csv',
        ],
    )
    copy_into_section(
        'section4_improvement',
        [
            FIG_DIR / 'fig8_s4_improvement.png',
            FIG_DIR / 'fig9_confusion_matrix.png',
            FIG_DIR / 'fig10_per_class_and_time.png',
            FIG_DIR / 'fig12_s4_ablation.png',
            REPORT_DIR / 'report_s4_CNB.txt',
            REPORT_DIR / 'report_s4_LR_weight_rp0.01.txt',
            REPORT_DIR / 'report_s4_LR_weight_rp0.05.txt',
            REPORT_DIR / 'report_s4_LR_weight_rp0.1.txt',
            REPORT_DIR / 'report_s4_LR_weight_rp0.5.txt',
            REPORT_DIR / 'report_s4_LR_weight_rp1.0.txt',
            REPORT_DIR / 'report_s4_summary.txt',
            REPORT_DIR / 'report_s4_deep_analysis.txt',
            REPORT_DIR / 'report_s4_MLP_word2vec.txt',
            REPORT_DIR / 'report_s4_ablation_A0.txt',
            REPORT_DIR / 'report_s4_ablation_A1.txt',
            REPORT_DIR / 'report_s4_ablation_A2.txt',
            REPORT_DIR / 'report_s4_ablation_A3.txt',
            REPORT_DIR / 'report_s4_ablation_A4.txt',
            REPORT_DIR / 'report_s4_ablation_summary.txt',
            DATA_DIR / 'results_s4_improvement.csv',
            DATA_DIR / 'results_s4_optional_mlp_word2vec.csv',
            DATA_DIR / 'results_s4_ablation.csv',
        ],
    )

    for section_name, desc in {
        'section1_baseline': 'Section 1 — Baseline（baseline 已标注）',
        'section2_model_comparison': 'Section 2 — Model Comparison',
        'section3_representation': 'Section 3 — Representation Comparison（含 Part A 与 Part B）',
        'section4_improvement': 'Section 4 — Improvement / Add-ons / Analysis',
    }.items():
        files = sorted((SECTION_DIR / section_name).iterdir())
        lines = [f'# {desc}', '', '本目录收录该 section 的相关图表、报告和结果数据。', '', '## 文件', '']
        for file in files:
            lines.append(f'- `{file.name}`')
        write_text(SECTION_DIR / section_name / 'README.md', '\n'.join(lines) + '\n')

    summary_lines = [
        '# Additional Experiments Summary',
        '',
        'This run adds Section 3 Part B and the missing Section 4 items.',
        '',
        '## New result files',
        '',
        '- `输出/data/results_s3_partb_embeddings.csv`',
        '- `输出/data/results_s4_optional_mlp_word2vec.csv`',
        '- `输出/data/results_s4_ablation.csv`',
        '- `输出/tables/overall_experiment_metrics.csv`',
        '- `输出/tables/per_class_f1_selected_models.csv`',
        '- `输出/tables/official_roadmap_status.csv`',
        '',
        '## Notes',
        '',
        '- Baseline is explicitly marked in `overall_experiment_metrics.csv`',
        '- Section folders are available under `输出/sections/`',
    ]
    write_text(OUT_ROOT / 'sections' / 'README.md', '\n'.join(summary_lines) + '\n')

    train.unpersist()
    test.unpersist()
    train_w.unpersist()
    spark.stop()
    print('\nDone. Added Section 3 Part B, MLP + Word2Vec, ablation study, and section-based outputs.')


if __name__ == '__main__':
    main()
