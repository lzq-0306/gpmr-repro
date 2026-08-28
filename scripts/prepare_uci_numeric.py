from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from ucimlrepo import fetch_ucirepo


SOURCES = {
    "pageblocks-full": 78,
    "statlog-landsat": 146,
}


def prepare(name: str, output_root: Path):
    repository = fetch_ucirepo(id=SOURCES[name])
    X = repository.data.features.copy().replace("?", np.nan)
    targets = repository.data.targets.copy()
    y = targets.iloc[:, 0] if isinstance(targets, pd.DataFrame) else targets
    X = X.apply(pd.to_numeric, errors="coerce")
    frame = X.assign(target=y.astype(str).to_numpy()).dropna(axis=0).reset_index(drop=True)
    destination = output_root / name
    destination.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination / "benchmark.csv", index=False)
    print(f"prepared {name}: {len(frame)} rows, {frame.shape[1] - 1} features")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--dataset", choices=[*SOURCES, "all"], default="all")
    args = parser.parse_args()
    selected = SOURCES if args.dataset == "all" else [args.dataset]
    for name in selected:
        prepare(name, args.output)


if __name__ == "__main__":
    main()
