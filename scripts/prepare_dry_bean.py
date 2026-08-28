"""Import the official UCI Dry Bean archive into the benchmark layout."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from scipy.io import arff


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    member = "DryBeanDataset/Dry_Bean_Dataset.arff"
    with ZipFile(args.archive) as archive:
        names = archive.namelist()
        if member not in names:
            raise ValueError(f"missing expected official member {member!r}")
        with archive.open(member) as binary_handle:
            with io.TextIOWrapper(binary_handle, encoding="utf-8") as text_handle:
                records, _ = arff.loadarff(text_handle)

    frame = pd.DataFrame(records)
    if "Class" not in frame:
        raise ValueError("ARFF does not contain the expected Class target")
    frame["Class"] = frame["Class"].map(
        lambda value: value.decode("utf-8") if isinstance(value, bytes) else str(value)
    )
    frame = frame.rename(columns={"Class": "target"})
    if frame.isna().any().any():
        raise ValueError("official Dry Bean data unexpectedly contain missing values")

    args.output.mkdir(parents=True, exist_ok=True)
    csv_path = args.output / "benchmark.csv"
    frame.to_csv(csv_path, index=False)
    counts = frame["target"].value_counts()
    metadata = {
        "name": "dry_bean",
        "uci_id": 602,
        "doi": "10.24432/C50S4B",
        "source_url": "https://archive.ics.uci.edu/dataset/602/dry",
        "archive_path": str(args.archive.resolve()),
        "archive_sha256": sha256(args.archive),
        "archive_member": member,
        "benchmark_sha256": sha256(csv_path),
        "rows": int(len(frame)),
        "features": int(frame.shape[1] - 1),
        "classes": int(counts.size),
        "class_distribution": {str(k): int(v) for k, v in counts.items()},
        "min_class": int(counts.min()),
        "max_class": int(counts.max()),
        "imbalance_ratio": float(counts.max() / counts.min()),
        "missing_values": 0,
        "license": "CC BY 4.0",
    }
    (args.output / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
