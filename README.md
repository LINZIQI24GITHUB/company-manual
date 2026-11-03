# FinanSI Company Manual

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-1f4d3a)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-1f4d3a)](LICENSE)
[![No ratings](https://img.shields.io/badge/ratings-none-1f4d3a)](#data-rules)

**A content-driven company manual for US and China listed companies.**

One company = one manual. The page count follows what the company actually discloses, not a fixed template.

- **NVIDIA** (NASDAQ: NVDA) · FY2026 10-K
- **中际旭创** (SZ: 300308) · FY2025 annual report
- Facts only: no ratings, no target price, no buy/sell call.
- Self-contained HTML; print to A4 PDF.

![NVIDIA company manual](assets/preview-nvda.png)

![中际旭创 company manual](assets/preview-zjxc.png)

## Quick start

Requires Python 3.11+. No package install, no API key, no network.

```bash
git clone https://github.com/finansi-work/company-manual.git
cd company-manual

python bin/manual.py --company nvda --open
python bin/manual.py --company zjxc --open
```

`--open` opens the HTML in your browser. Click **Print / Save PDF**, print A4.

Render both as separate manuals:

```bash
python bin/manual.py --all
```

Output:

```text
out/manual-nvda.html
out/manual-zjxc.html
```

Prebuilt sample PDFs: [NVIDIA](examples/manual-nvda.pdf) · [中际旭创](examples/manual-zjxc.pdf)

## Why this exists

Most “AI finance” output is a chat answer or a Markdown report. This project treats the deliverable as a **company manual**:

- a standardized entry for every company;
- 10-year reported financials;
- business mix and capital allocation when disclosed;
- sources and definitions on the page;
- variable length, because companies are not equally complicated.

The design reference is the page-by-page company manual tradition (Moody's / Value Line style). This project is not affiliated with either.

## What is inside

| Section | Content |
| --- | --- |
| Cover | identity, business, key facts, 10-year record, revenue strip |
| Business | description, pillars, segment mix when disclosed, company facts, data notes |
| Income | revenue / net-margin chart, 10-year table, observations, YoY growth |
| Balance & cash | 10-year balance sheet and cash flow, cash conversion, FCF, five-year cash table, assets/equity chart |
| Capital allocation | only if dividends or buybacks exist |
| Sources | sources, method, definitions |

Conditional sections are omitted when the data is not there. No empty sections, no estimates, no padding to hit a page target.

## Current demos

| Company | Period | Currency | Latest annual |
| --- | --- | --- | --- |
| NVIDIA | FY2017–FY2026 | US$ bn | FY2026 10-K, ended 2026-01-25 |
| 中际旭创 | 2016–2025 | 亿元 | 2025 annual report |

The two current demos both fit in 4 pages. That is a layout result, not a specification. A company with fewer years or no segment data will be shorter; a group with segments, buybacks, and governance history will be longer.

## Repository layout

```text
company-manual/
├─ bin/manual.py              # CLI: one company or --all
├─ templates/
│  ├─ manual.css              # paper, type, tables, panels
│  └─ manual-flow.css         # continuous page flow
├─ schema/company.schema.json # data contract
├─ data/
│  ├─ nvda/company.json
│  └─ zjxc/company.json
├─ assets/                    # cover previews, embedded font
├─ examples/                  # sample PDFs
├─ tests/                     # stdlib unittest
└─ .github/workflows/         # CI
```

## Add a company

1. Create `data/<slug>/company.json` following `schema/company.schema.json`.
2. Keep all money values in one currency and one unit; the renderer does not convert.
3. Use reported figures only. If a field is missing, use `null`; do not estimate.
4. Run:

```bash
python bin/manual.py --company <slug> --open
```

## Data rules

- Use annual reports, SEC XBRL, or another named public source.
- Every entry must list sources with URLs.
- Margins and FCF are computed from reported line items and labelled as computed.
- Flag accounting-scope changes (acquisitions, restatements) in `notes`.
- No adjusted, forecast, or vendor-estimated numbers.
- No ratings, scores, target prices, or trade recommendations.
- Data remains subject to the terms of its original source.

## Development

```bash
python -m unittest discover -s tests -v
python bin/manual.py --all --out out
```

No third-party dependencies for rendering. PDF export is done by the browser print dialog. CI renders both HTML files and uploads them as an artifact.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the PR checklist.

## License

Code and templates: MIT. Data and third-party content: original terms.
