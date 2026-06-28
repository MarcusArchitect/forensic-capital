# FC Risk Taxonomy v1.0
## Forensic Capital — DeFi Incident Classification Framework

**Version:** 1.0 | **Published:** 2026-05-31
**Dataset:** defi-incidents-2026.csv — 41 verified incidents (2021–2026)
**License:** CC-BY-4.0

---

## Overview

Unified classification of DeFi security incidents based on root cause analysis.
Derived from the Forensic Capital incident database of 41 verified incidents
totalling $6.13B in verified losses.

Each incident is assigned a single primary `vector_category` reflecting the
root exploitation mechanism, not the attack delivery method. For example,
a flash loan used to manipulate governance is classified as `GOVERNANCE`, not
`FLASH_LOAN`, because the flash loan is a delivery mechanism, not the vulnerability.

FC has published full forensic reports for 3 incident classes:
FC-001 (DVN_BRIDGE), FC-003 (CREDENTIAL_COMPROMISE), FC-004 (BRIDGE_VERIFICATION_GAP).

---

## Vector Classification Table

Sorted by total loss (descending). Figures from `defi-incidents-2026.csv`.

| Vector | Incidents | Total Loss | % of \$Total | FC Coverage |
|---|---:|---:|---:|---|
| ACCESS_CONTROL | 14 | $2,153,000,000 | 35.1% | — |
| BRIDGE_VERIFICATION_GAP | 5 | $1,704,280,000 | 27.8% | FC-004 |
| CREDENTIAL_COMPROMISE | 8 | $1,216,700,000 | 19.9% | FC-003 |
| FLASH_LOAN | 4 | $376,200,000 | 6.1% | — |
| DVN_BRIDGE | 1 | $292,000,000 | 4.8% | FC-001 |
| GOVERNANCE | 1 | $182,000,000 | 3.0% | — |
| PRICE_MANIPULATION | 6 | $102,600,000 | 1.7% | — |
| REENTRANCY | 2 | $100,500,000 | 1.6% | — |
| **TOTAL** | **41** | **$6,127,280,000** | **100%** | |

*Note: 1 row excluded (malformed source tag). 41 clean data rows used for statistics.*

---

## Vector Definitions

### ACCESS_CONTROL
Unauthorized execution of privileged protocol functions due to missing or
bypassed access control logic. Includes admin key compromise where the key
is used to call on-chain functions directly (not just custody loss).

**Signature incidents:** Bybit ($1.5B, Safe multisig UI compromise),
Radiant Capital ($50M, multisig key compromise), PlayDapp ($290M).

### BRIDGE_VERIFICATION_GAP
The bridge's message verification function accepts messages that should fail
the proof or signature check. The protocol accepts fraudulent messages as valid.

**Signature incidents:** BNB Chain Bridge ($570M, Merkle proof forgery),
Wormhole ($320M, guardian signature bypass), Nomad ($190M, zero-value replay),
Verus Bridge ($11.58M, checkCCEValues binding gap — FC-004).

### CREDENTIAL_COMPROMISE
Loss of a cryptographic credential (private key, seed phrase, API key) that
directly controls protocol funds or administrative capabilities.
Does not require an on-chain vulnerability — the credential itself is the attack surface.

**Signature incidents:** Ronin Bridge ($625M, validator key compromise),
Multichain ($126M, admin key), Mixin Network ($200M, cloud DB breach — FC-003 class).

### FLASH_LOAN
A flash loan is used as the primary delivery mechanism to exploit a protocol
vulnerability that would otherwise require substantial capital. The underlying
vulnerability may be an oracle, market, or arithmetic flaw.

**Signature incidents:** Euler Finance ($197M, donation attack),
Cream Finance ($130M, oracle manipulation), Beanstalk ($182M — classified GOVERNANCE
because the flash loan exploited a governance mechanism, not an oracle).

### DVN_BRIDGE
A specific subclass of bridge failure where the LayerZero DVN configuration
allows a single or insufficient set of verifiers to approve cross-chain messages.
Distinguished from BRIDGE_VERIFICATION_GAP by the architectural root cause:
configuration error rather than implementation bug.

**Signature incident:** KelpDAO ($292M, requiredDVNCount = 1 — FC-001).

### GOVERNANCE
A protocol's on-chain governance mechanism is exploited to pass malicious
proposals, drain treasury funds, or modify protocol parameters.
Flash loans are often used as delivery mechanism but the root cause is
the governance design (insufficient time-lock, low quorum requirements).

