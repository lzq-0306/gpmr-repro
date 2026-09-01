"""Reproduce the within-class final-mass permutation control."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler

from gpmr import GraphPosteriorMassRebalancing
from run_gpmr_benchmark import CLASSIFIERS, ROOT, scores


def main():
    config = json.loads((ROOT / "config" / "datasets.json").read_text(encoding="utf-8"))
    rows = []
    for item in config["datasets"]:
        frame = pd.read_csv(ROOT / item["path"])
        X = frame.drop(columns="target").to_numpy(float)
        y = LabelEncoder().fit_transform(frame.target.astype(str))
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
        for split, (train, test) in enumerate(cv.split(X, y), start=1):
            seed = 42 + split
            scaler = StandardScaler().fit(X[train])
            Xtrain, Xtest = scaler.transform(X[train]), scaler.transform(X[test])
            masses = {}
            for method, permute in (("gpmr_full", False), ("within_class_mass_permutation", True)):
                sampler = GraphPosteriorMassRebalancing(
                    k=7, rounds=16, bounded_mass=True, realization="linear",
                    random_state=seed, permute_final_mass=permute,
                )
                Xfit, yfit = sampler.fit_resample(Xtrain, y[train])
                masses[method] = sampler.mass_
                for classifier, factory in CLASSIFIERS.items():
                    prediction = factory(seed).fit(Xfit, yfit).predict(Xtest)
                    row = {"dataset": item["name"], "split": split,
                           "method": method, "classifier": classifier}
                    row.update(scores(y[test], prediction))
                    rows.append(row)
            for label in np.unique(y[train]):
                mask = y[train] == label
                assert np.array_equal(np.sort(masses["gpmr_full"][mask]),
                                      np.sort(masses["within_class_mass_permutation"][mask]))

    raw = pd.DataFrame(rows)
    assert len(raw) == 4500 and not raw.duplicated(
        ["dataset", "split", "method", "classifier"]
    ).any()
    output = ROOT / "results" / "matched_profile_control"
    output.mkdir(parents=True, exist_ok=True)
    raw.to_csv(output / "results.csv", index=False)
    block = raw.groupby(["dataset", "classifier", "method"], as_index=False).mean(numeric_only=True)
    block.to_csv(output / "block_summary.csv", index=False)
    dataset = block.groupby(["dataset", "method"], as_index=False).mean(numeric_only=True)
    dataset.to_csv(output / "dataset_summary.csv", index=False)
    wide = dataset.pivot(index="dataset", columns="method", values="gmean")
    delta = wide.gpmr_full - wide.within_class_mass_permutation
    summary = {"mean_gmean_full": float(wide.gpmr_full.mean()),
               "mean_gmean_permuted": float(wide.within_class_mass_permutation.mean()),
               "mean_delta": float(delta.mean()), "median_delta": float(delta.median()),
               "wins": int((delta > 0).sum()), "ties": int((delta == 0).sum()),
               "losses": int((delta < 0).sum()),
               "wilcoxon_pvalue": float(wilcoxon(delta, zero_method="zsplit").pvalue)}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
