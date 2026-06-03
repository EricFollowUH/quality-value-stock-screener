# 优质低估值股票筛选器

[English](README.md) | [中文](README.zh-CN.md)

`quality-value-stock-screener` 是一个 Codex skill，用于用行业差异化的质量和估值框架筛选公开交易股票。

它主要回答两个问题：

- 在一组股票代码里，哪些公司同时具备较高业务质量和较合理估值？
- 某一只具体股票在当前价格下是否值得进一步研究？

这个 skill 使用 6 维评分模型：

| 维度 | 检查内容 |
|---|---|
| 增长 | Revenue growth、ARR growth、客户数或交易量增长 |
| 质量 | Gross margin、Operating margin、ROIC/ROE、单位经济模型 |
| 现金流 | FCF margin、FCF conversion、FCF yield |
| 估值 | Forward P/E、EV/EBITDA、FCF yield、PEG、行业专用估值倍数 |
| 风险 | 资产负债表、杠杆、流动性、监管或周期风险 |
| 可持续性 | 护城河、留存率、生态、客户质量、管理层执行 |

## 为什么要按行业区分指标

好的股票筛选不能用一套标准硬套所有公司。银行不能用 SaaS 指标打分，REITs 不能主要看 EPS，半导体公司需要考虑周期位置，生物科技公司更需要看管线、临床节点和现金 runway，而不是 P/E。

这个 skill 内置以下行业模板：

- SaaS / 企业软件
- AI / 云 / 平台型科技
- 半导体 / 芯片设计
- 半导体设备 / 硬件
- 消费品牌 / 必需消费
- 零售 / 电商
- 工业 / 制造
- 能源 / 油气
- 银行
- 支付网络 / 金融基础设施
- 保险
- 公用事业
- REITs
- 生物科技 / 药物研发

## 安装

把仓库 clone 到 Codex skills 文件夹：

```bash
git clone https://github.com/EricFollowUH/quality-value-stock-screener \
  ~/.codex/skills/quality-value-stock-screener
```

如果要使用附带的筛选脚本，安装 `yfinance`：

```bash
python3 -m pip install --user yfinance
```

## 在 Codex 中使用

示例 prompt：

```text
Use $quality-value-stock-screener to screen NVDA META MSFT ADBE V CRM for quality and valuation.
```

```text
Use $quality-value-stock-screener to evaluate whether MSFT is worth buying now.
```

```text
Use $quality-value-stock-screener to compare PLTR, TSLA, AMZN, GOOGL, ORCL, ARM, CDNS, and NVDA.
```

skill 应输出：

- 行业分类
- 6 维评分表
- 30 分制总分
- 核心投资假设
- 估值解释
- 风险和反证条件
- 使用当前事实时的数据时效和来源

## 脚本筛选

直接运行附带脚本：

```bash
python3 scripts/screen_stocks.py --tickers NVDA META MSFT ADBE V CRM --format markdown
```

也支持 JSON 输出：

```bash
python3 scripts/screen_stocks.py --tickers MSFT --format json
```

脚本只是第一层研究辅助。它通过 `yfinance` 使用 Yahoo Finance 数据，数据可能滞后、不完整或存在口径问题。做出结论前，应回到公司官方财报、SEC filing、investor relations release 和最新新闻进行核查。

## 分数解释

| 总分 | 含义 | 默认动作 |
|---:|---|---|
| 25-30 | 高质量候选 | 值得深入研究和估值建模 |
| 20-24 | 有吸引力但不完美 | 找清楚关键风险和安全边际 |
| 15-19 | 普通或偏投机 | 只有在有明确催化或反转逻辑时观察 |
| <15 | 低优先级 | 通常跳过 |

## 仓库结构

```text
quality-value-stock-screener/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── disclaimer.md
│   ├── industry-framework.md
│   └── scoring-model.md
└── scripts/
    └── screen_stocks.py
```

## 研究边界

这个项目用于投资研究和股票筛选，不是个性化财务建议、税务建议、法律建议，也不是交易系统。

skill 不应给出确定性的买卖指令。好的输出应该解释：

- 为什么这只股票筛选结果好或不好
- 当前估值隐含了什么假设
- 哪些证据会推翻投资逻辑
- 做决定前需要刷新哪些数据

## License

目前尚未选择 license。如果计划让其他人复用，建议后续添加明确的开源 license，例如 MIT 或 Apache-2.0。
