# DVN Analysis Framework — Forensic Capital
**Version:** 1.0 | **FC-ID context:** FC-001, FC-004
**Published:** 2026-05-31
**License:** CC-BY-4.0

> Methodology for auditing Decentralized Verification Network (DVN) configurations
> on cross-chain bridge infrastructure. Primary case studies: FC-001 KelpDAO ($292M)
> and FC-004 Verus Bridge ($11.58M).

---

## Table of Contents

1. [Scope and Architecture Primer](#1-scope-and-architecture-primer)
2. [DVN Configuration Audit](#2-dvn-configuration-audit)
3. [Threshold and Quorum Analysis](#3-threshold-and-quorum-analysis)
4. [Key Custodian Mapping](#4-key-custodian-mapping)
5. [Signal Collection and On-Chain Indicators](#5-signal-collection-and-on-chain-indicators)
6. [Risk Scoring Model](#6-risk-scoring-model)
7. [Historical Incident Comparison](#7-historical-incident-comparison)

---

## 1. Scope and Architecture Primer

### 1.1 What Is a DVN?

A **Decentralized Verification Network (DVN)** is a set of permissioned off-chain verifiers
responsible for attesting to the validity of cross-chain messages before they are executed
on the destination chain. The term is used canonically in the LayerZero v2 architecture
but the underlying security pattern applies to all bridge designs that separate
*message relaying* from *message verification*.

### 1.2 Bridge Architectures in Scope

| Architecture | Canonical Implementation | Verification Layer |
|---|---|---|
| DVN multi-sig | LayerZero v2 | Configurable DVN set + threshold |
| Guardian model | Wormhole | 19-of-19 → 13-of-19 threshold |
| Validator set | Ronin, Axelar | Weighted stake + threshold |
| MPC / TSS | Multichain, Harmony Horizon | Shared secret + threshold |
| Custom relay | Nomad, Verus | Application-level proof verification |

### 1.3 Core Security Invariant

The fundamental invariant for any bridge in scope:

> **An adversary must compromise ≥ threshold_k verifiers simultaneously
> before a fraudulent message can be finalized on the destination chain.**

Any design, implementation, or configuration flaw that reduces the *effective*
threshold below the *declared* threshold is a DVN misconfiguration.

---

## 2. DVN Configuration Audit

### 2.1 On-Chain Configuration Reads

For LayerZero v2 deployments, the relevant parameters are stored on the
Endpoint contract. The following reads are required:

```
UlnConfig.confirmations          — block depth before message is eligible
UlnConfig.requiredDVNCount       — minimum DVN attestations required (k)
UlnConfig.optionalDVNCount       — optional DVN count
UlnConfig.optionalDVNThreshold   — how many optional DVNs must also attest
UlnConfig.dvns[]                 — ordered list of DVN addresses
```

### 2.2 Audit Checklist

- [ ] Read `requiredDVNCount` on-chain; verify matches project documentation
- [ ] Enumerate all addresses in `dvns[]`; verify each is a live, non-deprecated DVN
- [ ] Cross-check DVN operators against known custodian registry
- [ ] Verify `confirmations` meets destination chain finality requirements
- [ ] Check for `optionalDVNThreshold = 0` with non-zero `optionalDVNCount` (common gap)
- [ ] Confirm all DVN contracts are non-upgradeable or have timelocked upgrades
- [ ] Check if any DVN address resolves to an EOA or unverified contract

### 2.3 Threshold Bypass Patterns

The following configuration states create exploitable threshold bypasses:

| Pattern | Description | FC Incident |
|---|---|---|
| `requiredDVNCount = 1` | Single point of failure masquerading as multi-party | FC-001 |
| DVN address = EOA | Verification logic offloaded to unprotected key | — |
| Deprecated DVN in set | Old DVN still counts toward threshold; operator no longer monitors | — |
| Confirmation = 0 | Message finalized before any block confirmations | — |
| Custom verifier with unbounded input | Application-layer proof check has binding gap | FC-004 |

### 2.4 Value Binding Analysis

**Value binding** is the cryptographic or logical property that ties a proof,
signature, or attestation to a *specific* message payload and *specific*
source-destination pair. A binding gap exists when a verification function
accepts a valid-format proof without checking that the proof corresponds to
the exact message being finalized.

#### 2.4.1 Binding Gap Definition

A bridge has a value binding gap when the following holds:

```
verify(proof, message) returns TRUE
even when proof was generated for message' ≠ message
```

This allows an attacker to:
1. Observe or construct a proof that passes structural validation
2. Submit it with an attacker-controlled payload
3. Execute arbitrary cross-chain actions under the bridge's authority

#### 2.4.2 FC-001 KelpDAO — Threshold Binding Gap

In the FC-001 incident, the binding failure occurred at the *configuration* level
rather than the cryptographic level. The `requiredDVNCount = 1` parameter meant
that a single DVN attestation was sufficient to finalize any message, regardless
of the message content or destination.

**Binding gap type:** Configuration binding — threshold does not bind to message integrity
**Effective binding:** Any message approved by 1 DVN is considered verified
**Attack path:**
```
Attacker controls or compromises 1 DVN
→ DVN signs arbitrary cross-chain message
→ requiredDVNCount = 1 satisfied
→ Destination chain executes message
→ Bridge escrow drained
```

**Audit signal:** Read `requiredDVNCount` on-chain; compare to project's stated security model.
A project claiming "multi-party verification" with `requiredDVNCount = 1` has a configuration
binding gap independent of which DVN operators are in the set.

#### 2.4.3 FC-004 Verus Bridge — Source-Destination Binding Gap

The FC-004 incident (`checkCCEValues`, Verus Bridge, $11.58M, 2026-05-18) involved
a binding gap in the application-layer verification function. The bridge's cross-chain
export verification checked whether a proof was structurally valid but did not bind
the proof to the specific source chain and destination address of the transaction
being processed.

**Binding gap type:** Application-layer binding — proof validates format but not binding
**Effective binding:** Source chain ID and destination address were not constrained
**Attack path:**
```
Attacker constructs valid-format proof for arbitrary (source, destination)
→ checkCCEValues verifies proof structure: PASS
→ Source-destination binding check: ABSENT
→ Bridge credits destination address with attacker-specified amount
→ $11.58M drained over 23-minute window
```

**Audit signal:** For any custom verification function, verify:
- Proof is explicitly bound to `msg.sender` or caller address
- Proof is explicitly bound to source chain ID
- Proof is explicitly bound to token amount and contract address
- Proof cannot be replayed across different destination calls

#### 2.4.4 Binding Gap Comparison: FC-001 vs FC-004

| Dimension | FC-001 KelpDAO | FC-004 Verus Bridge |
|---|---|---|
| Gap location | DVN configuration layer | Application verification layer |
| Binding type | Threshold (k-of-n) | Source-destination |
| Audit visibility | On-chain read of `requiredDVNCount` | Source code review of `checkCCEValues` |
| Fix complexity | Config parameter change | Logic rewrite + audit |
| Loss | $292M | $11.58M |
| Recovery | Ongoing (75% bounty May 21 2026) | ~75% (~$8.5M bounty) |
| FC-001 pattern match | Direct | Indirect (same family) |

Both incidents demonstrate the same underlying principle: verification passes
because the *format* of the proof or attestation is valid, while the *binding*
between the proof and the specific transaction being authorized is absent or
misconfigured.

#### 2.4.5 Binding Audit Checklist

- [ ] For DVN threshold configs: `requiredDVNCount` ≥ 2; verify matches stated security model
- [ ] For custom verifiers: each `verify()` function explicitly checks `sourceChainId`
- [ ] For custom verifiers: each `verify()` function explicitly checks `destinationAddress`
- [ ] For custom verifiers: each `verify()` function explicitly checks `amount` or `payload hash`
- [ ] For relay designs: message nonce or sequence number prevents replay
- [ ] For proof-based systems: proof is bound to block height at time of submission
- [ ] No `if (proof != 0)` patterns (Nomad replay — zero-value treated as valid)

---

## 3. Threshold and Quorum Analysis

### 3.1 Declared vs. Effective Threshold

The **declared threshold** is the value stored on-chain (`requiredDVNCount`).
The **effective threshold** is the number of *independent* actors an adversary must
compromise to forge a valid attestation set.

These differ when:
- Multiple DVN slots are controlled by the same legal entity
- A DVN delegates key management to a shared custody provider
- A DVN uses the same HSM pool as another DVN in the same set

### 3.2 Entity Consolidation Methodology

```
1. Enumerate DVN addresses from on-chain config
2. Resolve each to an operator (public docs, ENS, Etherscan labels)
3. Map operators to legal entities (corporate registry, LinkedIn, public disclosure)
4. Identify shared infrastructure: same ASN, same cloud region, same key provider
5. Compute effective_threshold = distinct_entities_in_set / declared_threshold
```

**Risk flag:** `effective_threshold < declared_threshold` → consolidation risk.

### 3.3 Timing Attack Window

Even a correctly configured threshold can be bypassed if the block confirmation
requirement is set too low for the destination chain's reorg depth. Minimum values:

| Chain | Minimum Safe Confirmations |
|---|---|
| Ethereum mainnet | 12 (2 epochs) |
| BNB Smart Chain | 15 |
| Arbitrum | 1 (L2 sequencer finality) |
| Optimism | 1 (L2 sequencer finality) |
| Polygon | 256 |
| Solana | 32 (confirmed commitment) |

---

## 4. Key Custodian Mapping

### 4.1 Custodian Risk Taxonomy

| Level | Description | Risk |
|---|---|---|
| L0 | Air-gapped HSM, geographically distributed | Baseline |
| L1 | Cloud KMS (AWS KMS, GCP KMS, Azure Key Vault) | Medium — see FC-005 |
| L2 | Software wallet (MetaMask, Fireblocks API) | High |
| L3 | EOA with no multisig | Critical |

### 4.2 Cloud KMS Risk Note

The 2026 Resolv incident (`2026-03-23`, $25M) involved an AWS KMS service role
compromise. Cloud KMS is not equivalent to hardware isolation; IAM misconfiguration
or service role credential leakage can expose signing capability without directly
touching the private key material.

### 4.3 Mapping Process

```
For each DVN operator:
  1. Identify public signing address
  2. Check transaction history for deployer patterns
  3. Cross-reference with known custodian services (Fireblocks, Copper, Qredo)
  4. Flag if signing address has been active < 30 days (new key rotation — why?)
  5. Flag if signing address has no on-chain history before DVN registration
```

---

## 5. Signal Collection and On-Chain Indicators

### 5.1 Pre-Exploit Signals

The following on-chain patterns have preceded DVN-related exploits in the
Forensic Capital incident database:

| Signal | Lead Time | Example Incident |
|---|---|---|
| Unusual DVN config change (threshold reduced) | Hours–days | FC-001 |
| Large dormant bridge reserve movement | Minutes–hours | Ronin 2022 |
| DVN address replacement with unverified contract | Days | — |
| Message volume spike without corresponding TVL movement | Minutes | Nomad |
| Proof verification contract upgrade with no timelock | Days | FC-004 |

### 5.2 Monitoring Query Templates

**Detect threshold changes (LayerZero v2 Endpoint):**
```
Event: UlnConfigSet(address indexed oapp, uint32 eid, UlnConfig config)
Alert if: config.requiredDVNCount < previous_config.requiredDVNCount
```

**Detect DVN address rotation:**
```
Event: DVNsSet(address indexed oapp, address[] dvns)
Alert if: any address in dvns[] not in previous dvns[]
```

**Detect large outflow without inflow:**
```
Monitor: ERC20.Transfer from bridge_escrow to unknown_address
Alert if: transfer_amount > 5% bridge_TVL within 1 block
```

### 5.3 Off-Chain Signals

- DVN operator team changes (LinkedIn, GitHub commit history)
- Security audit scope explicitly excludes DVN configuration
- Bridge documentation contradicts on-chain config (e.g., claims k-of-n but chain shows 1-of-n)
- Project refuses to disclose DVN operator identities

---

## 6. Risk Scoring Model

### 6.1 DVN Risk Score (DRS) — Component Weights

| Component | Max Points | Description |
|---|---|---|
| Threshold adequacy | 30 | `requiredDVNCount` ≥ 3 and > 50% of DVN set |
| Entity independence | 25 | All DVN operators are distinct legal entities |
| Key custody level | 20 | All operators at L0 or L1 custodian level |
| Confirmation depth | 15 | Meets per-chain minimums (Section 3.3) |
| Upgrade governance | 10 | DVN contracts non-upgradeable or timelocked ≥ 48h |
| **TOTAL** | **100** | |

### 6.2 Scoring Thresholds

| DRS | Risk Band | Recommended Action |
|---|---|---|
| 85–100 | LOW | Monitor quarterly |
| 70–84 | MEDIUM | Monitor monthly; request operator disclosure |
| 50–69 | HIGH | Alert — consider public disclosure |
| < 50 | CRITICAL | Immediate disclosure warranted |

### 6.3 FC-001 KelpDAO DRS (Retrospective)

| Component | Score | Notes |
|---|---|---|
| Threshold adequacy | 5/30 | `requiredDVNCount = 1` at exploit time |
| Entity independence | 10/25 | Single operator behind declared DVN |
| Key custody level | 15/20 | L1 custody (cloud KMS) |
| Confirmation depth | 12/15 | Adequate confirmations set |
| Upgrade governance | 8/10 | Partial timelock |
| **Total** | **50/100** | **CRITICAL** |

### 6.4 FC-004 Verus Bridge DRS (Retrospective)

| Component | Score | Notes |
|---|---|---|
| Threshold adequacy | 20/30 | Multi-validator but binding gap bypassed threshold |
| Entity independence | 18/25 | Independent operators present |
| Key custody level | 16/20 | Mixed L1/L0 custody |
| Confirmation depth | 10/15 | Sub-optimal for Ethereum |
| Upgrade governance | 4/10 | `checkCCEValues` binding gap unaudited |
| **Total** | **68/100** | **HIGH** |

### 6.5 Incident Recovery Analysis

Verified recovery data for DVN-class bridge incidents. Rates reflect publicly
confirmed fund recovery as of 2026-05-31. Source: primary post-mortems.

| Incident | Date | Loss | Recovered | Rate | Recovery Mechanism |
|---|---|---|---|---|---|
| Wormhole | 2022-02-02 | $320M | $320M | 100% | Jump Trading covered full loss via treasury |
| Nomad | 2022-08-01 | $190M | ~$16M | ~8.4% | White hat returns |
| Ronin | 2022-03-23 | $624M | ~$5.8M | <1% | Binance seizure |
| KelpDAO (FC-001) | 2026-04-18 | $292M | ~$219M est. | ~75% (May 21 2026) | Partial bounty — PeckShield / Binance / KuCoin |
| Verus (FC-004) | 2026-05-18 | $11.58M | ~$8.5M | ~75% | Bounty programme |

**Key finding**: 2 of 5 incidents recovered < 10% of losses (Nomad ~8.4%, Ronin <1%).
Wormhole (100%) is an outlier — Jump Trading backstop is not a reproducible mechanism.
KelpDAO (~75%, May 2026) and Verus (~75%) reflect bounty return norms, not a systemic baseline.
Effective bridge security requires prevention, not recovery.

---

## 7. Historical Incident Comparison

### 7.1 DVN-Class Incidents — Forensic Capital Database

The following six incidents were selected for their direct relevance to DVN
threshold or bridge verification failures. All figures sourced from public post-mortems.

| Date | Protocol | Chain | Loss (USD) | Root Cause | DVN Pattern | Recovery | Source |
|---|---|---|---|---|---|---|---|
| 2022-02-02 | Wormhole | Solana+ETH | $320,000,000 | Guardian signature verification bypass | Signature forgery bypassed guardian threshold | 100% (Jump Trading) | rekt.news |
| 2022-08-01 | Nomad | Ethereum | $190,000,000 | Message root zero-value replay | Proof binding gap — any message auto-approved | ~8.4% (~$16M white hats) | rekt.news |
| 2022-10-07 | BNB Chain Bridge | BNB | $570,000,000 | Merkle proof forgery | Proof verification logic bypassed | Resolved | rekt.news |
| 2026-04-18 | KelpDAO (FC-001) | Ethereum | $292,000,000 | DVN threshold bypass | `requiredDVNCount = 1` in production config | ~75% (May 21 2026) | forensic-capital.com |
| 2026-05-18 | Verus Bridge (FC-004) | Ethereum | $11,580,000 | `checkCCEValues` binding gap | Application-layer binding skipped threshold | ~75% (~$8.5M bounty) | blockaid.io / forensic-capital.com |
| 2022-03-23 | Ronin Bridge | Ronin/Ethereum | $624,000,000 | Validator key compromise | 5-of-9 validator set — attacker captured 5 keys undetected | <1% (~$5.8M Binance) | Halborn post-mortem |

**Aggregate loss — 6 incidents: $2,007,580,000**

> **Key finding**: 2 of 6 incidents recovered < 10% of losses (Nomad ~8.4%, Ronin <1%).
> Wormhole 100% = outlier (Jump Trading treasury backstop — non-reproducible mechanism).
> KelpDAO (~75%, May 2026) and Verus (~75%) reflect bounty return norms, not a systemic baseline.
> Security must be built at prevention layer.

### 7.2 Pattern Synthesis

Three structural failure modes account for all six incidents:

**Mode A — Declared threshold ≠ Effective threshold** (FC-001, BNB Chain Bridge, Ronin)
The configuration parameter specifies a secure value but implementation,
key consolidation, or a single operator behind multiple DVN slots reduces
the actual adversarial cost to 1.

Ronin (2022-03-23): 5 of 9 validators compromised via targeted phishing.
Threshold bypassed with majority key control. $624M drained.
Source: Halborn post-mortem.

**Mode B — Proof binding gap** (Wormhole, Nomad, FC-004)
The verification function validates a proof format but does not bind the proof
to the specific message content being finalized. An attacker can supply a
valid proof for a different (or null) message to authorize arbitrary execution.

**Mode C — Replay / state ambiguity** (Nomad)
A zero-value or default state in the message root mapping is interpreted as
"proven" rather than "uninitialized," enabling any message to be replayed
without a valid proof.

### 7.3 Cross-Protocol Implications

The DVN threshold bypass pattern documented in FC-001 is architecturally
identical to the validator set consolidation risk in Ronin 2022
($624M, five of nine validators compromised by North Korea-affiliated attackers (Lazarus Group)).
The attack surface is preserved across different naming conventions:
"DVN," "guardian," "validator," and "relayer" all describe the same role —
an off-chain attester whose compromise determines bridge safety.

---

## Limitations and Disclosure

- This framework reflects public post-mortem information only.
- DVN operator identities are often partially or fully undisclosed; entity
  consolidation analysis (Section 4) may be incomplete.
- DRS scores in Section 6.3 and 6.4 are retrospective estimates based on
  public information available at the time of publication.
- This document does not constitute investment advice or a security guarantee
  for any protocol.
- Framework validated against FC-001 and FC-004 case studies only.
  Applicability to other architectures should be verified independently.

---

*Forensic Capital — [forensic-capital.com](https://forensic-capital.com)*
*FC-ID context: FC-001, FC-004 | Version 1.0 | CC-BY-4.0*
