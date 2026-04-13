| section   | item                                   | status   | note                                              |
|:----------|:---------------------------------------|:---------|:--------------------------------------------------|
| S1        | LR + TF-IDF unigram                    | done     | Section 1 baseline                                |
| S2        | LR                                     | done     | Section 2                                         |
| S2        | Complement NaiveBayes                  | done     | Section 2                                         |
| S2        | Decision Tree                          | done     | Section 2                                         |
| S2        | Random Forest                          | done     | Section 2                                         |
| S2        | OneVsRest + LinearSVC                  | done     | Section 2                                         |
| S3A       | TF-IDF unigram + LR                    | done     | Section 3 Part A                                  |
| S3A       | TF-IDF (1,2-gram) + LR                 | done     | Section 3 Part A                                  |
| S3A       | CountVectorizer + LR                   | done     | Section 3 Part A                                  |
| S3A       | Word2Vec + LR                          | done     | Section 3 Part A                                  |
| S3B       | GloVe + LR                             | done     | Section 3 Part B                                  |
| S3B       | BERT embedding + LR                    | done     | Section 3 Part B                                  |
| S4A       | Fine-grained text cleaning             | partial  | 统一清洗已做；ablation 中补做 light-cleaning 对照 |
| S4A       | Class weighting / imbalance handling   | done     | Section 4 core                                    |
| S4A       | Hyperparameter tuning                  | done     | Section 4 core                                    |
| S4A       | Optional MLP + Word2Vec                | done     | 本脚本新增                                        |
| S4B       | Confusion matrix                       | done     | 原 Section 4 深度分析                             |
| S4B       | Per-class precision / recall / F1      | done     | 原 Section 4 深度分析                             |
| S4B       | Hardest class pairs                    | done     | 原 Section 4 深度分析                             |
| S4B       | Ablation study                         | done     | 本脚本新增                                        |
| S4B       | Training time vs performance trade-off | done     | 原 Section 4 深度分析                             |