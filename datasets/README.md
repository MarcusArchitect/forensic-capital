# Datasets

## defi-incidents-2026.csv

DeFi incident database, 2026.
40+ verified incidents.

### Schema
date, protocol, chain, loss_usd,
vector_category, root_cause,
post_mortem_url, recovery_status

### Sources
Rekt News, official post-mortems,
CertiK, Chainalysis, DefiLlama,
Blockaid, SlowMist, PeckShield.

### License
CC-BY-4.0

### Disclaimer
Aggregated from public post-mortems.
No private data. No attribution
beyond public sources.
status field: resolved / partial /
unresolved / ongoing

---

## vector-stats.json *(generated — not in repo)*

`vector-stats.json` is a build artifact generated from `defi-incidents-2026.csv`.
It is listed in `.gitignore` and is not committed to the repository.

**Regenerate:**
```bash
python3 tools/analyze-vectors.py --update
```

Output: `datasets/vector-stats.json` (42 incidents, 9 vectors, CC-BY-4.0).

---

## dvn-operator-registry.json

Public registry of known LayerZero DVN operators.
10 operators documented from official LayerZero docs,
Etherscan, and public announcements.

### Schema

Each operator entry includes:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier |
| `name` | Operator display name |
| `entity` | Legal entity name |
| `custody_level` | L0–L3 (see below) |
| `address_mainnet` | Ethereum mainnet address (if public) |
| `verified_etherscan` | Address independently verified |
| `source` | Public source URL |
| `confidence` | `verified` / `inferred` / `unknown` — epistemological status of entry |
| `confidence_note` | Explanation of confidence classification |
| `fc_risk_note` | FC risk assessment note |

### Custody levels

| Level | Definition |
|-------|-----------|
| L0 | Protocol team / founding entity — single key custodian |
| L1 | Single independent entity — corporate/institutional |
| L2 | Multi-sig or threshold signing — distributed known parties |
| L3 | ZK-proof / cryptographic — minimal trust assumptions |

### Coverage

10 operators: L0×1 / L1×7 / L2×1 / L3×1
4 addresses independently verified on Etherscan.
Confidence: verified×4 / inferred×4 / unknown×2

### FC context

FC-001 KelpDAO ($292M): `requiredDVNCount = 1` with an L0 operator
created a single point of failure. Any L0 or L1 operator in a 1-of-1
configuration reproduces this attack surface.
Full analysis: forensic-capital.com/the-kelpdao-exploit/

### License
CC-BY-4.0

### Sources
LayerZero V2 docs, LayerZero ecosystem page,
Etherscan, Google Cloud blog.
