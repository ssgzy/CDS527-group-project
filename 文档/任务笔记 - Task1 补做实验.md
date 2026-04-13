# 任务笔记 - Task1 补做实验

> 最后更新：2026-04-13 11:25 HKT
> 关联：[[任务笔记 - Task1 内容梳理]] | [[结果索引]] | [[当前状态]] | [[下一步]] | [[会话日志]]

---

## 本轮目标
- 补做此前未完成的 Task 1 实验：
  - Section 3 Part B：`GloVe`、`BERT embedding`
  - Section 4：`MLP + Word2Vec`
  - Section 4：`ablation study`
- 同时重整 `输出/` 目录：
  - 按 `Section` 分类
  - 标出 `baseline`
  - 生成更适合直接引用的总表、F1 表、完成状态表

## 先验判断与实际结果

| 项目 | 开跑前判断 | 实际结果 | 结论 |
|------|------------|----------|------|
| `GloVe + LR` | 可能小幅提升，但不太可能稳定超过原最优 | `macro-F1 = 0.3312` | 判断基本正确 |
| `BERT embedding + LR` | 最有机会提分，但实现成本最高 | `macro-F1 = 0.3420`，`accuracy = 0.9323` | 提升了 accuracy，也接近原最优 macro-F1，但没有超过最终新最优 |
| `MLP + Word2Vec` | 大概率不会优于当前最优 | `macro-F1 = 0.1885` | 判断正确 |
| `ablation study` | 本身不负责提分，只负责分析 | **意外发现更优配置 `A4`，`macro-F1 = 0.4465`** | 说明旧清洗策略可能过强，ablation 实际找到了更优方案 |

## 环境与执行备注
- 使用环境：`conda activate CDS527`
- 依赖补充：
  - `gensim`
  - `transformers`
- 兼容修正：
  - Spark 3.1.2 强制使用 Java 11
  - 强制 `PYSPARK_PYTHON` 与 `PYSPARK_DRIVER_PYTHON` 指向当前 conda Python，避免 driver / worker 版本不一致
- 本轮新增脚本：
  - `工作区/run_additional_experiments.py`

## 本轮新增实验结果

### Section 3 Part B

| 方法 | macro-F1 | weighted-F1 | accuracy | train_sec |
|------|---------:|------------:|---------:|----------:|
| `BERT embedding (bert-base-uncased) + LR` | 0.3420 | 0.9092 | 0.9323 | 5.8 |
| `GloVe (twitter-100d) + LR` | 0.3312 | 0.8886 | 0.9135 | 2.3 |

判断：
- 如果只看 `accuracy`，BERT 很强
- 如果看项目主指标 `macro-F1`，BERT 仍未超过当前最终新最优 `A4`
- GloVe 有帮助，但收益有限

### Section 4 — Optional MLP + Word2Vec

| 方法 | macro-F1 | weighted-F1 | accuracy | train_sec |
|------|---------:|------------:|---------:|----------:|
| `MLP + Word2Vec (dim=100)` | 0.1885 | 0.8432 | 0.8910 | 20.1 |

判断：
- 比 `Word2Vec + LR` 还略差
- 不值得作为最终推荐方案

### Section 4 — Ablation Study

| ID | 配置 | macro-F1 | weighted-F1 | accuracy |
|----|------|---------:|------------:|---------:|
| `A4` | `Light cleaning only` | **0.4465** | **0.9009** | 0.8910 |
| `A2` | `No stopword removal` | 0.3530 | 0.8627 | 0.8459 |
| `A0` | `Full best (clean + stopwords + TF-IDF + class weight)` | 0.3453 | 0.8408 | 0.8045 |
| `A3` | `No IDF` | 0.3453 | 0.8408 | 0.8045 |
| `A1` | `No class weight` | 0.2367 | 0.8617 | 0.9023 |

关键解释：
- `A1` 明确证明：**class weight 仍然重要**
- `A3` 与 `A0` 一样，说明在当前配置下 `IDF` 不是主要增益来源
- `A4` 明显优于 `A0`，说明：
  - 旧版强清洗可能删掉了短文本中的有效信号
  - 在这个 Twitter 数据集上，保留更多原始文本形态更有利于少数类识别

## 当前最重要结论
- 之前没做的内容里，**真正把主指标拉上去的不是 GloVe/BERT/MLP，而是 ablation 里暴露出来的文本清洗策略**
- 如果以课程主线的 `macro-F1` 为准：
  - **当前全项目最优应改为 `A4 Light cleaning only + TF-IDF + class weight + LR`**
  - `macro-F1 = 0.4465`
- 如果只看 `accuracy`：
  - BERT 的 `0.9323` 更高
  - 但它对少数类覆盖太差，不适合作为最终主结论

## 本轮新增输出

### 数据表
- `输出/data/results_s3_partb_embeddings.csv`
- `输出/data/results_s4_optional_mlp_word2vec.csv`
- `输出/data/results_s4_ablation.csv`

### 报告
- `输出/reports/report_s3B_GloVe.txt`
- `输出/reports/report_s3B_BERT.txt`
- `输出/reports/report_s3B_summary.txt`
- `输出/reports/report_s4_MLP_word2vec.txt`
- `输出/reports/report_s4_ablation_A0.txt`
- `输出/reports/report_s4_ablation_A1.txt`
- `输出/reports/report_s4_ablation_A2.txt`
- `输出/reports/report_s4_ablation_A3.txt`
- `输出/reports/report_s4_ablation_A4.txt`
- `输出/reports/report_s4_ablation_summary.txt`

### 图表
- `输出/figures/fig11_s3b_embeddings.png`
- `输出/figures/fig12_s4_ablation.png`

### 汇总表
- `输出/tables/overall_experiment_metrics.csv`
- `输出/tables/macro_f1_ranking.csv`
- `输出/tables/per_class_f1_selected_models.csv`
- `输出/tables/official_roadmap_status.csv`

### 按 Section 整理后的目录
- `输出/sections/section1_baseline/`
- `输出/sections/section2_model_comparison/`
- `输出/sections/section3_representation/`
- `输出/sections/section4_improvement/`

## Notebook 同步策略
- 为避免打乱原有 Section 1–4 的主实验结构，本轮**没有把新代码插回原位置**
- 已将新增实验统一追加到 `工作区/Group_X.code.ipynb` 最底部：
  - `Section 10 — Supplementary Experiments (Appended)`
- 每段新增代码前都先加了 Markdown 说明
- 追加部分目前主要用于：
  - 读取补做实验的结果表
  - 展示新增图表
  - 展示新的总表与排名表
  - 给出补充结论

## 下一步建议
1. 把 `A4` 作为当前最终推荐配置，同步改进 Notebook、PPT、report 的口径
2. 检查 `Group_X_PPT_outline.md` 与正式 PPT 中是否仍沿用旧最优值 `0.3453`
3. 决定是否把 Notebook 重新运行并保存输出，避免提交时只有“干净源文件”
