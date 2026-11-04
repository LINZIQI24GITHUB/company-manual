#!/usr/bin/env python3
"""Render a 4-page company manual (HTML, print to PDF).

Usage:
    python bin/manual.py --company nvda --open
    python bin/manual.py --company zjxc --open
    python bin/manual.py --all
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import math
import webbrowser
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = ROOT / "templates" / "manual.css"
FONT_PATH = ROOT / "assets" / "bricolage.woff2"
DATA_DIR = ROOT / "data"

LABELS = {
    "en": {
        "manual": "COMPANY MANUAL",
        "facts": "FACTS ONLY",
        "inside": "INSIDE THIS MANUAL",
        "income": "Income statement",
        "balance": "Balance sheet & cash flow",
        "business": "Business & sources",
        "revenue": "Revenue",
        "gross_profit": "Gross profit",
        "operating_income": "Operating income",
        "net_income": "Net income",
        "gross_margin": "Gross margin",
        "operating_margin": "Operating margin",
        "net_margin": "Net margin",
        "roe": "ROE",
        "assets": "Total assets",
        "liabilities": "Total liabilities",
        "equity": "Shareholders' equity",
        "total_equity": "Total equity",
        "cash": "Cash",
        "debt": "Interest-bearing debt",
        "ocf": "Operating cash flow",
        "capex": "Capex",
        "fcf": "Free cash flow",
        "dividends": "Dividends",
        "buybacks": "Share repurchases",
        "year": "FY",
        "unit": "US$ bn",
        "latest": "Latest fiscal year",
        "cagr": "Revenue CAGR",
        "cash_conversion": "Cash conversion",
        "equity_ratio": "Equity ratio",
        "business_mix": "Business mix",
        "capital": "Capital allocation",
        "sources": "Sources",
        "notes": "Notes on the data",
        "colophon": "How to read this manual",
        "colophon_text": "This is a factual company manual. It contains reported figures, not ratings, forecasts, or recommendations. Every number is tied to a filing or a public financial data source.",
        "cover_note": "Reported figures only. No ratings, no target price, no buy/sell call. Not investment advice.",
        "disclaimer": "Disclaimer",
        "disclaimer_text": "This manual summarises publicly disclosed information. It is not investment advice and does not recommend buying or selling any security. Historical figures do not guarantee future results.",
        "disclaimer_alt": "不构成投资建议 · 历史数据不代表未来表现。",
        "cash_title": "Cash flow & capital returns",
        "cash_sub": "last five years",
        "growth": "Growth",
        "yoy": "YoY",
        "pillars": "Business pillars",
        "record": "10-year record",
        "record_sub": "reported",
        "method": "Method",
        "definitions": "Definitions",
        "series": "FinanSI Manual Series",
        "series_text": "01 NVIDIA · US<br>02 中际旭创 · China",
        "end_statement": "A company is not a score.",
        "end_sub": "Facts first. Ratings only with a methodology.",
        "end_kicker": "END OF MANUAL / 04",
        "roe_note": "Reported value where available; otherwise net income ÷ end equity.",
        "fcf_note": "Operating cash flow − capex; blank when capex is not reported.",
        "page": "PAGE",
    },
    "zh": {
        "manual": "公司手册",
        "facts": "只列事实",
        "inside": "本册目录",
        "income": "利润表",
        "balance": "资产负债表与现金流",
        "business": "业务与来源",
        "revenue": "营业收入",
        "gross_profit": "毛利",
        "operating_income": "营业利润",
        "net_income": "归母净利",
        "gross_margin": "毛利率",
        "operating_margin": "营业利润率",
        "net_margin": "净利率",
        "roe": "ROE",
        "assets": "总资产",
        "liabilities": "总负债",
        "equity": "归母权益",
        "total_equity": "总权益",
        "cash": "货币资金",
        "debt": "有息负债",
        "ocf": "经营现金流",
        "capex": "资本开支",
        "fcf": "自由现金流",
        "dividends": "分红",
        "buybacks": "回购",
        "year": "",
        "unit": "亿元",
        "latest": "最新年度",
        "cagr": "营收复合增速",
        "cash_conversion": "净现比",
        "equity_ratio": "权益比率",
        "business_mix": "业务结构",
        "capital": "资本配置",
        "sources": "来源",
        "notes": "数据说明",
        "colophon": "怎么读这本手册",
        "colophon_text": "这是一本公司事实手册。只收已披露数字，不做评分、不做预测、不给买卖建议。每个数字都能回到年报或公开财务数据源。",
        "cover_note": "只列已披露数字。无评分、无目标价、无买卖建议。不构成投资建议。",
        "disclaimer": "免责声明",
        "disclaimer_text": "本手册仅为公开披露信息的事实整理，不构成投资建议，也不构成对任何证券的买卖推荐。历史数据不代表未来表现。",
        "disclaimer_alt": "Not investment advice. Historical results do not guarantee future performance.",
        "cash_title": "现金流与资本回报",
        "cash_sub": "近五年",
        "growth": "增长",
        "yoy": "同比",
        "pillars": "业务支柱",
        "record": "十年记录",
        "record_sub": "已披露",
        "method": "方法",
        "definitions": "指标定义",
        "series": "FinanSI 手册系列",
        "series_text": "01 英伟达 · 美国<br>02 中际旭创 · 中国",
        "end_statement": "一家公司，不是一个分数。",
        "end_sub": "先看事实；评分必须带方法。",
        "end_kicker": "手册结束 / 04",
        "roe_note": "报告值优先；无报告值时用归母净利 ÷ 期末权益。",
        "fcf_note": "经营现金流 − 资本开支；capex 缺失时留空。",
        "page": "页",
    },
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_company(slug: str) -> dict:
    return json.loads((DATA_DIR / slug / "company.json").read_text(encoding="utf-8"))


def num(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "—"
    if abs(value) < 0.05:
        value = 0.0
    return f"{value:,.{digits}f}"


def pct(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.{digits}f}%"


def ratio(a: float | None, b: float | None) -> float | None:
    if a is None or b in (None, 0):
        return None
    return a / b


def chart_svg(rows: list[dict]) -> str:
    width, height = 680, 300
    left, right, top, bottom = 44, 24, 18, 30
    values = [float(r["revenue"] or 0) for r in rows]
    margins = [ratio(r.get("net_income"), r.get("revenue")) or 0 for r in rows]
    max_v = max(values) or 1
    max_m = max(0.05, max(margins) * 1.15)
    inner_w, inner_h = width - left - right, height - top - bottom
    step = inner_w / max(len(rows) - 1, 1)
    bar_w = min(26, step * 0.55)

    def x(i: int) -> float:
        return left + i * step

    def y(v: float) -> float:
        return top + (1 - v / max_v) * inner_h

    def ym(v: float) -> float:
        return top + (1 - v / max_m) * inner_h

    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Revenue and net margin">']
    for tick in range(4):
        value = max_v * tick / 3
        yy = y(value)
        parts.append(
            f'<line x1="{left}" y1="{yy:.1f}" x2="{width - right}" y2="{yy:.1f}" '
            'stroke="#151614" stroke-opacity="0.09"/>'
        )
        parts.append(
            f'<text x="{left - 7}" y="{yy + 3:.1f}" text-anchor="end" font-size="8.5" '
            f'fill="#6b6d64" font-family="Bricolage, Microsoft YaHei">{value:,.0f}</text>'
        )

    for i, row in enumerate(rows):
        v = float(row["revenue"] or 0)
        xx = x(i) - bar_w / 2
        yy = y(v)
        parts.append(
            f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{bar_w:.1f}" height="{top + inner_h - yy:.1f}" '
            'rx="1.5" fill="#1f4d3a"/>'
        )
        parts.append(
            f'<text x="{x(i):.1f}" y="{height - 8}" text-anchor="middle" font-size="7" '
            f'fill="#6b6d64" font-family="Bricolage, Microsoft YaHei">{esc(str(row["year"])[-2:])}</text>'
        )

    pts = " ".join(f"{x(i):.1f},{ym(m):.1f}" for i, m in enumerate(margins))
    parts.append(
        f'<polyline points="{pts}" fill="none" stroke="#b8732a" stroke-width="1.8" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    for i, m in enumerate(margins):
        parts.append(f'<circle cx="{x(i):.1f}" cy="{ym(m):.1f}" r="2.1" fill="#f7f4ec" stroke="#b8732a" stroke-width="1.5"/>')
    parts.append(
        f'<text x="{x(len(rows) - 1) - 6:.1f}" y="{ym(margins[-1]) - 8:.1f}" text-anchor="end" '
        f'font-size="8" fill="#b8732a" stroke="#f7f4ec" stroke-width="3" paint-order="stroke" '
        f'font-family="Bricolage, Microsoft YaHei">{margins[-1] * 100:.1f}%</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def income_table(c: dict, L: dict) -> str:
    rows = c["financials"]
    head = "".join(f"<th>{esc(r['year'])}</th>" for r in rows)
    specs = [
        ("revenue", "revenue", False),
        ("gross_profit", "gross_profit", False),
        ("operating_income", "operating_income", False),
        ("net_income", "net_income", False),
        ("gross_margin", "gross_margin", True),
        ("operating_margin", "operating_margin", True),
        ("net_margin", "net_margin", True),
        ("roe", "roe", True),
    ]
    body = []
    for key, label_key, is_pct in specs:
        cells = []
        for r in rows:
            if key == "gross_margin":
                v = ratio(r.get("gross_profit"), r.get("revenue"))
                cells.append(f"<td>{pct(v)}</td>")
            elif key == "operating_margin":
                v = ratio(r.get("operating_income"), r.get("revenue"))
                cells.append(f"<td>{pct(v)}</td>")
            elif key == "net_margin":
                v = ratio(r.get("net_income"), r.get("revenue"))
                cells.append(f"<td>{pct(v)}</td>")
            elif key == "roe":
                v = r.get("roe") if r.get("roe") is not None else ratio(r.get("net_income"), r.get("equity"))
                cells.append(f"<td>{pct(v)}</td>")
            else:
                cells.append(f"<td>{num(r.get(key))}</td>")
        body.append(f"<tr><td>{esc(L[label_key])}</td>{''.join(cells)}</tr>")
    return (
        f'<table class="fin-table"><thead><tr><th>{esc((L["year"] + " · ") if L["year"] else "")}{esc(L["unit"])}</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>'
    )


def growth_table(c: dict, L: dict) -> str:
    rows = c["financials"]
    head = "".join(f"<th>{esc(r['year'])}</th>" for r in rows)
    body = []
    for key, label_key in (("revenue", "revenue"), ("net_income", "net_income"), ("ocf", "ocf")):
        cells = []
        for i, r in enumerate(rows):
            prev = rows[i - 1] if i else None
            v = None
            if prev and prev.get(key) and r.get(key):
                v = r[key] / prev[key] - 1
            cells.append(f"<td>{pct(v)}</td>")
        body.append(f'<tr><td>{esc(L[label_key])} {esc(L["yoy"])}</td>{"".join(cells)}</tr>')
    return (
        f'<table class="fin-table"><thead><tr><th>{esc(L["growth"])} / {esc(L["yoy"])}</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>'
    )


def balance_table(c: dict, L: dict) -> str:
    rows = c["financials"]
    head = "".join(f"<th>{esc(r['year'])}</th>" for r in rows)
    specs = ["assets", "liabilities", "equity", "cash", "debt", "ocf", "capex", "fcf", "dividends", "buybacks"]
    labels = {
        "assets": L["assets"], "liabilities": L["liabilities"], "equity": L["equity"],
        "cash": L["cash"], "debt": L["debt"], "ocf": L["ocf"], "capex": L["capex"],
        "fcf": L["fcf"], "dividends": L["dividends"], "buybacks": L["buybacks"],
    }
    body = []
    for key in specs:
        cells = []
        for r in rows:
            if key == "fcf":
                v = None
                if r.get("ocf") is not None and r.get("capex") is not None:
                    v = r["ocf"] - r["capex"]
                cells.append(f"<td>{num(v)}</td>")
            else:
                cells.append(f"<td>{num(r.get(key))}</td>")
        body.append(f"<tr><td>{esc(labels[key])}</td>{''.join(cells)}</tr>")
    return (
        f'<table class="fin-table"><thead><tr><th>{esc((L["year"] + " · ") if L["year"] else "")}{esc(L["unit"])}</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>'
    )


def segment_table(c: dict) -> str:
    segs = c.get("segments") or []
    if not segs:
        return ""
    rows = []
    current = None
    for s in segs:
        if s["kind"] != current:
            current = s["kind"]
            rows.append(f'<tr class="kind"><td colspan="4">{esc(current)}</td></tr>')
        rows.append(
            f'<tr><td>{esc(s["name"])}</td><td>{num(s["revenue"])}</td>'
            f'<td>{num(s["share"])}%</td><td>{num(s["gm"])}%</td></tr>'
        )
    return (
        '<table class="seg-table"><thead><tr><th>2025</th><th>收入</th><th>占比</th><th>毛利率</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def capital_table(c: dict, L: dict) -> str:
    rows = c["financials"][-5:]
    body = []
    for r in rows:
        body.append(
            f'<tr><td>{esc(r["year"])}</td><td>{num(r.get("dividends"))}</td>'
            f'<td>{num(r.get("buybacks"))}</td>'
            f'<td>{num((r.get("dividends") or 0) + (r.get("buybacks") or 0))}</td></tr>'
        )
    return (
        '<table class="seg-table"><thead><tr><th>Year</th><th>Dividends</th><th>Buybacks</th><th>Total</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>'
    )


def observations(c: dict, L: dict) -> str:
    rows = c["financials"]
    first, last = rows[0], rows[-1]
    n = len(rows) - 1
    cagr = None
    if first.get("revenue") and last.get("revenue") and n > 0:
        cagr = (last["revenue"] / first["revenue"]) ** (1 / n) - 1
    gm0, gm1 = ratio(first.get("gross_profit"), first.get("revenue")), ratio(last.get("gross_profit"), last.get("revenue"))
    nm0, nm1 = ratio(first.get("net_income"), first.get("revenue")), ratio(last.get("net_income"), last.get("revenue"))
    conv = ratio(last.get("ocf"), last.get("net_income"))
    fcf = None
    if last.get("ocf") is not None and last.get("capex") is not None:
        fcf = last["ocf"] - last["capex"]
    if L["manual"] == "公司手册":
        items = [
            f"营收从 {esc(first['year'])} 的 {num(first.get('revenue'))} {esc(c['unit'])} 增至 {esc(last['year'])} 的 {num(last.get('revenue'))}，复合增速 <b>{pct(cagr)}</b>。",
            f"毛利率从 <b>{pct(gm0)}</b> 变为 <b>{pct(gm1)}</b>；净利率从 <b>{pct(nm0)}</b> 变为 <b>{pct(nm1)}</b>。",
            f"{esc(last['year'])} 经营现金流 {num(last.get('ocf'))}，归母净利 {num(last.get('net_income'))}，净现比 <b>{num(conv, 2)}x</b>。",
        ]
        if fcf is not None:
            items.append(f"{esc(last['year'])} 资本开支 {num(last.get('capex'))}，自由现金流 <b>{num(fcf)}</b>。")
    else:
        items = [
            f"Revenue grew from {num(first.get('revenue'))} in {esc(first['year'])} to {num(last.get('revenue'))} in {esc(last['year'])}, a <b>{pct(cagr)}</b> CAGR.",
            f"Gross margin moved from <b>{pct(gm0)}</b> to <b>{pct(gm1)}</b>; net margin from <b>{pct(nm0)}</b> to <b>{pct(nm1)}</b>.",
            f"FY2026 operating cash flow was {num(last.get('ocf'))} against net income of {num(last.get('net_income'))}: <b>{num(conv, 2)}x</b>.",
        ]
        if fcf is not None:
            items.append(f"Capex was {num(last.get('capex'))}; free cash flow <b>{num(fcf)}</b>.")
        if last.get("buybacks"):
            items.append(f"Capital returns: dividends {num(last.get('dividends'))}, buybacks <b>{num(last.get('buybacks'))}</b>.")
    return '<div class="obs-grid">' + "".join(f'<div class="obs">{x}</div>' for x in items) + "</div>"


def cash_table(c: dict, L: dict) -> str:
    rows = c["financials"][-5:]
    head = "".join(f"<th>{esc(r['year'])}</th>" for r in rows)
    body = []
    for key in ("ocf", "capex", "fcf", "dividends", "buybacks"):
        cells = []
        for r in rows:
            if key == "fcf":
                v = None
                if r.get("ocf") is not None and r.get("capex") is not None:
                    v = r["ocf"] - r["capex"]
                cells.append(f"<td>{num(v)}</td>")
            else:
                cells.append(f"<td>{num(r.get(key))}</td>")
        body.append(f"<tr><td>{esc(L[key])}</td>{''.join(cells)}</tr>")
    return (
        f'<div class="wide-section"><div class="kicker"><strong>{esc(L["cash_title"])}</strong> · {esc(L["cash_sub"])}</div>'
        f'<table class="cap-table"><thead><tr><th>{esc(L["unit"])}</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div>'
    )


def balance_chart(c: dict) -> str:
    rows = c["financials"][-5:]
    width, height = 680, 190
    left, right, top, bottom = 44, 12, 14, 26
    vals = [max(float(r.get("assets") or 0), float(r.get("equity") or 0)) for r in rows]
    mx = max(vals) or 1
    inner_w, inner_h = width - left - right, height - top - bottom
    step = inner_w / len(rows)
    bar_w = min(22, step * 0.25)

    def y(v: float) -> float:
        return top + (1 - v / mx) * inner_h

    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Assets and equity">']
    for tick in range(3):
        value = mx * tick / 2
        yy = y(value)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width - right}" y2="{yy:.1f}" stroke="#151614" stroke-opacity="0.09"/>')
        parts.append(
            f'<text x="{left - 7}" y="{yy + 3:.1f}" text-anchor="end" font-size="8.5" fill="#6b6d64" '
            f'font-family="Bricolage, Microsoft YaHei">{value:,.0f}</text>'
        )
    for i, r in enumerate(rows):
        cx = left + step * (i + 0.5)
        for j, (key, color) in enumerate((("assets", "#1f4d3a"), ("equity", "#b8732a"))):
            v = float(r.get(key) or 0)
            xx = cx - bar_w - 1.5 + j * (bar_w + 3)
            parts.append(
                f'<rect x="{xx:.1f}" y="{y(v):.1f}" width="{bar_w:.1f}" height="{top + inner_h - y(v):.1f}" '
                f'rx="1.2" fill="{color}"/>'
            )
        parts.append(
            f'<text x="{cx:.1f}" y="{height - 7}" text-anchor="middle" font-size="7" fill="#6b6d64" '
            f'font-family="Bricolage, Microsoft YaHei">{esc(str(r["year"])[-2:])}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def cover_strip(c: dict, L: dict) -> str:
    rows = c["financials"]
    vals = [float(r.get("revenue") or 0) for r in rows]
    positive = [v for v in vals if v > 0]
    lo = min(positive) if positive else 1.0
    hi = max(vals) if vals else 1.0
    denom = math.log(hi) - math.log(lo) if hi > lo and lo > 0 else 1.0

    def height(v: float) -> float:
        if v <= 0:
            return 2.0
        return 8.0 + 92.0 * (math.log(v) - math.log(lo)) / denom

    bars = "".join(
        f'<div class="strip-bar {"latest" if i == len(rows) - 1 else ""}" '
        f'style="height:{max(2, min(100, height(float(r.get("revenue") or 0)))):.1f}%"></div>'
        for i, r in enumerate(rows)
    )
    years = "".join(f"<span>{esc(str(r['year'])[-2:])}</span>" for r in rows)
    return (
        '<div class="cover-strip">'
        f'<div class="strip-head"><span><b>10-year revenue</b> · log scale · {esc(rows[0]["year"])}–{esc(rows[-1]["year"])}</span>'
        f'<span>{esc(c["unit"])}</span></div>'
        f'<div class="strip-bars">{bars}</div>'
        f'<div class="strip-years">{years}</div>'
        "</div>"
    )


def cover(c: dict, L: dict) -> str:
    facts = "".join(
        f'<div class="fact"><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div></div>'
        for k, v in c["key_facts"]
    )
    pillars = "".join(f"<span>{esc(p[0])}</span>" for p in c["business_pillars"])
    identity = f"Founded <b>{esc(c['founded'])}</b> · HQ <b>{esc(c['hq'])}</b> · FY end <b>{esc(c['fy_end'])}</b>"
    if L["manual"] == "公司手册":
        identity = f"成立 <b>{esc(c['founded'])}</b> · 上市 <b>{esc(c.get('listed', '—'))}</b> · <b>{esc(c['hq'])}</b> · 员工 <b>{esc(c['employees'])}</b>"
    return f"""
