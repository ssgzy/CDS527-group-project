# PPT 大纲修订版（含文件映射）

## 文档目的

- 基于用户提供的 `revised_ppt_outline.md` 进行二次核对与重组。
- 在保留原主线优点的前提下，补上老师作业要求中必须明确呈现的内容。
- 为每一页标注建议引用的实际文件，方便后续制作 PPT。

## 本次复查结论（基于最新项目输出）

- 已重新检查项目目录中最近更新的实验结果文件。
- 最近一轮新增内容主要集中在：
- `Section 3 Part B`：`GloVe`、`BERT embedding`
- `Section 4`：`MLP + Word2Vec`
- `Section 4`：`ablation study`
- 当前全项目最佳结果没有被推翻，仍然是：
- `A4 Light cleaning only + TF-IDF + class weight + LR`
- `macro-F1 = 0.4465`
- 因此本大纲主线仍成立，但 Task 1 的结尾页需要改成“以 A4 为最终结论，以 weighted LR 为中间里程碑”，不能继续把旧的 `0.3453` 讲成最终最优。

## 对原修订大纲的整体判断

- 整体方向是合理的。Task 1 主线已经比旧版清楚，能够体现 `baseline -> comparison -> improvement -> final best` 的逻辑。
- 但仍有 5 个需要修正的地方，否则会影响老师对“是否完整覆盖作业要求”的判断。

## 需要修正的关键点

- `Slide 3` 中的样本量与切分表述需要更严谨。
- 当前项目源文件是 `1299` 行，但实际建模流程按 `text` 去重后使用 `1298` 条。
- 当前切分不是严格意义上的 sklearn `stratified split`，而是 PySpark `sampleBy(label, 0.8, seed=42)` 后再 `subtract` 得到测试集，因此更准确的说法应为“near-stratified / label-aware split”。
- `Slide 8` 把 `S3 Part A` 与 `S3 Part B` 混在一起了，建议明确区分“PySpark 内部表示比较”和“补充 embedding 比较”。
- `Slide 11` 中的 “angry vs sad remained the hardest confused pair” 与当前深度分析输出不一致。现有 `report_s4_deep_analysis.txt` 显示最大错分对是 `true happy -> predicted surprise`。如果不想讲具体 pair，可以改成“minority classes remained unstable, with disgust still hardest overall”。
- Task 2 当前只有 “5Vs / flywheel / final synthesis”，但老师要求的是：`background`, `how you approach the problem/data`, `solution description`, `critical evaluation`。因此需要把 Task 2 扩成至少 3 页主体内容，而不是 2 页后直接总结。
- 建议把 sanity check 结果合并进 Task 1 结尾页，用一句话说明“未发现明显标签映射、切分、评估错误证据”，这样能增强结果可信度。

## 新版 PPT 结构建议

### Slide 1 — Title Slide

- 目的：交代主题与组别信息。
- 建议内容：
- 标题：`Big Data Analytics: Text Classification and the Google Ecosystem`
- 课程名、学期、组员姓名
- 文件建议：
- `CDS527.pptx`
- `Group_Project_2026_T2 .docx`

### Slide 2 — Assignment Scope and Presentation Map

- 目的：先把老师要求的两个 task 明确切开，避免听众误以为是同一类任务。
- 建议内容：
- `Task 1: System Development`
- 要回答的问题：如何基于给定文本数据构建、比较、优化分类系统
- `Task 2: Case Study`
- 要回答的问题：如何从 Big Data 视角分析 Google 的问题、方案与风险
- 说明本次汇报结构：Task 1 约 10 分钟，Task 2 约 4 分钟，结论约 1 分钟
- 文件建议：
- `tmp/docs/Group_Project_2026_T2.txt`
- `文档/任务笔记 - 阅读作业要求.md`
- `/Users/sam/Downloads/revised_ppt_outline.md`

### Slide 3 — Task 1 Problem Definition and Evaluation Setup

