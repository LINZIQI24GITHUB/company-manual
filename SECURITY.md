# Security

## Report a vulnerability

Please use GitHub's private vulnerability reporting:

<https://github.com/LINZIQI24GITHUB/finansi-company-manual/security/advisories/new>

Do not open a public issue for a security problem.

## Scope

This project renders local JSON into static HTML. It does not call a network API, store credentials, or execute user-supplied code. The main security surface is:

- malicious HTML/JSON strings in company data;
- dependency and CI supply-chain issues;
- data licensing violations.

## Data

Do not commit API keys, broker credentials, private filings, or licensed market data. Demo data must be redistributable or used with permission.
