# Task2 报告结构

> 最后更新：2026-04-04
> 关联：[[任务笔记 - Task2 Google Case]] | [[Task2 论点素材]] | [[Task2 下一步]]

---

## 整体定位

- 字数限制：3 页以内（Word report）
- 风格：学术性 case study，有分析深度，结构清晰
- 核心论述线索：Big Data challenge → Google 的解决方案 → 批判性评估

---

## Section 1：Background of the Case

### Objective
介绍 Google 的业务背景，点明为何 Google 是 Big Data 的典型代表

### Key Points
- Google 搜索索引规模（~100PB）——直接说明 Big Data 特征
- Google 从搜索扩展到多产品线（Chrome、Gmail、Android、Maps、Ads）
- 所有产品均以 Big Data 为核心驱动力
- 互联网的持续高速增长是问题产生的外部背景

### Evidence from Case
> "More than any other company, Google are probably responsible for introducing us to the benefits of analysing and interpreting Big Data in our day-to-day lives."
> "The size of Google's index… is estimated to stand at around 100 petabytes."

### Paragraph Direction
1 段：Google 在 Big Data 领域的标志性地位 + 索引规模数据
2 段：产品扩张路径说明数据战略的一贯性

---

## Section 2：Big Data Characteristics and Problem Analysis

### Objective
用 5V 框架分析 Google 面临的 Big Data 挑战，与 case 文本直接挂钩

### Key Points

| 特征 | Google 的挑战 |
|------|--------------|
| **Volume** | 100PB 索引；数十亿网页；持续增长，无法人工处理 |
| **Velocity** | 实时搜索响应；网页内容持续更新 |
| **Variety** | 文本、邮件、地图、语音、手机数据、传感器（无人车/Home） |
| **Veracity** | 计算机无法自动判断信息好坏；有用性因人而异 |
| **Value** | 从数据提取商业价值（广告定向、个性化服务） |

### Evidence from Case
> "Building an index isn't trivial. It would take an army of humans an eternity…"
> "How would computers know what was good information and what was pointless noise?"
> "Google has a diverse set of data (e.g., email, map, voice, mobile phone data)…"

### Paragraph Direction
1 段：Volume + Velocity（规模与速度挑战）
2 段：Variety + Veracity（多样性与质量判断挑战）
3 段：Value（从数据中提取价值的战略意义）

---

## Section 3：Proposed Big Data Solution

### Objective
阐述 Google 针对上述挑战所采用的大数据解决方案

### Key Points

**技术层面：**
- **Googlebot 爬虫**：自动化索引整个互联网
- **PageRank 算法**：用链接关系评估页面权威性，解决 Veracity 问题
- **分布式基础设施**：GFS（Google File System）解决 Volume；MapReduce 解决并行计算；BigTable 解决结构化存储
- **机器学习**：RankBrain 等 ML 模型提升搜索相关性，解决个性化问题

**战略层面：**
- **跨产品数据整合**：Gmail + Maps + Android + Search 构建统一用户画像
- **广告生态**：将数据分析能力转化为 Google Ads 商业价值
- **新域扩张**：无人驾驶（Waymo）、Google Home 作为数据采集的新入口

### Evidence from Case
- Case 描述问题，隐含解决方向（索引自动化、相关性判断、数据多样化管理）
- 可结合公开知识补充 GFS/MapReduce/PageRank（需在报告中标注来源）

### Paragraph Direction
1 段：自动化索引与 PageRank（解决 Volume + Veracity）
2 段：分布式计算基础设施（解决 Velocity + Volume）
3 段：跨产品数据整合与商业化（解决 Value）

---

## Section 4：Critical Evaluation of the Solution

### Objective
批判性评估 Google 方案的优缺点及未来挑战

### Key Points

**优势（Strengths）：**
- 搜索精确度与响应速度达到行业领先水平
- 跨产品数据整合形成竞争壁垒
- 持续的技术创新能力（ML、AI、Quantum Computing）

**局限性（Limitations）：**
- **隐私问题**：大规模数据采集引发用户隐私争议（GDPR 合规压力）
- **算法偏见**：PageRank 和 ML 模型存在偏见风险，可能强化信息茧房
- **垄断风险**：数据优势形成市场垄断，受反垄断监管
- **数据安全**：集中式数据存储带来安全风险

**未来挑战：**
- 新数据领域（无人驾驶、IoT、语音）的监管不确定性
- AI 生成内容对搜索索引质量的冲击
- 全球数据主权法规的差异化合规要求

### Paragraph Direction
1 段：方案的技术优势与商业成功
2 段：隐私、算法偏见、垄断等批判性问题
3 段：面向未来的挑战与应对方向

---

## Section 5（可选）：Conclusion

### Key Points
- 重申 central problem statement
- 总结 Google 方案的核心逻辑
- 一句话点明对大数据领域的启示

---

## 篇幅分配参考（3 页）

| Section | 预计篇幅 |
|---------|---------|
| S1 Background | ~0.4 页 |
| S2 Big Data Analysis | ~0.7 页 |
| S3 Proposed Solution | ~0.8 页 |
| S4 Critical Evaluation | ~0.7 页 |
| S5 Conclusion | ~0.2 页 |
| 参考文献 | ~0.2 页 |
| **合计** | **~3.0 页** |
