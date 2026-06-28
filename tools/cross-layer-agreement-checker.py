#!/usr/bin/env python3
"""
cross-layer-agreement-checker.py
Forensic Capital — cross-layer verification tooling
Detect cross-layer asset identity disagreement in dual-verification bridge architectures

Applies to any dual-verification bridge architecture, including relay-proof
and zk-light-client designs.

Usage:
  python cross-layer-agreement-checker.py --demo
  python cross-layer-agreement-checker.py

See: forensic-capital.com
"""

# ──────────────────────────────────────────────────────────────────────────────
# Security principle: "ambiguous proofs must fail closed"
#
# Fail-safe defaults (Saltzer & Schroeder, 1975 — "The Protection of
# Information in Computer Systems", Proceedings of the IEEE): when the
# correct resolution is ambiguous, access decisions must default to denial.
#
# Applied to dual-verification bridge architectures: a payload that two
# independent layers resolve to different identities, or that carries more
# than one valid identity, cannot be safely processed. The only conservative
# response is REJECT — fail closed. Permitting ambiguous proofs to pass
# collapses the security guarantee of the second verification layer entirely.
# ──────────────────────────────────────────────────────────────────────────────

import argparse
import sys
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

VERSION    = "1.0.0"
TOOL_NAME  = "FC Cross-Layer Agreement Checker"
TOOL_LABEL = "Forensic Capital — cross-layer verification tooling"
FC_URL     = "forensic-capital.com"

# ──────────────────────────────────────────────────────────────────────────────
# Core verification logic
# ──────────────────────────────────────────────────────────────────────────────

# Failure reason codes returned alongside REJECT verdicts
REASON_VACUOUS_PROOF       = "vacuous_proof"        # identity_count == 0
REASON_MULTIPLE_IDENTITIES = "multiple_identities"  # identity_count > 1
REASON_LAYER_DISAGREEMENT  = "layer_disagreement"   # a != b, count == 1


def check_agreement(
    resolution_layer_a: str | None,
    resolution_layer_b: str | None,
    identity_count: int,
) -> tuple[str, str | None]:
    """
    Verify cross-layer identity agreement for a bridge payload.

    A payload is safe to process (PASS) only when:
      1. Exactly one identity is present (identity_count == 1)
      2. Both independent verification layers resolve to the same identity

    Any deviation produces REJECT with a precise failure reason:
      vacuous_proof       — identity_count == 0: no identity present; proof is vacuous
      multiple_identities — identity_count > 1: payload is ambiguous
      layer_disagreement  — identity_count == 1 but layer A and layer B disagree

    Edge cases handled:
      identity_count == 0 : REJECT with vacuous_proof
      identity_count > 1  : REJECT with multiple_identities
      None input          : treated as unresolved → triggers layer_disagreement
      empty string input  : normalised to None → triggers layer_disagreement

    Args:
        resolution_layer_a: Identity string resolved by verification layer A.
        resolution_layer_b: Identity string resolved by verification layer B.
        identity_count:     Number of distinct identities the payload encodes.

    Returns:
        (verdict, reason)
        verdict : "PASS" or "REJECT — fail closed required"
        reason  : None on PASS;
                  one of REASON_VACUOUS_PROOF, REASON_MULTIPLE_IDENTITIES,
                  or REASON_LAYER_DISAGREEMENT on REJECT
    """
    # Normalise: treat None and empty string as unresolved
    a: str | None = resolution_layer_a if resolution_layer_a else None
    b: str | None = resolution_layer_b if resolution_layer_b else None

    # Rule 1a: vacuous proof — payload carries no identity at all
    if identity_count == 0:
        return "REJECT — fail closed required", REASON_VACUOUS_PROOF

    # Rule 1b: ambiguous proof — payload carries more than one identity
    if identity_count > 1:
        return "REJECT — fail closed required", REASON_MULTIPLE_IDENTITIES

    # Rule 2: both layers must agree on that single identity
    if a != b:
        return "REJECT — fail closed required", REASON_LAYER_DISAGREEMENT

    return "PASS", None


# ──────────────────────────────────────────────────────────────────────────────
# Demo scenarios — synthetic, generic, no external dependencies
# Each case exercises one distinct branch of the verification logic.
# ──────────────────────────────────────────────────────────────────────────────

