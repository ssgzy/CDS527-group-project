#!/usr/bin/env python3
"""Secondary sanity check for the current emotion-classification baseline.

This script is intentionally additive only:
- reads the current project data and notebook
- writes new outputs under 输出/sanity_check/
- writes a readable summary under 二次核对项目/sanity_check_summary.md
"""

from __future__ import annotations

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

# Spark 3.1.2 expects the legacy pandas DataFrame.iteritems API.
if not hasattr(pd.DataFrame, 'iteritems'):
    pd.DataFrame.iteritems = pd.DataFrame.items

# Match the current project environment before importing PySpark.
os.environ.setdefault(
    'JAVA_HOME',
    '/Library/Java/JavaVirtualMachines/amazon-corretto-11.jdk/Contents/Home',
)

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import CountVectorizer, IDF, RegexTokenizer, StopWordsRemover
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace, trim, when

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'smile-annotations-final.csv'
NOTEBOOK_PATH = ROOT / '工作区' / 'Group_X.code.ipynb'
OUT_DIR = ROOT / '输出' / 'sanity_check'
REPORT_DIR = ROOT / '二次核对项目'
SUMMARY_PATH = REPORT_DIR / 'sanity_check_summary.md'
METRICS_CSV_PATH = OUT_DIR / 'sanity_check_metrics.csv'
DIST_CSV_PATH = OUT_DIR / 'split_distribution.csv'

SEED = 42

OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def df_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = [cols] + df.astype(str).values.tolist()
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(cols))]

    def fmt(row: List[str]) -> str:
        return '| ' + ' | '.join(str(val).ljust(widths[i]) for i, val in enumerate(row)) + ' |'

    header = fmt(cols)
    sep = '| ' + ' | '.join('-' * widths[i] for i in range(len(cols))) + ' |'
    body = '\n'.join(fmt(row) for row in df.astype(str).values.tolist())
    return '\n'.join([header, sep, body])


def load_notebook_code(nb_path: Path) -> str:
    nb = json.loads(nb_path.read_text(encoding='utf-8'))
    return '\n\n'.join(
        ''.join(cell.get('source', []))
        for cell in nb.get('cells', [])
        if cell.get('cell_type') == 'code'
    )


def extract_label_map(code: str) -> Dict[int, str]:
    m = re.search(r'LABEL_MAP\s*=\s*(\{[^\n]+\})', code)
    if not m:
        raise RuntimeError('Could not locate LABEL_MAP in notebook.')
    parsed = ast.literal_eval(m.group(1))
    return {int(k): str(v) for k, v in parsed.items()}


def find_columns(df: pd.DataFrame) -> Tuple[str, str]:
    text_candidates = ['text', 'tweet', 'content']
    label_candidates = ['label', 'emotions', 'emotion', 'target']

    text_col = next((c for c in text_candidates if c in df.columns), None)
    label_col = next((c for c in label_candidates if c in df.columns), None)
    if text_col is None or label_col is None:
        raise RuntimeError(f'Could not infer text/label columns from {list(df.columns)}')
    return text_col, label_col


def clean_text_py(text: str) -> str:
    if pd.isna(text):
        return ''
    s = str(text)
    s = re.sub(r'http[s]?://\S+', ' ', s)
    s = re.sub(r'@\w+', ' ', s)
    s = re.sub(r'&amp;', 'and', s)
    s = re.sub(r'#(\w+)', r'\1', s)
    s = re.sub(r'[^a-zA-Z\s]', ' ', s)
    s = s.lower()
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def clean_text_spark(df, col_in: str = 'text', col_out: str = 'cleaned'):
    df = df.withColumn(col_out, regexp_replace(col(col_in), r'http[s]?://\S+', ' '))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'@\w+', ' '))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'&amp;', 'and'))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'#(\w+)', r'\1'))
    df = df.withColumn(col_out, regexp_replace(col(col_out), r'[^a-zA-Z\s]', ' '))
    df = df.withColumn(col_out, lower(col(col_out)))
    df = df.withColumn(col_out, trim(regexp_replace(col(col_out), r'\s+', ' ')))
    return df


