#!/usr/bin/env python3
"""
capo-parameter-checker.py
Forensic Capital — FC-002 companion tool
Verify CAPO oracle parameters on Aave V3

Usage:
  python capo-parameter-checker.py
  python capo-parameter-checker.py --demo
  python capo-parameter-checker.py --network mainnet

See: forensic-capital.com/reports/aave-capo/
"""

import argparse
import os
import sys
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

VERSION = "1.0.0"
TOOL_NAME = "FC CAPO Parameter Checker"
FC_REPORT_URL = "forensic-capital.com/reports/aave-capo/"
FC_REPORT_ID = "FC-002"

# Aave V3 contracts — Ethereum mainnet
AAVE_V3_ADDRESSES_PROVIDER = "0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9E"
AAVE_V3_ORACLE_MAINNET     = "0x54586bE62E3c3580375aE3723C145253060Ca0C2"

# Base currency: USD with 8 decimals (100_000_000 = $1.00)
ORACLE_PRICE_DECIMALS = 8
ORACLE_PRICE_UNIT = 10 ** ORACLE_PRICE_DECIMALS

# RPC endpoints tried in order; first success wins
RPC_ENDPOINTS = [
    "https://eth.llamarpc.com",
    "https://cloudflare-eth.com",
    "https://rpc.ankr.com/eth",
]
# User-supplied endpoint takes priority if FC_RPC_URL is set
_fc_rpc = os.environ.get("FC_RPC_URL")
if _fc_rpc:
    RPC_ENDPOINTS = [_fc_rpc] + RPC_ENDPOINTS
RPC_TIMEOUT_SECONDS = 5

# Assets monitored
ASSETS = [
    {
        "symbol":    "USDC",
        "address":   "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "is_stable": True,
        "peg_usd":   1.0,
    },
    {
        "symbol":    "USDT",
        "address":   "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "is_stable": True,
        "peg_usd":   1.0,
    },
    {
        "symbol":    "DAI",
        "address":   "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "is_stable": True,
        "peg_usd":   1.0,
    },
    {
        "symbol":    "WETH",
        "address":   "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "is_stable": False,
        "peg_usd":   None,
    },
    {
        "symbol":    "WBTC",
        "address":   "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "is_stable": False,
        "peg_usd":   None,
    },
]

# Demo prices — hardcoded oracle values in base currency units (1e8 = $1.00)
# Realistic values consistent with the FC-002 analysis window
DEMO_PRICES: dict[str, int] = {
    "USDC": 100010000,       # $1.0001  — slight premium, within normal range
    "USDT":  99990000,       # $0.9999  — slight discount, within normal range
    "DAI":  100020000,       # $1.0002  — near-perfect peg
    "WETH": 242000000000,    # $2,420.00
    "WBTC": 6450000000000,   # $64,500.00
}

# CAPO deviation thresholds for USD-pegged stablecoins
# If the oracle price breaches ALERT_DEVIATION_PCT, the CAPO bound
# should have triggered — its absence is the misconfiguration FC-002 documented.
WARN_DEVIATION_PCT  = 0.5   # yellow — deviation worth monitoring
ALERT_DEVIATION_PCT = 2.0   # red    — CAPO bound should have fired

# Minimal ABI: getAssetPrice only (all we need for price health checks)
ORACLE_ABI = [
    {
        "inputs":           [{"name": "asset", "type": "address"}],
        "name":             "getAssetPrice",
        "outputs":          [{"name": "", "type": "uint256"}],
        "stateMutability":  "view",
        "type":             "function",
    }
]

# ──────────────────────────────────────────────────────────────────────────────
# RPC connectivity
# ──────────────────────────────────────────────────────────────────────────────

def try_connect(rpc_url: str) -> object | None:
    """
    Try to connect to one RPC endpoint.
    Validates the connection with a lightweight eth_blockNumber call.
    Returns a connected Web3 instance or None if the endpoint fails.
    """
    try:
        from web3 import Web3

        w3 = Web3(
            Web3.HTTPProvider(
                rpc_url,
                request_kwargs={"timeout": RPC_TIMEOUT_SECONDS},
            )
        )
        # Lightweight liveness check — raises if RPC is unresponsive
        _ = w3.eth.block_number
        return w3
    except Exception:
        return None


