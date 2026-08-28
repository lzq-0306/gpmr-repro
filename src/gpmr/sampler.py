"""Graph Posterior Mass Rebalancing (GPMR)."""

from __future__ import annotations

import numpy as np
from scipy.sparse import csc_matrix
from sklearn.neighbors import NearestNeighbors


class GraphPosteriorMassRebalancing:
    """Optimize integer sample mass under a class-balanced local posterior.

    A fixed reverse-neighbour graph defines how the multiplicity of observation
    ``i`` contributes to the local posterior at observation ``j``.  Positive
    and negative projected-gradient moves respectively duplicate and remove
    observations until every class reaches the fixed boundary-derived target
    described in the accompanying manuscript.
    """

    def __init__(
        self, *, k: int = 7, rounds: int = 16, epsilon: float = 1e-6,
        optimize_additions: bool = True, optimize_removals: bool = True,
        random_state: int = 42, bounded_mass: bool = False,
        realization: str = "duplicate",
    ):
        self.k = k
        self.rounds = rounds
        self.epsilon = epsilon
        self.optimize_additions = optimize_additions
        self.optimize_removals = optimize_removals
        self.random_state = random_state
        self.bounded_mass = bounded_mass
        if realization not in {"duplicate", "linear", "barycenter"}:
            raise ValueError(f"unknown realization: {realization}")
        self.realization = realization

    def fit_resample(self, X, y):
        X = np.asarray(X)
        y = np.asarray(y)
        labels, encoded, counts = np.unique(y, return_inverse=True, return_counts=True)
        n, classes = len(y), len(labels)
        if n < 2:
            return X.copy(), y.copy()

        neighbors = min(self.k + 1, n)
        distances, indices = NearestNeighbors(n_neighbors=neighbors).fit(X).kneighbors(X)
        radius = np.maximum(distances[:, -1], self.epsilon)
        weights = np.exp(-distances / radius[:, None])
        rows = np.repeat(np.arange(n), neighbors)
        graph = csc_matrix((weights.ravel(), (rows, indices.ravel())), shape=(n, n))

        mass = np.ones(n, dtype=np.int64)
        rng = np.random.default_rng(self.random_state)
        middle = float(np.median(counts))
        minority_counts = counts[counts < middle]
        majority_counts = counts[counts > middle]
        if not len(minority_counts) and not len(majority_counts):
            target = int(counts[0])
        elif not len(majority_counts):
            target = int(np.mean(minority_counts))
        elif not len(minority_counts):
            target = int(np.mean(majority_counts))
        else:
            target = int(np.mean((minority_counts.max(), majority_counts.min())))
        desired = np.full(classes, target, dtype=np.int64)
        remaining = desired - counts
        alpha = 1.0 / (classes * counts[encoded])

        for step in range(self.rounds):
            if not np.any(remaining):
                break
            total_support = np.asarray(graph @ mass).ravel() + self.epsilon
            class_support = np.empty((n, classes), dtype=float)
            for class_id in range(classes):
                class_support[:, class_id] = np.asarray(
                    graph @ (mass * (encoded == class_id))
                ).ravel() + self.epsilon

            steps_left = self.rounds - step
            for class_id in range(classes):
                need = int(remaining[class_id])
                if need == 0:
                    continue
                query = -alpha / total_support
                own_rows = encoded == class_id
                query = query.copy()
                query[own_rows] += alpha[own_rows] / class_support[own_rows, class_id]
                gradient = np.asarray(graph.T @ query).ravel()
                candidates = np.flatnonzero(encoded == class_id)
                batch = min(abs(need), max(1, int(np.ceil(abs(need) / steps_left))))
                if need > 0:
                    # Repetition is allowed across rounds, enforcing diminishing
                    # returns through posterior recomputation.
                    eligible = candidates
                    if self.bounded_mass:
                        cap = int(np.ceil(target / counts[class_id]))
                        eligible = eligible[mass[eligible] < cap]
                    if self.optimize_additions:
                        chosen = eligible[np.argsort(gradient[eligible])[-batch:]]
                    else:
                        chosen = rng.choice(eligible, size=min(batch, len(eligible)),
                                            replace=False)
                    mass[chosen] += 1
                    remaining[class_id] -= len(chosen)
                else:
                    removable = candidates[mass[candidates] > 0]
                    if self.optimize_removals:
                        chosen = removable[np.argsort(gradient[removable])[:batch]]
                    else:
                        chosen = rng.choice(removable, size=min(batch, len(removable)),
                                            replace=False)
                    mass[chosen] -= 1
                    remaining[class_id] += len(chosen)

        # Complete any rounding remainder deterministically using the final gradient.
        for class_id, need in enumerate(remaining):
            candidates = np.flatnonzero(encoded == class_id)
            if need > 0:
                while need > 0:
                    eligible = candidates
                    if self.bounded_mass:
                        cap = int(np.ceil(target / counts[class_id]))
                        eligible = eligible[mass[eligible] < cap]
                    take = eligible[:need]
                    mass[take] += 1
                    need -= len(take)
            elif need < 0:
                removable = candidates[mass[candidates] > 0][:(-need)]
                mass[removable] -= 1
        self.mass_ = mass.copy()
        self.target_count_ = target
        retained = np.flatnonzero(mass > 0)
        X_parts = [X[retained]]
        y_parts = [y[retained]]
        if self.realization == "duplicate":
            extra = np.repeat(np.arange(n), np.maximum(mass - 1, 0))
            if len(extra):
                X_parts.append(X[extra])
                y_parts.append(y[extra])
        else:
            for class_id in range(classes):
                class_rows = np.flatnonzero(encoded == class_id)
                for row in class_rows:
                    quantity = int(max(mass[row] - 1, 0))
                    if quantity == 0:
                        continue
                    peers = class_rows[class_rows != row]
                    if not len(peers):
                        generated = np.repeat(X[row][None, :], quantity, axis=0)
                    elif self.realization == "linear":
                        peer_distances = np.linalg.norm(X[peers] - X[row], axis=1)
                        nearest = peers[np.argsort(peer_distances)[: min(self.k, len(peers))]]
                        generated = []
                        for offset in range(quantity):
                            neighbor = nearest[offset % len(nearest)]
                            fraction = (offset + 1) / (quantity + 1)
                            generated.append(X[row] + fraction * (X[neighbor] - X[row]))
                        generated = np.asarray(generated)
                    else:
                        peer_distances = np.linalg.norm(X[peers] - X[row], axis=1)
                        order = np.argsort(peer_distances)[: min(self.k, len(peers))]
                        nearest, distances_local = peers[order], peer_distances[order]
                        scale = max(float(distances_local[-1]), self.epsilon)
                        local_weights = np.exp(-distances_local / scale)
                        centroid = np.average(X[nearest], axis=0, weights=local_weights)
                        fractions = np.arange(1, quantity + 1)[:, None] / (quantity + 1)
                        generated = X[row] + fractions * (centroid - X[row])
                    X_parts.append(generated)
                    y_parts.append(np.full(quantity, labels[class_id], dtype=y.dtype))
        return np.vstack(X_parts), np.concatenate(y_parts)
