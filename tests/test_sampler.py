import numpy as np

from gpmr import GraphPosteriorMassRebalancing


def test_deterministic_and_balanced_target():
    rng = np.random.default_rng(7)
    X = np.vstack([rng.normal(0, 1, (30, 3)), rng.normal(2, 1, (10, 3)), rng.normal(-2, 1, (5, 3))])
    y = np.repeat([0, 1, 2], [30, 10, 5])
    a = GraphPosteriorMassRebalancing(k=3, rounds=4, bounded_mass=True, realization="linear", random_state=9)
    b = GraphPosteriorMassRebalancing(k=3, rounds=4, bounded_mass=True, realization="linear", random_state=9)
    Xa, ya = a.fit_resample(X, y)
    Xb, yb = b.fit_resample(X, y)
    assert np.array_equal(ya, yb)
    assert np.allclose(Xa, Xb)
    counts = np.unique(ya, return_counts=True)[1]
    assert len(set(counts.tolist())) == 1


def test_mass_permutation_preserves_each_class_profile():
    rng = np.random.default_rng(11)
    X = np.vstack([rng.normal(0, 1, (24, 2)), rng.normal(3, 1, (8, 2))])
    y = np.repeat([0, 1], [24, 8])
    settings = dict(k=3, rounds=4, bounded_mass=True, realization="linear", random_state=5)
    full = GraphPosteriorMassRebalancing(**settings)
    permuted = GraphPosteriorMassRebalancing(**settings, permute_final_mass=True)
    full.fit_resample(X, y)
    permuted.fit_resample(X, y)
    for label in np.unique(y):
        rows = y == label
        assert np.array_equal(np.sort(full.mass_[rows]), np.sort(permuted.mass_[rows]))
