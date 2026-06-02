#!/usr/bin/env python3
"""
dvn-config-checker.py
Forensic Capital — FC-001 companion tool
Verify LayerZero V2 DVN configuration health on Ethereum mainnet

Usage:
  python dvn-config-checker.py
  python dvn-config-checker.py --demo
  python dvn-config-checker.py --network mainnet

DVN (Decentralized Verification Network) threshold misconfiguration
is the root cause of the KelpDAO FC-001 incident ($292M, 2026-04-18).
This tool checks the requiredDVNCount and optionalDVNCount parameters
against the FC risk scoring model.

See: forensic-capital.com/the-kelpdao-exploit/
"""

import argparse
import os
import sys
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

VERSION = "1.0.0"
TOOL_NAME = "FC DVN Config Checker"
FC_REPORT_URL = "forensic-capital.com/the-kelpdao-exploit/"
FC_REPORT_ID = "FC-001"

# LayerZero V2 Endpoint — Ethereum mainnet
# Source: LayerZero official docs + on-chain verification
LZ_ENDPOINT_V2_MAINNET = "0x1a44076050125825900e736c501f859c50fE728C"

# Known SendUln302 library address (LayerZero V2 mainnet)
# Used as the lib parameter when querying UlnConfig
LZ_SEND_LIB_302 = "0xbB2Ea70C9E858123480642Cf96acbcce1372dCe1"

# OApp examples for live demo (well-known LayerZero integrations)
# Only used in live mode when --oapp flag is provided
EXAMPLE_OAPPS = {
    "stargate_usdc": "0xc026395860Db2d07ee33e05fE50ed7bD583189C7",
}

# Destination EID — Ethereum mainnet is 30101 in LZ V2
DEST_EID_ETH_MAINNET = 30101

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

