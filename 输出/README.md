# 输出目录说明

本目录存放 Task 1 全部实验的可视化图表、文本报告和结果数据。
目录结构：

```
输出/
  figures/   可视化图表（PNG）
  reports/   文本评估报告（TXT）
  data/      结构化结果数据（CSV）
  README.md  本文档
```

---

 ## figures/ — 可视化图表

### EDA 系列

| 文件                            | 内容说明                                                                                    |
| ----------------------------- | --------------------------------------------------------------------------------------- |
| `fig1_label_distribution.png` | 标签分布图（左：各类计数柱状图，右：占比饼图）。直观展示数据集严重不平衡：happy 占 89.1%，disgust 仅 1%。                        |
| `fig2_word_count.png`         | 文本词数分布（左：整体直方图，含均值/中位数线；右：按情绪类别叠加直方图）。少数类（angry/disgust/sad）平均词数显著高于 happy，说明负面情绪表达更啰嗦。 |
| `fig3_wordcount_boxplot.png`  | 各情绪类别词数箱线图，直观对比每类文本长度的分布范围与异常值。                                                         |
| `fig4_text_noise.png`         | 文本噪声特征统计（URL/@ 提及/# 标签/非 ASCII/HTML 实体），横向柱状图。所有推文均含 @ 提及，45.5% 含 URL，说明预处理必须处理这些噪声。    |
| `fig5_wordclouds.png`         | 5 类情绪各自的词云图（2×3 布局）。预处理已去除 URL/@/标点，展示各类高频情感词汇。                                         |

### 实验结果系列

| 文件 | 内容说明 |
|------|---------|
| `fig6_s2_model_comparison.png` | Section 2 模型比较图（左：macro-F1 单项柱状图；右：macro-F1 / weighted-F1 / accuracy 三指标并排对比）。可清楚看到 accuracy 的误导性——RF accuracy=89% 但 macro-F1 最低。 |
| `fig7_s3_repr_comparison.png` | Section 3 表示方法比较图（左：macro-F1 柱状图含 Baseline 参考线；右：三指标对比）。R1/R2/R3 三柱完全等高，视觉上呈现固定 LR 下 BOW 系列特征无差异的实验结果；R4（Word2Vec）柱最低。 |
| `fig8_s4_improvement.png` | Section 4 改进结果（左：各配置 macro-F1 柱状图含双参考线；右：LR+ClassWeight regParam 灵敏度折线图）。最优 LR+Weight(rp=0.5)=0.3453 超越双参考线。 |
| `fig9_confusion_matrix.png` | 最优模型（LR+Weight rp=0.5）混淆矩阵（左：计数；右：行归一化）。可清晰看到 happy 仍占主体，但少数类 recall 有所提升；主要混淆对：happy→surprise（18），happy→sad（8）。 |
| `fig10_per_class_and_time.png` | 左：最优模型 per-class precision/recall/F1 分组柱状图；右：全实验训练时间 vs macro-F1 散点图（灰色=历史实验，红色=S4 新增）。 |

---

## reports/ — 文本评估报告

### EDA 报告

| 文件 | 内容说明 |
|------|---------|
| `report_eda.txt` | EDA 核心统计摘要：样本规模、标签分布（含百分比）、词数统计（min/max/mean/median/std）、各类别均值词数、文本噪声特征汇总。 |

### Section 1 — Baseline

| 文件 | 内容说明 |
|------|---------|
| `report_s1_baseline.txt` | Baseline（TF-IDF unigram + LR）完整评估报告：Pipeline 配置、切分参数、三项指标、per-class precision/recall/F1/support，含结果解读说明及 LR 优化警告记录。 |

### Section 2 — Model Comparison

