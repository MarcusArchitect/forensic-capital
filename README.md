# Forensic Capital

[![FC Tools](https://github.com/MarcusArchitect/forensic-capital/actions/workflows/tools-check.yml/badge.svg)](https://github.com/MarcusArchitect/forensic-capital/actions/workflows/tools-check.yml)

Independent forensic intelligence for DeFi bridge incidents.
Source-traceable. SHA-256 sealed. Passive OSINT only.
[forensic-capital.com](https://forensic-capital.com)

---

## Published Incident Reports

| ID | Protocol | Loss | FC Class | Vector | Date | Status |
|---|---|---|---|---|---|---|
| [FC-001](https://forensic-capital.com/reports/fc-001-kelpdao/) | KelpDAO | $292M | FC-CLASS-004 | DVN threshold bypass | 2026-04-18 | CLOSED |
| [FC-003](https://forensic-capital.com/reports/resolv/) | Resolv | $25M | FC-CLASS-002 | AWS KMS credential compromise | 2026-03-22 | CLOSED |
| [FC-004](https://forensic-capital.com/reports/fc-004-verus/) | Verus Bridge | $11.58M | FC-CLASS-001 | Bridge verification gap | 2026-05-18 | CLOSED |
| [FC-005](https://forensic-capital.com/reports/fc-005-gravity/) | Gravity Bridge | $5.4M | FC-CLASS-001 | Cross-chain registry corruption | 2026-05-29/30 | ACTIVE |

> FC-005 and FC-006 are active engagements. Published reports follow engagement close and client approval.

**Corpus:** 20 incidents tracked · $6.13B aggregate · 4 failure classes

---

## Failure Class Taxonomy

| Class | Name | Description |
|---|---|---|
| FC-CLASS-001 | Cross-Chain State Validation Failure | Verification gap between layers — registry corruption, relay/Core disagreement |
| FC-CLASS-002 | Privileged Key Compromise | Off-chain signing key compromised — no code defect |
| FC-CLASS-003 | Cross-Layer Interpretation Failure | Two components parse the same payload, resolve different identities |
| FC-CLASS-004 | Verifier Set Misconfiguration | DVN/validator threshold insufficient to prevent collusion |

---

## Tools

**[cross-layer-agreement-checker.py](tools/cross-layer-agreement-checker.py)**
Detect cross-layer asset identity disagreement in dual-verification bridge architectures.
Three reason codes: `vacuous_proof` · `multiple_identities` · `layer_disagreement`
Stdlib only. Applies to relay-proof and zk-light-client designs.
python cross-layer-agreement-checker.py --demo

**[dvn-config-checker.py](tools/dvn-config-checker.py)**
Verify LayerZero V2 DVN configuration health.
Companion to FC-001 KelpDAO ($292M DVN threshold bypass).
Checks: requiredDVNCount, threshold ratio, risk scoring.
python dvn-config-checker.py --demo

**[analyze-vectors.py](tools/analyze-vectors.py)**
Compute attack vector statistics from defi-incidents-2026.csv.
Breakdown by vector: count, total loss, % of dataset, FC coverage.
python analyze-vectors.py --demo

> All tools run out-of-the-box (`--demo`, no dependencies). Live on-chain mode: set `FC_RPC_URL`.

---

## Datasets

**[defi-incidents-2026.csv](datasets/defi-incidents-2026.csv)**
42 verified DeFi incidents · 2021–2026 · $6.13B aggregate
Schema: `date | protocol | chain | loss_usd | vector_category | root_cause | post_mortem_url | recovery_status | source_primary`
License: CC-BY-4.0

**[dvn-operator-registry.json](datasets/dvn-operator-registry.json)**
12 LayerZero DVN operators — custody levels L0–L3.
Confidence: verified×4 / inferred×5 / unknown×3.
License: CC-BY-4.0

---

## Methodology

**Source hierarchy:** on-chain data → official post-mortems → CertiK / Chainalysis / Halborn → secondary coverage.

**Confidence tiers:** Every finding is classified ESTABLISHED (on-chain or primary-source confirmed), INFERRED (logical elimination from confirmed data), or UNVERIFIED (open question, no primary source). Unverified items appear in Open Questions — never in conclusions.

**Confidence threshold:** 70%. Below threshold: declared UNKNOWN.

**Integrity:** Each published report is SHA-256 sealed at publication date, anchored in public repository commit history.

**Scope:** Bridge and cross-chain verification failures only. Incidents outside this perimeter are tracked internally, not published here.

---

## Contact

[forensic-capital.com](https://forensic-capital.com) · research@forensic-capital.com

---

*Forensic Capital maintains 2–3 active mandates. Incidents above $5M or regulatory exposure only.*
