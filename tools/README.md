# FC Tools — Forensic Capital

Public companion tools for Forensic Capital incident reports.

---

## dvn-config-checker.py

**FC-001 companion** — Verify LayerZero V2 DVN configuration health on Ethereum mainnet.

DVN (Decentralized Verification Network) threshold misconfiguration is the root cause
of the KelpDAO FC-001 incident ($292M, 2026-04-18). A `requiredDVNCount` of 1 allows
a single compromised DVN to approve fraudulent cross-chain messages unilaterally.
Full analysis: [forensic-capital.com/the-kelpdao-exploit/](https://forensic-capital.com/the-kelpdao-exploit/)

### What it checks

For each DVN configuration (3 in demo mode):

- `requiredDVNCount` and `optionalDVNCount` from `getUlnConfig` on LZ V2 Endpoint
- Threshold ratio = required / (required + optional)
- Flag if `requiredDVNCount = 1` (CRITICAL — FC-001 pattern)
- Flag if ratio < 33% (CRITICAL), < 50% (HIGH), < 75% (MEDIUM)
- Automatic fallback to demo mode if all RPCs unreachable

### Dependencies

```
web3>=6.0.0
```

Install:
```bash
pip install web3
```

### Usage

**Demo mode** (no network required — always works):
```bash
python3 dvn-config-checker.py --demo
```

**Live mode** (queries Ethereum mainnet):
```bash
python3 dvn-config-checker.py
python3 dvn-config-checker.py --network mainnet
```

Live mode tries 3 public RPC endpoints in order:
1. `eth.llamarpc.com`
2. `cloudflare-eth.com`
3. `rpc.ankr.com/eth`

If all fail, falls back to demo mode automatically.

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All configurations within acceptable bounds |
| `1`  | One or more MEDIUM, HIGH, or CRITICAL conditions detected |

### Output (demo mode — verified 2026-05-31)

```
=== FC DVN Config Checker ===
Forensic Capital | FC-001 companion
forensic-capital.com/the-kelpdao-exploit/

Network   : Ethereum Mainnet
Mode      : [DEMO]
Timestamp : 2026-05-31 17:35 UTC

─────────────────────────────────────────────

Config    : KelpDAO-style
Desc      : 1-of-1 configuration — FC-001 attack pattern
Required  : 1 DVN
Optional  : 0 DVNs
Threshold : 1/1 = 100% required
            BUT single point of failure
Confirms  : 15 blocks
Risk      : 🔴 CRITICAL
Reason    : 1-of-1 = FC-001 pattern — single DVN controls bridge security

─────────────────────────────────────────────

Config    : Standard Bridge
Desc      : 3-of-5 multi-party configuration — industry baseline
Required  : 3 DVNs
Optional  : 2 DVNs
Threshold : 3/5 = 60% required
Confirms  : 15 blocks
Risk      : 🟡 MEDIUM
Reason    : Threshold 3/5 = 60% — majority but below 75%

─────────────────────────────────────────────

Config    : Minimal Threshold
Desc      : 2-of-6 — low threshold relative to DVN pool size
Required  : 2 DVNs
Optional  : 4 DVNs
Threshold : 2/6 = 33% required
Confirms  : 12 blocks
Risk      : 🟠 HIGH
Reason    : Threshold 2/6 = 33% — below 50% majority

─────────────────────────────────────────────

Summary   : 3/3 configs checked
Flags     : 🔴 1 CRITICAL — immediate review required
            🟠 1 HIGH     — threshold below 50%
            🟡 1 MEDIUM   — monitor threshold trend

─────────────────────────────────────────────

FC-001 context: KelpDAO ($292M, 2026-04-18) demonstrated
  that a requiredDVNCount of 1 allows a single compromised
  DVN to approve fraudulent cross-chain messages unilaterally.
  A valid DVN configuration requires ≥ 3 required DVNs
  with a threshold ratio > 50% of the total DVN pool.

⚠  DEMO MODE — configurations are hardcoded illustrative data.
   Run without --demo for live on-chain verification.

Full analysis : forensic-capital.com/the-kelpdao-exploit/
Version       : 1.0.0 | FC-001
```

### Contracts queried

| Contract | Address |
|----------|---------|
| LayerZero V2 Endpoint (mainnet) | `0x1a44076050125825900e736c501f859c50fE728C` |
| SendUln302 library              | `0xbB2Ea70C9E858123480642Cf96acbcce1372dCe1` |

### Risk scoring model

| Threshold ratio | Risk band |
|----------------|-----------|
| `requiredDVNCount = 1` | 🔴 CRITICAL (overrides ratio) |
| < 33% | 🔴 CRITICAL |
| 33–50% | 🟠 HIGH |
| 51–75% | 🟡 MEDIUM |
| > 75% | ✅ ACCEPTABLE |

---

## analyze-vectors.py

**Dataset companion** — Compute attack vector statistics from `defi-incidents-2026.csv`.
Breaks down 42 DeFi incidents by vector category: count, total loss, % of dataset,
and which incidents have a published FC report.

### Usage

**Console table** (stdlib only, no install):
```bash
python3 analyze-vectors.py
```

**Export JSON** to `datasets/vector-stats.json`:
```bash
python3 analyze-vectors.py --json
python3 analyze-vectors.py --update   # alias
```

**Demo mode** (no CSV required — always works):
```bash
python3 analyze-vectors.py --demo
```

### Output (live mode — 41 incidents)

```
=== FC Vector Analysis ===
Forensic Capital | defi-incidents-2026.csv
forensic-capital.com/defi/

Total      : 41 incidents / $6.13B

──────────────────────────────────────────────────────────────────────────
VECTOR                                 N    % N          LOSS    % $  FC
──────────────────────────────────────────────────────────────────────────
ACCESS_CONTROL                        14  34.1%        $2.15B  35.1%  —
BRIDGE_VERIFICATION_GAP                5  12.2%        $1.70B  27.8%  —
CREDENTIAL_COMPROMISE                  8  19.5%        $1.22B  19.9%  —
FLASH_LOAN                             4   9.8%       $376.2M   6.1%  —
DVN_BRIDGE                             1   2.4%       $292.0M   4.8%  KelpDAO
GOVERNANCE                             1   2.4%       $182.0M   3.0%  —
PRICE_MANIPULATION                     6  14.6%       $102.6M   1.7%  —
REENTRANCY                             2   4.9%       $100.5M   1.6%  —
──────────────────────────────────────────────────────────────────────────
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Dataset parsed and output produced |
| `1`  | Dataset empty or unreadable |

### Dependencies

Standard library only. No install required.

---

## cross-layer-agreement-checker.py

**Forensic Capital — cross-layer verification tooling** — Detect asset identity disagreement across dual-verification bridge layers.

Cross-layer interpretation mismatch occurs when two independent verification layers resolve
different identities from the same payload, or when a payload encodes more than one valid
identity. Applies to any dual-verification bridge architecture, including relay-proof and
zk-light-client designs.
[forensic-capital.com](https://forensic-capital.com)

### What it checks

For each verification scenario:

- Exact agreement between `resolution_layer_a` and `resolution_layer_b`
- Payload identity count (must equal 1 for unambiguous processing)
- REJECT if `identity_count ≠ 1` (reason: `multiple_identities`)
- REJECT if layer resolutions differ (reason: `layer_disagreement`)
- Edge cases: None inputs, empty strings, identity_count = 0

### Dependencies

Standard library only. No install required.

### Usage

**Demo mode** (no network required — always works):
```bash
python3 cross-layer-agreement-checker.py --demo
```

**Production use** — import `check_agreement()` directly:
```python
from tools.cross_layer_agreement_checker import check_agreement
verdict, reason = check_agreement(
    resolution_layer_a=layer_a_output,
    resolution_layer_b=layer_b_output,
    identity_count=payload_identity_count,
)
```

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All cases passed (or demo mode) |
| `1`  | One or more REJECT conditions detected |

### Output (demo mode — verified 2026-06-28)

```
=== FC Cross-Layer Agreement Checker ===
Forensic Capital | cross-layer verification tooling
forensic-capital.com

Mode      : [DEMO]
Timestamp : 2026-06-28 21:02 UTC

─────────────────────────────────────────────

Case      : Perfect agreement
Desc      : Both layers resolve to the same identity; payload is unambiguous
Layer A   : asset_alpha
Layer B   : asset_alpha
Identities: 1
Verdict   : ✅ PASS

─────────────────────────────────────────────

Case      : Layer disagreement
Desc      : Layer A and Layer B resolve to different identities from the same payload
Layer A   : asset_alpha
Layer B   : asset_beta
Identities: 1
Verdict   : 🔴 REJECT
Reason    : layer_disagreement

─────────────────────────────────────────────

Case      : Dual-identity payload
Desc      : Payload encodes two valid identities — ambiguous proof, cannot be trusted
Layer A   : asset_alpha
Layer B   : asset_alpha
Identities: 2
Verdict   : 🔴 REJECT
Reason    : multiple_identities

─────────────────────────────────────────────

Summary   : 3/3 cases checked
Flags     : 🔴 2 REJECT(s) — fail-closed enforcement required

─────────────────────────────────────────────

Security principle: ambiguous proofs must fail closed.
  In dual-verification bridge architectures, a payload
  that two independent layers resolve differently — or
  that encodes more than one valid identity — cannot be
  safely processed. REJECT is the only conservative
  response. Applies to relay-proof and zk-light-client
  designs alike. Permitting ambiguous proofs to pass
  collapses the guarantee of dual verification entirely.

⚠  DEMO MODE — scenarios are hardcoded illustrative data.
   Integrate check_agreement() with your bridge resolver
   to verify live payloads.

Forensic Capital : forensic-capital.com
Version          : 1.0.0 | Forensic Capital — cross-layer verification tooling
```

---

Forensic Capital — [forensic-capital.com](https://forensic-capital.com)
