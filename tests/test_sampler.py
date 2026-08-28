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