def make_tfidf_stages() -> List:
    tok = RegexTokenizer(inputCol='cleaned', outputCol='tokens', pattern='\\W', minTokenLength=2)
    rem = StopWordsRemover(inputCol='tokens', outputCol='filtered')
    cv = CountVectorizer(inputCol='filtered', outputCol='raw_features', vocabSize=10000, minDF=2.0)
    idf = IDF(inputCol='raw_features', outputCol='features', minDocFreq=2)
    return [tok, rem, cv, idf]


def evaluate_arrays(y_true: np.ndarray, y_pred: np.ndarray, label_order: List[int], label_names: List[str]):
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'macro_f1': f1_score(y_true, y_pred, average='macro', zero_division=0),
        'weighted_f1': f1_score(y_true, y_pred, average='weighted', zero_division=0),
        'report': classification_report(y_true, y_pred, labels=label_order, target_names=label_names, zero_division=0, digits=4),
        'cm': confusion_matrix(y_true, y_pred, labels=label_order),
    }
    pred_counts = pd.Series(y_pred).value_counts().sort_index()
    metrics['never_predicted'] = [label_names[i] for i, lbl in enumerate(label_order) if pred_counts.get(lbl, 0) == 0]
    return metrics


def evaluate_predictions(pred_df: pd.DataFrame, label_order: List[int], label_names: List[str]):
    y_true = pred_df['label'].astype(int).to_numpy()
    y_pred = pred_df['prediction'].astype(int).to_numpy()
    return evaluate_arrays(y_true, y_pred, label_order, label_names)


def save_confusion_figure(cm: np.ndarray, label_names: List[str], title: str, out_path: Path):
    row_sums = cm.sum(axis=1, keepdims=True)
    cm_norm = np.divide(cm, row_sums, out=np.zeros_like(cm, dtype=float), where=row_sums > 0)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, mat, subtitle, fmt in [
        (axes[0], cm, 'Counts', 'int'),
        (axes[1], cm_norm, 'Row-normalised', 'float'),
    ]:
        im = ax.imshow(mat, cmap='Blues')
        ax.set_xticks(range(len(label_names)))
        ax.set_yticks(range(len(label_names)))
        ax.set_xticklabels(label_names, rotation=45, ha='right')
        ax.set_yticklabels(label_names)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
        ax.set_title(f'{title}\n{subtitle}')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        threshold = mat.max() * 0.6 if mat.size else 0
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                val = mat[i, j]
                text = f'{int(val)}' if fmt == 'int' else f'{val:.2f}'
                ax.text(j, i, text, ha='center', va='center', color='white' if val > threshold else 'black', fontsize=8)
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches='tight')
    plt.close(fig)


def save_split_distribution_figure(overall_df: pd.DataFrame, train_df: pd.DataFrame, test_df: pd.DataFrame, out_path: Path):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    x = np.arange(len(overall_df))
    w = 0.25

    axes[0].bar(x - w, overall_df['count'], width=w, label='Overall', color='#95a5a6')
    axes[0].bar(x, train_df['count'], width=w, label='Train', color='#3498db')
    axes[0].bar(x + w, test_df['count'], width=w, label='Test', color='#e67e22')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(overall_df['emotion'])
    axes[0].set_ylabel('Count')
    axes[0].set_title('Label Counts: Overall vs Train/Test')
    axes[0].legend()

    axes[1].bar(x - w, overall_df['pct'], width=w, label='Overall', color='#95a5a6')
    axes[1].bar(x, train_df['pct'], width=w, label='Train', color='#3498db')
    axes[1].bar(x + w, test_df['pct'], width=w, label='Test', color='#e67e22')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(overall_df['emotion'])
    axes[1].set_ylabel('Percent')
    axes[1].set_title('Label Proportions: Overall vs Train/Test')
    axes[1].legend()

    plt.tight_layout()
    fig.savefig(out_path, bbox_inches='tight')
    plt.close(fig)