# Minimal ABI for getUlnConfig
ENDPOINT_ABI = [
    {
        "inputs": [
            {"name": "oapp", "type": "address"},
            {"name": "lib",  "type": "address"},
            {"name": "eid",  "type": "uint32"},
        ],
        "name": "getUlnConfig",
        "outputs": [
            {
                "components": [
                    {"name": "confirmations",          "type": "uint64"},
                    {"name": "requiredDVNCount",        "type": "uint8"},
                    {"name": "optionalDVNCount",        "type": "uint8"},
                    {"name": "optionalDVNThreshold",    "type": "uint8"},
                    {"name": "requiredDVNs",            "type": "address[]"},
                    {"name": "optionalDVNs",            "type": "address[]"},
                ],
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

# ──────────────────────────────────────────────────────────────────────────────
# Demo configurations — hardcoded realistic data
# Reflect the FC-001 KelpDAO attack surface and comparable configurations.
# Not for production decisions.
# ──────────────────────────────────────────────────────────────────────────────

DEMO_CONFIGS = [
    {
        "label": "KelpDAO-style",
        "description": "1-of-1 configuration — FC-001 attack pattern",
        "confirmations": 15,
        "requiredDVNCount": 1,
        "optionalDVNCount": 0,
        "optionalDVNThreshold": 0,
        "requiredDVNs": ["0xfd6865c841c2d64565562fCc7e05e619A30615f0"],
        "optionalDVNs": [],
    },
    {
        "label": "Standard Bridge",
        "description": "3-of-5 multi-party configuration — industry baseline",
        "confirmations": 15,
        "requiredDVNCount": 3,
        "optionalDVNCount": 2,
        "optionalDVNThreshold": 1,
        "requiredDVNs": [
            "0x589dEDbD617e0CBcB916A9223F4d1300c294236b",  # LayerZero Labs DVN
            "0x8Fbb3ce4F61E4d974a73636bc48AF0dbFC7a35A4",  # Google Cloud DVN
            "0x9bdf3aE7E2e3D211811E5444177d9808BcC17b38",  # Nethermind DVN
        ],
        "optionalDVNs": [
            "0xA09dB5142654e3eB5Cf547D66833FAe7097B21C3",
            "0xc097ab8CD7b053326DFe9fB3E3a31a0CCe3B526f",
        ],
    },
    {
        "label": "Minimal Threshold",
        "description": "2-of-6 — low threshold relative to DVN pool size",
        "confirmations": 12,
        "requiredDVNCount": 2,
        "optionalDVNCount": 4,
        "optionalDVNThreshold": 1,
        "requiredDVNs": [
            "0x589dEDbD617e0CBcB916A9223F4d1300c294236b",
            "0x8Fbb3ce4F61E4d974a73636bc48AF0dbFC7a35A4",
        ],
        "optionalDVNs": [
            "0x9bdf3aE7E2e3D211811E5444177d9808BcC17b38",
            "0xA09dB5142654e3eB5Cf547D66833FAe7097B21C3",
            "0xc097ab8CD7b053326DFe9fB3E3a31a0CCe3B526f",
            "0xE70C6291BF97fF8C05A20537A4eC17C540e461e4",
        ],
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Risk scoring model
# ──────────────────────────────────────────────────────────────────────────────

# Thresholds: percentage of required DVNs over total DVN pool
RISK_CRITICAL_THRESHOLD = 33.0   # < 33% OR requiredDVNCount = 1
RISK_HIGH_THRESHOLD     = 50.0   # 33–50%
RISK_MEDIUM_THRESHOLD   = 75.0   # 51–75%
# > 75% = ACCEPTABLE


def compute_risk(required: int, optional: int) -> tuple:
    """
    Evaluate DVN configuration risk based on threshold ratio.

    The effective security of a DVN set depends on:
    1. The absolute count of required DVNs (single point of failure check)
    2. The ratio of required DVNs to total DVN pool (proportional threshold)

    Returns:
        (risk_label, flag_level, reason, ratio_pct)
        flag_level 0 = acceptable
        flag_level 1 = medium
        flag_level 2 = high
        flag_level 3 = critical
    """
    total = required + optional

    # Single point of failure — always critical regardless of ratio
    if required == 1:
        return (
            "🔴 CRITICAL",
            3,
            "1-of-1 = FC-001 pattern — single DVN controls bridge security",
            100.0 if total == 1 else (100.0 / total),
        )

    if total == 0:
        return ("🔴 CRITICAL", 3, "No DVNs configured", 0.0)

    ratio = (required / total) * 100.0

    if ratio < RISK_CRITICAL_THRESHOLD:
        return (
            "🔴 CRITICAL",
            3,
            f"Threshold {required}/{total} = {ratio:.0f}% — attacker needs only {required} DVN(s)",
            ratio,
        )
    if ratio <= RISK_HIGH_THRESHOLD:
        return (
            "🟠 HIGH",
            2,
            f"Threshold {required}/{total} = {ratio:.0f}% — below 50% majority",
            ratio,
        )
    if ratio <= RISK_MEDIUM_THRESHOLD:
        return (
            "🟡 MEDIUM",
            1,
            f"Threshold {required}/{total} = {ratio:.0f}% — majority but below 75%",
            ratio,
        )
    return (
        "✅ ACCEPTABLE",
        0,
        f"Threshold {required}/{total} = {ratio:.0f}% — strong majority",
        ratio,
    )


# ──────────────────────────────────────────────────────────────────────────────
# RPC connectivity
# ──────────────────────────────────────────────────────────────────────────────

def try_connect(rpc_url: str):
    """
    Attempt connection to one RPC endpoint.
    Validates with a lightweight eth_blockNumber call.
    Returns a connected Web3 instance or None.
    """
    try:
        from web3 import Web3

        w3 = Web3(
            Web3.HTTPProvider(
                rpc_url,
                request_kwargs={"timeout": RPC_TIMEOUT_SECONDS},
            )
        )
        _ = w3.eth.block_number  # liveness check — raises if unresponsive
        return w3
    except Exception:
        return None


def get_connected_web3():
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
# On-chain DVN config fetching
# ──────────────────────────────────────────────────────────────────────────────

def fetch_uln_config_on_chain(w3, oapp_addr: str, eid: int) -> dict | None:
    """
    Call getUlnConfig(oapp, lib, eid) on the LayerZero V2 Endpoint.

    Returns a dict with the UlnConfig fields, or None on failure.
    """
    try:
        from web3 import Web3

        endpoint = w3.eth.contract(
            address=Web3.to_checksum_address(LZ_ENDPOINT_V2_MAINNET),
            abi=ENDPOINT_ABI,
        )
        result = endpoint.functions.getUlnConfig(
            Web3.to_checksum_address(oapp_addr),
            Web3.to_checksum_address(LZ_SEND_LIB_302),
            eid,
        ).call()

        # result is a tuple matching UlnConfig struct order
        return {
            "confirmations":        result[0],
            "requiredDVNCount":     result[1],
            "optionalDVNCount":     result[2],
            "optionalDVNThreshold": result[3],
            "requiredDVNs":         list(result[4]),
            "optionalDVNs":         list(result[5]),
        }
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Output formatting
# ──────────────────────────────────────────────────────────────────────────────

SEP = "─" * 45


def print_header(mode: str, network: str, rpc_url: str | None) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    print()
    print(f"=== {TOOL_NAME} ===")
    print(f"Forensic Capital | {FC_REPORT_ID} companion")
    print(FC_REPORT_URL)
    print()
    print(f"Network   : Ethereum {network.capitalize()}")
    print(f"Mode      : [{mode}]")
    print(f"Timestamp : {ts} UTC")
    if rpc_url and mode == "LIVE":
        print(f"RPC       : {rpc_url.replace('https://', '')}")
    print()
    print(SEP)


def print_config_result(cfg: dict, risk: str, flag: int, reason: str, ratio: float) -> None:
    label   = cfg["label"]
    req     = cfg["requiredDVNCount"]
    opt     = cfg["optionalDVNCount"]
    total   = req + opt
    confs   = cfg["confirmations"]
    descr   = cfg["description"]

    print()
    print(f"Config    : {label}")
    print(f"Desc      : {descr}")
    print(f"Required  : {req} DVN{'s' if req != 1 else ''}")
    print(f"Optional  : {opt} DVN{'s' if opt != 1 else ''}")

    if total > 0:
        print(f"Threshold : {req}/{total} = {ratio:.0f}% required")
    else:
        print("Threshold : N/A — no DVNs")

    if req == 1 and total == 1:
        print("            BUT single point of failure")
    elif req == 1:
        print(f"            BUT {req}-of-{total} = 1 DVN can approve alone")

    print(f"Confirms  : {confs} blocks")
    print(f"Risk      : {risk}")
    print(f"Reason    : {reason}")
    print()
    print(SEP)


def print_footer(n_critical: int, n_high: int, n_medium: int, n_ok: int, mode: str) -> None:
    total = n_critical + n_high + n_medium + n_ok
    print()
    print(f"Summary   : {total}/{total} configs checked")

    flags = n_critical + n_high + n_medium
    if flags == 0:
        print("Flags     : ✅ 0 anomalies detected")
    else:
        if n_critical:
            print(f"Flags     : 🔴 {n_critical} CRITICAL — immediate review required")
        if n_high:
            print(f"            🟠 {n_high} HIGH     — threshold below 50%")
        if n_medium:
            print(f"            🟡 {n_medium} MEDIUM   — monitor threshold trend")

    print()
    print(SEP)
    print()
    print(f"FC-001 context: KelpDAO ($292M, 2026-04-18) demonstrated")
    print(f"  that a requiredDVNCount of 1 allows a single compromised")
    print(f"  DVN to approve fraudulent cross-chain messages unilaterally.")
    print(f"  A valid DVN configuration requires ≥ 3 required DVNs")
    print(f"  with a threshold ratio > 50% of the total DVN pool.")
    print()
    if mode == "DEMO":
        print("⚠  DEMO MODE — configurations are hardcoded illustrative data.")
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
    Execute DVN configuration checks.

    In demo mode: evaluates 3 hardcoded representative configurations.
    In live mode: attempts on-chain read for EXAMPLE_OAPPS; falls back to demo.

    Exit codes:
      0  — all configurations within acceptable bounds
      1  — one or more MEDIUM, HIGH, or CRITICAL conditions detected
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

    print_header(mode, network, rpc_url)

    configs_to_check = list(DEMO_CONFIGS)

    # In live mode, attempt on-chain reads for known OApps
    if mode == "LIVE":
        live_configs = []
        for name, oapp_addr in EXAMPLE_OAPPS.items():
            cfg_on_chain = fetch_uln_config_on_chain(w3, oapp_addr, DEST_EID_ETH_MAINNET)
            if cfg_on_chain:
                cfg_on_chain["label"]       = f"Live: {name}"
                cfg_on_chain["description"] = f"On-chain config for {oapp_addr[:10]}..."
                live_configs.append(cfg_on_chain)
            else:
                print(
                    f"[FC] Live config unavailable for {name} — using demo fallback.",
                    file=sys.stderr,
                )

        if live_configs:
            configs_to_check = live_configs
        else:
            print(
                "[FC] All live reads failed — using demo configurations.",
                file=sys.stderr,
            )

    n_critical = 0
    n_high     = 0
    n_medium   = 0
    n_ok       = 0

    for cfg in configs_to_check:
        req  = cfg["requiredDVNCount"]
        opt  = cfg["optionalDVNCount"]

        risk, flag, reason, ratio = compute_risk(req, opt)

        if flag == 3:
            n_critical += 1
        elif flag == 2:
            n_high += 1
        elif flag == 1:
            n_medium += 1
        else:
            n_ok += 1

        print_config_result(cfg, risk, flag, reason, ratio)

    print_footer(n_critical, n_high, n_medium, n_ok, mode)
    if force_demo:
        return 0  # Demo mode exits 0 — demonstrates detection capability, not a live finding
    return 1 if (n_critical + n_high + n_medium) > 0 else 0


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dvn-config-checker",
        description=(
            "FC DVN Config Checker\n"
            "Verify LayerZero V2 DVN configuration health on Ethereum mainnet.\n"
            f"{FC_REPORT_ID} companion — Forensic Capital"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python dvn-config-checker.py --demo\n"
            "  python dvn-config-checker.py\n"
            "  python dvn-config-checker.py --network mainnet\n"
            "\n"
            f"See: {FC_REPORT_URL}"
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Demo mode: hardcoded illustrative configs, no network required",
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