<article class="page">
  <div class="topline">
    <div class="brand"><span class="brand-mark"><svg width="16" height="16" viewBox="0 0 18 18" fill="none"><path d="M3.5 13.5V9.5" stroke="#f7f4ec" stroke-width="2.2" stroke-linecap="round"/><path d="M9 13.5V5" stroke="#f7f4ec" stroke-width="2.2" stroke-linecap="round"/><path d="M14.5 13.5V7.5" stroke="#f7f4ec" stroke-width="2.2" stroke-linecap="round"/></svg></span><span class="brand-name">Finan<span>SI</span></span></div>
    <div class="mid">{esc(L["manual"])} · {esc(c["fy_label"])}</div>
  </div>

  <div class="cover-main">
    <div class="cover-left">
      <div class="eyebrow">{esc(c["fy_label"])} · {esc(c["exchange"])} · {esc(c["unit"])}</div>
      <h1 class="{'cn' if L['manual'] == '公司手册' else ''}">{esc(c["name"])}</h1>
      <div class="ticker-line"><b>{esc(c["ticker"])}</b><span>{esc(c["legal_name"])}</span></div>
      <p class="lede">{esc(c["business"])}</p>
      <div class="cover-pillars">{pillars}</div>
    </div>
    <aside class="cover-right">
      <div class="index-box">
        <div class="k">{esc(L["inside"])}</div>
        <div class="index-list">
          <div class="index-row"><span class="t">01 · {esc(L["income"])}</span><span class="p">02</span></div>
          <div class="index-row"><span class="t">02 · {esc(L["balance"])}</span><span class="p">03</span></div>
          <div class="index-row"><span class="t">03 · {esc(L["business"])}</span><span class="p">04</span></div>
        </div>
      </div>
      <div class="fact-grid">{facts}</div>
      <div class="identity">{identity}</div>
    </aside>
  </div>

  {cover_strip(c, L)}

  <div class="page-foot"><span class="left">{esc(L["cover_note"])}</span><span class="right">01 / 04</span></div>
