| section   | subsection                       | experiment                                            | role               |   macro_f1 |   weighted_f1 |   accuracy |   train_sec |
|:----------|:---------------------------------|:------------------------------------------------------|:-------------------|-----------:|--------------:|-----------:|------------:|
| S4        | Ablation Study                   | Light cleaning only                                   | analysis           |   0.446515 |      0.900859 |   0.890977 |         3.5 |
| S4        | Ablation Study                   | No stopword removal                                   | analysis           |   0.352985 |      0.862657 |   0.845865 |         3.4 |
| S4        | Improvement Core                 | LR+Weight (rp=0.5)                                    | experiment         |   0.345307 |      0.840762 |   0.804511 |         3.7 |
| S4        | Ablation Study                   | Full best (clean + stopwords + TF-IDF + class weight) | analysis           |   0.345307 |      0.840762 |   0.804511 |         3.1 |
| S4        | Ablation Study                   | No IDF                                                | analysis           |   0.345307 |      0.840762 |   0.804511 |         3.1 |
| S3        | Representation Comparison Part B | BERT embedding (bert-base-uncased)                    | experiment         |   0.342038 |      0.909174 |   0.932331 |         5.8 |
| S4        | Improvement Core                 | LR+Weight (rp=0.05)                                   | experiment         |   0.337503 |      0.84375  |   0.815789 |         6.2 |
| S4        | Improvement Core                 | LR+Weight (rp=1.0)                                    | experiment         |   0.334864 |      0.839582 |   0.800752 |         3.2 |
| S4        | Improvement Core                 | CNB (S2 reference)                                    | reference          |   0.333238 |      0.845481 |   0.815789 |         1   |
| S2        | Model Comparison                 | Complement NaiveBayes                                 | experiment         |   0.333238 |      0.845481 |   0.815789 |         1   |
| S4        | Improvement Core                 | LR+Weight (rp=0.1)                                    | experiment         |   0.333092 |      0.842166 |   0.81203  |         4.6 |
| S4        | Improvement Core                 | LR+Weight (rp=0.01)                                   | experiment         |   0.331346 |      0.841162 |   0.81203  |         8   |
| S3        | Representation Comparison Part B | GloVe (twitter-100d)                                  | experiment         |   0.331198 |      0.888644 |   0.913534 |         2.3 |
| S2        | Model Comparison                 | OneVsRest + LinearSVC                                 | experiment         |   0.314219 |      0.876563 |   0.890977 |       129.7 |
| S2        | Model Comparison                 | Decision Tree (maxDepth=10)                           | experiment         |   0.29467  |      0.880865 |   0.909774 |         2.9 |
| S4        | Ablation Study                   | No class weight                                       | analysis           |   0.2367   |      0.861664 |   0.902256 |         4.1 |
| S1        | Baseline                         | TF-IDF unigram + LR                                   | baseline           |   0.2337   |      0.859    |   0.8985   |         8.3 |
| S3        | Representation Comparison Part A | CountVectorizer (no IDF)                              | experiment         |   0.233666 |      0.859049 |   0.898496 |         6.2 |
| S3        | Representation Comparison Part A | TF-IDF (1,2-gram)                                     | experiment         |   0.233666 |      0.859049 |   0.898496 |        13.1 |
| S3        | Representation Comparison Part A | TF-IDF (unigram)                                      | baseline-reference |   0.233666 |      0.859049 |   0.898496 |         9.5 |
| S2        | Model Comparison                 | Logistic Regression (multinomial, regParam=0.1)       | baseline-reference |   0.233666 |      0.859049 |   0.898496 |         8.3 |
| S3        | Representation Comparison Part A | Word2Vec (dim=100)                                    | experiment         |   0.188889 |      0.845029 |   0.894737 |         8   |
| S2        | Model Comparison                 | Random Forest (numTrees=100)                          | experiment         |   0.188889 |      0.845029 |   0.894737 |         5.4 |
| S4        | Optional MLP + Word2Vec          | MLP + Word2Vec (dim=100)                              | optional           |   0.188469 |      0.843152 |   0.890977 |        20.1 |