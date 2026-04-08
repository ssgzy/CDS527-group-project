# 任务笔记 - Task1 内容梳理

## 任务目标
- 梳理 Task 1 的正式要求、硬性约束、交付内容和可执行结构
- 明确 Jupyter Notebook 至少需要覆盖哪些部分
- 为后续 PySpark 实现、实验记录和分工提供框架

## 来源文件
- `tmp/docs/Group_Project_2026_T2.txt`
- `tmp/docs/SMILE_Twitter_Emotion_Dataset.txt`
- `smile-annotations-final.csv`
- [[任务笔记 - 阅读作业要求]]
- [[数据说明]]

## Task 1 的本质
- 用老师给定的 business textual dataset 构建一个文本分类决策支持系统
- 目标不是只训练一个模型，而是完成一套包含基线、比较、调参、可视化与改进实验的完整分析流程
- 最终主交付物是一个 `Jupyter Notebook`

## Task 1 必做内容
1. 数据与任务定义
   - 说明数据来源、字段、标签和分类任务
   - 明确老师指定的 data split 与 evaluation metric
   - 说明任何预处理假设
2. Baseline model
   - 至少实现一个基础模型
   - 课程文档示例是 logistic regression
3. 模型比较
   - 比较多种 data analytics model
   - 文档举例有 decision tree、gradient boosting tree 等
   - 实际选型必须兼顾 PySpark 可实现性和多分类适配性
4. 词表示或特征表示比较
   - 文档举例有 BERT、GloVe、Word2Vec
   - 实务上应优先选择 PySpark 主导下可落地的方法
   - 可考虑 TF-IDF、CountVectorizer、HashingTF、Word2Vec 作为核心比较对象
5. 超参数调优
   - 对不同模型和特征方法进行调参
   - 报告最佳参数组合和对应分数
6. 数据统计与可视化
   - 需要有图表和统计描述
   - 可包含类别分布、文本长度分布、高频词、词云、集中趋势和离散程度等
7. Baseline 改进方法探索
   - 评分会看新颖性、多样性、实现难度和效果提升
   - 可考虑文本清洗策略、n-gram、特征组合、类别不平衡处理、权重或采样方案等
8. 简短总结说明
   - Notebook 中需附一个短表格和或少于 300 字的说明
   - 概述模型、超参数、可视化方法、分数和关键结论

## Notebook 建议结构
1. 项目背景与任务定义
2. 数据读取、Schema 与标签说明
3. 数据质量检查与基础 EDA
4. 统一预处理与特征工程管线
5. Baseline 模型
6. 特征表示比较
7. 模型比较
8. 超参数调优
9. 改进方法实验
10. 最终结果对比与结论
11. 少于 300 字的总结表格或文字

## 官方实验大纲（来源：PySpark.png）

`PySpark.png` 是本次项目的官方实验路线图，定义了 4 个 Section：

### Section 1 — Baseline
| # | 分类器 | 特征表示 | 备注 |
|---|--------|---------|------|
| 1 | Logistic Regression | TF-IDF (unigram) | baseline |

### Section 2 — Model Comparison under the Same Features
固定特征：TF-IDF

| # | 分类器 |
|---|--------|
| 1 | Logistic Regression |
| 2 | **Complement Naive Bayes** |
| 3 | Decision Tree |
| 4 | Random Forest |
| 5 | **OneVsRest + LinearSVC** |

> 注意：Section 2 使用 Complement NaiveBayes（不是普通 NaiveBayes），以及 OneVsRest + LinearSVC

### Section 3 — Representation Comparison under the Same Classifier
固定分类器：Logistic Regression

**Part A（PySpark 原生可实现）：**
| # | 特征表示 |
|---|---------|
| 1 | TF-IDF (unigram) |
| 2 | TF-IDF (1,2-gram) |
| 3 | CountVectorizer |
| 4 | Word2Vec |

**Part B（可选，超出当前核心实验矩阵范围，本次 Task 1 不纳入）：**
| # | 特征表示 | 状态 |
|---|---------|------|
| 5 | GloVe | ❌ 不纳入（需外部权重，超出 PySpark 原生主线） |
| 6 | BERT embedding | ❌ 不纳入（需外部预训练模型，超出 PySpark 原生主线） |

> Part B 可在报告"局限性与未来方向"中提及，但不作为正式对比实验

### Section 4 — Improvement, Deep Analysis, and High-Score Add-ons

**Part A — Improvement methods：**
- Fine-grained text cleaning
- Class weighting / imbalance handling
- Hyperparameter tuning
- （Optional）MLP + Word2Vec