</article>
"""


def income_page(c: dict, L: dict) -> str:
    rows = c["financials"]
    first, last = rows[0], rows[-1]
    years = len(rows) - 1
    cagr = None
    if first.get("revenue") and last.get("revenue") and years > 0:
        cagr = (last["revenue"] / first["revenue"]) ** (1 / years) - 1
    latest_margin = ratio(last.get("net_income"), last.get("revenue"))
    latest_roe = last.get("roe") if last.get("roe") is not None else ratio(last.get("net_income"), last.get("equity"))
    return f"""
<article class="page">
  <div class="page-head">
    <div><div class="no">01 / {esc(L["income"]).upper()}</div><h2>{esc(L["income"])}</h2></div>
    <div class="meta">{esc(L["latest"])} · {esc(last["year"])}<br>{esc(c["unit"])}</div>
  </div>
  <div class="chart-wrap">
    <div class="chart-legend"><span><i class="legend-dot bar"></i>{esc(L["revenue"])}</span><span><i class="legend-dot line"></i>{esc(L["net_margin"])}</span></div>
    <div class="chart">{chart_svg(rows)}</div>
  </div>
  {income_table(c, L)}
  {observations(c, L)}
  <div class="wide-section"><div class="kicker"><strong>{esc(L["growth"])}</strong> · {esc(L["yoy"])}</div>{growth_table(c, L)}</div>
  <div class="callout">
    <div><div class="k">{esc(L["cagr"])} · {esc(rows[0]["year"])}–{esc(last["year"])}</div><div class="v">{pct(cagr)}</div><div class="n">复利口径；两期营收均为已披露年报数。</div></div>
    <div><div class="k">{esc(L["net_margin"])} · {esc(last["year"])}</div><div class="v">{pct(latest_margin)}</div><div class="n">归母净利 ÷ 营业收入。</div></div>
    <div><div class="k">{esc(L["roe"])} · {esc(last["year"])}</div><div class="v">{pct(latest_roe)}</div><div class="n">{esc(L["roe_note"])}</div></div>
  </div>
  <div class="page-foot"><span class="left">Source: {esc(c["sources"][0][0])} · figures as reported; margins computed from reported values.</span><span class="right">02 / 04</span></div>
