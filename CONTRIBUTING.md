# Contributing

Thanks for considering a contribution. This repository is deliberately narrow: **one company, one manual, facts only**.

## What we accept

- A new company entry with a named public source.
- Corrections to reported figures, with a source link.
- A new conditional section that is useful across companies.
- Rendering fixes that improve print quality.
- Tests and documentation improvements.

## What we do not accept

- Ratings, scores, target prices, buy/sell language.
- Forecasts, adjusted figures presented as reported, or vendor estimates.
- Invented numbers, invented sources, or “example” data that looks real.
- Scraped market data committed to the repository.
- Paid/proprietary skills copied from another project.

## Add a company

1. Create `data/<slug>/company.json` following `schema/company.schema.json`.
2. Keep every money value in one currency and one unit.
3. Add sources with URLs. If a field is missing, use `null`; do not estimate.
4. Run:

   ```bash
   python bin/manual.py --company <slug> --open
   ```

5. Check the cover, tables, and page flow in print preview.
6. Add the slug to the `companies` list in `bin/manual.py` only if it should be part of `--all`.

## Data checklist

- [ ] Every figure is reported or computed from reported line items.
- [ ] Computed margins/FCF are labelled as computed.
- [ ] Fiscal year end and currency/unit are explicit.
- [ ] Accounting-scope changes are in `notes`.
- [ ] Sources include URLs.
- [ ] No ratings, forecasts, or recommendations.
- [ ] Data redistribution terms are compatible with a public repository.

## Code checklist

- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] `python bin/manual.py --all --out out` renders both demos.
- [ ] No fixed page count was introduced.
- [ ] No closing tagline or company directory was added.
- [ ] Print preview is A4, with no white page ring or dark margin.

## License

By contributing, you agree that code and templates are licensed under MIT. Data and third-party content remain under their original terms.
