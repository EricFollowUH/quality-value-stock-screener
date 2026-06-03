# Quality Value Stock Screener

[English](README.md) | [中文](README.zh-CN.md)

`quality-value-stock-screener` is a Codex skill for screening public equities with an industry-aware quality and valuation framework.

It helps answer two common research questions:

- Which stocks in a ticker list screen as high-quality and reasonably valued?
- Is a specific stock worth deeper research at the current price?

The skill uses a six-factor scorecard:

| Dimension | What It Checks |
|---|---|
| Growth | Revenue growth, ARR growth, customer or volume growth |
| Quality | Gross margin, operating margin, ROIC/ROE, unit economics |
| Cash flow | FCF margin, FCF conversion, FCF yield |
| Valuation | Forward P/E, EV/EBITDA, FCF yield, PEG, sector-specific multiples |
| Risk | Balance sheet, leverage, liquidity, regulatory or cycle risk |
| Sustainability | Moat, retention, ecosystem, customer quality, execution |

## Why Industry-Aware Screening Matters

A good stock screen must use different standards for different business models. A bank should not be scored with SaaS metrics. A REIT should not be judged primarily by EPS. A semiconductor company needs cycle awareness. A biotech company may need pipeline and cash runway analysis more than P/E.

This skill includes industry templates for:

- SaaS / enterprise software
- AI / cloud / platform technology
- Semiconductors / chip design
- Semiconductor equipment / hardware
- Consumer brands / staples
- Retail / e-commerce
- Industrials / manufacturing
- Energy / oil and gas
- Banks
- Payment networks / financial infrastructure
- Insurance
- Utilities
- REITs
- Biotech / drug development

## Install

Clone the repository into your Codex skills folder:

```bash
git clone https://github.com/EricFollowUH/quality-value-stock-screener \
  ~/.codex/skills/quality-value-stock-screener
```

If you want to use the optional screening script, install `yfinance`:

```bash
python3 -m pip install --user yfinance
```

## Use In Codex

Example prompts:

```text
Use $quality-value-stock-screener to screen NVDA META MSFT ADBE V CRM for quality and valuation.
```

```text
Use $quality-value-stock-screener to evaluate whether MSFT is worth buying now.
```

```text
Use $quality-value-stock-screener to compare PLTR, TSLA, AMZN, GOOGL, ORCL, ARM, CDNS, and NVDA.
```

The skill should return:

- Industry classification
- Six-factor score table
- Total score out of 30
- Key thesis
- Valuation interpretation
- Risk and disconfirming evidence
- Data freshness and sources when current facts are used

## Scripted Screening

Run the bundled script directly:

```bash
python3 scripts/screen_stocks.py --tickers NVDA META MSFT ADBE V CRM --format markdown
```

JSON output is also available:

```bash
python3 scripts/screen_stocks.py --tickers MSFT --format json
```

The script is a first-pass research aid. It uses Yahoo Finance data through `yfinance`, which can be stale or incomplete. Review output against official company filings and investor relations releases before drawing conclusions.

## Score Interpretation

| Total Score | Meaning | Default Action |
|---:|---|---|
| 25-30 | High-quality candidate | Worth deeper research and valuation work |
| 20-24 | Attractive but imperfect | Identify key risk and required margin of safety |
| 15-19 | Ordinary or speculative | Watch only with a clear catalyst or turnaround thesis |
| <15 | Low priority | Usually pass |

## Repository Structure

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

## Research Boundaries

This project is for investment research and stock screening. It is not personalized financial advice, tax advice, legal advice, or a trading system.

The skill should not produce guaranteed buy/sell instructions. A strong output should explain:

- Why the stock screens well or poorly
- What assumptions the current valuation implies
- What evidence would break the thesis
- What data should be refreshed before making a decision

## License

No license has been selected yet. If you plan to make this reusable by others, add an explicit open-source license such as MIT or Apache-2.0.