</article>
"""


def balance_page(c: dict, L: dict) -> str:
    last = c["financials"][-1]
    assets, liab, eq = last.get("assets"), last.get("liabilities"), last.get("equity")
    eq_bar = last.get("total_equity") if last.get("total_equity") is not None else eq
    liab_pct = ratio(liab, assets) or 0
    eq_pct = ratio(eq_bar, assets) or 0
    conversion = ratio(last.get("ocf"), last.get("net_income"))
    fcf = None
    if last.get("ocf") is not None and last.get("capex") is not None:
        fcf = last["ocf"] - last["capex"]
    return f"""
<article class="page">
  <div class="page-head">
    <div><div class="no">02 / {esc(L["balance"]).upper()}</div><h2>{esc(L["balance"])}</h2></div>
    <div class="meta">{esc(c["fy_label"])} · {esc(c["unit"])}<br>{esc(c["currency"])}</div>
  </div>
  <div class="split">
    <div>{balance_table(c, L)}</div>
    <div class="side-stack">
      <div class="panel">
        <div class="k">{esc(last["year"])} · {esc(L["assets"])}</div>
        <div class="big">{num(assets)}</div>
        <div class="balance-bar"><span class="liab" style="width:{liab_pct * 100:.1f}%"></span><span class="eq" style="width:{eq_pct * 100:.1f}%"></span></div>
        <div class="balance-legend"><span>{esc(L["liabilities"])} <b>{pct(liab_pct)}</b></span><span>{esc(L["total_equity"])} <b>{pct(eq_pct)}</b></span></div>
      </div>
      <div class="panel">
        <div class="k">{esc(L["cash_conversion"])}</div>
        <div class="big">{num(conversion, 2)}x</div>
        <div class="small">{esc(L["ocf"])} {num(last.get("ocf"))} ÷ {esc(L["net_income"])} {num(last.get("net_income"))}</div>
      </div>
      <div class="panel">
        <div class="k">{esc(L["fcf"])} · {esc(last["year"])}</div>
        <div class="big">{num(fcf)}</div>
        <div class="small">{esc(L["ocf"])} − {esc(L["capex"])}；{esc(L["fcf_note"])}。</div>
      </div>
    </div>
  </div>
  {cash_table(c, L)}
  <div class="wide-section">
    <div class="kicker"><strong>{esc(L["assets"])} / {esc(L["total_equity"])}</strong> · {esc(L["cash_sub"])}</div>
    <div class="chart-legend"><span><i class="legend-dot bar"></i>{esc(L["assets"])}</span><span><i class="legend-dot line" style="background:var(--amber)"></i>{esc(L["equity"])}</span></div>
    <div class="chart">{balance_chart(c)}</div>
  </div>
  <div class="page-foot"><span class="left">Source: {esc(c["sources"][0][0])} · balance-sheet values are period-end; cash and debt are as reported.</span><span class="right">03 / 04</span></div>
