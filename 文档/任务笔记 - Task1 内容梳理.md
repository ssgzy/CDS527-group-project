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

**Part B（需要外部资源，实现复杂度较高）：**
| # | 特征表示 |
|---|---------|
| 5 | GloVe |
| 6 | BERT embedding |

> 注意：Part B 的 GloVe 和 BERT embedding 需要外部预训练权重，与 PySpark 集成方式需单独设计

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

## 建议实验矩阵（对应 PySpark.png）
1. **Section 1**：TF-IDF + LR（baseline）
2. **Section 2**：TF-IDF + {LR, Complement NaiveBayes, Decision Tree, Random Forest, OneVsRest+LinearSVC}
3. **Section 3A**：LR + {TF-IDF unigram, TF-IDF 1,2-gram, CountVectorizer, Word2Vec}
4. **Section 3B**（可选，需外部资源）：LR + {GloVe, BERT}
5. **Section 4A**：改进方法（清洗、类别不平衡、调参）
6. **Section 4B**：深度分析（混淆矩阵、per-class 指标、ablation）

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
- 已说明数据、标签、任务和实验口径
- 已实现至少一个 baseline
- 已完成多模型比较
- 已完成多特征表示比较
- 已完成超参数调优并记录最佳结果
- 已完成 EDA 与可视化
- 已完成至少一组 baseline 改进实验
- 已给出最终结果对比表
- 已写出少于 300 字的总结说明

## 硬性约束
- 代码必须以 PySpark 为主
- 整个项目必须使用同一套 data split
- 整个项目必须使用同一套 evaluation metric
- 不能把大量核心实现写成标准 Python 后再包装成 Notebook

## 当前可直接开展的内容
- 清洗并理解当前 CSV 的字段和标签分布
- 先设计 PySpark Notebook 的章节骨架
- 先确定一组 PySpark 优先的 baseline 与候选模型
- 先定义需要记录的实验表格字段

## 当前仍待确认的内容
- 老师指定的 standardized data split 是什么
- 老师指定的 evaluation metric 是什么
- 是否允许在 PySpark 主体下接入外部 embedding 结果
- 数据说明文档与实际 CSV 条数不一致的原因

## 建模注意点
- 当前数据是 5 类情绪分类任务，且类别明显不平衡，见 [[数据说明]]
- 文档给出的部分模型示例不一定直接适配 PySpark 多分类场景，选型时要验证可行性
- 如果使用复杂 embedding，必须确保最终呈现仍符合“PySpark 为主”的评分要求

## 当前结论
- Task 1 至少需要覆盖“数据理解 + 基线 + 模型比较 + 特征比较 + 调参 + 可视化 + 改进实验 + 简短总结”这 8 个部分
- 当前最合理的下一步不是直接写最终 Notebook，而是先确认 split 和 metric，并把 Notebook 骨架、实验矩阵与记录模板定下来

## 相关链接
- [[项目总览]]
- [[当前状态]]
- [[数据说明]]
- [[问题与坑点]]
- [[下一步]]
