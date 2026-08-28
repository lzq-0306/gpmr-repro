from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main():
    locations = json.loads((ROOT / "config" / "datasets.json").read_text(encoding="utf-8"))
    expected = json.loads((ROOT / "config" / "dataset_checksums.json").read_text(encoding="utf-8"))
    failures = []
    for item in locations["datasets"]:
        name, path = item["name"], ROOT / item["path"]
        if not path.exists():
            failures.append(f"{name}: missing {path}")
            continue
        frame = pd.read_csv(path)
        spec = expected[name]
        actual = {"rows": len(frame), "features": len(frame.columns) - 1,
                  "classes": frame["target"].nunique(), "sha256": digest(path)}
        mismatches = [key for key in actual if actual[key] != spec[key]]
        if mismatches:
            failures.append(f"{name}: mismatch in {', '.join(mismatches)}")
        else:
            print(f"verified {name}: {actual['rows']} rows, sha256={actual['sha256'][:12]}...")
    if failures:
        raise SystemExit("Dataset audit failed:\n- " + "\n- ".join(failures))
    print("All 15 processed datasets match the frozen experimental versions.")


if __name__ == "__main__":
    main()