- 目的：在进入结果前，先把问题定义、数据规模、核心难点、评价协议讲清楚。
- 建议内容：
- 数据源：`smile-annotations-final.csv`
- 源文件共 `1299` 行；当前项目按 `text` 去重后，建模样本为 `1298`
- 五分类情绪任务：`surprise / angry / disgust / happy / sad`
- `happy` 占比约 `89%`
- 解释为什么不能只看 accuracy，为什么要以 `macro-F1` 为主指标
- 说明当前项目使用固定切分和固定指标，保证 section 间可比性
- 建议把 split 写成：
- `PySpark sampleBy(label, 0.8, seed=42), producing near-stratified train/test proportions`
- 文件建议：
- `smile-annotations-final.csv`
- `输出/figures/fig1_label_distribution.png`
- `输出/sanity_check/split_distribution.png`
- `二次核对项目/sanity_check_summary.md`

### Slide 4 — EDA: Short, Noisy, and Biased Text

- 目的：用 1 页把短文本、噪声、类别偏置三个痛点讲明白。
- 建议内容：
- 文本短，语义上下文有限
- 文本含 URL、mention、hashtag、特殊符号等平台噪声
- 词汇分布受 `happy` 类主导
- 由此引出：预处理与类别不平衡都会强烈影响下游结果
- 文件建议：
- `输出/figures/fig2_word_count.png`
- `输出/figures/fig3_wordcount_boxplot.png`
- `输出/figures/fig4_text_noise.png`
- `输出/figures/fig5_wordclouds.png`
- `输出/reports/report_eda.txt`

### Slide 5 — Unified PySpark Experimental Framework

- 目的：对应老师 Task 1 要求里的“baseline、比较、调参、可视化、改进方法”，让后面 4 个 section 看起来是一个统一实验设计。
- 建议内容：
- 统一 pipeline：`Cleaning -> RegexTokenizer -> StopWordsRemover -> Feature Representation -> Classifier`
- 统一控制变量：
- 同一切分
- 同一主指标
- 同一 PySpark 主体实现
- 4 个实验 section：
- `S1 Baseline`
- `S2 Model comparison`
- `S3 Representation comparison`
- `S4 Improvement + ablation`
- 文件建议：
- `PySpark.png`
- `工作区/Group_X.code.ipynb`
- `工作区/run_additional_experiments.py`
- `文档/实验协议.md`
- `输出/tables/official_roadmap_status.md`

### Slide 6 — S1 Baseline: Lower Bound Performance

- 目的：明确 baseline 是什么，以及为什么它只是下界。
- 建议内容：
- Baseline：`TF-IDF (unigram) + Logistic Regression`
- 主结果：`macro-F1 = 0.2337`
- 解释：模型强烈偏向多数类 `happy`
- 用一句话强调：后续所有方法都需要与这个 baseline 比较
- 文件建议：
- `输出/sections/section1_baseline/overall_experiment_metrics.csv`
- `输出/sections/section1_baseline/report_s1_baseline.txt`
- `输出/sanity_check/baseline_confusion_matrix.png`

### Slide 7 — S2 Model Comparison under Fixed TF-IDF

- 目的：展示在固定表示下，单纯换分类器会带来什么差异。
- 建议内容：
- 比较模型：
- LR
- CNB
- DT
- RF
- OVR + LinearSVC
- 结论：
- `Complement NaiveBayes` 是本 section 最优，`macro-F1 = 0.3332`
- 它显著优于 baseline，但不是全项目最终最优
- 可以补一句效率对比：`CNB` 很快，`OVR-SVC` 很慢
- 文件建议：
- `输出/sections/section2_model_comparison/results_s2_model_comparison.csv`
- `输出/sections/section2_model_comparison/fig6_s2_model_comparison.png`
- `输出/sections/section2_model_comparison/report_s2_summary.txt`
- `输出/tables/overall_experiment_metrics.md`

### Slide 8 — S3 Representation Comparison: Native Features vs Supplementary Embeddings