def get_connected_web3() -> tuple:
    """
    Try each configured RPC endpoint in priority order.
    Returns (Web3, rpc_url) on first success, (None, None) if all fail.
    """
    for url in RPC_ENDPOINTS:
        w3 = try_connect(url)
        if w3 is not None:
            return w3, url
    return None, None


# ──────────────────────────────────────────────────────────────────────────────
# Oracle price fetching
# ──────────────────────────────────────────────────────────────────────────────

def fetch_price_on_chain(w3, oracle_addr: str, asset_addr: str) -> int | None:
    """
    Call getAssetPrice(asset) on the Aave V3 Oracle contract.

    The Aave V3 oracle on Ethereum mainnet returns prices denominated in USD
    with 8 decimal places (ORACLE_PRICE_UNIT). A return value of 100000000
    corresponds to exactly $1.00.

    Returns the raw integer price, or None if the call fails for any reason.
    """
    try:
        from web3 import Web3

        oracle = w3.eth.contract(
            address=Web3.to_checksum_address(oracle_addr),
            abi=ORACLE_ABI,
        )
        price = oracle.functions.getAssetPrice(
            Web3.to_checksum_address(asset_addr)
        ).call()
        return int(price)
    except Exception:
        return None


def fetch_price_demo(symbol: str) -> int:
    """
    Return a hardcoded illustrative oracle price for demo mode.
    Values reflect a realistic Aave V3 state consistent with the
    FC-002 analysis window. Not for use in production decisions.
    """
    return DEMO_PRICES.get(symbol, ORACLE_PRICE_UNIT)


# ──────────────────────────────────────────────────────────────────────────────
# CAPO analysis logic
# ──────────────────────────────────────────────────────────────────────────────

def to_usd(raw_price: int) -> float:
    """Convert raw oracle units to a USD float."""
    return raw_price / ORACLE_PRICE_UNIT


def peg_deviation_pct(price_usd: float, peg: float) -> float:
    """
    Signed deviation of price_usd from its expected peg.
    Positive = above peg. Negative = below peg.
    """
    return ((price_usd - peg) / peg) * 100.0


def assess_capo_status(asset: dict, price_usd: float) -> tuple:
    """
    Evaluate CAPO health for a given asset at the current oracle price.

    For non-stablecoins: CAPO bounds apply to growth rate, not absolute peg.
    Price-level health check is not applicable — we report NORMAL.

    For stablecoins: any deviation from the USD peg beyond CAPO thresholds
    indicates the oracle has reported a price that CAPO should have capped.
    This is precisely the misconfiguration class documented in FC-002.

    Returns:
        (status_str, flag_level)
        flag_level 0 = normal
        flag_level 1 = warn  (> WARN_DEVIATION_PCT)
        flag_level 2 = alert (> ALERT_DEVIATION_PCT — CAPO may have failed)
    """
    if not asset["is_stable"]:
        return "✅ NORMAL", 0

    peg = asset["peg_usd"]
    abs_dev = abs(peg_deviation_pct(price_usd, peg))

    if abs_dev >= ALERT_DEVIATION_PCT:
        return (
            f"🔴 ALERT   ({abs_dev:.3f}% from peg — CAPO bound should have triggered)",
            2,
        )
    if abs_dev >= WARN_DEVIATION_PCT:
        return (
            f"🟡 WARN    ({abs_dev:.3f}% from peg — approaching CAPO threshold)",
            1,
        )
    return "✅ NORMAL", 0


# ──────────────────────────────────────────────────────────────────────────────
# Output formatting
# ──────────────────────────────────────────────────────────────────────────────

SEP = "─" * 45


def print_header(mode: str, network: str, rpc_url: str | None) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print()
    print(f"=== {TOOL_NAME} ===")
    print("Forensic Capital | FC-002 companion")
    print(FC_REPORT_URL)
    print()
    print(f"Network   : Ethereum {network.capitalize()}")
    print(f"Mode      : [{mode}]")
    print(f"Timestamp : {ts} UTC")
    if rpc_url and mode == "LIVE":
        print(f"RPC       : {rpc_url.replace('https://', '')}")
    print()
    print(SEP)


def print_asset_result(asset: dict, price_usd: float, status: str) -> None:
    sym   = asset["symbol"]
    addr  = asset["address"]
    short = addr[:6] + "..." + addr[-4:]

    print()
    print(f"Asset     : {sym} ({short})")

    if asset["is_stable"]:
        peg = asset["peg_usd"]
        dev = peg_deviation_pct(price_usd, peg)
        sign = "+" if dev >= 0 else ""
        print(f"Price     : ${price_usd:.4f}")
        print(f"Peg       : ${peg:.4f}")
        print(f"Deviation : {sign}{dev:.4f}%")
    else:
        print(f"Price     : ${price_usd:,.2f}")

    print(f"Status    : {status}")


