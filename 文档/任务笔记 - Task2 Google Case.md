# 任务笔记 - Task2 Google Case

> 最后更新：2026-04-04
> 关联：[[Task2 报告结构]] | [[Task2 论点素材]] | [[Task2 下一步]] | [[当前状态]]

---

## Step 1：Case 内容拆解

### Case 背景（Background）

- Google 是将 Big Data 引入日常生活的标志性公司
- Google 搜索索引估计规模：**~100 petabytes**（1 亿 GB），是 Big Data 的典型体现
- 过去十年 Google 从搜索引擎扩展至：
  - Web 浏览器（Chrome）
  - 电子邮件（Gmail）
  - 手机操作系统（Android）
  - 地图服务（Google Maps）
  - 全球最大在线广告网络（Google Ads）
- 所有产品线均以 Big Data 技术为基础

### 明确写出的 Business Problem

Case 文本直接描述以下核心挑战：

1. **规模问题（Volume）**：互联网自 1990s 以来以惊人速度增长，数据量极大
2. **分布问题（Distribution）**：数据分布在全球各地的服务器，用户访问跨越千里
3. **索引问题（Indexing）**：无法依靠人工建立全面索引，必须依赖自动化计算机处理
4. **相关性判断问题（Relevance/Veracity）**：计算机默认无法区分"有用"与"无用"信息；有用与否还因人而异
5. **数据多样化问题（Variety）**：Google 已拥有 email、map、voice、mobile 等多种数据；未来还将涉及无人驾驶汽车、Google Home 等新型数据

### 可合理推导的 Big Data Challenge（5V 框架）

| 维度 | 具体挑战 |
|------|----------|
| Volume | 100PB 索引；数十亿网页；持续增长 |
| Velocity | 实时搜索响应；网页内容持续更新；用户行为实时反馈 |
| Variety | 文本、图片、视频、地理位置、邮件、语音、传感器数据 |
| Veracity | 区分高质量信息与噪声；个性化相关性判断 |
| Value | 从数据中提取商业价值（广告定向、用户洞察） |

### 可用的 Big Data 分析角度

1. **搜索与索引技术**：Googlebot 爬虫、倒排索引、PageRank 算法
2. **分布式基础设施**：GFS（Google File System）、MapReduce、BigTable
3. **机器学习与 AI**：相关性排序、个性化推荐、语音识别
4. **跨产品数据整合**：搜索 + Gmail + Maps + Android 形成用户画像
5. **新兴数据领域**：无人驾驶（传感器数据）、Google Home（语音数据）、IoT

---

## Step 2：Central Problem Statement（两个版本）

### 版本 A（聚焦核心搜索问题）

> "How can Google effectively index, rank, and retrieve relevant information from a continuously expanding internet, while ensuring search results are accurate and personalised for each individual user?"

适合：偏技术路线，聚焦搜索引擎本身

### 版本 B（更宏观的 Big Data 战略视角）★ 推荐

> "Given the explosive growth of internet data in terms of volume, variety, and velocity, how should Google design a scalable Big Data infrastructure that enables real-time search relevance, cross-product data integration, and expansion into new data domains such as autonomous vehicles and smart home devices?"

适合：覆盖更广，能支撑 3V/5V 分析框架，也能引出跨产品数据战略，更适合 3 页 report 的论述深度

**推荐理由**：版本 B 既能串联 case 中所有提到的挑战，又为后续 Solution 和 Evaluation 章节提供充足论述空间。

---

## Step 3：报告结构

详见 [[Task2 报告结构]]

---

## 进度记录

- [x] Step 1：读取并拆解 case（2026-04-04）
- [x] Step 2：确定 problem statement（2026-04-04）
- [x] Step 3：搭建报告结构（2026-04-04）
- [x] Step 4：填充各节 bullet-point 大纲（2026-04-04）
- [x] Step 5a：Section 1 Background 段落完成（2026-04-04）→ [[Task2 报告草稿]]
- [x] Step 5b：Section 2 Big Data Analysis 段落（2026-04-04）
- [x] Step 5c：Section 3 Proposed Solution 段落（2026-04-04）
- [x] Step 5d：Section 4 Critical Evaluation 段落（2026-04-04）
- [x] Step 5e：Section 5 Conclusion 段落（2026-04-04）
