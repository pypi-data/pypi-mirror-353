import numpy as np
import brain_indexer.experimental


def test_query_order():
    points = np.random.uniform(-100.0, 300.0, size=(123, 3))
    order = brain_indexer.experimental.space_filling_order(points)

    assert len(set(order)) == points.shape[0]
    assert np.min(order) == 0
    assert np.max(order) == points.shape[0] - 1