DEMO_CASES: list[dict] = [
    {
        "label":               "Perfect agreement",
        "description":         "Both layers resolve to the same identity; payload is unambiguous",
        "resolution_layer_a":  "asset_alpha",
        "resolution_layer_b":  "asset_alpha",
        "identity_count":      1,
    },
    {
        "label":               "Layer disagreement",
        "description":         "Layer A and Layer B resolve to different identities from the same payload",
        "resolution_layer_a":  "asset_alpha",
        "resolution_layer_b":  "asset_beta",
        "identity_count":      1,
    },
    {
        "label":               "Dual-identity payload",
        "description":         "Payload encodes two valid identities — ambiguous proof, cannot be trusted",
        "resolution_layer_a":  "asset_alpha",
        "resolution_layer_b":  "asset_alpha",
        "identity_count":      2,
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Output formatting
# ──────────────────────────────────────────────────────────────────────────────

SEP = "─" * 45


def print_header(mode: str) -> None:
    """Print standard FC tool header."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    print()
    print(f"=== {TOOL_NAME} ===")
    print("Forensic Capital | cross-layer verification tooling")
    print(FC_URL)
    print()
    print(f"Mode      : [{mode}]")
    print(f"Timestamp : {ts} UTC")
    print()
    print(SEP)


def print_case_result(
    case: dict,
    verdict: str,
    reason: str | None,
) -> None:
    """Print the formatted result for a single verification case."""
    is_pass = verdict == "PASS"
    verdict_display = "✅ PASS" if is_pass else "🔴 REJECT"

    a_display = case["resolution_layer_a"] or "(unresolved)"
    b_display = case["resolution_layer_b"] or "(unresolved)"

    print()
    print(f"Case      : {case['label']}")
    print(f"Desc      : {case['description']}")
    print(f"Layer A   : {a_display}")
    print(f"Layer B   : {b_display}")
    print(f"Identities: {case['identity_count']}")
    print(f"Verdict   : {verdict_display}")
    if reason:
        print(f"Reason    : {reason}")
    print()
    print(SEP)


def print_footer(n_pass: int, n_reject: int, mode: str) -> None:
    """Print summary, security context, and mode disclaimer."""
    total = n_pass + n_reject
    print()
    print(f"Summary   : {n_pass} PASS / {n_reject} REJECT  ({total} cases)")

    if n_reject == 0:
        print("Flags     : ✅ 0 anomalies detected")
    else:
        print(f"Flags     : 🔴 {n_reject} REJECT(s) — fail-closed enforcement required")

    print()
    print(SEP)
    print()
    print("Security principle: ambiguous proofs must fail closed.")
    print("  In dual-verification bridge architectures, a payload")
    print("  that two independent layers resolve differently — or")
    print("  that encodes more than one valid identity — cannot be")
    print("  safely processed. REJECT is the only conservative")
    print("  response. Applies to relay-proof and zk-light-client")
    print("  designs alike. Permitting ambiguous proofs to pass")
    print("  collapses the guarantee of dual verification entirely.")
    print()
    if mode == "DEMO":
        print("⚠  DEMO MODE — scenarios are hardcoded illustrative data.")
        print("   Integrate check_agreement() with your bridge resolver")
        print("   to verify live payloads.")
        if n_reject > 0:
            plural = "s" if n_reject != 1 else ""
            print(f"   Production behavior: the {n_reject} REJECT case{plural} above return exit 1 outside --demo.")
    print()
    print(f"Forensic Capital : {FC_URL}")
    print(f"Version          : {VERSION} | {TOOL_LABEL}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────────────────────────────────────

def run(force_demo: bool = False) -> int:
    """
    Execute cross-layer agreement checks against all configured cases.

    --demo always exits 0 (it demonstrates detection on fixtures);
    production run() exits 1 on any REJECT.

    In demo mode: evaluates 3 synthetic scenarios covering the PASS case,
    layer disagreement, and a dual-identity payload.

    Exit codes:
      0  — all cases passed; or --demo regardless of findings
      1  — one or more REJECT conditions detected (production only)
    """
    mode = "DEMO"
    print_header(mode)

    n_pass   = 0
    n_reject = 0

    for case in DEMO_CASES:
        verdict, reason = check_agreement(
            resolution_layer_a=case["resolution_layer_a"],
            resolution_layer_b=case["resolution_layer_b"],
            identity_count=case["identity_count"],
        )

        if verdict == "PASS":
            n_pass += 1
        else:
            n_reject += 1

        print_case_result(case, verdict, reason)

    print_footer(n_pass, n_reject, mode)

    if force_demo:
        # Demo mode exits 0 — demonstrates detection capability, not a live finding
        return 0
    return 1 if n_reject > 0 else 0


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="cross-layer-agreement-checker",
        description=(
            "FC Cross-Layer Agreement Checker\n"
            "Detect asset identity disagreement across dual-verification bridge layers.\n"
            "cross-layer verification tooling — Forensic Capital"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cross-layer-agreement-checker.py --demo\n"
            "  python cross-layer-agreement-checker.py\n"
            "\n"
            f"See: {FC_URL}"
        ),
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Demo mode: 3 synthetic scenarios, no network required",
    )
    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args   = parser.parse_args()
    code   = run(force_demo=args.demo)
    sys.exit(code)


if __name__ == "__main__":
    main()
