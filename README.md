# Forensic Capital — Research

[![FC Tools](https://github.com/MarcusArchitect/forensic-capital/actions/workflows/tools-check.yml/badge.svg)](https://github.com/MarcusArchitect/forensic-capital/actions/workflows/tools-check.yml)

Forensic intelligence for DeFi.
Independent. Passive OSINT only.
forensic-capital.com

## Published Incident Reports

| ID | Protocol | Loss | Vector | Date |
|---|---|---|---|---|
| FC-001 | KelpDAO | $292M | DVN Bridge Misconfiguration | 2026-04-18 |
| FC-003 | Resolv | $25M | AWS KMS Credential Compromise | 2026-03-22 |
| FC-004 | Verus Bridge | $11.58M | Bridge Verification Gap | 2026-05-18 |

→ Full reports: forensic-capital.com/defi/

> Scope note: Forensic Capital's published corpus covers bridge and cross-chain verification failures only. Incidents outside this perimeter (e.g. oracle parameter misconfiguration) are tracked internally, not here.

## Repository Contents

### /tools
**[dvn-config-checker.py](tools/dvn-config-checker.py)**
Verify LayerZero V2 DVN configuration health.
Companion to FC-001 KelpDAO ($292M DVN threshold bypass).
Checks: requiredDVNCount, threshold ratio, risk scoring.

**[analyze-vectors.py](tools/analyze-vectors.py)**
Compute attack vector statistics from defi-incidents-2026.csv.
Breakdown by vector: count, total loss, % of dataset, FC coverage.


> **Note:** Tools ship with illustrative reference data and run out-of-the-box (`--demo`, no dependencies). Live on-chain mode is optional and uses your own RPC endpoint via `FC_RPC_URL`.

### /datasets
**[defi-incidents-2026.csv](datasets/defi-incidents-2026.csv)**
41 verified DeFi incidents, 2026.
Schema: date | protocol | chain | loss_usd |
vector_category | root_cause | source_url | status
License: CC-BY-4.0
Sources: Rekt News, CertiK, Chainalysis, DefiLlama.

**[dvn-operator-registry.json](datasets/dvn-operator-registry.json)**
10 LayerZero DVN operators — custody levels L0–L3.
Confidence: verified×4 / inferred×4 / unknown×2.
License: CC-BY-4.0

### /methodology
**[dvn-analysis-framework.md](methodology/dvn-analysis-framework.md)**
Framework for DVN multi-sig analysis
on LayerZero/Wormhole/Axelar bridges.
Underlying methodology for FC-001 KelpDAO ($292M).

**[fc-risk-taxonomy.md](methodology/fc-risk-taxonomy.md)**
Unified DeFi attack vector taxonomy.
8 categories, 41 incidents, $6.13B aggregate.
Classification basis for defi-incidents-2026.csv.

## Methodology

100% passive OSINT.
No proprietary system access.
No NDA engagement.
Confidence threshold: 70%.
Below threshold: declared UNKNOWN.

Sources: on-chain data, official post-mortems,
CertiK, Chainalysis, Halborn, DefiLlama,
Blockaid, SlowMist, PeckShield.

## Contact

forensic-capital.com/defi/
research@forensic-capital.com

---
*Forensic Capital maintains 2–3 active mandates.
Incidents above $5M or regulatory exposure only.*
