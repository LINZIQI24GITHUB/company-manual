---
name: company-manual
description: >-
  Generate a content-driven company manual for a US or China listed company.
  One company = one manual; page count follows disclosed content, not a fixed
  four-page template. Sections include business, 10-year income statement,
  balance sheet, cash flow, segment mix, capital allocation, and sources.
  No ratings, forecasts, target prices, or buy/sell recommendations.
  Demo companies: NVIDIA (NVDA), Apple (AAPL), Tesla (TSLA), 中际旭创 (300308), 宁德时代 (300750), 贵州茅台 (600519), 中国平安 (601318).
---

# FinanSI Company Manual

A company manual, not a scorecard and not a fixed-page brochure.

**One company = one manual.** The manual runs as long as the company's disclosed content requires. The current demos happen to fit in four pages; that is a result, not a specification.

## When to use

- You need a sourced company manual, not a slide of opinions.
- You want a fixed visual language for US and China companies.
- You want 10-year records that can be printed as a reference.
- You want to add a company without forcing it into a fixed page count.

Do not use it to produce ratings, target prices, or trade recommendations.

## Run

```bash
python bin/manual.py --company nvda --open
python bin/manual.py --company aapl --open
python bin/manual.py --company tsla --open
python bin/manual.py --company zjxc --open
python bin/manual.py --company catl --open
python bin/manual.py --company moutai --open
python bin/manual.py --company pingan --open
python bin/manual.py --all
```

Output is written to `out/manual-<slug>.html`. Print to A4 PDF from the browser.

## Length is content-driven

Conditional sections:

- **Always**: cover, business, income statement, balance sheet, cash flow, sources.
- **Only if present**: segment mix, capital allocation (dividends / buybacks), cash & debt detail, governance facts.
- **Optional**: company facts, accounting-scope notes, definitions.

Do not add empty sections to reach a target page count. If a field is missing, render `—` or omit the section.

## Data contract

`data/<slug>/company.json`:

- `name`, `legal_name`, `ticker`, `exchange`
- `locale`: `en` or `zh`
- `currency`, `unit`, `symbol`
- `fy_label`, `fy_end`
- `founded`, `hq`, `employees`, `industry`
- `business`: one factual paragraph
- `business_pillars`: `[[title, description], ...]`
- `key_facts`: `[[label, value], ...]`
- `financials`: annual rows, oldest to newest:
  - `year`, `revenue`, `gross_profit`, `operating_income`, `net_income`
  - `assets`, `liabilities`, `equity`, `total_equity` (optional)
  - `cash`, `debt`, `ocf`, `capex`, `dividends`, `buybacks`
  - `roe` (reported, optional; decimal), `eps` (optional)
- `segments`: optional `{kind, name, revenue, share, gm}`
- `notes`: data caveats
- `sources`: `[[label, url], ...]`

All money values use the same `unit`; the renderer does not convert currencies.

## Guardrails

- Use reported figures only. Do not introduce adjusted, forecast, or vendor-estimated numbers.
- Margins and FCF are computed from reported line items; label them as computed.
- Every manual must list its sources.
- Every manual must end with the fixed disclaimer block (locale text plus the other language):
  not investment advice, no buy/sell recommendation, historical results do not guarantee future
  performance. Do not remove or reword it into a rating.
- No ratings, no scores, no target prices, no buy/sell language.
- If a field is missing, render `—`; do not estimate.
- Fiscal years and currencies must be explicit on the cover.
- For A-share companies, flag material accounting-scope changes (e.g. acquisitions) in `notes`.
- Keep the cover's 10-year revenue strip log-scaled and labelled.
- Do not add a closing tagline or a company directory at the end.

## Output

- Cover: identity, business, key facts, 10-year record, 10-year revenue strip.
- Business: description, pillars, segments when available, company facts, notes.
- Income: chart, 10-year table, observations, YoY growth.
- Balance & cash: 10-year table, cash conversion, FCF, five-year cash table, assets/equity chart.
- Capital allocation: only if dividends or buybacks exist.
- Sources: sources, method, definitions.

The document flows continuously; page breaks follow content, not a fixed count.

## Design

Cream paper, deep green, amber. Bricolage Grotesque. Print CSS is included. The HTML is self-contained and does not call the network.
