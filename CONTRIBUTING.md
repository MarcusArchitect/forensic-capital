# Contributing — Forensic Capital Research

Corrections to public data improve the quality of the shared record.
This document describes how to propose a correction to a dataset
or registry entry in this repository.

---

## What we publish

- **`datasets/defi-incidents-2026.csv`** — DeFi incident database aggregated from public post-mortems
- **`datasets/dvn-operator-registry.json`** — LayerZero DVN operator registry aggregated from public documentation
- **`methodology/dvn-analysis-framework.md`** — Bridge DVN analysis methodology

All data is sourced from public information. No NDA. No private data.

---

## Known limitations (transparency, not gaps)

Some entries carry explicit confidence levels:

| Confidence | Meaning |
|------------|---------|
| `verified` | Address or fact confirmed by primary source |
| `inferred` | Derived from indirect signals; primary source not confirmed |
| `unknown` | Ecosystem listing only; details unverified |

`inferred` and `unknown` entries are published deliberately — partial public
information is more useful than omission, provided the confidence level is clear.

---

## How to submit a correction

### Correction format

Open a GitHub Issue with the following fields:

```
File:            datasets/dvn-operator-registry.json
                 datasets/defi-incidents-2026.csv
                 methodology/dvn-analysis-framework.md

Field:           [exact field name, e.g. custody_level, loss_usd, date]

Current value:   [exact current value in the file]

Proposed value:  [exact proposed replacement]

Primary source:  [URL to a publicly accessible primary source]
                 Accepted: official documentation, Etherscan label,
                 on-chain transaction, official blog, corporate registry.
                 Not accepted: secondary aggregators without attribution.

Notes:           [optional — context for the correction]
```

### What qualifies as a valid correction

- A factual error in date, loss amount, protocol name, or on-chain address
- A confidence level that is too high given available public evidence
- A field that has been superseded by new public disclosure
- A missing operator or incident that meets inclusion criteria

### What does not qualify

- Requests to remove an entry because it reflects negatively on a project
- Corrections without a verifiable primary source
- Disputes about analytical conclusions (e.g., DRS scores) without data errors

---

## Corrections to DVN operator entries

If you are a DVN operator and a field in `dvn-operator-registry.json`
incorrectly describes your custody model or infrastructure, please submit
a correction with:

- Your official documentation URL confirming the correct description
- The specific field(s) in error and the correct value(s)
- Contact information (optional — for follow-up verification)

Corrections from operators will update the `confidence` field to `verified`
once the primary source is confirmed.

---

## Contact

For corrections involving sensitive or non-public information that cannot
be submitted via a public GitHub Issue, use the responsible disclosure channel:

**forensic-capital.com/vdp/**

This channel is monitored for security-relevant corrections and
data quality reports. Response within 48 hours for incident data corrections.

---

## Scope of this repository

This repository contains public research tools and datasets only.
It does not contain FC mandate outputs, client reports, or signal inventory data.

---

*Forensic Capital — [forensic-capital.com](https://forensic-capital.com)*
