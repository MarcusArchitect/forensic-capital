# Methodology

## dvn-analysis-framework.md

Framework for auditing DVN (Decentralized Verification Network) multi-sig
configurations on cross-chain bridge infrastructure.

**Version:** 1.0 | **FC-ID context:** FC-001, FC-004
**License:** CC-BY-4.0

### Scope

Applicable to bridges using:
- LayerZero DVN architecture
- Wormhole Guardian model
- Axelar validator set
- Custom multi-sig bridge designs

### Framework Sections

1. Scope and Architecture Primer
2. DVN Configuration Audit
3. Threshold and Quorum Analysis
4. Key Custodian Mapping
5. Signal Collection and On-Chain Indicators
6. Risk Scoring Model (DRS /100)
7. Historical Incident Comparison

### Application

FC-001 KelpDAO $292M — primary case study (`requiredDVNCount = 1` bypass).
FC-004 Verus $11.58M — `checkCCEValues` binding gap.

### What the framework covers

- **DRS risk scoring /100** — 5-component weighted score (threshold, entity independence, key custody, confirmation depth, upgrade governance)
- **Value binding gap taxonomy** — configuration binding (FC-001) vs. source-destination binding (FC-004): formal definition, attack paths, audit checklist
- **5-incident comparative table** — Wormhole / Nomad / BNB Bridge / KelpDAO / Verus ($1.38B aggregate)
- **Threshold and quorum analysis** — declared vs. effective threshold, entity consolidation methodology, timing attack windows
- **On-chain monitoring queries** — `UlnConfigSet`, `DVNsSet`, large outflow detection
- **Key custodian mapping process** — L0/L1/L2/L3 risk taxonomy, cloud KMS risk note (FC-003 Resolv context)

### 5-Incident Reference Table

| Date | Protocol | Loss | Pattern |
|---|---|---|---|
| 2022-02-02 | Wormhole | $320M | Guardian signature forgery |
| 2022-08-01 | Nomad | $190M | Zero-value replay |
| 2022-10-07 | BNB Chain Bridge | $570M | Merkle proof forgery |
| 2026-04-18 | KelpDAO (FC-001) | $292M | DVN threshold bypass |
| 2026-05-18 | Verus Bridge (FC-004) | $11.58M | checkCCEValues binding gap |

Aggregate: **$1.38B** across 5 incidents.

---

Forensic Capital — [forensic-capital.com](https://forensic-capital.com)
