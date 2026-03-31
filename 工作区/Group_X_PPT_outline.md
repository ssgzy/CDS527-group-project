# CDS527 Big Data Analytics — Group Presentation Outline
## Task 1 (Text Classification) + Task 2 (Google Case Study)
### Approximate duration: 15 minutes

---

## Slide 1 — Title Slide
- Title: "Big Data Analytics for Text Classification and Case Study: Google"
- Course: CDS527 Big Data Analytics — Language Models
- Group members: ZEPENG GU, ZHEN ZHANG, MING GAO, ZHENXIAO YANG, NWANKWO Udoka, KAIWEN LIU, WENHAO CHEN
- Term 2, 2025-2026

---

## Slide 2 — Agenda
- Task 1: Building a text emotion classifier using PySpark
  - Dataset overview
  - Experimental pipeline
  - Key results
- Task 2: Google Big Data case study
- Conclusions and reflections

---

## PART 1: TASK 1 — Text Emotion Classification (approx. 10 min)

---

## Slide 3 — Dataset: SMILE Twitter Emotion Dataset
- Source: 13 British museum Twitter accounts, 2013–2015
- 1,299 tweets after preprocessing
- 5 emotion classes: happy, angry, sad, surprise, disgust
- **Severely imbalanced**: happy accounts for ~89% of all samples
- Key challenge: standard accuracy is misleading — macro-F1 used throughout
- Evaluation protocol: stratified 80/20 split (seed=42), macro-F1 as primary metric

---

## Slide 4 — Exploratory Data Analysis
- Class distribution bar chart → visualises the severe imbalance
- Tweet length distribution → most tweets are 60–120 characters
- Word frequency analysis → top-50 most common tokens before and after stopword removal
- Word cloud by emotion class → happy class dominated by positive cultural/event words
- Key insight: standard bag-of-words features will be heavily biased toward happy-class vocabulary

---

## Slide 5 — Experimental Pipeline (PySpark)
All experiments use a unified PySpark ML Pipeline:
```
RegexTokenizer → StopWordsRemover → [Feature Representation] → [Classifier]
```
- Feature representations tested: TF-IDF (unigram), TF-IDF (bigram), CountVectorizer, Word2Vec
- Classifiers tested: Logistic Regression (LR), Complement Naive Bayes (CNB), Decision Tree (DT), Random Forest (RF), OneVsRest + LinearSVC
- All experiments use the same train/test split for fair comparison

---

## Slide 6 — Section 1: Baseline Result
- Configuration: TF-IDF (unigram) + Logistic Regression, no class weighting
- Macro-F1 = **0.2337**
- The model predicts "happy" for almost all samples due to class imbalance
- This establishes the lower bound — any improvement must beat 0.2337

---

## Slide 7 — Section 2: Model Comparison (fixed TF-IDF features)
| Model | Macro-F1 |
|-------|---------|
| Logistic Regression | 0.2337 |
| **Complement Naive Bayes** | **0.3332** |
| Decision Tree | ~0.22 |
| Random Forest | ~0.23 |
| OneVsRest + LinearSVC | ~0.23 |

- Complement NaiveBayes (CNB) handles class imbalance better by design — it trains each class's complement
- CNB achieved +42.5% relative improvement over baseline without any class rebalancing
- Tree-based methods showed similar weakness to LR under imbalance

---

## Slide 8 — Section 3: Feature Representation Comparison (fixed LR)
| Feature | Macro-F1 |
|---------|---------|
| TF-IDF unigram | 0.2337 |
| TF-IDF bigram | 0.2337 |
| CountVectorizer | 0.2337 |
| Word2Vec | 0.2337 |

- Under the fixed-LR, no-class-weighting protocol, all four representations converged to identical results
- Interpretation: within this experimental setting, LR's bias toward the majority class dominates regardless of feature space
- This does not mean features are unimportant in general — the result is specific to this protocol
- Key implication: address class imbalance before exploring feature engineering

---

## Slide 9 — Section 4: Improvement — Class Weighting + Hyperparameter Tuning
**Inverse-frequency class weights applied to LR:**
- disgust ×20.6, surprise ×7.1, sad ×6.3, angry ×4.9, happy ×0.2

**regParam sweep (5 values): [0.01, 0.05, 0.1, 0.5, 1.0]**

| Config | regParam | Macro-F1 |
|--------|----------|---------|
| LR + Weight | 0.01 | 0.3198 |
| LR + Weight | 0.05 | 0.3226 |
| LR + Weight | 0.10 | 0.3285 |
| **LR + Weight** | **0.50** | **0.3453** |
| LR + Weight | 1.00 | 0.3423 |

- Best result: **macro-F1 = 0.3453** (regParam=0.5) — +47.7% over baseline

---

