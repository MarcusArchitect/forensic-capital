# FC Tools — Forensic Capital

Public companion tools for Forensic Capital incident reports.

---

## capo-parameter-checker.py

**FC-002 companion** — Verify Aave V3 CAPO oracle parameter health on Ethereum mainnet.

CAPO (Capped Composite Oracle) is the Aave V3 mechanism that bounds asset prices
to prevent oracle manipulation. FC-002 documented misconfiguration risk linked to
a $26M incident on oracle-dependent protocols.
Full analysis: [forensic-capital.com/reports/aave-capo/](https://forensic-capital.com/reports/aave-capo/)

### What it checks

For each of 5 Aave V3 assets (USDC, USDT, DAI, WETH, WBTC):

- Current oracle price via `getAssetPrice` on the Aave V3 Oracle contract
- USD deviation from peg for stablecoins
- Flag if deviation > 0.5% (WARN)
- Flag if deviation > 2.0% (ALERT — CAPO bound should have triggered)
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
python3 capo-parameter-checker.py --demo
```

**Live mode** (queries Ethereum mainnet):
```bash
python3 capo-parameter-checker.py
python3 capo-parameter-checker.py --network mainnet
```

Live mode tries 3 public RPC endpoints in order:
1. `eth.llamarpc.com`
2. `cloudflare-eth.com`
3. `rpc.ankr.com/eth`

If all fail, falls back to demo mode automatically.

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All assets within normal bounds |
| `1`  | One or more WARN or ALERT conditions detected |

### Output (demo mode — verified 2026-05-31)

```
=== FC CAPO Parameter Checker ===
Forensic Capital | FC-002 companion
forensic-capital.com/reports/aave-capo/

Network   : Ethereum Mainnet
Mode      : [DEMO]
Timestamp : 2026-05-31 16:33:19 UTC

─────────────────────────────────────────────

Asset     : USDC (0xA0b8...eB48)
Price     : $1.0001
Peg       : $1.0000
Deviation : +0.0100%
Status    : ✅ NORMAL

Asset     : USDT (0xdAC1...1ec7)
Price     : $0.9999
Peg       : $1.0000
Deviation : -0.0100%
Status    : ✅ NORMAL

Asset     : DAI (0x6B17...1d0F)
Price     : $1.0002
Peg       : $1.0000
Deviation : +0.0200%
Status    : ✅ NORMAL

Asset     : WETH (0xC02a...6Cc2)
Price     : $2,420.00
Status    : ✅ NORMAL

Asset     : WBTC (0x2260...C599)
Price     : $64,500.00
Status    : ✅ NORMAL

─────────────────────────────────────────────

Summary   : 5/5 assets checked
Flags     : ✅ 0 anomalies detected

─────────────────────────────────────────────

FC-002 context: The Aave CAPO (Capped Composite Oracle)
  bounds asset prices to prevent oracle manipulation.
  FC-002 documented CAPO misconfiguration risk linked
  to a $26M oracle-dependent incident. This tool verifies
  current CAPO parameter health: stablecoin deviations
  that exceed CAPO bounds indicate the price cap mechanism
  may not have triggered correctly — a critical risk for
  any protocol using Aave V3 price feeds as collateral.

⚠  DEMO MODE — prices are hardcoded illustrative data.
   Run without --demo for live on-chain verification.

Full analysis : forensic-capital.com/reports/aave-capo/
Version       : 1.0.0 | FC-002
```

### Contracts queried

| Contract | Address |
|----------|---------|
| Aave V3 Addresses Provider | `0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9E` |
| Aave V3 Oracle (mainnet)   | `0x54586bE62E3c3580375aE3723C145253060Ca0C2` |

### Assets monitored

| Symbol | Address | Type |
|--------|---------|------|
| USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | Stablecoin |
| USDT | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | Stablecoin |
| DAI  | `0x6B175474E89094C44Da98b954EedeAC495271d0F` | Stablecoin |
| WETH | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | Volatile |
| WBTC | `0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` | Volatile |

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

### Output (live mode — 42 incidents)

```
=== FC Vector Analysis ===
Forensic Capital | defi-incidents-2026.csv
forensic-capital.com/defi/

Total      : 42 incidents / $6.15B

──────────────────────────────────────────────────────────────────────────
VECTOR                                 N    % N          LOSS    % $  FC
──────────────────────────────────────────────────────────────────────────
ACCESS_CONTROL                        14  33.3%        $2.15B  35.0%  —
BRIDGE_VERIFICATION_GAP                5  11.9%        $1.70B  27.7%  —
CREDENTIAL_COMPROMISE                  8  19.0%        $1.22B  19.8%  —
FLASH_LOAN                             4   9.5%       $376.2M   6.1%  —
DVN_BRIDGE                             1   2.4%       $292.0M   4.7%  KelpDAO
GOVERNANCE                             1   2.4%       $182.0M   3.0%  —
PRICE_MANIPULATION                     6  14.3%       $102.6M   1.7%  —
REENTRANCY                             2   4.8%       $100.5M   1.6%  —
ORACLE_MISCONFIGURATION                1   2.4%        $26.0M   0.4%  Aave
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

Forensic Capital — [forensic-capital.com](https://forensic-capital.com)
