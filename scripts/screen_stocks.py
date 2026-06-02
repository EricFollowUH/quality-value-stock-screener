#!/usr/bin/env python3
"""Screen public equities with industry-aware quality/value heuristics.

This script is a first-pass research aid. It uses Yahoo Finance via yfinance
when available and should be reviewed against official filings before any
investment conclusion.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

try:
    import yfinance as yf
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: yfinance. Install it with:\n"
        "  python3 -m pip install --user yfinance"
    ) from exc


DIMENSIONS = ("growth", "quality", "cash_flow", "valuation", "risk", "sustainability")


@dataclass
class Score:
    ticker: str
    name: str
    sector: str
    industry: str
    template: str
    current_price: float | None
    total_score: int
    growth: int
    quality: int
    cash_flow: int
    valuation: int
    risk: int
    sustainability: int
    reasons: dict[str, str]
    metrics: dict[str, Any]


def safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return None
        return out
    except (TypeError, ValueError):
        return None


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def num(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1f}"


def clamp(score: int) -> int:
    return max(0, min(5, score))


def classify_template(sector: str, industry: str) -> str:
    text = f"{sector} {industry}".lower()
    if "reit" in text:
        return "REITs"
    if "bank" in text:
        return "Banks"
    if "credit services" in text or "payment" in text:
        return "Payment networks / financial infrastructure"
    if "insurance" in text:
        return "Insurance"
    if "biotechnology" in text or "biotech" in text:
        return "Biotech / drug development"
    if "utilities" in text:
        return "Utilities"
    if "energy" in text or "oil" in text or "gas" in text:
        return "Energy / oil and gas"
    if "semiconductor" in text:
        return "Semiconductors / chip design"
    if "software" in text:
        return "SaaS / enterprise software"
    if "internet content" in text or "internet retail" in text or "cloud" in text:
        return "AI / cloud / platform technology"
    if "retail" in text or "e-commerce" in text:
        return "Retail / e-commerce"
    if "consumer defensive" in text or "household" in text or "beverages" in text:
        return "Consumer brands / staples"
    if "industrial" in text or "manufacturing" in text or "equipment" in text:
        return "Industrials / manufacturing"
    if sector == "Technology":
        return "AI / cloud / platform technology"
    return "General quality/value"


def growth_score(template: str, revenue_growth: float | None, earnings_growth: float | None) -> tuple[int, str]:
    growth = revenue_growth if revenue_growth is not None else earnings_growth
    if growth is None:
        return 2, "Growth data unavailable; defaulted to neutral-low."
    if template in {"Consumer brands / staples", "Utilities", "Banks", "Insurance", "REITs"}:
        thresholds = (0.10, 0.06, 0.03, 0.00)
    elif template == "Payment networks / financial infrastructure":
        thresholds = (0.15, 0.08, 0.04, 0.00)
    elif template == "Energy / oil and gas":
        thresholds = (0.12, 0.06, 0.02, -0.05)
    else:
        thresholds = (0.30, 0.15, 0.07, 0.00)
    if growth >= thresholds[0]:
        score = 5
    elif growth >= thresholds[1]:
        score = 4
    elif growth >= thresholds[2]:
        score = 3
    elif growth >= thresholds[3]:
        score = 2
    else:
        score = 1
    return score, f"Revenue growth {pct(revenue_growth)}; earnings growth {pct(earnings_growth)}."


def quality_score(template: str, gross_margin: float | None, operating_margin: float | None, roe: float | None) -> tuple[int, str]:
    score = 0
    if template == "Banks":
        score += 3 if roe and roe > 0.12 else 2 if roe and roe > 0.08 else 1
    else:
        if gross_margin is not None:
            score += 2 if gross_margin >= 0.70 else 1 if gross_margin >= 0.40 else 0
        if operating_margin is not None:
            score += 2 if operating_margin >= 0.25 else 1 if operating_margin >= 0.10 else 0
        if roe is not None:
            score += 1 if roe >= 0.15 else 0
    return clamp(score), f"Gross margin {pct(gross_margin)}, operating margin {pct(operating_margin)}, ROE {pct(roe)}."


def cash_flow_score(fcf: float | None, operating_cashflow: float | None, market_cap: float | None, revenue: float | None) -> tuple[int, str]:
    fcf_yield = fcf / market_cap if fcf is not None and market_cap else None
    fcf_margin = fcf / revenue if fcf is not None and revenue else None
    conversion = fcf / operating_cashflow if fcf is not None and operating_cashflow else None
    score = 2
    if fcf is not None and fcf < 0:
        score = 1
    if fcf_margin is not None:
        if fcf_margin >= 0.20:
            score = 5
        elif fcf_margin >= 0.10:
            score = 4
        elif fcf_margin >= 0.03:
            score = 3
        elif fcf_margin < 0:
            score = 1
    if fcf_yield is not None and fcf_yield >= 0.05:
        score = max(score, 4)
    return score, f"FCF yield {pct(fcf_yield)}, FCF margin {pct(fcf_margin)}, FCF/OCF {pct(conversion)}."


def valuation_score(
    template: str,
    forward_pe: float | None,
    peg: float | None,
    ev_ebitda: float | None,
    fcf: float | None,
    market_cap: float | None,
    revenue_growth: float | None,
) -> tuple[int, str]:
    fcf_yield = fcf / market_cap if fcf is not None and market_cap else None
    score = 2
    if template in {"Banks", "Insurance"}:
        score = 4 if forward_pe and forward_pe < 12 else 3 if forward_pe and forward_pe < 18 else 2
    elif template == "Energy / oil and gas":
        score = 5 if fcf_yield and fcf_yield > 0.08 else 4 if ev_ebitda and ev_ebitda < 8 else 3
    else:
        if forward_pe is not None:
            if forward_pe < 18:
                score = 5
            elif forward_pe < 28:
                score = 4
            elif forward_pe < 45:
                score = 3
            elif forward_pe < 70:
                score = 2
            else:
                score = 1
        if peg is not None and peg < 1.2:
            score = min(5, score + 1)
        if revenue_growth is not None and revenue_growth > 0.30 and forward_pe and forward_pe < 45:
            score = max(score, 4)
        if fcf_yield is not None and fcf_yield > 0.05:
            score = max(score, 4)
        if ev_ebitda is not None and ev_ebitda > 60:
            score = min(score, 2)
    return clamp(score), f"Forward P/E {num(forward_pe)}, PEG {num(peg)}, EV/EBITDA {num(ev_ebitda)}, FCF yield {pct(fcf_yield)}."


def risk_score(total_cash: float | None, total_debt: float | None, ebitda: float | None, debt_to_equity: float | None) -> tuple[int, str]:
    net_debt_to_ebitda = None
    if total_cash is not None and total_debt is not None and ebitda:
        net_debt_to_ebitda = (total_debt - total_cash) / ebitda
    score = 3
    if net_debt_to_ebitda is not None:
        if net_debt_to_ebitda < 0:
            score = 5
        elif net_debt_to_ebitda < 1.5:
            score = 4
        elif net_debt_to_ebitda < 3.0:
            score = 3
        elif net_debt_to_ebitda < 5.0:
            score = 2
        else:
            score = 1
    elif debt_to_equity is not None:
        score = 4 if debt_to_equity < 50 else 3 if debt_to_equity < 150 else 2
    return score, f"Cash {human_money(total_cash)}, debt {human_money(total_debt)}, net debt/EBITDA {num(net_debt_to_ebitda)}."


def sustainability_score(template: str, gross_margin: float | None, operating_margin: float | None, revenue_growth: float | None, roe: float | None) -> tuple[int, str]:
    score = 3
    if template in {"AI / cloud / platform technology", "SaaS / enterprise software", "Semiconductors / chip design"}:
        score += 1
    if gross_margin is not None and gross_margin >= 0.70:
        score += 1
    if operating_margin is not None and operating_margin >= 0.25:
        score += 1
    if revenue_growth is not None and revenue_growth < 0:
        score -= 1
    if roe is not None and roe < 0:
        score -= 1
    return clamp(score), f"Template {template}; margin profile and growth used as moat proxies."


def human_money(value: float | None) -> str:
    if value is None:
        return "n/a"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}T"
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    return f"{value:.0f}"


def score_ticker(ticker: str) -> Score:
    info = yf.Ticker(ticker).info
    sector = info.get("sector") or ""
    industry = info.get("industry") or ""
    template = classify_template(sector, industry)

    metrics = {
        "currentPrice": safe_float(info.get("currentPrice") or info.get("regularMarketPrice")),
        "marketCap": safe_float(info.get("marketCap")),
        "forwardPE": safe_float(info.get("forwardPE")),
        "pegRatio": safe_float(info.get("pegRatio")),
        "enterpriseToEbitda": safe_float(info.get("enterpriseToEbitda")),
        "profitMargins": safe_float(info.get("profitMargins")),
        "operatingMargins": safe_float(info.get("operatingMargins")),
        "grossMargins": safe_float(info.get("grossMargins")),
        "revenueGrowth": safe_float(info.get("revenueGrowth")),
        "earningsGrowth": safe_float(info.get("earningsGrowth")),
        "returnOnEquity": safe_float(info.get("returnOnEquity")),
        "freeCashflow": safe_float(info.get("freeCashflow")),
        "operatingCashflow": safe_float(info.get("operatingCashflow")),
        "totalRevenue": safe_float(info.get("totalRevenue")),
        "totalCash": safe_float(info.get("totalCash")),
        "totalDebt": safe_float(info.get("totalDebt")),
        "ebitda": safe_float(info.get("ebitda")),
        "debtToEquity": safe_float(info.get("debtToEquity")),
    }

    reasons: dict[str, str] = {}
    growth, reasons["growth"] = growth_score(template, metrics["revenueGrowth"], metrics["earningsGrowth"])
    quality, reasons["quality"] = quality_score(
        template, metrics["grossMargins"], metrics["operatingMargins"], metrics["returnOnEquity"]
    )
    cash_flow, reasons["cash_flow"] = cash_flow_score(
        metrics["freeCashflow"], metrics["operatingCashflow"], metrics["marketCap"], metrics["totalRevenue"]
    )
    valuation, reasons["valuation"] = valuation_score(
        template,
        metrics["forwardPE"],
        metrics["pegRatio"],
        metrics["enterpriseToEbitda"],
        metrics["freeCashflow"],
        metrics["marketCap"],
        metrics["revenueGrowth"],
    )
    risk, reasons["risk"] = risk_score(metrics["totalCash"], metrics["totalDebt"], metrics["ebitda"], metrics["debtToEquity"])
    sustainability, reasons["sustainability"] = sustainability_score(
        template, metrics["grossMargins"], metrics["operatingMargins"], metrics["revenueGrowth"], metrics["returnOnEquity"]
    )
    total = sum([growth, quality, cash_flow, valuation, risk, sustainability])

    return Score(
        ticker=ticker.upper(),
        name=info.get("shortName") or "",
        sector=sector,
        industry=industry,
        template=template,
        current_price=metrics["currentPrice"],
        total_score=total,
        growth=growth,
        quality=quality,
        cash_flow=cash_flow,
        valuation=valuation,
        risk=risk,
        sustainability=sustainability,
        reasons=reasons,
        metrics=metrics,
    )


def render_markdown(scores: list[Score]) -> str:
    ordered = sorted(scores, key=lambda item: item.total_score, reverse=True)
    lines = [
        "# Quality Value Stock Screen",
        "",
        "First-pass screen using public market data. Review against official filings before making investment decisions.",
        "",
        "| Rank | Ticker | Name | Template | Price | Score | Growth | Quality | Cash Flow | Valuation | Risk | Sustainability |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, score in enumerate(ordered, 1):
        price = "n/a" if score.current_price is None else f"{score.current_price:.2f}"
        lines.append(
            f"| {idx} | {score.ticker} | {score.name} | {score.template} | {price} | {score.total_score} | "
            f"{score.growth} | {score.quality} | {score.cash_flow} | {score.valuation} | {score.risk} | {score.sustainability} |"
        )
    lines.append("")
    lines.append("## Details")
    for score in ordered:
        lines.extend(
            [
                "",
                f"### {score.ticker} - {score.name}",
                f"- Industry: {score.sector} / {score.industry}",
                f"- Template: {score.template}",
                f"- Score: {score.total_score}/30",
            ]
        )
        for dimension in DIMENSIONS:
            label = dimension.replace("_", " ").title()
            lines.append(f"- {label}: {getattr(score, dimension)}/5. {score.reasons[dimension]}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score public stocks for quality plus valuation.")
    parser.add_argument("--tickers", nargs="+", required=True, help="Ticker symbols, e.g. NVDA META MSFT ADBE V CRM.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    scores = [score_ticker(ticker) for ticker in args.tickers]
    if args.format == "json":
        print(json.dumps([asdict(score) for score in scores], ensure_ascii=False, indent=2, default=str))
    else:
        print(render_markdown(scores))


if __name__ == "__main__":
    main()