</article>
"""


def business_page(c: dict, L: dict) -> str:
    pillars = "".join(
        f'<div class="pillar"><div class="t">{esc(p[0])}</div><div class="d">{esc(p[1])}</div></div>'
        for p in c["business_pillars"]
    )
    notes = "".join(f'<div class="note">{esc(n)}</div>' for n in c.get("notes", []))
    sources = "".join(
        f'<div class="source"><b>{esc(label)}</b><a href="{esc(url)}">{esc(url)}</a></div>'
        for label, url in c["sources"]
    )
    segments = segment_table(c)
    capital = capital_table(c, L) if L["manual"] != "公司手册" else ""
    if segments:
        mix_block = f'<div class="h3">{esc(L["business_mix"])} · 2025</div>{segments}'
    else:
        mix_block = ""
    capital_block = f'<div class="h3">{esc(L["capital"])}</div>{capital}' if capital else ""
    identity = (
        f'<div class="h3">Company facts</div>'
        f'<div class="notes"><div class="note">Founded {esc(c["founded"])} · HQ {esc(c["hq"])} · FY end {esc(c["fy_end"])}</div>'
        f'<div class="note">Ticker {esc(c["ticker"])} · {esc(c["exchange"])}</div></div>'
    )
    if L["manual"] == "公司手册":
        identity = (
            '<div class="h3">公司事实</div>'
            f'<div class="notes"><div class="note">成立 {esc(c["founded"])} · 上市 {esc(c.get("listed", "—"))} · {esc(c["hq"])}</div>'
            f'<div class="note">员工 {esc(c["employees"])} · 董事长 {esc(c.get("chairman", "—"))} · 审计 {esc(c.get("auditor", "—"))}</div></div>'
        )
    first, last = c["financials"][0], c["financials"][-1]
    record = (
        f'<div class="method"><div class="kicker"><strong>{esc(L["record"])}</strong> · {esc(L["record_sub"])}</div>'
        f'<div class="record"><span>{esc(L["revenue"])}</span><b>{num(first.get("revenue"))} → {num(last.get("revenue"))}</b></div>'
        f'<div class="record"><span>{esc(L["net_income"])}</span><b>{num(first.get("net_income"))} → {num(last.get("net_income"))}</b></div>'
        f'<div class="record"><span>{esc(L["ocf"])}</span><b>{num(first.get("ocf"))} → {num(last.get("ocf"))}</b></div>'
        "</div>"
    )
    if L["manual"] == "公司手册":
        method_text = (
            f"数字为 {esc(c['unit'])} 的已披露年度数据；利润率由报表科目相除得到；"
            f"财年截止 {esc(c['fy_end'])}。不引入调整数、预测数或第三方估算。"
        )
    else:
        method_text = (
            f"Figures are reported annual numbers in {esc(c['unit'])}. Margins are computed as the ratio of reported line items. "
            f"Fiscal year ends on {esc(c['fy_end'])}. No adjusted, forecast, or vendor-estimated figures are introduced."
        )
    method = (
        f'<div class="method"><div class="kicker"><strong>{esc(L["method"])}</strong></div>'
        f"<p>{method_text}</p></div>"
    )
    definitions = (
        f'<div class="method"><div class="kicker"><strong>{esc(L["definitions"])}</strong></div>'
        f'<p>{"营业收入 = 报表顶行；毛利率 = 毛利 ÷ 营业收入；经营现金流 = 经营活动现金流净额；自由现金流 = 经营现金流 − 资本开支；ROE = 报告值优先，否则归母净利 ÷ 期末权益。" if L["manual"] == "公司手册" else "Revenue = reported top line; Gross margin = gross profit ÷ revenue; OCF = net cash from operating activities; FCF = OCF − capex; ROE = reported value where available, otherwise net income ÷ end equity."}</p></div>'
    )
    return f"""