**Signature incident:** Beanstalk ($182M, flash loan governance proposal exploit).

### PRICE_MANIPULATION
An attacker manipulates the price reported by a spot or oracle-based price
feed to borrow against inflated collateral or trigger incorrect liquidations.
The price feed works as designed but is used in a protocol context where
manipulation is economically viable.

**Signature incidents:** KyberSwap ($48.8M, tick boundary exploit),
Polter Finance ($12M, empty market flash loan), KiloEx ($7.4M).

### REENTRANCY
Recursive calls into a contract before state is finalized, allowing
a function to be executed multiple times with the initial state.
Includes compiler-level reentrancy bugs (Curve/Vyper).

**Signature incidents:** Curve Finance ($73.5M, Vyper compiler bug),
Penpie ($27M, staking pool reentrancy).

---

## FC Coverage

Full forensic analysis published for the following incident classes:

| FC ID | Protocol | Vector | Loss | Status | Coverage Level |
|---|---|---|---:|---|---|
| FC-001 | KelpDAO | DVN_BRIDGE | $292,000,000 | Partial | Full forensic |
| FC-003 | Resolv | CREDENTIAL_COMPROMISE | $25,000,000 | Partial | Full forensic |
| FC-004 | Verus Bridge | BRIDGE_VERIFICATION_GAP | $11,580,000 | Partial | Full forensic |

FC-001, FC-003, and FC-004 represent 3 distinct vector classes — no two FC reports
cover the same attack surface. Combined: $328,580,000 in documented losses.

---

## Key Findings

### Finding 1 — ACCESS_CONTROL dominates by incident count and total loss

14 incidents / $2.15B (35% of total losses).
Bybit ($1.5B, 2025) alone accounts for 24% of all losses in the database.
Excluding Bybit, ACCESS_CONTROL drops to $653M across 13 incidents —
still the largest category by count.

**Implication:** Key management and multisig governance are the primary
DeFi attack surface by volume. Hardware security modules, MPC custody,
and multisig threshold management are the highest-leverage defensive investments.

### Finding 2 — Bridge class is underestimated when split

BRIDGE_VERIFICATION_GAP (5 incidents, $1.70B) and DVN_BRIDGE (1 incident, $292M)
share the same architectural root: cross-chain message verification failure.
Combined: 6 incidents, $1,996,280,000 — **32.6% of all losses**, making it
the second largest attack class after ACCESS_CONTROL.

**Implication:** Cross-chain bridge infrastructure represents the second
most critical attack surface. DVN configuration audits (FC-001 methodology)
and bridge verification logic reviews (FC-004 methodology) should be standard
practice for any protocol with cross-chain exposure.

### Finding 3 — CREDENTIAL_COMPROMISE is the most underestimated class

8 incidents / $1.22B (19.8% of losses). However, this class is structurally
different from on-chain vulnerabilities: **no smart contract audit can detect
credential compromise risk**. It requires operational security reviews,
key custody assessments, and social engineering threat modeling.

The Resolv incident (FC-003, $25M, AWS KMS service role) demonstrates
that cloud-managed key infrastructure is not equivalent to air-gapped custody.

---

## Bridge Class — Combined View

When BRIDGE_VERIFICATION_GAP and DVN_BRIDGE are merged into a single
"BRIDGE_CLASS" for cross-protocol analysis:

| Class | Incidents | Total Loss | % of Dataset |
|---|---:|---:|---:|
| ACCESS_CONTROL | 14 | $2,153,000,000 | 35.1% |
| **BRIDGE_CLASS** | **6** | **$1,996,280,000** | **32.6%** |
| CREDENTIAL_COMPROMISE | 8 | $1,216,700,000 | 19.9% |
| FLASH_LOAN + PRICE_MANIPULATION | 10 | $478,800,000 | 7.8% |
| GOVERNANCE + REENTRANCY | 3 | $282,500,000 | 4.6% |

---

## License and Sourcing

**License:** CC-BY-4.0
**Dataset:** defi-incidents-2026.csv (this repository)
**Primary sources:** Rekt News, CertiK, Chainalysis, DefiLlama, Blockaid, SlowMist
**FC reports:** forensic-capital.com

All figures are aggregated from public post-mortems. No private data.
No attribution beyond public sources.

---

*Forensic Capital — [forensic-capital.com/defi/](https://forensic-capital.com/defi/)*
*FC Risk Taxonomy v1.0 | CC-BY-4.0 | 2026-05-31*
