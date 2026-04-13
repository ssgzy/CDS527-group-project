# 输出目录说明

本目录存放 Task 1 的图表、评估报告、结构化结果表，以及按 `Section` 重新整理后的引用入口。

## 当前最重要结论
- baseline：`TF-IDF unigram + Logistic Regression`
- 当前主指标：`macro-F1`
- **当前全项目最高 macro-F1：`0.4465`**
- 最优配置：`Section 4 Ablation / A4 / Light cleaning only + TF-IDF + class weight + LR (regParam=0.5)`

## 目录结构

```text
输出/
  data/       各 Section 的原始结果 CSV
  figures/    正式图表 PNG
  reports/    各实验文本报告 TXT
  sections/   按 Section 重新整理后的输出入口
  tables/     汇总表、排名表、per-class F1 表
  sanity_check/ 二次核对脚本的辅助输出
  README.md
```

说明：
- 旧版导出时遗留的根目录图片仍保留，例如 `输出/fig1_label_distribution.png`
- **正式引用时优先使用** `输出/figures/`、`输出/reports/`、`输出/data/`、`输出/tables/`、`输出/sections/`

## 按 Section 快速查看

### Section 1 — Baseline
- 目录：`输出/sections/section1_baseline/`
- 核心文件：
  - `report_s1_baseline.txt`
  - `overall_experiment_metrics.csv`
- 角色标记：
  - `TF-IDF unigram + LR` 已在总表中明确标记为 `baseline`

### Section 2 — Model Comparison
- 目录：`输出/sections/section2_model_comparison/`
- 核心文件：
  - `results_s2_model_comparison.csv`
  - `report_s2_summary.txt`
  - `fig6_s2_model_comparison.png`
- 最优模型：
  - `Complement NaiveBayes`
  - `macro-F1 = 0.3332`

### Section 3 — Representation Comparison
- 目录：`输出/sections/section3_representation/`
- Part A：
  - `results_s3_repr_comparison.csv`
  - `report_s3_summary.txt`
  - `fig7_s3_repr_comparison.png`
- Part B：
  - `results_s3_partb_embeddings.csv`
  - `report_s3B_summary.txt`
  - `fig11_s3b_embeddings.png`
- 结果摘要：
  - `GloVe + LR`：`macro-F1 = 0.3312`
  - `BERT embedding + LR`：`macro-F1 = 0.3420`

### Section 4 — Improvement / Deep Analysis
- 目录：`输出/sections/section4_improvement/`
- 核心文件：
  - `results_s4_improvement.csv`
  - `results_s4_optional_mlp_word2vec.csv`
  - `results_s4_ablation.csv`
  - `report_s4_summary.txt`
  - `report_s4_MLP_word2vec.txt`
  - `report_s4_ablation_summary.txt`
  - `fig8_s4_improvement.png`
  - `fig9_confusion_matrix.png`
  - `fig10_per_class_and_time.png`
  - `fig12_s4_ablation.png`
- 结果摘要：
  - 原 S4 主线最佳：`LR+Weight (rp=0.5)`，`macro-F1 = 0.3453`
  - `MLP + Word2Vec`：`macro-F1 = 0.1885`
  - **Ablation 最优 A4 / Light cleaning only：`macro-F1 = 0.4465`**

## 推荐直接引用的表格

位于 `输出/tables/`：

- `overall_experiment_metrics.csv` / `.md`
  - 全部实验统一总表
  - 包含 `section`、`subsection`、`experiment`、`role`
  - 已明确标出 `baseline`
- `macro_f1_ranking.csv` / `.md`
  - 按 `macro-F1` 排序
  - 适合直接写结论或答辩
- `per_class_f1_selected_models.csv` / `.md`
  - 对比关键模型的各类别 F1
  - 适合解释“为什么某些模型 accuracy 高但 macro-F1 不高”
- `official_roadmap_status.csv` / `.md`
  - 对照 `PySpark.png` 的官方路线图
  - 现在所有此前缺项都已补做，`Ablation study` 与 `MLP + Word2Vec` 已补齐

## 推荐直接引用的结果数字

| 位置 | 配置 | macro-F1 | weighted-F1 | accuracy |
|------|------|---------:|------------:|---------:|
| S1 baseline | TF-IDF unigram + LR | 0.2337 | 0.8590 | 0.8985 |
| S2 best | Complement NaiveBayes | 0.3332 | 0.8455 | 0.8158 |
| S3 Part B best | BERT embedding + LR | 0.3420 | 0.9092 | 0.9323 |
| S4 original best | LR + class weight (rp=0.5) | 0.3453 | 0.8408 | 0.8045 |
| **Current overall best** | **A4 Light cleaning only + TF-IDF + class weight + LR** | **0.4465** | **0.9009** | **0.8910** |

## 解释建议

- 如果老师看的是 **主指标 `macro-F1`**：
  - 当前应以 `A4 Light cleaning only` 作为最优配置
- 如果只看 **accuracy**：
  - `BERT embedding + LR` 更高，达到 `0.9323`
  - 但它几乎不识别 `surprise`、`sad`、`disgust`
  - 因此不应取代 `macro-F1` 作为主结论

## 关联文档
- [[结果索引]]
- [[任务笔记 - Task1 内容梳理]]
- [[任务笔记 - Task1 补做实验]]
- [[实验协议]]
