from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, f1_score, recall_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from gpmr import GraphPosteriorMassRebalancing

ROOT = Path(__file__).resolve().parents[1]
CLASSIFIERS = {
    "cart": lambda seed: DecisionTreeClassifier(random_state=seed),
    "knn": lambda seed: KNeighborsClassifier(n_neighbors=5),
    "rf": lambda seed: RandomForestClassifier(n_estimators=100, random_state=seed, n_jobs=1),
}


def multiclass_gmean(y_true, y_pred):
    recalls = recall_score(y_true, y_pred, average=None, labels=np.unique(y_true), zero_division=0)
    return float(np.prod(np.maximum(recalls, 1e-12)) ** (1.0 / len(recalls)))


def scores(y_true, y_pred):
    recalls = recall_score(y_true, y_pred, average=None, labels=np.unique(y_true), zero_division=0)
    return {
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "gmean": multiclass_gmean(y_true, y_pred),
        "worst_class_recall": float(recalls.min()),
    }


def main():
    config = json.loads((ROOT / "config" / "datasets.json").read_text(encoding="utf-8"))
    rows = []
    for item in config["datasets"]:
        path = ROOT / item["path"]
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}; see README.md")
        frame = pd.read_csv(path)
        X = frame.drop(columns="target").to_numpy(float)
        y = LabelEncoder().fit_transform(frame["target"].astype(str))
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
        for split, (train, test) in enumerate(cv.split(X, y), start=1):
            seed = 42 + split
            scaler = StandardScaler().fit(X[train])
            X_train, X_test = scaler.transform(X[train]), scaler.transform(X[test])
            sampler = GraphPosteriorMassRebalancing(
                k=7, rounds=16, bounded_mass=True, realization="linear", random_state=seed
            )
            started = time.perf_counter()
            X_fit, y_fit = sampler.fit_resample(X_train, y[train])
            sampling_seconds = time.perf_counter() - started
            for name, factory in CLASSIFIERS.items():
                model = factory(seed)
                model.fit(X_fit, y_fit)
                row = {"dataset": item["name"], "split": split, "classifier": name,
                       "train_before": len(train), "train_after": len(y_fit),
                       "sampling_seconds": sampling_seconds}
                row.update(scores(y[test], model.predict(X_test)))
                rows.append(row)
        print(f"finished {item['name']}", flush=True)
    output = ROOT / "results" / "gpmr_split_results.csv"
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
