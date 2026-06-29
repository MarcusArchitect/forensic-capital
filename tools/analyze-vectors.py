#!/usr/bin/env python3
"""
analyze-vectors.py — Forensic Capital
Vector category statistics from defi-incidents-2026.csv

Usage:
    python3 analyze-vectors.py              # console table
    python3 analyze-vectors.py --json       # write datasets/vector-stats.json
    python3 analyze-vectors.py --update     # alias for --json
    python3 analyze-vectors.py --demo       # demo mode (no CSV required)

Version: 1.0.0 | FC dataset companion
forensic-capital.com/defi/
"""

import csv
import json
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict

# ── paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.dirname(SCRIPT_DIR)
CSV_PATH    = os.path.join(REPO_ROOT, "datasets", "defi-incidents-2026.csv")
JSON_OUT    = os.path.join(REPO_ROOT, "datasets", "vector-stats.json")

# ── FC incident URLs ─────────────────────────────────────────────────────────
FC_REPORTS = {
    "KelpDAO":     "forensic-capital.com/the-kelpdao-exploit/",
    "Resolv":      "forensic-capital.com/reports/resolv/",
    "Verus_Bridge":"forensic-capital.com/reports/fc-004-verus/",
    "Gravity_Bridge":"forensic-capital.com/reports/fc-005-gravity/",
}

# ── demo data (hardcoded, always works) ──────────────────────────────────────
DEMO_ROWS = [
    {"date":"2022-02-02","protocol":"Wormhole",     "loss":321000000,"vector":"BRIDGE_VERIFICATION_GAP","fc":False},
    {"date":"2022-03-23","protocol":"Ronin_Bridge",  "loss":624000000,"vector":"CREDENTIAL_COMPROMISE",  "fc":False},
    {"date":"2022-08-01","protocol":"Nomad",         "loss":190700000,"vector":"BRIDGE_VERIFICATION_GAP","fc":False},
    {"date":"2022-10-07","protocol":"BNB_Chain_Bridge","loss":570000000,"vector":"BRIDGE_VERIFICATION_GAP","fc":False},
    {"date":"2023-03-13","protocol":"Euler_Finance", "loss":197000000,"vector":"FLASH_LOAN",             "fc":False},
    {"date":"2025-02-21","protocol":"Bybit",         "loss":1500000000,"vector":"ACCESS_CONTROL",        "fc":False},
    {"date":"2026-04-18","protocol":"KelpDAO",       "loss":292000000,"vector":"DVN_BRIDGE",             "fc":True},
    {"date":"2026-03-22","protocol":"Resolv",        "loss":25000000, "vector":"CREDENTIAL_COMPROMISE",  "fc":True},
    {"date":"2026-05-18","protocol":"Verus_Bridge",  "loss":11580000, "vector":"BRIDGE_VERIFICATION_GAP","fc":True},
    {"date":"2026-05-29","protocol":"Gravity_Bridge", "loss":5400000,  "vector":"BRIDGE_VERIFICATION_GAP","fc":True},
]

# ── helpers ───────────────────────────────────────────────────────────────────
def load_csv():
    rows = []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(r for r in f if not r.startswith("#"))
        for row in reader:
            rows.append({
                "date":     row["date"],
                "protocol": row["protocol"],
                "loss":     int(row["loss_usd"]),
                "vector":   row["vector_category"],
                "fc":       "forensic-capital.com" in row.get("source_primary",""),
            })
    return rows

def compute_stats(rows):
    total_loss  = sum(r["loss"] for r in rows)
    total_count = len(rows)
    vectors = defaultdict(lambda: {"count":0,"loss":0,"fc_protocols":[]})

    for r in rows:
        v = r["vector"]
        vectors[v]["count"] += 1
        vectors[v]["loss"]  += r["loss"]
        if r["fc"]:
            vectors[v]["fc_protocols"].append(r["protocol"])

    stats = []
    for v, d in sorted(vectors.items(), key=lambda x: -x[1]["loss"]):
        stats.append({
            "vector":       v,
            "count":        d["count"],
            "loss_usd":     d["loss"],
            "pct_count":    round(d["count"] / total_count * 100, 1),
            "pct_loss":     round(d["loss"]  / total_loss  * 100, 1),
            "fc_protocols": d["fc_protocols"],
        })
    return stats, total_loss, total_count

def fmt_usd(n):
    if n >= 1_000_000_000: return f"${n/1_000_000_000:.2f}B"
    if n >= 1_000_000:     return f"${n/1_000_000:.1f}M"
    return f"${n:,}"

def print_table(stats, total_loss, total_count, mode_label=""):
    LINE = "─" * 90
    print()
    print("=== FC Vector Analysis ===")
    print(f"Forensic Capital | defi-incidents-2026.csv{mode_label}")
    print(f"forensic-capital.com/defi/")
    print()
    print(f"Timestamp  : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Total      : {total_count} incidents / {fmt_usd(total_loss)}")
    print()
    print(LINE)
    print(f"{'VECTOR':<35} {'N':>4}  {'% N':>5}  {'LOSS':>12}  {'% $':>5}  FC")
    print(LINE)
    for s in stats:
        fc_tag = ", ".join(s["fc_protocols"]) if s["fc_protocols"] else "—"
        print(f"{s['vector']:<35} {s['count']:>4}  {s['pct_count']:>4.1f}%  "
              f"{fmt_usd(s['loss_usd']):>12}  {s['pct_loss']:>4.1f}%  {fc_tag}")
    print(LINE)
    print()

def write_json(stats, total_loss, total_count):
    out = {
        "generated":    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source":       "defi-incidents-2026.csv",
        "total_incidents": total_count,
        "total_loss_usd":  total_loss,
        "license":      "CC-BY-4.0",
        "fc_context":   "forensic-capital.com/defi/",
        "vectors":      stats,
    }
    with open(JSON_OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Written → {JSON_OUT}")
    return out

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    args      = sys.argv[1:]
    demo_mode = "--demo" in args
    json_mode = "--json" in args or "--update" in args

    if demo_mode:
        rows  = DEMO_ROWS
        label = " [DEMO]"
    else:
        try:
            rows  = load_csv()
            label = ""
        except FileNotFoundError:
            print(f"⚠  CSV not found at {CSV_PATH} — falling back to demo mode")
            rows  = DEMO_ROWS
            label = " [DEMO — CSV not found]"

    stats, total_loss, total_count = compute_stats(rows)
    print_table(stats, total_loss, total_count, label)

    if json_mode:
        write_json(stats, total_loss, total_count)

    # exit 1 if any vector has 0 incidents (sanity check)
    if total_count == 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
