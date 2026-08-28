"""Import the exact KEEL-style benchmark files archived by MC-CCR authors."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def import_dat(path: Path, output_root: Path) -> dict:
    inputs, outputs = [], []
    metadata_lines = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("@"):
                break
            metadata_lines += 1
            lowered = line.lower()
            if lowered.startswith("@input"):
                inputs = [item.strip() for item in line[6:].strip().split(",")]
            elif lowered.startswith("@output"):
                outputs = [item.strip() for item in line[7:].strip().split(",")]
    frame = pd.read_csv(path, skiprows=metadata_lines, header=None, skipinitialspace=True)
    if inputs and outputs and len(inputs) + len(outputs) == frame.shape[1]:
        frame.columns = inputs + outputs
        X = pd.get_dummies(frame[inputs], dtype=float)
        y = frame[outputs[0]].astype(str)
    else:
        X = pd.get_dummies(frame.iloc[:, :-1], dtype=float)
        y = frame.iloc[:, -1].astype(str)
    name = path.stem.replace("-full", "")
    target = output_root / name
    target.mkdir(parents=True, exist_ok=True)
    csv_path = target / "benchmark.csv"
    X.assign(target=y.to_numpy()).to_csv(csv_path, index=False)
    counts = y.value_counts().to_dict()
    digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    report = {"name": name, "source": str(path.resolve()), "rows": len(X),
              "features_after_one_hot": X.shape[1], "classes": len(counts),
              "class_distribution": {str(k): int(v) for k, v in counts.items()},
              "imbalance_ratio": float(max(counts.values()) / min(counts.values())),
              "benchmark_sha256": digest}
    (target / "metadata.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reports = []
    for path in sorted(args.source.glob("*-full.dat")):
        report = import_dat(path, args.output)
        reports.append(report)
        print(f"{report['name']}: n={report['rows']} d={report['features_after_one_hot']} C={report['classes']}")
    (args.output / "manifest.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

