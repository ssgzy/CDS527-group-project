# PPT 与 Report 需补充说明

> 最后更新：2026-04-13
> 关联：[[二次核对项目 - 主文档]] | [[流程设计复核]] | [[Baseline 选择与适配性]] | [[数据版本与标签分布复核]] | [[可复现性与产物同步]]

---

## 必须写清楚的 5 个点

### 1. 数据口径

- 老师给定版本：`1299` 条
- 实际建模：去除 1 条文本重复后 `1298` 条
- 所有图表和实验结果均以 `1298` 条建模样本为准

### 2. baseline 的定位

- baseline 不是最终答案，而是参照点
- 选择 `TF-IDF + LR` 是因为：
  - 课程示例支持
  - PySpark 原生易实现
  - 文本分类常规强基线

### 3. 这套流程为什么不是胡乱操作

- 因为它是控制变量设计：
  - S1 建基线
  - S2 固定特征换模型
  - S3 固定模型换表示
  - S4 针对真正瓶颈做改进

### 4. 为什么主指标必须是 macro-F1

- 你的数据里 `happy` 约占 `89%`
- accuracy 会天然虚高
- 只有 macro-F1 才能公平反映少数类表现

### 5. 为什么最终最佳方案是 LR + class weights

- S3 已经证明：在固定 LR 且不处理不平衡时，换特征没有突破
- 因此把改进重点放到 class weighting 是有证据支持的，而不是盲调

---

## 建议补进 report 的一句话

- “The workflow was intentionally organised as a controlled progression rather than a random trial-and-error process: we first established a standard sparse-text baseline, then isolated classifier effects, then isolated representation effects, and finally targeted the empirically identified bottleneck of class imbalance.”

---

## 建议补进 PPT 的 1 页或 1 段说明

### 标题建议

- `Why This Workflow Is Rational`
- 或 `Why Class Imbalance Became the Main Lever`

### 内容建议

1. baseline 暴露了多数类偏置
2. S2 证明换分类器能带来提升，CNB 最优
3. S3 证明在固定 LR 下换表示无效
4. 因此 S4 转向 class weighting，得到全项目最优 `0.3453`

---

## 已发现的 PPT / 大纲不同步点

### 1. `工作区/Group_X_PPT_outline.md` 不是最终事实来源

- 该大纲里有旧数字，不能再直接拿来讲
- 已发现的旧值包括：
  - S2 中 `DT / RF / OVR-SVC` 的数值是过期的
  - S3 中 `Word2Vec` 被写成 `0.2337`，实际应为 `0.1889`
  - S4 中多个 `regParam` 对应值过期

### 2. 最终 PPT 成品大体已修正

- 抽查 `CDS527.pptx` 可见：
  - S2 页核心数值已正确
  - S3 页 `Word2Vec = 0.1889` 已正确
  - S4 页 `0.3453` 和调参图已正确

### 3. 最终 PPT 仍有 1 处需要修正

- `Under the Hood: Diagnostics & Trade-offs` 这一页写了：
  - `angry <-> sad are the most confused pair`
- 但根据 `report_s4_deep_analysis.txt` 和混淆矩阵，真实 Top pairs 是：
  - `happy → surprise` = 18
  - `happy → sad` = 8
  - `happy → disgust` = 5
  - `angry → happy` = 5
- 因此这页结论应改，不然会被质疑“图和字不一致”

---

## 口头答辩时可以直接说的话

- “The workflow was not random. We deliberately separated model comparison from representation comparison, and the results showed that class imbalance, not feature swapping, was the dominant bottleneck.”
- “Our baseline was intentionally simple and standard. Its failure was analytically useful, because it told us exactly where the real problem was.”
- “The final improvement was therefore motivated by evidence from earlier sections, not by arbitrary tuning.”

---

## 回链

- [[二次核对项目 - 主文档]]
- [[结果索引]]
- [[结论层级汇总]]
- [[任务笔记 - Task1 内容梳理]]