- 目的：把 S3 分清楚，不再把 Part A 和 Part B 混成一件事。
- 建议内容：
- `Part A: PySpark-native representations`
- TF-IDF unigram
- TF-IDF bigram
- CountVectorizer
- Word2Vec
- 结果：仅替换表示并不能解决 macro-F1 偏低问题
- `Part B: Supplementary embeddings`
- GloVe + LR: `0.3312`
- BERT embedding + LR: `0.3420`
- 结论：
- 更强表示有帮助
- 但如果不先处理 imbalance / preprocessing，提升仍受限
- 口径建议：
- 这一页要明确说 `Part B` 是“补做的 supplementary comparison”
- 不建议把 `BERT = 0.3420` 讲成最终推荐方案，因为课程主指标和最终最优仍然是 `A4 = 0.4465`
- 文件建议：
- `输出/sections/section3_representation/results_s3_repr_comparison.csv`
- `输出/sections/section3_representation/results_s3_partb_embeddings.csv`
- `输出/sections/section3_representation/fig7_s3_repr_comparison.png`
- `输出/sections/section3_representation/fig11_s3b_embeddings.png`
- `输出/sections/section3_representation/report_s3_summary.txt`
- `输出/sections/section3_representation/report_s3B_summary.txt`

### Slide 9 — S4 Improvement Core: Class Weighting

- 目的：把 “class imbalance 是主矛盾” 这一点正式立住。
- 建议内容：
- 在 Logistic Regression 中加入 inverse-frequency class weight
- 展示 `regParam` sweep
- 强调最优原始 S4 结果：
- `LR + class weight (regParam=0.5) = 0.3453`
- 解释：
- class weighting 明显缓解了 majority collapse
- 这比单纯替换特征更关键
- 文件建议：
- `输出/sections/section4_improvement/results_s4_improvement.csv`
- `输出/sections/section4_improvement/fig8_s4_improvement.png`
- `输出/sections/section4_improvement/report_s4_summary.txt`

### Slide 10 — Final Best Configuration from Ablation

- 目的：明确告诉老师你不只是“调参”，还做了结构性分析，最后找到了全项目最佳方案。
- 建议内容：
- Ablation study 结论：
- `A4: Light cleaning only + TF-IDF + class weight + LR`
- `macro-F1 = 0.4465`
- 与几个关键里程碑做对比：
- baseline `0.2337`
- S2 best CNB `0.3332`
- S4 weighted LR `0.3453`
- current overall best `0.4465`
- 解释：
- 过强清洗会损失短文本中的有效情绪信号
- 最佳结果来自 “较轻预处理 + 类别平衡”
- 可补 1 句最新 per-class 现象：
- `A4` 下 `surprise` 与 `angry` 明显改善，但 `disgust` 仍为最难类别
- 文件建议：
- `输出/sections/section4_improvement/results_s4_ablation.csv`
- `输出/sections/section4_improvement/fig12_s4_ablation.png`
- `输出/sections/section4_improvement/report_s4_ablation_summary.txt`
- `输出/reports/report_s4_ablation_A4.txt`
- `输出/tables/macro_f1_ranking.md`

### Slide 11 — Task 1 Wrap-up: Diagnostics, Trade-offs, and Validation

- 目的：把“结果是什么”和“结果是否可信”放在同一页收束。
- 建议内容：
- 关键诊断：
- `A4` 让 `surprise` 与 `angry` 的表现明显改善
- `disgust` 仍然最难，`sad` 仍偏弱
- 如果要讲 confusion matrix，要明确说明 `fig9_confusion_matrix.png` 对应的是原 `weighted LR (rp=0.5)` 深度分析，不是 `A4`
- 因此本页不建议再把具体 “hardest pair” 作为主句，避免口径和最终最优配置脱节
- 补 1 句 sanity check：
- 未发现明显标签映射错误、切分错误、评估错误或直接泄漏证据
- trade-off：
- `CNB` 快且强
- `weighted LR` 是原主线最佳
- `A4` 是最终整体最佳
- 文件建议：
- `输出/reports/report_s4_ablation_A4.txt`
- `输出/sections/section4_improvement/fig10_per_class_and_time.png`
- `输出/reports/report_s4_deep_analysis.txt`
- `输出/tables/per_class_f1_selected_models.md`
- `二次核对项目/sanity_check_summary.md`
- `输出/sanity_check/balanced_confusion_matrix.png`
- `输出/sections/section4_improvement/fig9_confusion_matrix.png`