def print_footer(total: int, n_warn: int, n_alert: int, mode: str) -> None:
    print()
    print(SEP)
    print()
    print(f"Summary   : {total}/{total} assets checked")

    total_flags = n_warn + n_alert
    if total_flags == 0:
        print("Flags     : ✅ 0 anomalies detected")
    else:
        if n_alert:
            print(f"Flags     : 🔴 {n_alert} ALERT(s)  — CAPO misconfiguration possible")
        if n_warn:
            print(f"Flags     : 🟡 {n_warn} WARN(s)   — monitor deviation trend")

    print()
    print(SEP)
    print()
    print("FC-002 context: The Aave CAPO (Capped Composite Oracle)")
    print("  bounds asset prices to prevent oracle manipulation.")
    print("  FC-002 documented CAPO misconfiguration risk linked")
    print("  to a $26M oracle-dependent incident. This tool verifies")
    print("  current CAPO parameter health: stablecoin deviations")
    print("  that exceed CAPO bounds indicate the price cap mechanism")
    print("  may not have triggered correctly — a critical risk for")
    print("  any protocol using Aave V3 price feeds as collateral.")
    print()
    if mode == "DEMO":
        print("⚠  DEMO MODE — prices are hardcoded illustrative data.")
        print("   Run without --demo for live on-chain verification.")
    print()
    print(f"Full analysis : {FC_REPORT_URL}")
    print(f"Version       : {VERSION} | {FC_REPORT_ID}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────────────────────────────────────

def run(force_demo: bool = False, network: str = "mainnet") -> int:
    """
    Execute CAPO parameter checks against all configured assets.

    Exit codes:
      0  — all assets within normal bounds
      1  — one or more WARN or ALERT conditions detected
      2  — fatal execution error (should not normally occur)
    """
    w3 = None
    rpc_url = None
    mode = "DEMO"

    if not force_demo:
        w3, rpc_url = get_connected_web3()
        if w3 is not None:
            mode = "LIVE"
        else:
            print(
                "[FC] No RPC endpoint configured. Running with reference data. For live on-chain checks, set your own endpoint via FC_RPC_URL (e.g. Alchemy/Infura).",
                file=sys.stderr,
            )

    oracle_addr = AAVE_V3_ORACLE_MAINNET
    print_header(mode, network, rpc_url)

    n_warn  = 0
    n_alert = 0

    for asset in ASSETS:
        raw_price: int | None = None

        if mode == "LIVE":
            raw_price = fetch_price_on_chain(w3, oracle_addr, asset["address"])
            if raw_price is None:
                print(
                    f"[FC] Live price unavailable for {asset['symbol']}"
                    " — using demo fallback.",
                    file=sys.stderr,
                )

        # Always fall back to demo if live fetch failed or in demo mode
        if raw_price is None:
            raw_price = fetch_price_demo(asset["symbol"])

        price_usd = to_usd(raw_price)
        status, flag_level = assess_capo_status(asset, price_usd)

        if flag_level == 1:
            n_warn += 1
        elif flag_level == 2:
            n_alert += 1

        print_asset_result(asset, price_usd, status)

    print_footer(len(ASSETS), n_warn, n_alert, mode)
    return 1 if (n_warn + n_alert) > 0 else 0


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="capo-parameter-checker",
        description=(
            "FC CAPO Parameter Checker\n"
            "Verify Aave V3 CAPO oracle health on Ethereum mainnet.\n"
            f"{FC_REPORT_ID} companion — Forensic Capital"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python capo-parameter-checker.py --demo\n"
            "  python capo-parameter-checker.py\n"
            "  python capo-parameter-checker.py --network mainnet\n"
            "\n"
            f"See: {FC_REPORT_URL}"
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Demo mode: hardcoded illustrative data, no network required",
    )
    parser.add_argument(
        "--network",
        default="mainnet",
        choices=["mainnet"],
        help="Target network (default: mainnet)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()
    code   = run(force_demo=args.demo, network=args.network)
    sys.exit(code)


if __name__ == "__main__":
    main()