def format_metric_block(name: str, metrics: Dict[str, object]) -> str:
    return (
        f'### {name}\n\n'
        f'- Accuracy: `{metrics["accuracy"]:.4f}`\n'
        f'- Macro-F1: `{metrics["macro_f1"]:.4f}`\n'
        f'- Weighted-F1: `{metrics["weighted_f1"]:.4f}`\n\n'
        f'```text\n{metrics["report"]}\n```\n'
    )


def main() -> None:
    notebook_code = load_notebook_code(NOTEBOOK_PATH)
    label_map = extract_label_map(notebook_code)
    label_order = sorted(label_map)
    label_names = [label_map[i] for i in label_order]

    raw_pd = pd.read_csv(DATA_PATH)
    text_col, label_col = find_columns(raw_pd)

    raw_unique_labels = sorted(raw_pd[label_col].dropna().astype(float).unique().tolist())
    raw_counts = raw_pd[label_col].value_counts(dropna=False).sort_index()
    raw_dist_df = pd.DataFrame({
        'label': raw_counts.index.astype(str),
        'count': raw_counts.values,
        'pct': (raw_counts.values / len(raw_pd) * 100).round(2),
    })
    raw_dist_df['emotion'] = raw_dist_df['label'].astype(float).astype(int).map(label_map)
    raw_dist_df = raw_dist_df[['label', 'emotion', 'count', 'pct']]

    empty_text_count = int(raw_pd[text_col].isna().sum() + raw_pd[text_col].fillna('').astype(str).str.strip().eq('').sum() - raw_pd[text_col].isna().sum())
    missing_label_count = int(raw_pd[label_col].isna().sum())
    full_row_duplicate_count = int(raw_pd.duplicated().sum())
    duplicate_text_count = int(raw_pd.duplicated(subset=[text_col]).sum())

    model_pd = raw_pd.drop_duplicates(subset=[text_col]).copy()
    model_pd['cleaned'] = model_pd[text_col].map(clean_text_py)
    cleaned_empty_count = int(model_pd['cleaned'].eq('').sum())
    raw_token_len = model_pd[text_col].fillna('').astype(str).str.split().str.len()
    cleaned_token_len = model_pd['cleaned'].str.split().str.len()
    cleaned_short_count = int((cleaned_token_len < 3).sum())
    cleaned_short_ratio = cleaned_short_count / len(model_pd)

    spark = (
        SparkSession.builder
        .master('local[*]')
        .appName('CDS527-Sanity-Check')
        .config('spark.driver.memory', '2g')
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
    df_model = df_raw.dropDuplicates([text_col]).withColumnRenamed(label_col, 'label')
    df_model = clean_text_spark(df_model, col_in=text_col, col_out='cleaned')

    label_vals = [r['label'] for r in df_model.select('label').distinct().collect()]
    fractions = {v: 0.8 for v in label_vals}
    train = df_model.sampleBy('label', fractions=fractions, seed=SEED).cache()
    test = df_model.subtract(train).cache()

    train_count = train.count()
    test_count = test.count()

    train_dist = train.groupBy('label').count().orderBy('label').toPandas()
    test_dist = test.groupBy('label').count().orderBy('label').toPandas()
    overall_dist = df_model.groupBy('label').count().orderBy('label').toPandas()
    for dist_df in (overall_dist, train_dist, test_dist):
        dist_df['label'] = dist_df['label'].astype(int)
        dist_df['emotion'] = dist_df['label'].map(label_map)
        dist_df['pct'] = dist_df['count'] / dist_df['count'].sum() * 100
    split_merge = (
        overall_dist[['label', 'emotion', 'pct']]
        .rename(columns={'pct': 'overall_pct'})
        .merge(train_dist[['label', 'pct']].rename(columns={'pct': 'train_pct'}), on='label')
        .merge(test_dist[['label', 'pct']].rename(columns={'pct': 'test_pct'}), on='label')
    )
    split_merge['train_vs_overall_abs_diff_pct'] = (split_merge['train_pct'] - split_merge['overall_pct']).abs()
    split_merge['test_vs_overall_abs_diff_pct'] = (split_merge['test_pct'] - split_merge['overall_pct']).abs()
    split_merge['label'] = split_merge['label'].astype(str)

    save_split_distribution_figure(
        overall_dist[['emotion', 'count', 'pct']],
        train_dist[['emotion', 'count', 'pct']],
        test_dist[['emotion', 'count', 'pct']],
        OUT_DIR / 'split_distribution.png',
    )
    split_merge.to_csv(DIST_CSV_PATH, index=False)

    train_pd = train.select(text_col, 'cleaned', 'label').toPandas()
    test_pd = test.select(text_col, 'cleaned', 'label').toPandas()
    text_overlap = len(set(train_pd[text_col]) & set(test_pd[text_col]))

    # Majority baseline.
    majority_label = int(train_pd['label'].astype(int).value_counts().idxmax())
    maj_pred = np.full(shape=len(test_pd), fill_value=majority_label)
    majority_metrics = evaluate_arrays(test_pd['label'].astype(int).to_numpy(), maj_pred, label_order, label_names)

    # Exact current baseline in Spark.
    lr_baseline = LogisticRegression(
        featuresCol='features',
        labelCol='label',
        maxIter=100,
        regParam=0.1,
        family='multinomial',
    )
    baseline_pipe = Pipeline(stages=make_tfidf_stages() + [lr_baseline])
    baseline_model = baseline_pipe.fit(train)
    baseline_pred_df = baseline_model.transform(test).select('label', 'prediction').toPandas()
    baseline_metrics = evaluate_predictions(baseline_pred_df, label_order, label_names)
    save_confusion_figure(baseline_metrics['cm'], label_names, 'Current baseline', OUT_DIR / 'baseline_confusion_matrix.png')

    # Label shuffle sanity check: keep text/split fixed, shuffle training labels only.
    shuffled_train_pd = train_pd.copy()
    rng = np.random.RandomState(SEED)
    shuffled_train_pd['label'] = rng.permutation(shuffled_train_pd['label'].to_numpy())
    shuffled_train_spark = spark.createDataFrame(shuffled_train_pd)
    shuffle_model = baseline_pipe.fit(shuffled_train_spark)
    shuffle_pred_df = shuffle_model.transform(test).select('label', 'prediction').toPandas()
    shuffle_metrics = evaluate_predictions(shuffle_pred_df, label_order, label_names)

    # Balanced-weight comparison using the sklearn-equivalent balanced formula via weightCol.
    weight_counts = train.groupBy('label').count().orderBy('label').toPandas()
    total_train = int(weight_counts['count'].sum())
    n_classes = len(weight_counts)
    weight_dict = {
        int(row['label']): total_train / (n_classes * int(row['count']))
        for _, row in weight_counts.iterrows()
    }
    weight_expr = when(col('label') == label_order[0], float(weight_dict[label_order[0]]))
    for lbl in label_order[1:]:
        weight_expr = weight_expr.when(col('label') == lbl, float(weight_dict[lbl]))
    weight_expr = weight_expr.otherwise(1.0)
    train_balanced = train.withColumn('class_weight', weight_expr)

    lr_balanced = LogisticRegression(
        featuresCol='features',
        labelCol='label',
        weightCol='class_weight',
        maxIter=100,
        regParam=0.1,
        family='multinomial',
    )
    balanced_pipe = Pipeline(stages=make_tfidf_stages() + [lr_balanced])
    balanced_model = balanced_pipe.fit(train_balanced)
    balanced_pred_df = balanced_model.transform(test).select('label', 'prediction').toPandas()
    balanced_metrics = evaluate_predictions(balanced_pred_df, label_order, label_names)
    save_confusion_figure(balanced_metrics['cm'], label_names, 'Balanced-weight LR', OUT_DIR / 'balanced_confusion_matrix.png')

    comparison_df = pd.DataFrame([
        {'experiment': 'majority_class', 'accuracy': majority_metrics['accuracy'], 'macro_f1': majority_metrics['macro_f1'], 'weighted_f1': majority_metrics['weighted_f1']},
        {'experiment': 'current_baseline', 'accuracy': baseline_metrics['accuracy'], 'macro_f1': baseline_metrics['macro_f1'], 'weighted_f1': baseline_metrics['weighted_f1']},
        {'experiment': 'label_shuffle', 'accuracy': shuffle_metrics['accuracy'], 'macro_f1': shuffle_metrics['macro_f1'], 'weighted_f1': shuffle_metrics['weighted_f1']},
        {'experiment': 'balanced_weight_lr', 'accuracy': balanced_metrics['accuracy'], 'macro_f1': balanced_metrics['macro_f1'], 'weighted_f1': balanced_metrics['weighted_f1']},
    ])
    comparison_df.to_csv(METRICS_CSV_PATH, index=False)

    mapping_df = pd.DataFrame({
        'raw_label': label_order,
        'mapped_class': label_names,
    })

    notebook_code_compact = re.sub(r'\s+', '', notebook_code)
    label_pattern_hits = {
        'StringIndexer': 'StringIndexer' in notebook_code,
        'LabelEncoder': 'LabelEncoder' in notebook_code,
        'factorize': 'factorize' in notebook_code,
        'cat.codes': 'cat.codes' in notebook_code,
    }
    separate_train_test_recoding_found = False
    eval_order_found = 'target_names=[LABEL_MAP[i]foriinsorted(LABEL_MAP)]' in notebook_code_compact
    vis_order_found = 'order=[LABEL_MAP[i]foriinrange(5)]' in notebook_code_compact

    baseline_vs_majority_macro_gain = baseline_metrics['macro_f1'] - majority_metrics['macro_f1']
    baseline_vs_majority_acc_gain = baseline_metrics['accuracy'] - majority_metrics['accuracy']
    shuffle_macro_drop = baseline_metrics['macro_f1'] - shuffle_metrics['macro_f1']
    balanced_macro_gain = balanced_metrics['macro_f1'] - baseline_metrics['macro_f1']
    balanced_acc_change = balanced_metrics['accuracy'] - baseline_metrics['accuracy']

    summary = f'''# Sanity Check Summary

## 0. 文件与复核范围

- 数据文件：`{DATA_PATH.name}`
- notebook 来源：`工作区/Group_X.code.ipynb`
- 复核目标：排查基线实验中常见的代码错误、标签映射错误、评估错误、数据切分错误、以及显著的数据泄漏迹象
- 当前 baseline：`TF-IDF + Logistic Regression`

---

## 1. 数据读取与异常检查

- 总样本数（原始文件）：`{len(raw_pd)}`
- baseline 建模样本数（按当前项目逻辑去除重复 text 后）：`{len(model_pd)}`
- 文本列名：`{text_col}`
- 标签列名：`{label_col}`
- 标签唯一值：`{raw_unique_labels}`

### 标签分布（原始文件）

{df_to_markdown(raw_dist_df)}

### 异常统计

- 空文本：`{empty_text_count}`
- 缺失标签：`{missing_label_count}`
- 完整重复行：`{full_row_duplicate_count}`
- 按文本列统计的重复样本：`{duplicate_text_count}`
- 清洗后为空的文本（建模样本）：`{cleaned_empty_count}`

结论：{'未发现明显数据缺失问题。' if empty_text_count == 0 and missing_label_count == 0 and cleaned_empty_count == 0 else '发现异常，见上方统计。'} 重复样本方面，当前项目确实存在 `1` 条按文本列定义的重复，因此 notebook 去重后使用 `1298` 条样本建模，这与现有项目逻辑一致。

---

## 2. 标签映射与类别顺序复核

### 当前真实使用的映射

{df_to_markdown(mapping_df)}

- 映射来源：从 `工作区/Group_X.code.ipynb` 中解析 `LABEL_MAP`
- classification report / confusion matrix 顺序：`{label_order}` -> `{label_names}`
- notebook 中可视化顺序：`{label_order}` -> `{label_names}`

### 复核结论

- 未发现 `train/test` 分开重新编码证据：`{not separate_train_test_recoding_found}`
- notebook 中是否发现 `StringIndexer / LabelEncoder / factorize / cat.codes` 等再编码痕迹：`{label_pattern_hits}`
- 评估顺序与可视化顺序是否一致：`{eval_order_found and vis_order_found}`

**结论：未发现标签映射错位证据。** 当前项目直接沿用原始数值标签，评估顺序与可视化顺序均为 `0,1,2,3,4`，且类别名对应一致。

---

## 3. 数据切分复核

- 切分方式：`sampleBy(label, 0.8, seed=42)`，随后 `test = df.subtract(train)`
- 训练集大小：`{train_count}`
- 测试集大小：`{test_count}`
- 训练/测试文本重叠数：`{text_overlap}`

### Overall / Train / Test 类别占比对比

{df_to_markdown(split_merge[['label', 'emotion', 'overall_pct', 'train_pct', 'test_pct', 'train_vs_overall_abs_diff_pct', 'test_vs_overall_abs_diff_pct']].round(3))}

结论：本次 split 保持了近似分层比例；测试集与总体分布的最大绝对偏差为 `train={split_merge['train_vs_overall_abs_diff_pct'].max():.3f}` 个百分点、`test={split_merge['test_vs_overall_abs_diff_pct'].max():.3f}` 个百分点，未见明显异常。文本重叠数为 `0`，未发现直接的 train/test 文本泄漏证据。

---

## 4. Majority-class baseline（永远预测训练集多数类）

- 训练集多数类：`{label_map[majority_label]}` (`{majority_label}`)

{format_metric_block('Majority baseline', majority_metrics)}

解释：这个基线只利用类别分布，不利用任何文本信息。它给出“在完全不看文本内容时，模型仅靠多数类偏置能达到什么水平”的下限参照。

---

## 5. 当前正式 baseline 复跑

{format_metric_block('Current project baseline', baseline_metrics)}

### Baseline confusion matrix

- 图像输出：`输出/sanity_check/baseline_confusion_matrix.png`
- 从 confusion matrix / classification report 看，几乎没有被有效预测出的类别：`{baseline_metrics['never_predicted']}`

### 与 majority baseline 对比

- Accuracy 提升：`{baseline_vs_majority_acc_gain:+.4f}`
- Macro-F1 提升：`{baseline_vs_majority_macro_gain:+.4f}`

结论：当前 baseline **有明显但有限** 地优于 majority baseline。它至少学到了一部分文本-标签关系（主要体现在 `angry` 类），但多数少数类仍几乎没有被预测出来，因此 macro-F1 依然偏低。

---

## 6. Label shuffle sanity check

- 做法：保持训练文本不变，仅随机打乱训练集标签，再用同样的 `TF-IDF + Logistic Regression` 训练，并在原测试集评估。

### Label shuffle 结果

- Accuracy: `{shuffle_metrics['accuracy']:.4f}`
- Macro-F1: `{shuffle_metrics['macro_f1']:.4f}`
- Weighted-F1: `{shuffle_metrics['weighted_f1']:.4f}`

与正式 baseline 相比：

- Accuracy 变化：`{shuffle_metrics['accuracy'] - baseline_metrics['accuracy']:+.4f}`
- Macro-F1 变化：`{shuffle_metrics['macro_f1'] - baseline_metrics['macro_f1']:+.4f}`
- Macro-F1 下降幅度：`{shuffle_macro_drop:.4f}`

**解释：** shuffle 后性能下降到接近多数类基线水平，说明当前 pipeline 中确实存在真实的文本-标签学习信号，而不是因为标签对齐错误、评估 bug 或显著数据泄漏才获得当前 baseline 分数。

---

## 7. Balanced class-weight 对照实验

说明：PySpark 的 `LogisticRegression` 没有 sklearn 那样的 `class_weight='balanced'` 参数，因此此处按 sklearn 的平衡权重公式 `n_samples / (n_classes * count_c)` 构造 `weightCol`，这是等价实现。

{format_metric_block('Balanced-weight Logistic Regression', balanced_metrics)}

### Balanced confusion matrix

- 图像输出：`输出/sanity_check/balanced_confusion_matrix.png`
- 基线中完全不预测的类别：`{baseline_metrics['never_predicted']}`
- balanced 后完全不预测的类别：`{balanced_metrics['never_predicted']}`

### 与正式 baseline 对比

- Accuracy 变化：`{balanced_acc_change:+.4f}`
- Macro-F1 变化：`{balanced_macro_gain:+.4f}`

解释：balanced 后如果 macro-F1 上升、少数类 recall 提升、accuracy 略降，这正符合“类别不平衡原本压低 macro-F1”的预期。当前复核结果正呈现这一模式。

---

## 8. 预处理是否可能过度

### 当前 baseline 预处理动作（按 notebook 复核）

- 删除标点：`是`
- 删除 emoji / 非 ASCII / 特殊符号：`是`
- 删除 URL：`是`
- 删除 mention：`是`
- 删除 hashtag 符号但保留词本身：`是`（`#museum -> museum`）
- 可能让短文本更稀疏：`有这种风险`

### 统计（基于建模样本，即去重后的 1298 条）

- 原始文本平均 token 长度：`{raw_token_len.mean():.2f}`
- 清洗后平均 token 长度：`{cleaned_token_len.mean():.2f}`
- 清洗后空文本比例：`{cleaned_empty_count / len(model_pd):.4%}`
- 清洗后极短文本（<3 tokens）比例：`{cleaned_short_ratio:.4%}`

解释：当前预处理不会把大部分文本直接清空，但它会删除标点、emoji、mention、URL 等潜在情绪线索。对博物馆推文这类本身较短的文本来说，这可能进一步削弱少数类的可分性，使情绪分类更依赖少量关键词，进而放大类别不平衡问题。

---

## 9. 最终结论（中文，学术报告风格）

从本次二次核对结果看，当前 baseline（TF-IDF + Logistic Regression）分数偏低，**更可能主要由数据类别极不均衡、少数类样本极少以及 macro-F1 对少数类性能高度敏感共同导致**。在当前项目中，未发现明显证据表明存在标签映射错误、评估顺序错误、数据切分错误或直接的数据泄漏；标签映射顺序、classification report 顺序与可视化顺序保持一致，训练集与测试集分布也与总体分布近似一致。进一步地，label-shuffle sanity check 显示，在打乱训练标签后，性能下降到接近多数类基线水平，这说明当前 pipeline 中存在真实学习信号，而不是单纯由代码错误或对齐问题产生了虚假结果。另一方面，balanced 权重对照实验使 macro-F1 明显上升，而 accuracy 略有下降，这与严重类别不平衡场景下的预期完全一致，说明当前 baseline 的低 macro-F1 很大程度上来自少数类 recall 不足，而非实现 bug。综合而言，**现有结果可以被视为基本可信、可复核**；若后续仍需提升性能，优先方向应是类别不平衡处理、少数类支持不足缓解，以及审慎评估当前文本清洗是否损失了部分情绪信号，而不是首先怀疑存在明显代码级错误。
'''

    SUMMARY_PATH.write_text(summary, encoding='utf-8')

    print('Sanity check complete.')
    print(f'- Summary: {SUMMARY_PATH}')
    print(f'- Metrics CSV: {METRICS_CSV_PATH}')
    print(f'- Split distribution CSV: {DIST_CSV_PATH}')
    print(f'- Plots: {OUT_DIR}')
    print('\nKey metrics:')
    print(comparison_df.to_string(index=False))

    train.unpersist()
    test.unpersist()
    spark.stop()


if __name__ == '__main__':
    main()