**Part B — Analysis methods：**
- Confusion matrix
- Per-class precision / recall / F1
- Hardest class pairs
- Ablation study
- Training time vs performance trade-off

---

## 环境确认（2026-03-31 更新）
- conda 环境：`CDS527`
- Python 版本：`3.10.19`
- **PySpark 版本：`3.1.2`**（注：旧记录中 4.1.1 为系统全局版本，项目实际使用 CDS527 环境中的 3.1.2）
- JupyterLab：`4.5.3`
- 核心组件确认可用：
  - `RegexTokenizer`, `StopWordsRemover`, `CountVectorizer`, `IDF`, `HashingTF`, `Word2Vec`
  - `LogisticRegression`, `NaiveBayes`, `DecisionTreeClassifier`, `RandomForestClassifier`
  - `OneVsRest`, `LinearSVC`, `MultilayerPerceptronClassifier`
- 启动方式：`conda run -n CDS527` 或激活 CDS527 环境后运行 Jupyter

## 实验矩阵执行结果（对应 PySpark.png）
1. **Section 1**：TF-IDF + LR（baseline）→ macro-F1=0.2337 ✅
2. **Section 2**：TF-IDF + {LR, CNB, DT, RF, OVR-SVC}→ 最优 CNB=0.3332 ✅
3. **Section 3A**：LR + {TF-IDF unigram, TF-IDF 1,2-gram, CountVectorizer, Word2Vec}→ 固定 LR 下 BOW 系列无差异 ✅
4. **Section 3B**：❌ 不纳入（GloVe/BERT 超出 PySpark 原生主线范围）
5. **Section 4A**：LR + 逆频率类别权重，regParam 调参 → 最优 LR+Weight rp=0.5，macro-F1=0.3453 ✅
6. **Section 4B**：混淆矩阵、per-class 指标、最难混淆对、训练时间 vs 性能 ✅

## 建议实验记录字段
- `experiment_id`
- `data_version`
- `split_version`
- `metric`
- `preprocess`
- `feature_method`
- `model`
- `hyperparameters`
- `score`
- `notes`

## 完成判定清单
- ✅ 已说明数据、标签、任务和实验口径
- ✅ 已实现至少一个 baseline（TF-IDF + LR，macro-F1=0.2337）
- ✅ 已完成多模型比较（5 种分类器，Section 2）
- ✅ 已完成多特征表示比较（4 种表示方法，Section 3A）
- ✅ 已完成超参数调优并记录最佳结果（regParam 5 值调参，Section 4A）
- ✅ 已完成 EDA 与可视化（fig1–fig5，EDA 报告）
- ✅ 已完成至少一组 baseline 改进实验（LR + 类别权重，Section 4A）
- ✅ 已给出最终结果对比表（Notebook Section 9，输出/data/ CSV）
- ✅ 已写出少于 300 字的总结说明（Notebook Section 9，298 词）

## 硬性约束
- 代码必须以 PySpark 为主
- 整个项目必须使用同一套 data split
- 整个项目必须使用同一套 evaluation metric
- 不能把大量核心实现写成标准 Python 后再包装成 Notebook

## 最终结论（2026-03-31）
- Task 1 所有 8 个必做内容已全部完成 ✅
- Notebook `Group_X.code.ipynb` Section 0–9 全部就绪
- 最优系统：LR + TF-IDF unigram + 逆频率类别权重（regParam=0.5），macro-F1=**0.3453**
- 关键发现：类别不平衡处理（类别权重）比特征表示选择更有效；accuracy 在此数据集上完全不可信

## 2026-04-01 文件审计结论
- `工作区/Group_X.code.ipynb` 已包含 Section 0–9，Task 1 主线结构完整
- `输出/figures/`、`输出/reports/`、`输出/data/` 中已存在与 S1–S4 对应的图表、报告和 CSV
- 当前保存的 Notebook 未保留 `execution_count` 和 cell outputs，说明现版本更像“干净源文件”而不是“已运行成品”
- `工作区/Group_X_PPT_outline.md` 中部分 Task 1 数值与正式结果不一致：
  - Section 2 中 DT / OVR-SVC 数值偏低
  - Section 3 中 Word2Vec 被误写为 0.2337，正式结果为 0.1889
  - Section 4 中多组 LR+Weight 调参结果与 `results_s4_improvement.csv` 不一致
- 如果老师要求直接打开 Notebook 查看运行结果，建议在最终提交前重新运行并保存一份带输出版本
- 从实验内容角度看，Task 1 已完成；从交付封装角度看，仍需做最终一致性检查