<article class="page">
  <div class="page-head">
    <div><div class="no">03 / {esc(L["business"]).upper()}</div><h2>{esc(L["business"])}</h2></div>
    <div class="meta">{esc(c["name"])} · {esc(c["ticker"])}<br>{esc(c["fy_label"])}</div>
  </div>
  <div class="two-col">
    <div>
      <p class="body-text">{esc(c["business"])}</p>
      <div class="h3">{esc(L["pillars"])}</div>
      <div class="pillar-list">{pillars}</div>
      {mix_block}
      <div class="h3">{esc(L["notes"])}</div>
      <div class="notes">{notes}</div>
    </div>
    <div>
      {identity}
      {capital_block}
      {record}
      <div class="h3">{esc(L["sources"])}</div>
      <div class="sources">{sources}</div>
      {method}
      {definitions}
      <div class="colophon" style="margin-top:4mm">
        <div class="k">{esc(L["colophon"])}</div>
        <p>{esc(L["colophon_text"])}</p>
      </div>
    </div>
  </div>
  <div class="page-foot"><span class="left">Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} · {esc(c["fy_label"])} · {esc(c["unit"])} · no ratings, no forecasts.</span><span class="right">04 / 04</span></div>
</article>
"""


def flow_head(no: str, title: str, meta: str) -> str:
    return (
        '<div class="block-head">'
        f'<div><div class="no">{esc(no)}</div><h2>{esc(title)}</h2></div>'
        f'<div class="meta">{meta}</div></div>'
    )


def flow_cover(c: dict, L: dict) -> str:
    rows = c["financials"]
    facts = "".join(
        f'<div class="fact"><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div></div>'
        for k, v in c["key_facts"]
    )
    pillars = "".join(f"<span>{esc(p[0])}</span>" for p in c["business_pillars"])
    identity = f"Founded <b>{esc(c['founded'])}</b> · HQ <b>{esc(c['hq'])}</b> · FY end <b>{esc(c['fy_end'])}</b>"
    if L["manual"] == "公司手册":
        identity = f"成立 <b>{esc(c['founded'])}</b> · 上市 <b>{esc(c.get('listed', '—'))}</b> · <b>{esc(c['hq'])}</b> · 员工 <b>{esc(c['employees'])}</b>"
    return f"""
<section class="cover-page company-cover">
  <div class="topline">
    <div class="brand"><span class="brand-mark"><svg width="16" height="16" viewBox="0 0 18 18" fill="none"><path d="M3.5 13.5V9.5" stroke="#f7f4ec" stroke-width="2.2" stroke-linecap="round"/><path d="M9 13.5V5" stroke="#f7f4ec" stroke-width="2.2" stroke-linecap="round"/><path d="M14.5 13.5V7.5" stroke="#f7f4ec" stroke-width="2.2" stroke-linecap="round"/></svg></span><span class="brand-name">Finan<span>SI</span></span></div>
    <div class="mid">{esc(L["manual"])} · {esc(c["fy_label"])}</div>
  </div>
  <div class="entry-top"><span><b>COMPANY MANUAL</b> / {esc(c["fy_label"])}</span><span>{esc(c["exchange"])} · {esc(c["currency"])} · {esc(c["unit"])}</span></div>
  <div class="entry-main">
    <div>
      <h1 class="{'cn' if L['manual'] == '公司手册' else ''}">{esc(c["name"])}</h1>
      <div class="ticker"><b>{esc(c["ticker"])}</b><span>{esc(c["legal_name"])}</span></div>
      <p class="lede">{esc(c["business"])}</p>
      <div class="pillars">{pillars}</div>
    </div>
    <aside>
      <div class="fact-grid">{facts}</div>
      <div class="identity">{identity}</div>
    </aside>
  </div>
  <div class="cover-body">
    <div class="cover-index">
      <div class="kicker"><strong>INSIDE</strong></div>
      <div class="cover-index-row"><span>01</span><b>{esc(L["business"])}</b></div>
      <div class="cover-index-row"><span>02</span><b>{esc(L["income"])}</b></div>
      <div class="cover-index-row"><span>03</span><b>{esc(L["balance"])}</b></div>
      <div class="cover-index-row"><span>04</span><b>{esc(L["cash_title"])}</b></div>
      <div class="cover-index-row"><span>05</span><b>{esc(L["sources"])}</b></div>
    </div>
    <div class="cover-record">
      <div class="kicker"><strong>10-YEAR RECORD</strong> · {esc(rows[0]["year"])}–{esc(rows[-1]["year"])}</div>
      <div class="cover-record-row"><span>{esc(L["revenue"])}</span><b>{num(rows[0].get("revenue"))} → {num(rows[-1].get("revenue"))}</b></div>
      <div class="cover-record-row"><span>{esc(L["net_income"])}</span><b>{num(rows[0].get("net_income"))} → {num(rows[-1].get("net_income"))}</b></div>
      <div class="cover-record-row"><span>{esc(L["ocf"])}</span><b>{num(rows[0].get("ocf"))} → {num(rows[-1].get("ocf"))}</b></div>
    </div>
  </div>
  {cover_strip(c, L)}
  <div class="cover-note">{esc("Source: " if L["manual"] != "公司手册" else "来源：")}{esc(c["sources"][0][0])}</div>
