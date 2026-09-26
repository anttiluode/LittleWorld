#!/usr/bin/env python3
"""Run the frozen LittleWorld v0 panel and write a machine-readable receipt."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from littleworld.experiment import Config, frozen_gate, run_panel, summarize


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-start", type=int, default=200)
    parser.add_argument("--seeds", type=int, default=12)
    parser.add_argument("--out", type=Path, default=Path("results/v0.json"))
    args = parser.parse_args()

    panel = run_panel(range(args.seed_start, args.seed_start + args.seeds), Config())
    summary = summarize(panel)
    receipt = {
        "experiment": "littleworld-v0-marked-event-coupling",
        "claim_boundary": (
            "constructed proof-of-mechanism: state-dependent marked sender events "
            "plus receiver memory improve hidden-world prediction under matched event budgets"
        ),
        "panel": panel,
        "summary": summary,
        "gate": frozen_gate(summary),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"summary": summary, "gate": receipt["gate"]}, indent=2))
    return 0 if receipt["gate"]["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