## 2026-04-08 对照审计：官方 4 个 Section 是否每项都真的测试过

### 结论先说
- **不是每一项都测试过。**
- 更准确地说：
  - **Section 1：已完整测试**
  - **Section 2：已完整测试**
  - **Section 3：Part A 已完整测试；Part B 明确未测试**
  - **Section 4：只测试了其中一部分；不是图里列的每个方法都跑过**

### 逐项对照

| 官方大纲 | 方法/项目 | 实际状态 | 证据 |
|---|---|---|---|
| Section 1 | Logistic Regression + TF-IDF unigram | ✅ 已测试 | `工作区/Group_X.code.ipynb` Section 5；`输出/reports/report_s1_baseline.txt` |
| Section 2 | Logistic Regression | ✅ 已测试 | `输出/reports/report_s2_LR.txt` |
| Section 2 | Complement NaiveBayes | ✅ 已测试 | `输出/reports/report_s2_CNB.txt` |
| Section 2 | Decision Tree | ✅ 已测试 | `输出/reports/report_s2_DT.txt` |
| Section 2 | Random Forest | ✅ 已测试 | `输出/reports/report_s2_RF.txt` |
| Section 2 | OneVsRest + LinearSVC | ✅ 已测试 | `输出/reports/report_s2_OVR-SVC.txt` |
| Section 3 Part A | TF-IDF unigram + LR | ✅ 已测试 | `输出/reports/report_s3_R1.txt` |
| Section 3 Part A | TF-IDF (1,2-gram) + LR | ✅ 已测试 | `输出/reports/report_s3_R2.txt` |
| Section 3 Part A | CountVectorizer + LR | ✅ 已测试 | `输出/reports/report_s3_R3.txt` |
| Section 3 Part A | Word2Vec + LR | ✅ 已测试 | `输出/reports/report_s3_R4.txt` |
| Section 3 Part B | GloVe + LR | ❌ 未测试 | 已在本 note 和 [[结果索引]] 中明确标记为不纳入 |
| Section 3 Part B | BERT embedding + LR | ❌ 未测试 | 已在本 note 和 [[结果索引]] 中明确标记为不纳入 |
| Section 4 Part A | Fine-grained text cleaning | ⚠️ 仅做了统一清洗，不算单独对比实验 | Notebook 中有 `clean_text()`，但没有“清洗前后/不同清洗策略”的独立比较结果 |
| Section 4 Part A | Class weighting / imbalance handling | ✅ 已测试 | `输出/reports/report_s4_summary.txt` 与各 `report_s4_LR_weight_*.txt` |
| Section 4 Part A | Hyperparameter tuning | ✅ 已测试 | `regParam ∈ {0.01, 0.05, 0.1, 0.5, 1.0}`，见 `results_s4_improvement.csv` |
| Section 4 Part A | Optional MLP + Word2Vec | ❌ 未测试 | Notebook 仅导入了 `MultilayerPerceptronClassifier`，无对应结果文件 |
| Section 4 Part B | Confusion matrix | ✅ 已测试 | `输出/figures/fig9_confusion_matrix.png`；`report_s4_deep_analysis.txt` |
| Section 4 Part B | Per-class precision / recall / F1 | ✅ 已测试 | `report_s4_deep_analysis.txt`；`fig10_per_class_and_time.png` |
| Section 4 Part B | Hardest class pairs | ✅ 已测试 | `report_s4_deep_analysis.txt` |
| Section 4 Part B | Ablation study | ❌ 未测试 | Notebook 与输出目录中无 ablation 对比结果 |
| Section 4 Part B | Training time vs performance trade-off | ✅ 已测试 | `fig10_per_class_and_time.png` |

### 你现在这份项目最准确的说法
- 你**确实完整跑了**：
  - Section 1 全部
  - Section 2 全部
  - Section 3 Part A 全部
  - Section 4 中的 `class weighting`、`hyperparameter tuning`、`confusion matrix`、`per-class metrics`、`hardest class pairs`、`training time vs performance`
- 你**明确没跑**：
  - Section 3 Part B 的 `GloVe`
  - Section 3 Part B 的 `BERT embedding`
  - Section 4 的 `Optional MLP + Word2Vec`
  - Section 4 的 `ablation study`
- 你**做了相关处理但不能说成“单独测试过”**：
  - `fine-grained text cleaning`
  - 原因：你有统一文本清洗流程，但没有把不同清洗策略作为独立实验变量去比较

## 相关链接
- [[项目总览]]
- [[当前状态]]
- [[数据说明]]
- [[问题与坑点]]
- [[下一步]]