</section>
"""


def flow_business(c: dict, L: dict) -> str:
    pillars = "".join(
        f'<div class="pillar"><div class="t">{esc(p[0])}</div><div class="d">{esc(p[1])}</div></div>'
        for p in c["business_pillars"]
    )
    facts = (
        f'<div class="h3">Company facts</div>'
        f'<div class="notes"><div class="note">Founded {esc(c["founded"])} · HQ {esc(c["hq"])} · FY end {esc(c["fy_end"])}</div>'
        f'<div class="note">Ticker {esc(c["ticker"])} · {esc(c["exchange"])}</div></div>'
    )
    if L["manual"] == "公司手册":
        facts = (
            '<div class="h3">公司事实</div>'
            f'<div class="notes"><div class="note">成立 {esc(c["founded"])} · 上市 {esc(c.get("listed", "—"))} · {esc(c["hq"])}</div>'
            f'<div class="note">员工 {esc(c["employees"])} · 董事长 {esc(c.get("chairman", "—"))} · 审计 {esc(c.get("auditor", "—"))}</div></div>'
        )
    seg = f'<div class="h3">{esc(L["business_mix"])}</div>{segment_table(c)}' if c.get("segments") else ""
    notes = "".join(f'<div class="note">{esc(n)}</div>' for n in c.get("notes", []))
    return f"""
<section class="block">
  {flow_head("01 / " + L["business"], L["business"], f'{esc(c["name"])} · {esc(c["ticker"])}')}
  <div class="business-single">
    <p class="body-text">{esc(c["business"])}</p>
    <div class="h3">{esc(L["pillars"])}</div>
    <div class="pillar-list">{pillars}</div>
    {seg}
    {facts}
    <div class="h3">{esc(L["notes"])}</div>
    <div class="notes">{notes}</div>
  </div>
</section>
"""


def flow_income(c: dict, L: dict) -> str:
    rows = c["financials"]
    return f"""
<section class="block keep">
  {flow_head("02 / " + L["income"], L["income"], f'{esc(rows[-1]["year"])} · {esc(c["unit"])}')}
  <div class="chart-legend"><span><i class="legend-dot bar"></i>{esc(L["revenue"])}</span><span><i class="legend-dot line"></i>{esc(L["net_margin"])}</span></div>
  <div class="chart">{chart_svg(rows)}</div>
</section>
<section class="block keep">
  {income_table(c, L)}
  {observations(c, L)}
  <div class="wide-section"><div class="kicker"><strong>{esc(L["growth"])}</strong> · {esc(L["yoy"])}</div>{growth_table(c, L)}</div>
</section>
"""


def cash_table(c: dict, L: dict) -> str:
    rows = c["financials"][-5:]
    head = "".join(f"<th>{esc(r['year'])}</th>" for r in rows)
    body = []
    for key in ("ocf", "capex", "fcf", "dividends", "buybacks"):
        cells = []
        for r in rows:
            if key == "fcf":
                value = None
                if r.get("ocf") is not None and r.get("capex") is not None:
                    value = r["ocf"] - r["capex"]
                cells.append(f"<td>{num(value)}</td>")
            else:
                cells.append(f"<td>{num(r.get(key))}</td>")
        body.append(f"<tr><td>{esc(L[key])}</td>{''.join(cells)}</tr>")
    return (
        f'<table class="cap-table"><thead><tr><th>{esc(L["unit"])}</th>{head}</tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table>'
    )


def flow_balance(c: dict, L: dict) -> str:
    last = c["financials"][-1]
    assets, liab = last.get("assets"), last.get("liabilities")
    eq_bar = last.get("total_equity") if last.get("total_equity") is not None else last.get("equity")
    liab_pct = ratio(liab, assets) or 0
    eq_pct = ratio(eq_bar, assets) or 0
    conversion = ratio(last.get("ocf"), last.get("net_income"))
    fcf = None
    if last.get("ocf") is not None and last.get("capex") is not None:
        fcf = last["ocf"] - last["capex"]
    panels = f"""
<div class="side-stack">
  <div class="panel"><div class="k">{esc(last["year"])} · {esc(L["assets"])}</div><div class="big">{num(assets)}</div>
    <div class="balance-bar"><span class="liab" style="width:{liab_pct * 100:.1f}%"></span><span class="eq" style="width:{eq_pct * 100:.1f}%"></span></div>
    <div class="balance-legend"><span>{esc(L["liabilities"])} <b>{pct(liab_pct)}</b></span><span>{esc(L["total_equity"])} <b>{pct(eq_pct)}</b></span></div>
  </div>
  <div class="panel"><div class="k">{esc(L["cash_conversion"])}</div><div class="big">{num(conversion, 2)}x</div>
    <div class="small">{esc(L["ocf"])} {num(last.get("ocf"))} ÷ {esc(L["net_income"])} {num(last.get("net_income"))}</div></div>
  <div class="panel"><div class="k">{esc(L["fcf"])} · {esc(last["year"])}</div><div class="big">{num(fcf)}</div>
    <div class="small">{esc(L["ocf"])} − {esc(L["capex"])}；{esc(L["fcf_note"])}。</div></div>
