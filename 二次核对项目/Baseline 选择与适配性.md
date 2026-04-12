# Baseline 选择与适配性

> 最后更新：2026-04-13
> 关联：[[二次核对项目 - 主文档]] | [[流程设计复核]] | [[数据版本与标签分布复核]] | [[PPT 与 Report 需补充说明]]

---

## 你的 baseline 是什么

- **Baseline 方法**：`TF-IDF (unigram) + Logistic Regression`
- notebook 实现位置：
  - `工作区/Group_X.code.ipynb`
  - `Section 5 — Section 1: Baseline`
  - 核心实现代码在 **Cell 16**

### 实际 pipeline

`clean_text → RegexTokenizer → StopWordsRemover → CountVectorizer → IDF → LogisticRegression`

### 关键参数

- `CountVectorizer(vocabSize=10000, minDF=2)`
- `IDF(minDocFreq=2)`
- `LogisticRegression(maxIter=100, regParam=0.1, family='multinomial')`

### 实际结果

- macro-F1 = `0.2337`
- weighted-F1 = `0.8590`
- accuracy = `0.8985`

---

## 这个 baseline 对你的数据是否合理

## 判断

- **作为 baseline：合理**
- **作为最终方案：不够**

## 为什么它作为 baseline 是合理的

### 1. 这是文本分类的标准起点

- `TF-IDF + LR` 是经典、强基线、可解释且易复现。
- 对小规模文本分类尤其常见。

### 2. 它符合课程要求和 PySpark 主线

- 作业说明把 logistic regression 直接举成 baseline 例子。
- 这个方案完全基于 PySpark ML Pipeline，符合“主要基于 PySpark”的要求。

### 3. 它适合做后续比较的参照物

- 它简单、稳定、容易解释。
- 之后不管换模型还是换特征，都可以清楚地说“比 baseline 提升了多少”。

---

## 为什么它不适合直接拿来做最终模型

### 1. 你的数据极端不平衡

- `happy` 占比约 `89.06%`
- `disgust` 只有 `13` 条
- baseline 的 LR 在这种分布下天然会偏向多数类

### 2. 结果已经直接证明 baseline 被多数类牵着走

- `happy` 的 F1 接近 `0.95`
- `surprise / disgust / sad` 的 F1 都是 `0`
- 只有 `angry` 被部分识别，F1 = `0.22`

### 3. accuracy 在这里是虚高

- `0.8985` 的 accuracy 看起来很好
- 但实质上模型几乎一直在预测 `happy`
- 所以真正该看的指标是 `macro-F1`

---

## 最准确的说法

- “This is a reasonable baseline for sparse text classification, but it is not sufficient for this dataset because the class imbalance is so severe that the model collapses toward the majority class.”

---

## 需要写进 report / PPT 的解释点

1. baseline 不是“拍脑袋选的”，而是课程示例和文本分类常规做法
2. baseline 的作用是建立参照下限，不是承诺它会是最优方法
3. baseline 失效的根本原因不是 LR 本身错误，而是类别不平衡太严重
4. 正因为 baseline 暴露了这个问题，后面才合理地转向 `CNB` 和 `class weighting`

---

## 回链

- [[二次核对项目 - 主文档]]
- [[实验协议]]
- [[结果索引]]
- [[任务笔记 - Task1 内容梳理]]