### Slide 12 — Task 2 Framing: Google as a Big Data Case

- 目的：从 Task 1 平滑切到 Task 2，并先对齐老师要求里的 “background description”。
- 建议内容：
- Google 为什么是典型 Big Data case
- 用 5Vs 做背景介绍：
- Volume
- Velocity
- Variety
- Veracity
- Value
- 强调：这部分不是公司介绍，而是 case framing
- 文件建议：
- `Google.docx`
- `tmp/docs/Google.txt`
- `文档/任务笔记 - Task2 Google Case.md`
- `文档/Task2 论点素材.md`

### Slide 13 — Task 2 Approach and Proposed Solution

- 目的：对应老师要求里的 “how you approach the problem/data” 与 “description of the solution”。
- 建议内容：
- Google 面对的问题：
- web-scale indexing
- information quality and noise
- cross-product data integration
- 你的分析框架：
- statistical analysis
- visual analysis
- machine learning
- semantic analysis
- 提出的 solution：
- intelligent indexing / ranking
- cross-product data flywheel
- privacy-aware data integration
- 文件建议：
- `文档/Task2 报告草稿.md`
- `文档/Task2 报告结构.md`
- `文档/Task2 论点素材.md`
- `tmp/docs/Group_X.report.txt`

### Slide 14 — Task 2 Critical Evaluation and KPI

- 目的：补齐老师 rubric 里最容易漏掉的 “critical evaluation of the solution”。
- 建议内容：
- strengths：
- data flywheel
- infrastructure moat
- fast experimentation
- risks：
- privacy and regulation
- filter bubbles / information diversity
- AI-generated content and LLM search disruption
- KPI / SMART 示例：
- relevance quality
- spam rate
- user satisfaction
- revenue or engagement quality metric
- 文件建议：
- `文档/Task2 报告草稿.md`
- `文档/Task2 下一步.md`
- `tmp/docs/Group_X.report.txt`

### Slide 15 — Final Synthesis

- 目的：把 Task 1 与 Task 2 统一成一个课程层面的结论。
- 建议内容：
- `Task 1` 结论：
- 数据不平衡和预处理策略比“盲目换特征”更关键
- `Task 2` 结论：
- Big Data 竞争优势来自规模、整合与反馈回路，但同时受制于合规、信任与 AI 变局
- 统一结论：
- 好的 Big Data 系统不只追求 performance，也要兼顾 robustness 与 responsibility
- 文件建议：
- `输出/tables/macro_f1_ranking.md`
- `输出/tables/overall_experiment_metrics.md`
- `文档/结论层级汇总.md`
- `文档/Overall Summary 素材.md`

## 建议保留的 Appendix / Backup Slides

- `输出/tables/per_class_f1_selected_models.md`
- `输出/tables/official_roadmap_status.md`
- `输出/sections/section4_improvement/fig9_confusion_matrix.png`
- `输出/sections/section4_improvement/fig10_per_class_and_time.png`
- `输出/sections/section3_representation/fig11_s3b_embeddings.png`
- `二次核对项目/sanity_check_baseline.ipynb`
- `二次核对项目/sanity_check_summary.md`

## 最终判断

- 这个修订后的大纲是合理的，而且比原版更贴近老师作业要求。
- 关键改进点不在于“多讲背景知识”，而在于把背景知识放到正确位置：
- 在 Task 1 前先交代 `problem + metric + protocol`
- 在 Task 2 前先交代 `case framing + approach + evaluation`
- 经过这次对最新实验结果的复查后，本大纲仍然成立，且已同步纳入：
- `S3 Part B` 的补做 embedding 实验
- `S4 ablation` 找到的最新全项目最优 `A4 = 0.4465`
- 只要按本版结构制作 PPT，Task 1 和 Task 2 的边界会明显清楚很多，老师要求的展示点也会更完整。
