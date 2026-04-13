# 项目总览

## 项目基本信息
- 项目名称：CDS527 Group Assignment
- 项目根目录：`/Users/sam/Documents/Documents - sam的MacBook Pro/LU课程资料/CDS527 Big Data Analytics Language Models/CDS527 group project`
- 执行环境：conda `CDS527`（PySpark 3.1.2，Java 11）
- Task 1 数据：`smile-annotations-final.csv`
- Task 2 case：`Google.docx`
- 官方路线图：`PySpark.png`

## 当前统一口径
- 原始 CSV：`1299` 行
- 建模样本：按 `text` 去重后 `1298` 行
- 固定切分：`sampleBy(label, 0.8, seed=42)` 得到近似分层的 `1032 / 266`
- 主指标：`macro-F1`
- baseline：`TF-IDF unigram + Logistic Regression`，`macro-F1 = 0.2337`
- 当前全项目最优：`A4 Light cleaning only + TF-IDF + class weight + LR`，`macro-F1 = 0.4465`

## Task 1 结果摘要

| Section | 最佳配置 | macro-F1 |
|---------|---------|---------:|
| S1 Baseline | TF-IDF unigram + LR | 0.2337 |
| S2 Model Comparison | Complement NaiveBayes | 0.3332 |
| S3 Part B best | BERT embedding + LR | 0.3420 |
| S4 original best | LR + class weight (rp=0.5) | 0.3453 |
| **Current overall best** | **A4 Light cleaning only + TF-IDF + class weight + LR** | **0.4465** |

## 当前项目状态
- Task 1 主线实验完成
- Task 1 补做实验完成：`GloVe`、`BERT embedding`、`MLP + Word2Vec`、`ablation study`
- 输出目录已按 `sections/`、`tables/` 重整
- sanity check 已完成，未发现明显标签映射错误、切分错误、评估错误或直接泄漏证据
- 文本文档已按最新结果同步

## 主要目录
- `文档/`：项目笔记、实验协议、总结材料
- `工作区/Group_X.code.ipynb`：Task 1 notebook
- `工作区/Group_X_PPT_outline.md`：当前权威 PPT 大纲
- `工作区/Group_X.report.docx`：Task 2 report
- `工作区/Group_X.gai.docx`：GAI 声明
- `输出/`：图表、结果表、报告文本、section 索引
- `二次核对项目/`：二次核对、sanity check、PPT 同步文档

## 推荐入口
- `文档/结果索引.md`
- `文档/当前状态.md`
- `文档/结论层级汇总.md`
- `二次核对项目/PPT大纲-修订版-含文件映射.md`
- `二次核对项目/sanity_check_summary.md`