</div>
"""
    return f"""
<section class="block keep">
  {flow_head("03 / " + L["balance"], L["balance"], f'{esc(c["fy_label"])} · {esc(c["currency"])}')}
  <div class="balance-split"><div>{balance_table(c, L)}</div>{panels}</div>
</section>
"""


def flow_cash(c: dict, L: dict) -> str:
    return f"""
<section class="block keep">
  {flow_head("04 / " + L["cash_title"], L["cash_title"], f'{esc(L["cash_sub"])} · {esc(c["unit"])}')}
  {cash_table(c, L)}
  <div class="wide-section">
    <div class="kicker"><strong>{esc(L["assets"])} / {esc(L["total_equity"])}</strong> · {esc(L["cash_sub"])}</div>
    <div class="chart-legend"><span><i class="legend-dot bar"></i>{esc(L["assets"])}</span><span><i class="legend-dot line" style="background:var(--amber)"></i>{esc(L["total_equity"])}</span></div>
    <div class="chart">{balance_chart(c)}</div>
  </div>
</section>
"""


def flow_capital(c: dict, L: dict) -> str:
    has = any((r.get("dividends") or 0) > 0 or (r.get("buybacks") or 0) > 0 for r in c["financials"])
    if not has:
        return ""
    return f"""
<section class="block keep">
  {flow_head("05 / " + L["capital"], L["capital"], f'{esc(c["fy_label"])} · {esc(c["unit"])}')}
  {capital_table(c, L)}
  <div class="kicker" style="margin-top:3mm">{esc(c.get("capital_note", ""))}</div>
</section>
"""


def flow_sources(c: dict, L: dict) -> str:
    sources = "".join(
        f'<div class="source"><b>{esc(label)}</b><a href="{esc(url)}">{esc(url)}</a></div>'
        for label, url in c["sources"]
    )
    if L["manual"] == "公司手册":
        method_text = (
            f"数字为 {esc(c['unit'])} 的已披露年度数据；利润率由报表科目相除得到；"
            f"财年截止 {esc(c['fy_end'])}。不引入调整数、预测数或第三方估算。"
        )
        defs_text = "营业收入 = 报表顶行；毛利率 = 毛利 ÷ 营业收入；经营现金流 = 经营活动现金流净额；自由现金流 = 经营现金流 − 资本开支；ROE = 报告值优先，否则归母净利 ÷ 期末权益。"
    else:
        method_text = (
            f"Figures are reported annual numbers in {esc(c['unit'])}. Margins are computed as the ratio of reported line items. "
            f"Fiscal year ends on {esc(c['fy_end'])}. No adjusted, forecast, or vendor-estimated figures are introduced."
        )
        defs_text = "Revenue = reported top line; Gross margin = gross profit ÷ revenue; OCF = net cash from operating activities; FCF = OCF − capex; ROE = reported value where available, otherwise net income ÷ end equity."
    return f"""
<section class="block">
  {flow_head("06 / " + L["sources"], L["sources"], f'{esc(c["name"])} · {esc(c["fy_label"])}')}
  <div class="business-single">
    <div class="sources">{sources}</div>
    <div class="method"><div class="kicker"><strong>{esc(L["method"])}</strong></div><p>{method_text}</p></div>
    <div class="method"><div class="kicker"><strong>{esc(L["definitions"])}</strong></div><p>{defs_text}</p></div>
    <div class="method disclaimer"><div class="kicker"><strong>{esc(L["disclaimer"])}</strong></div><p>{esc(L["disclaimer_text"])}</p><p class="disclaimer-alt">{esc(L["disclaimer_alt"])}</p></div>
  </div>
</section>
"""


def render(c: dict) -> str:
    css = CSS_PATH.read_text(encoding="utf-8") + "\n" + (ROOT / "templates" / "manual-flow.css").read_text(encoding="utf-8")
    font_face = ""
    if FONT_PATH.exists():
        b64 = base64.b64encode(FONT_PATH.read_bytes()).decode("ascii")
        font_face = (
            "@font-face{font-family:'Bricolage';font-style:normal;font-weight:200 800;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');font-display:swap;}}"
        )
    L = LABELS.get(c.get("locale", "en"), LABELS["en"])
    body = flow_cover(c, L) + '<section class="entry">' + flow_business(c, L) + flow_income(c, L) + flow_balance(c, L) + flow_cash(c, L) + flow_capital(c, L) + flow_sources(c, L) + "</section>"
    return f"""<!doctype html>
<html lang="{'zh-CN' if c.get('locale') == 'zh' else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(c["name"])} · Company Manual · FinanSI</title>
<style>{font_face}{css}</style>
</head>
<body>
<div class="print-bar"><span class="hint">A4 · content-driven pages · print to PDF</span><button type="button" onclick="window.print()">Print / Save PDF</button></div>
<main class="volume single">{body}</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a company manual")
    parser.add_argument("--company", help="company slug: nvda / zjxc")
    parser.add_argument("--all", action="store_true", help="render all companies")
    parser.add_argument("--out", type=Path, help="output directory")
    parser.add_argument("--open", action="store_true", help="open result in browser")
    args = parser.parse_args()

    slugs = ["nvda", "zjxc"] if args.all or not args.company else [args.company]
    out_dir = args.out or ROOT / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    first_path = None
    for slug in slugs:
        c = load_company(slug)
        path = out_dir / f'manual-{slug}.html'
        path.write_text(render(c), encoding="utf-8")
        first_path = first_path or path
        print(f"OK  {path}")
        print(f"URL {path.resolve().as_uri()}")
    print("打印 / 保存为 PDF：打开后点右上角按钮，或 Ctrl/Cmd+P")
    if args.open and first_path:
        webbrowser.open(first_path.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
