# Task2 论点素材

> 最后更新：2026-04-04
> 关联：[[任务笔记 - Task2 Google Case]] | [[Task2 报告结构]]

---

## 直接来自 Case 的原文引用

| 引用 | 用途 |
|------|------|
| "More than any other company, Google are probably responsible for introducing us to the benefits of analysing and interpreting Big Data in our day-to-day lives." | S1 Background 开场 |
| "The size of Google's index… is estimated to stand at around 100 petabytes (or 100 million gigabytes!)" | S1 Volume 证据 |
| "The Internet is a big place – since we moved online in the 1990s, it's been growing at a phenomenal rate" | S2 Volume/Velocity 背景 |
| "Information is uploaded to servers that may be located anywhere in the world" | S2 分布式挑战 |
| "It would take an army of humans an eternity to come up with anything approaching a comprehensive database" | S2 自动化索引必要性 |
| "How would computers know what was good information and what was pointless noise?" | S2 Veracity 核心问题 |
| "By default, computers can't determine this on their own… what's useless to one person may be critical to another" | S2 个性化/Veracity |
| "Google has a diverse set of data (e.g., email, map, voice, mobile phone data)" | S2 Variety |
| "Driverless car and Google Home" | S2/S4 未来数据领域 |
| "How these data can be used is also a consideration for Google's future planning" | S3/S4 战略方向 |

---

## 补充知识点（需在报告中标注来源）

### 技术解决方案
- **PageRank**（Brin & Page, 1998）：通过超链接网络评估页面权威性，是解决 Veracity 问题的核心算法
- **GFS（Google File System）**（Ghemawat et al., 2003）：分布式文件系统，处理 PB 级数据
- **MapReduce**（Dean & Ghemawat, 2004）：并行计算框架，实现大规模数据处理
- **BigTable**（Chang et al., 2006）：结构化数据存储，支持高并发读写
- **RankBrain**（2015）：机器学习模型，提升长尾查询的搜索相关性

### Big Data 5V 框架定义（供报告引用）
- Laney（2001）提出原始 3V（Volume, Velocity, Variety）
- 后续学者补充 Veracity（IBM）和 Value（Oracle/IDC）

### 批判性评估论点
- **GDPR（2018）**：欧盟数据保护条例，对 Google 数据采集模式形成合规压力
- **算法偏见**：搜索结果排序可能强化特定观点，导致信息过滤气泡（Filter Bubble）
- **反垄断**：美国司法部和欧盟委员会对 Google 搜索市场垄断的调查（2020–2024）
- **数据主权**：不同国家对数据跨境流动的限制（中国、俄罗斯、印度等）

---

## 论述逻辑链

```
互联网规模爆炸式增长（外部背景）
    ↓
Google 面临 5V Big Data 挑战（问题分析）
    ↓
自动化爬取 + PageRank + 分布式计算 + ML（技术解决方案）
    ↓
跨产品数据整合 + 广告变现（商业价值实现）
    ↓
隐私/算法/垄断挑战（批判性评估）
    ↓
新数据领域（无人驾驶/IoT）带来的下一轮挑战（未来展望）
```

---

## 待补充

- [ ] 确认参考文献格式（APA / Harvard）
- [ ] 为 PageRank/GFS/MapReduce 找具体引用来源
- [ ] 确认 case 中是否暗示了特定的分析框架（SWOT / 5V / 其他）
