import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "public_comparison"


def close(actual, expected, tolerance=5e-5):
    if not np.isclose(actual, expected, atol=tolerance, rtol=0):
        raise AssertionError(f"expected {expected}, obtained {actual}")


def verify_holm(wide, reference, saved, key, zero_method, p="p", adjusted_p="p_holm"):
    if wide.isna().any().any() or set(saved[key]) != set(wide.columns) - {reference}:
        raise AssertionError("incomplete paired comparison")
    calculated = pd.Series({method: wilcoxon(wide[reference] - wide[method],
        alternative="two-sided", zero_method=zero_method).pvalue
        for method in wide if method != reference}).sort_values()
    adjusted = (calculated * np.arange(len(calculated), 0, -1)).cummax().clip(upper=1)
    saved = saved.set_index(key).reindex(calculated.index)
    np.testing.assert_allclose(saved[p], calculated, atol=1e-10, rtol=0)
    np.testing.assert_allclose(saved[adjusted_p], adjusted, atol=1e-10, rtol=0)
    return set(adjusted[adjusted < .05].index)


def main():
    methods = pd.read_csv(RESULTS / "method_summary.csv")
    blocks = pd.read_csv(RESULTS / "block_summary.csv")
    allowed = {"gpmr_v3", "none", "ros", "rus", "allknn", "smote",
               "borderline_smote", "global_cs", "mdo", "soup", "mc_ccr",
               "gmm_sampling", "kde_reconstructed", "gdhs_lc_official",
               "mc_mbrc_reconstructed"}
    if set(blocks["method"]) != allowed:
        raise AssertionError("public comparison method set differs from the frozen protocol")
    if methods.shape[0] != 15 or blocks.shape[0] != 45 * 15:
        raise AssertionError("unexpected public comparison dimensions")
    gpmr = methods.loc[methods["method"] == "gpmr_v3"].iloc[0]
    close(gpmr["mean_gmean"], 0.6819638524)
    close(gpmr["mean_worst_recall"], 0.5494617515)
    close(gpmr["mean_rank"], 4.9333333333)
    if int(gpmr["first_blocks"]) != 11 or int(gpmr["top3_blocks"]) != 21:
        raise AssertionError("GPMR placement counts differ from the manuscript")
    if blocks.duplicated(["dataset", "classifier", "method"]).any():
        raise AssertionError("duplicate public block keys")
    means = blocks.groupby(["dataset", "method"]).gmean.mean().unstack()
    if means.shape != (15, 15):
        raise AssertionError("unexpected dataset-level dimensions")
    significant = verify_holm(means, "gpmr_v3",
        pd.read_csv(RESULTS / "holm_dataset_level.csv"), "baseline", "wilcox",
        "pvalue_unadjusted", "pvalue_holm")
    if len(significant) != 6:
        raise AssertionError("dataset-level significance differs from manuscript")
    test = friedmanchisquare(*(means[m] for m in means))
    saved = pd.read_csv(RESULTS / "friedman_dataset_level.csv").iloc[0]
    close(test.statistic, saved.statistic, 1e-10)
    close(test.pvalue, saved.pvalue, 1e-10)
    folder = ROOT / "results" / "component_ablation"
    ablation = pd.read_csv(folder / "block_summary.csv")
    if len(ablation) != 225 or ablation.duplicated(["dataset", "classifier", "method"]).any():
        raise AssertionError("invalid component blocks")
    for unit, keys in [("45_blocks", ["dataset", "classifier"]), ("15_datasets", ["dataset"])]:
        wide = ablation.groupby(keys + ["method"]).gmean.mean().unstack()
        if verify_holm(wide, "gpmr_full", pd.read_csv(folder / f"ablation_{unit}.csv"),
                       "method", "zsplit"):
            raise AssertionError("unexpected significant component comparison")
    matched = ROOT / "results" / "matched_profile_control"
    matched_summary = json.loads((matched / "summary.json").read_text(encoding="utf-8"))
    close(matched_summary["mean_delta"], 0.0194720687, 1e-10)
    close(matched_summary["wilcoxon_pvalue"], 0.072998046875, 1e-12)
    print("Verified: 15 conditions, 45 blocks, and 6/14 dataset-level Holm contrasts.")
    print("No component survives Holm correction; matched-profile p=0.0730.")


if __name__ == "__main__":
    main()
