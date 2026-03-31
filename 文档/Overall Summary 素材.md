# Overall Summary 素材

本文档持续积累 Task 1 Notebook 中 <300 words 总结所需的素材。
每完成一个 Section 后更新一次。最终从此拼出定稿。

---

## 1. 数据文件与样本规模

- 数据集：SMILE Twitter Emotion Dataset
- 来源：13 个英国博物馆 Twitter 账号的提及推文（2013–2015）
- 原始记录：1,299 行；去除 1 条 text 重复后有效样本 **1,298 行**
- 任务类型：5 类情绪分类（surprise / angry / disgust / happy / sad）
- 关键挑战：**类别严重不平衡**（happy 占 89.1%，disgust 仅 1.0%）
- 切分：stratified 80/20，seed=42 → Train 1,032 / Test 266
- 评价主指标：macro-F1（各类等权平均）

---

## 2. Baseline 方法与核心结果

- 方法：TF-IDF (unigram, vocabSize=10000, minDF=2) + Logistic Regression (multinomial)
- 预处理：去除 URL/@mention/#symbol/HTML 实体 → 保留纯英文小写词
- macro-F1：**0.2337**；accuracy：0.8985（虚高，近乎全预测 happy）
- 关键数字：happy F1=0.95；其余 4 类 F1 ≈ 0（仅 angry=0.22）
- **重要结论**：高 accuracy 在不平衡数据下无意义；macro-F1 才是真实性能指标

---

## 3. 模型比较阶段（Section 2）

- 固定特征：TF-IDF unigram；比较 5 种分类器
- 最佳：**Complement NaiveBayes**，macro-F1=**0.3332**（较基线 +42.5%）
  - angry F1=0.55（最高），sad F1=0.12，surprise F1=0.09
  - 训练最快（1.0s），专为不平衡文本分类设计
- 最差：Random Forest，macro-F1=0.1889（低于基线），少数类全 0
  - accuracy=89.5% 反而是所有模型中最高的之一——完美佐证 accuracy 的误导性
- 关键发现：accuracy 排名与 macro-F1 排名完全相反；不平衡场景必须用 macro-F1

---

## 4. 表示方法比较阶段（Section 3）

- 固定分类器：LR；比较 TF-IDF unigram / TF-IDF bigram / CountVectorizer / Word2Vec
- **关键发现**：在固定 LR 的当前设置下，TF-IDF unigram / bigram / CountVectorizer 三者产生了相同的预测结果（macro-F1=0.2337）；Word2Vec 更差（0.1889）
- **当前设置下的结论**：在固定 LR 且不处理类别不平衡的条件下，测试的 BOW 系列表示方法均未突破基线；这表明在当前配置中，类别不平衡与分类器敏感性的影响可能比特征表示选择更为主导
- 候选句："Within the fixed-LR protocol, changing feature representations (unigrams, bigrams, CountVectorizer) produced identical results (macro-F1=0.2337), suggesting that class imbalance handling may be a stronger lever than feature choice in this experimental setting."

---

## 5. 改进方法带来的主要变化（Section 4）

- 方法：LR + 逆频率类别权重（weight[c] = n_total / (n_classes × count[c])）+ regParam 调参
- **最优配置**：LR + 类别权重（regParam=0.5）→ macro-F1=**0.3453**
  - 较 S1 Baseline（0.2337）提升 **+47.7%**
  - 略优于 S2 CNB（0.3332），但差距小（+0.0121）
  - angry F1=0.56（最佳），surprise F1=0.14（有所改善），sad F1=0.12
- **关键权衡**：accuracy 从 90% 降至 80%——类别权重调整后模型预测更分散，部分 happy 被误判为少数类；这是精确率–召回率权衡，在 macro-F1 框架下是净正收益
- **disgust 仍为 0**：训练集仅 10 条、测试集 3 条，权重达 ×20.6 仍无法学到可泛化特征；为数据层面限制
- 候选句："Adding inverse-frequency class weights to Logistic Regression (regParam=0.5) achieves macro-F1=0.3453 — the best result across all experiments (+47.7% over baseline), at the cost of reducing accuracy from 90% to 80% as the model learns to predict minority classes more actively."

---

## 6. 当前最重要的实验结论（持续更新）

1. **类别不平衡是本数据集的核心挑战**：任何默认分类器在不处理不平衡的情况下都会退化为"全预测 happy"
2. **accuracy 完全不适合作为本任务的主指标**：macro-F1 是唯一能反映真实多分类能力的指标
3. **Complement NaiveBayes 是目前最优的分类器**（macro-F1=0.3332）：设计上针对不平衡文本，比 LR 高 42.5%
4. **在固定 LR + 不处理类别不平衡的条件下，BOW 系列特征表示选择未带来性能差异**：Section 3 在当前设置下表明，换用 bigram 或去掉 IDF 不足以突破不平衡带来的限制（结论限于当前协议范围）
5. **类别权重调整是最有效的改进方向**：Section 4 验证——LR + 逆频率类别权重（rp=0.5）达到全项目最优 macro-F1=0.3453，+47.7% over baseline
6. **disgust 类（13 条训练样本）几乎无法被任何基础方法识别**：数据层面的限制，需在报告中坦诚说明

---

## 7. 最终 <300 words 总结的候选句子

### 候选句（已验证的数字和结论，可直接引用）

- "The dataset contains 1,298 tweets from 13 British museum accounts, labelled into 5 emotion classes with severe imbalance: happy accounts for 89.1% of samples."
- "All experiments follow a fixed protocol: stratified 80/20 split (seed=42), evaluated primarily by macro-F1 to fairly weight all five classes."
- "The baseline (TF-IDF unigram + Logistic Regression) achieves macro-F1=0.2337, with accuracy=0.8985 — the high accuracy is misleading as the model nearly always predicts 'happy'."
- "In the model comparison (Section 2), Complement Naive Bayes achieves the best macro-F1=0.3332 (+42.5% over baseline), with angry F1=0.55 — the highest minority-class recognition across all models."
- "Random Forest, despite 89.5% accuracy, achieves the lowest macro-F1=0.1889, confirming that accuracy is an unreliable metric under class imbalance."
- "Within the fixed-LR protocol, changing feature representations (unigrams, bigrams, CountVectorizer) produced identical results (macro-F1=0.2337), suggesting that class imbalance handling may be a stronger lever than feature choice in this experimental setting. Word2Vec performed worst (0.1889), as averaged dense embeddings lose the sparse discriminative signals needed for this small, imbalanced dataset."
- "Adding inverse-frequency class weights to Logistic Regression (regParam=0.5) achieves the best macro-F1=0.3453 across all experiments (+47.7% over baseline), demonstrating that class imbalance handling is a more impactful lever than feature representation changes in this setting."
- "disgust remains at F1=0.00 across all models due to extreme data scarcity (10 training, 3 test samples) — a data-level limitation that should be acknowledged in the report rather than attributed to modelling failure."

---

## 更新记录

| 日期 | 更新内容 |
|------|---------|
| 2026-03-31 | 初始创建，填入 Section 1 & 2 素材 |
| 2026-03-31 | 补入 Section 3 素材（第 4 节 & 第 7 节候选句）；按审阅意见软化过强措辞 |
| 2026-03-31 | Step 9 完成：补入 Section 4 素材（第 5 节、第 6 点第 5 条、第 7 节候选句） |