## Slide 10 — Deep Analysis: Confusion Matrix and Per-Class Breakdown
- Confusion matrix: after class weighting, minority classes (disgust, surprise, sad) are now predicted
- Per-class F1:
  - happy: high recall (dominant class)
  - angry, sad, surprise: improved but still low (data scarcity)
  - disgust: fewest samples — hardest to classify
- Hardest confused pairs: angry↔sad (semantically similar negative emotions)
- Training time vs. performance: CNB is fastest; LR+Weight at rp=0.5 offers best F1/time trade-off

---

## Slide 11 — Task 1 Final Results Summary
| Section | Best Configuration | Macro-F1 |
|---------|-------------------|---------|
| S1 Baseline | TF-IDF + LR | 0.2337 |
| S2 Model Comparison | TF-IDF + CNB | 0.3332 |
| S3 Feature Comparison | Fixed LR — no difference | 0.2337 |
| **S4 Improvement** | **LR + Class Weights (rp=0.5)** | **0.3453** |

**Key finding:** Class imbalance handling has a stronger impact than feature representation choice in this dataset. The data flywheel effect — where the majority class dominates training — must be corrected before other optimisations become visible.

---

## PART 2: TASK 2 — Google Big Data Case Study (approx. 4 min)

---

## Slide 12 — Google: Big Data at Scale (Background)
- Core product: Search engine with 100+ petabyte index, 8.5 billion daily queries
- Ecosystem: Gmail, Maps, Android, Chrome, YouTube, Waymo, Google Cloud
- The 5Vs of Google's Big Data:
  - **Volume**: 100PB web index; 500 hours of YouTube video per minute
  - **Velocity**: Real-time search indexing, millisecond ad auctions
  - **Variety**: Structured logs, HTML, images, video, voice, spatial data
  - **Veracity**: Web spam, misinformation, AI-generated content noise
  - **Value**: $237B advertising revenue (2023); AI product development

---

## Slide 13 — How Google Approaches the Problem (4 Analytics Dimensions)
1. **Statistical Analysis**: Large-scale A/B testing on ranking and ads; anomaly detection for spam
2. **Visual Analysis**: Google Analytics heatmaps, Looker dashboards, Google Maps spatial clustering
3. **Machine Learning**: RankBrain (2015) neural query understanding; TensorFlow + TPUs for model training; YouTube recommendations; Gmail spam/Smart Reply
4. **Semantic Analysis**: Knowledge Graph (2012) entity extraction; BERT/MUM for conversational query intent understanding

---

## Slide 14 — Google's Solution Framework (3 Components)
1. **Intelligent Indexing Pipeline**: Distributed crawlers → MapReduce → PageRank → spam classifiers (gradient-boosted trees)
2. **Multi-modal Ranking and Personalisation**: BERT/MUM for semantic matching; collaborative filtering for personalisation; continuous retraining on live user signals
3. **Cross-Product Data Integration with Privacy**: Apache Kafka/Pub-Sub event streaming across Gmail/Maps/Android/Waymo; differential privacy + federated learning to preserve user privacy

---

## Slide 15 — Critical Evaluation: Strengths and Risks
**Strengths:**
- Data flywheel: more users → better models → more users (self-reinforcing moat)
- Proven infrastructure: Bigtable, Spanner, TPUs at billion-query scale
- End-to-end ML pipelines enabling rapid experimentation

**Limitations and Risks:**
- Privacy/regulatory risk: GDPR, EU Digital Markets Act, antitrust scrutiny
- Filter bubble: personalisation may reduce information diversity
- Data quality: SEO spam and AI-generated content challenge quality at scale
- Competitive disruption: LLM-based search (ChatGPT, Perplexity) disrupts the traditional search paradigm; Google must accelerate Gemini integration

**SMART KPIs:** NDCG > 0.85; user satisfaction > 4.2/5; spam rate < 0.1% of indexed pages; revenue per query growth

---

## Slide 16 — Conclusions and Reflections
**Task 1 takeaways:**
- PySpark ML Pipelines enable scalable, reproducible NLP experiments
- Class imbalance is the dominant challenge in this dataset — must be addressed before tuning features or hyperparameters
- Complement NaiveBayes is a strong, fast baseline for imbalanced text classification
- Best system: LR + inverse-frequency class weights (regParam=0.5), macro-F1 = 0.3453

**Task 2 takeaways:**
- Google's competitive advantage is deeply structural — the data flywheel compounds over time
- Technical capability is mature; the primary strategic risk is regulatory and societal
- Generative AI (Gemini) is Google's necessary response to LLM-based search disruption

**Future directions:**
- Apply BERT/transformer embeddings as features (beyond PySpark native pipeline)
- Data augmentation for minority emotion classes
- Explore ensemble methods combining CNB and LR+Weight

---

*End of presentation outline. Approximate total: 15 slides, 15 minutes.*
*Use this outline as input to NotebookLM to generate speaker notes and slide content.*
