---
name: quality-value-stock-screener
description: Use when screening public stocks for quality plus reasonable valuation, ranking a ticker list, comparing investment candidates, or evaluating whether a specific stock is attractive. Applies industry-aware metrics for growth, quality, cash flow, valuation, risk, and sustainability; useful for requests like "screen undervalued quality stocks", "score MSFT", "compare NVDA META ADBE", or "is this stock worth researching?"
---

# Quality Value Stock Screener

## Purpose

Use this skill to turn equity questions into structured research, not buy/sell commands. The core output is an industry-aware scorecard that separates business quality from valuation and includes the assumptions that would disprove the thesis.

Default language should match the user. For Chinese users, use Chinese while preserving finance terms such as FCF, ROIC, EV/EBITDA, ARR, NRR, PEG, and P/FFO.

## Core Workflow

1. **Clarify the task type**
   - Single-stock analysis: evaluate one ticker.
   - Candidate screening: rank a user-provided ticker list.
   - Open-ended screening: build a conservative candidate pool first, then score it.

2. **Refresh current facts**
   - For current investment questions, verify latest price, valuation, financials, earnings date, and recent material news.
   - Prefer official investor relations filings/releases for financial claims; use market-data sources for prices and valuation snapshots.
   - If live data is unavailable, state that clearly and mark the result as a framework-only analysis.

3. **Classify the industry**
   - Pick the closest template from `references/industry-framework.md`.
   - Do not use one generic valuation method across all sectors.
   - Use banks, insurance, REITs, energy, SaaS, AI/cloud, semiconductor, consumer, industrial, utility, and biotech templates differently.

4. **Score the company**
   - Use the six dimensions from `references/scoring-model.md`:
     growth, quality, cash flow, valuation, risk, sustainability.
   - Score each from 0 to 5, total 30.
   - Explain each score in one or two concrete facts.

5. **Separate recommendation tiers**
   - 25-30: high-quality candidate; worth deeper research.
   - 20-24: attractive but needs risk/safety-margin work.
   - 15-19: ordinary or speculative; require a clear catalyst.
   - Under 15: usually pass unless there is a defined turnaround thesis.

6. **Always include risk and disconfirmation**
   - List the facts that would make the thesis wrong.
   - Avoid certainty words such as guaranteed, risk-free, sure win, or must buy.
   - For portfolio advice, discuss role and sizing qualitatively unless the user gives constraints.

## Scripted Screening

For ticker-list screening, prefer running:

```bash
python3 scripts/screen_stocks.py --tickers NVDA META MSFT ADBE V CRM --format markdown
```

The script uses `yfinance` when available. If missing, install it in the user environment only when appropriate:

```bash
python3 -m pip install --user yfinance
```

Use script output as a first pass. Still review the result manually, especially for banks, REITs, biotech, one-time accounting items, stale data, or obvious data-provider errors.

## Output Shape

For a single stock:

```markdown
## Direct Answer

Ticker:
Industry template:
Score: X/30
Conclusion: worth deeper research / watchlist / wait for price / avoid

| Dimension | Score | Reason |
|---|---:|---|
| Growth |  |  |
| Quality |  |  |
| Cash flow |  |  |
| Valuation |  |  |
| Risk |  |  |
| Sustainability |  |  |

Key thesis:
Disconfirming evidence:
Data checked:

## Deeper Challenge

Explain whether the user may be confusing a good company with a good stock, a low multiple with undervaluation, or a strong narrative with financial proof.
```

For screening:

```markdown
## Direct Answer

Top candidates:

| Rank | Ticker | Industry | Score | Why it screens well |
|---:|---|---|---:|---|

## Deeper Challenge

Discuss concentration risk, missing sectors, valuation sensitivity, and what data should be verified before buying.
```

## Reference Files

- `references/industry-framework.md`: industry-specific standards and risk signals.
- `references/scoring-model.md`: six-factor scoring rules and interpretation.
- `references/disclaimer.md`: safety language for investment outputs.

## Boundaries

This skill supports research and screening. It does not provide personalized financial advice, guaranteed returns, tax advice, legal advice, or instructions to trade. If the user asks for a definite trade, reframe into thesis, risk, valuation, time horizon, and position-size considerations.
