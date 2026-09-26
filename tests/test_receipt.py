import json
from pathlib import Path

from littleworld.experiment import frozen_gate, summarize


def test_committed_v0_receipt_matches_frozen_gate():
    receipt = json.loads(Path("results/v0.json").read_text())
    assert receipt["panel"]["seeds"] == list(range(200, 212))
    summary = summarize(receipt["panel"])
    assert summary == receipt["summary"]
    assert frozen_gate(summary) == receipt["gate"]
    assert receipt["gate"]["pass"] is True