| 文件 | 内容说明 |
|------|---------|
| `report_s2_LR.txt` | LR（Baseline 参考）per-class 报告：macro-F1=0.2337，仅 angry 有少量识别（F1=0.22）。 |
| `report_s2_CNB.txt` | Complement NaiveBayes per-class 报告：macro-F1=0.3332（Section 2 最优），angry F1=0.55，sad F1=0.12，surprise F1=0.09。 |
| `report_s2_DT.txt` | Decision Tree per-class 报告：macro-F1=0.2947，angry F1=0.52，训练速度快（2.9s）。 |
| `report_s2_RF.txt` | Random Forest per-class 报告：macro-F1=0.1889（最差），所有少数类均为 0，accuracy=89% 完全误导。 |
| `report_s2_OVR-SVC.txt` | OneVsRest + LinearSVC per-class 报告：macro-F1=0.3142（Section 2 第二），surprise F1=0.22，耗时 129.7s。 |
| `report_s2_summary.txt` | Section 2 五模型汇总对比表（macro-F1 / weighted-F1 / accuracy / 耗时），一行一模型。 |
| `report_s3_R1.txt` | Section 3 — TF-IDF unigram + LR（与 S1 Baseline 一致，作为 S3 参考对照）。 |
| `report_s3_R2.txt` | Section 3 — TF-IDF 1,2-gram + LR。结果与 R1 完全相同，验证 bigram 无增益。 |
| `report_s3_R3.txt` | Section 3 — CountVectorizer（无 IDF）+ LR。结果与 R1/R2 完全相同。 |
| `report_s3_R4.txt` | Section 3 — Word2Vec (dim=100) + LR。macro-F1=0.1889，最差，angry F1=0。 |
| `report_s3_summary.txt` | Section 3 四方法汇总对比表。 |
| `report_s4_LR_weight_rp0.01.txt` | Section 4 — LR+Weight (regParam=0.01) per-class 报告：macro-F1=0.3313。 |
| `report_s4_LR_weight_rp0.05.txt` | Section 4 — LR+Weight (regParam=0.05) per-class 报告：macro-F1=0.3375。 |
| `report_s4_LR_weight_rp0.1.txt` | Section 4 — LR+Weight (regParam=0.1) per-class 报告：macro-F1=0.3331。 |
| `report_s4_LR_weight_rp0.5.txt` | Section 4 — **LR+Weight (regParam=0.5)**，全项目最优：macro-F1=**0.3453**，angry F1=0.56，surprise F1=0.14，sad F1=0.12。 |
| `report_s4_LR_weight_rp1.0.txt` | Section 4 — LR+Weight (regParam=1.0) per-class 报告：macro-F1=0.3349。 |
| `report_s4_CNB.txt` | Section 4 — CNB S2 参考（重跑验证）：macro-F1=0.3332，结果与 S2 一致。 |
| `report_s4_summary.txt` | Section 4 全配置汇总对比表（含双参考线数值）。 |
| `report_s4_deep_analysis.txt` | Section 4 深度分析报告：per-class 指标、混淆矩阵（文字版）、hardest misclassification pairs Top 10。 |

---

## data/ — 结构化结果数据

| 文件 | 内容说明 | 列说明 |
|------|---------|--------|
| `results_s2_model_comparison.csv` | Section 2 模型比较结果（可用 Excel/pandas 打开）。每行一个模型，包含 short（简称）、display（全称）、macro_f1、weighted_f1、accuracy、train_sec（训练耗时秒）。 |
| `results_s3_repr_comparison.csv` | Section 3 表示方法比较结果，同格式。注意 R1/R2/R3 的 macro_f1 完全相同（0.2337），为项目在固定 LR 设置下的关键实验结果。 |
| `results_s4_improvement.csv` | Section 4 改进方法结果（LR+Weight × 5 regParam + CNB reference），列含 display、type、regParam、macro_f1、weighted_f1、accuracy、train_sec。 |

---

## 实验协议（查阅）

所有实验遵循统一协议，见 `文档/实验协议.md`：
- 数据：`smile-annotations-final.csv`，去 text 重复后 **1298 行**
- 切分：stratified 80/20，**seed=42**，train=1032 / test=266
- 主指标：**macro-F1**（sklearn，等权平均 5 类）
- 辅助：weighted-F1、accuracy
