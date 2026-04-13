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
- 切分：固定 `sampleBy(label, 0.8, seed=42)` 协议 → Train 1,032 / Test 266
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

- 原主线方法：LR + 逆频率类别权重（weight[c] = n_total / (n_classes × count[c])）+ regParam 调参
- **原主线最优**：LR + 类别权重（regParam=0.5）→ macro-F1=**0.3453**
  - 较 S1 Baseline（0.2337）提升 **+47.7%**
  - 略优于 S2 CNB（0.3332）
- **补做 ablation 后的当前最终最优**：`A4 Light cleaning only + TF-IDF + class weight + LR`
  - macro-F1=**0.4465**
  - weighted-F1=**0.9009**
  - accuracy=**0.8910**
- 关键解释：
  - `A1 No class weight = 0.2367`，说明 class weight 仍然是必要条件
  - `A4 > A0`，说明旧版强清洗删掉了短文本中的有效情绪信号
  - `disgust` 仍为 0，说明极少样本类别仍受数据上限限制
- 候选句："Ablation reveals that the strongest final configuration is not simply weighted LR, but light cleaning only + TF-IDF + class-weighted Logistic Regression, which lifts macro-F1 to 0.4465. This indicates that preserving more signal in short tweets is as important as handling class imbalance."

---

## 6. 当前最重要的实验结论（持续更新）

1. **类别不平衡是本数据集的核心挑战**：任何默认分类器在不处理不平衡的情况下都会退化为"全预测 happy"
2. **accuracy 完全不适合作为本任务的主指标**：macro-F1 是唯一能反映真实多分类能力的指标
3. **Complement NaiveBayes 是目前最优的分类器**（macro-F1=0.3332）：设计上针对不平衡文本，比 LR 高 42.5%
4. **在固定 LR + 不处理类别不平衡的条件下，BOW 系列特征表示选择未带来性能差异**：Section 3 在当前设置下表明，换用 bigram 或去掉 IDF 不足以突破不平衡带来的限制（结论限于当前协议范围）
5. **类别不平衡处理是关键改进方向**：原主线 weighted LR 已验证这一点，ablation 进一步证明“class weight + 更轻的清洗”才是最终最优组合
6. **当前全项目最优不是 0.3453，而是 A4 = 0.4465**：这意味着最终主结论必须从“class weight alone”升级为“class weight + light cleaning”
7. **disgust 类（13 条训练样本）几乎无法被任何基础方法识别**：数据层面的限制，需在报告中坦诚说明

---

## 7. 最终 <300 words 总结的候选句子

### 候选句（已验证的数字和结论，可直接引用）

- "The dataset contains 1,298 tweets from 13 British museum accounts, labelled into 5 emotion classes with severe imbalance: happy accounts for 89.1% of samples."
- "All experiments follow a fixed protocol: a label-aware 80/20 `sampleBy` split (seed=42), evaluated primarily by macro-F1 to fairly weight all five classes."
- "The baseline (TF-IDF unigram + Logistic Regression) achieves macro-F1=0.2337, with accuracy=0.8985 — the high accuracy is misleading as the model nearly always predicts 'happy'."
- "In the model comparison (Section 2), Complement Naive Bayes achieves the best macro-F1=0.3332 (+42.5% over baseline), with angry F1=0.55 — the highest minority-class recognition across all models."
- "Random Forest, despite 89.5% accuracy, achieves the lowest macro-F1=0.1889, confirming that accuracy is an unreliable metric under class imbalance."
- "Within the fixed-LR protocol, changing feature representations (unigrams, bigrams, CountVectorizer) produced identical results (macro-F1=0.2337), suggesting that class imbalance handling may be a stronger lever than feature choice in this experimental setting. Word2Vec performed worst (0.1889), as averaged dense embeddings lose the sparse discriminative signals needed for this small, imbalanced dataset."
- "The original weighted-LR improvement raises macro-F1 to 0.3453, but the final ablation shows an even stronger result: light cleaning only + TF-IDF + class-weighted Logistic Regression reaches macro-F1=0.4465, indicating that preprocessing strength and class imbalance must be considered together."
- "disgust remains at F1=0.00 across all models due to extreme data scarcity (10 training, 3 test samples) — a data-level limitation that should be acknowledged in the report rather than attributed to modelling failure."

---

## 更新记录

| 日期 | 更新内容 |
|------|---------|
| 2026-03-31 | 初始创建，填入 Section 1 & 2 素材 |
| 2026-03-31 | 补入 Section 3 素材（第 4 节 & 第 7 节候选句）；按审阅意见软化过强措辞 |
| 2026-03-31 | Step 9 完成：补入 Section 4 素材（原主线 weighted LR） |
| 2026-04-13 | 按补做实验结果更新：当前最终最优改为 `A4 = 0.4465`，同步修正候选句与结论口径 |
