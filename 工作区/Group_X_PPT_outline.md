# CDS527 Big Data Analytics — Final Presentation Outline
## Task 1: Text Classification System + Task 2: Google Case Study
### Approximate duration: 15 minutes

---

## Slide 1 — Title Slide
- Title: `Big Data Analytics: Text Classification and the Google Ecosystem`
- Course: CDS527 Big Data Analytics — Language Models
- Group members and student IDs
- Term 2, 2025-2026

---

## Slide 2 — Assignment Scope and Presentation Map
- This presentation covers the two required parts of the group project.
- `Task 1: System Development`
  - Build, compare, and improve a PySpark-based text classification system.
- `Task 2: Case Study`
  - Analyse Google from a Big Data perspective and propose a solution framework.
- Presentation flow:
  - Task 1 about 10 minutes
  - Task 2 about 4 minutes
  - Final synthesis about 1 minute

---

## PART 1: TASK 1 — Text Emotion Classification

---

## Slide 3 — Problem Definition and Evaluation Setup
- Goal: classify each tweet into one of 5 emotion classes
- Data file: `smile-annotations-final.csv`
- Raw dataset: `1299` rows
- Modelling dataset used in the pipeline: `1298` rows after one duplicate-by-text removal
- Classes: `surprise`, `angry`, `disgust`, `happy`, `sad`
- Core difficulty: `happy` accounts for about `89%` of the data
- Main evaluation metric: `macro-F1`
- Fixed protocol:
  - PySpark-first pipeline
  - fixed label-aware split via `sampleBy(label, 0.8, seed=42)`
  - resulting train/test sizes: `1032 / 266`

---

## Slide 4 — Data Characteristics and EDA Insights
- Tweets are short and noisy, with limited semantic context
- Text contains URLs, mentions, hashtags, punctuation, and other platform artefacts
- The label distribution is extremely imbalanced toward `happy`
- Key implication:
  - high accuracy can be achieved by majority prediction alone
  - a robust system must improve minority-class recognition

---

## Slide 5 — Unified Experimental Framework
- All Task 1 experiments follow a common PySpark pipeline:
  - `Cleaning -> RegexTokenizer -> StopWordsRemover -> Feature Representation -> Classifier`
- Fair-comparison controls:
  - same split
  - same main metric
  - same PySpark-based workflow
- Four experiment blocks:
  - `S1 Baseline`
  - `S2 Model comparison`
  - `S3 Representation comparison`
  - `S4 Improvement and ablation`

---

## Slide 6 — S1 Baseline
- Baseline method: `TF-IDF (unigram) + Logistic Regression`
- Result:
  - `macro-F1 = 0.2337`
  - `accuracy = 0.8985`
- Interpretation:
  - accuracy looks high because the model predicts the majority class very often
  - minority classes are poorly recognised
- This baseline serves as the lower-bound reference for later comparisons

---

## Slide 7 — S2 Model Comparison under Fixed TF-IDF
| Model | Macro-F1 |
|-------|---------:|
| Logistic Regression | 0.2337 |
| **Complement Naive Bayes** | **0.3332** |
| Decision Tree | 0.2947 |
| OneVsRest + LinearSVC | 0.3142 |
| Random Forest | 0.1889 |

- Best model in this section: `Complement Naive Bayes`
- Key message:
  - changing the classifier helps
  - but the strongest gains still come from handling imbalance

---

## Slide 8 — S3 Representation Comparison
- `Part A: PySpark-native representations (fixed LR)`
  - TF-IDF unigram: `0.2337`
  - TF-IDF bigram: `0.2337`
  - CountVectorizer: `0.2337`
  - Word2Vec: `0.1889`
- `Part B: Supplementary embedding comparison`
  - GloVe + LR: `0.3312`
  - BERT embedding + LR: `0.3420`
- Interpretation:
  - stronger representations can help
  - but representation alone does not solve the imbalance problem

---

## Slide 9 — S4 Improvement Core: Class Weighting
- Keep the baseline backbone but add inverse-frequency class weights to Logistic Regression
- `regParam` sweep:
  - `0.01 -> 0.3313`
  - `0.05 -> 0.3375`
  - `0.10 -> 0.3331`
  - `0.50 -> 0.3453`
  - `1.00 -> 0.3349`
- Best result within the original improvement block:
  - `TF-IDF + weighted LR (regParam=0.5)`
  - `macro-F1 = 0.3453`
- This confirms that class imbalance is the main bottleneck

---

## Slide 10 — Final Best Configuration from Ablation
- Additional ablation study tests whether the preprocessing pipeline is too aggressive
- Final overall best result:
  - `A4 Light cleaning only + TF-IDF + class weight + LR`
  - `macro-F1 = 0.4465`
  - `accuracy = 0.8910`
- Milestone comparison:
  - baseline: `0.2337`
  - S2 best CNB: `0.3332`
  - weighted LR core result: `0.3453`
  - final overall best A4: `0.4465`
- Interpretation:
  - lighter preprocessing preserves useful emotion signal in short texts
  - imbalance handling remains necessary, but over-cleaning also hurts performance

---

## Slide 11 — Task 1 Wrap-up: Diagnostics and Validation
- Per-class behaviour under the final best A4 setup:
  - `angry` improves clearly
  - `surprise` recall improves clearly
  - `sad` remains weak
  - `disgust` remains the hardest class because the sample size is extremely small
- Sanity-check findings:
  - no clear evidence of label-mapping errors
  - no clear evidence of split errors
  - no clear evidence of evaluation bugs or direct leakage
- Final Task 1 conclusion:
  - low `macro-F1` is more plausibly caused by imbalance, minority-class scarcity, and preprocessing effects than by code errors

---

## PART 2: TASK 2 — Google Big Data Case Study

---

## Slide 12 — Google as a Big Data Case
- Google is a representative Big Data ecosystem because it operates at global scale across many products
- Background through the 5Vs:
  - `Volume`: web index, search logs, video, email, maps, cloud data
  - `Velocity`: real-time search, advertising auctions, streaming signals
  - `Variety`: text, image, video, audio, geospatial and behavioural data
  - `Veracity`: misinformation, spam, AI-generated noise, quality control
  - `Value`: ranking quality, ads revenue, recommendation systems, product optimisation

---

## Slide 13 — Task 2 Approach and Proposed Solution
- Problem framing:
  - web-scale indexing and retrieval
  - information quality under noisy and heterogeneous data
  - cross-product integration without losing control of privacy and governance
- Analytical approach:
  - statistical analysis
  - visual analysis
  - machine learning
  - semantic analysis
- Proposed solution framework:
  - intelligent indexing and ranking
  - cross-product data flywheel
  - privacy-aware integration and continuous model improvement

---

## Slide 14 — Critical Evaluation and KPI
- Strengths:
  - scale advantage and infrastructure moat
  - strong experimentation capability
  - data flywheel across products
- Risks:
  - privacy and regulatory pressure
  - information bubbles and fairness concerns
  - competitive pressure from LLM-based search
  - quality degradation from AI-generated content
- Example KPIs:
  - relevance quality
  - spam rate
  - user satisfaction
  - engagement or revenue quality metrics

---

## Slide 15 — Final Synthesis
- `Task 1` shows that in imbalanced text classification, data distribution and preprocessing strategy matter more than blindly swapping models
- `Task 2` shows that Big Data advantage depends not only on scale, but also on governance, trust, and strategic adaptation
- Overall lesson:
  - strong Big Data systems must balance performance, robustness, and responsibility

---

*Authoritative presentation text should follow this outline. If the exported `.pptx` differs, this outline is the current source of truth.*
