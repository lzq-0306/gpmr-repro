from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "public_comparison"


def close(actual, expected, tolerance=5e-5):
    if not np.isclose(actual, expected, atol=tolerance, rtol=0):
        raise AssertionError(f"expected {expected}, obtained {actual}")


def main():
    methods = pd.read_csv(RESULTS / "method_summary.csv")
    blocks = pd.read_csv(RESULTS / "block_summary.csv")
    holm = pd.read_csv(RESULTS / "holm_vs_gpmr.csv")
    allowed = {"gpmr_v3", "none", "ros", "rus", "allknn", "smote",
               "borderline_smote", "global_cs", "mdo", "soup", "mc_ccr",
               "gmm_sampling", "kde_reconstructed"}
    if set(blocks["method"]) != allowed:
        raise AssertionError("public comparison method set differs from the frozen protocol")
    if methods.shape[0] != 13 or blocks.shape[0] != 45 * 13:
        raise AssertionError("unexpected public comparison dimensions")
    gpmr = methods.loc[methods["method"] == "gpmr_v3"].iloc[0]
    close(gpmr["mean_gmean"], 0.6819638524)
    close(gpmr["mean_worst_recall"], 0.5494617515)
    close(gpmr["mean_rank"], 4.1777777778)
    if int(gpmr["first_blocks"]) != 13 or int(gpmr["top3_blocks"]) != 25:
        raise AssertionError("GPMR placement counts differ from the manuscript")
    if len(holm) != 12 or not holm["significant_0_05"].all():
        raise AssertionError("Holm result set differs from the manuscript")
    print("Frozen public comparison verified: 13 conditions, 45 blocks, 12 significant contrasts.")


if __name__ == "__main__":
    main()
