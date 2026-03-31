# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an academic group project for CDS527 (Big Data Analytics – Language Models) at Lingnan University, Term 2 2025-2026. It has two deliverables:

- **Task 1 (30%):** Build a text classification decision support system using the SMILE Twitter Emotion Dataset
- **Task 2 (10%):** Case study on Google's Big Data approach
- **Oral Presentation (20%)**

**Submission deadline:** 30 April 2025 23:59 HKT *(deadline year may be a typo — confirm with instructor)*

## Critical Constraint: PySpark Required

**All Task 1 code must use PySpark as the primary tool.** Heavy reliance on standard Python results in grade deductions. Use `pyspark.ml` for all ML pipelines, feature engineering, and model training.

## Environment Setup

**All code runs in the `CDS527` conda environment** (Python 3.10.19, PySpark 3.1.2, JupyterLab 4.5.3).

```bash
conda activate CDS527
jupyter lab
```

Verify PySpark is available:

```bash
conda run -n CDS527 python3 -c "import pyspark; print(pyspark.__version__)"
# Expected: 3.1.2
```

Verify core ML components:

```bash
conda run -n CDS527 python3 -c "
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, CountVectorizer, IDF, HashingTF, Word2Vec
from pyspark.ml.classification import LogisticRegression, NaiveBayes, DecisionTreeClassifier, RandomForestClassifier, MultilayerPerceptronClassifier, OneVsRest, LinearSVC
from pyspark.ml import Pipeline
print('OK')
"
```

Extract DOCX files to text (macOS):

```bash
textutil -convert txt 'Group_Project_2026_T2 .docx' -output 'tmp/docs/Group_Project_2026_T2.txt'
```

## Dataset

**File:** `smile-annotations-final.csv` — 1,299 tweets from 13 British museum Twitter accounts (2013–2015)

**Label distribution (severely imbalanced):**
- happy (3.0): ~89%
- angry (1.0): ~4.4%
- sad (4.0): ~2.8%
- surprise (0.0): ~2.7%
- disgust (2.0): ~1.0%

*Note: The SMILE dataset documentation describes 3,085 tweets; the actual CSV has 1,299. This discrepancy is unresolved.*

The evaluation metric and data split method must be **consistent across all experiments** — these haven't been confirmed with the instructor yet.

## Task 1 Architecture

**Baseline pipeline:**
```
RegexTokenizer → StopWordsRemover → CountVectorizer → IDF → LogisticRegression
```

**Experiment matrix (all using PySpark Pipelines):**

1. **Feature representation comparison** (hold model = LogisticRegression):
   - CountVectorizer + IDF
   - HashingTF + IDF
   - Word2Vec

2. **Model comparison** (hold best features):
   - LogisticRegression, NaiveBayes, DecisionTreeClassifier, RandomForestClassifier, MultilayerPerceptronClassifier

3. **Hyperparameter tuning** on top combinations

4. **Baseline improvement experiments:**
   - NGram features, vocabulary tuning, class imbalance handling, text cleaning

**Notebook structure (planned):**
1. Background & task definition
2. Data loading, schema, label explanation
3. Data quality & EDA (bar charts, word clouds, distributions)
4. Unified preprocessing pipeline
5. Baseline model
6. Feature representation comparison
7. Model comparison
8. Hyperparameter tuning
9. Improvement experiments
10. Final results & conclusions
11. ≤300-word summary table

## Submission Files

| File | Description |
|------|-------------|
| `Group_X.code.ipynb` | Jupyter Notebook with all Task 1 code |
| `Group_X.report.docx` | Case study report (max 3 pages) |
| `Group_X.present.pptx` | Presentation slides |
| `Group_X.gai.docx` | GAI declaration sheet |
| `work_distribution.docx` | Per-student work breakdown (individual) |

## Documentation

Project planning docs live in `文档/` (Obsidian notes, in Chinese). Key files:
- `文档/当前状态.md` — current status and what's pending
- `文档/任务笔记 - Task1 内容梳理.md` — detailed Task 1 breakdown and checklist
- `文档/问题与坑点.md` — known issues and unresolved questions
- `日志/会话日志.md` — execution log with timestamps

## Open Issues

1. Deadline year typo (says 2025, course is 2025-2026 T2) — confirm with instructor
2. Data split method and evaluation metric not yet specified — **do not finalize experiments until confirmed**
3. Dataset size discrepancy (doc: 3,085 vs actual: 1,299 rows)
4. Submission file count mismatch in the assignment spec (says "three files", lists five)
