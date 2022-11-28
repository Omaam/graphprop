"""Tutorial.
"""

from scipy import signal
from scipy import stats
from numpy.typing import ArrayLike
import matplotlib.pyplot as plt
import numpy as np

import graphprop


def compute_ccf(in1: ArrayLike, in2: ArrayLike, maxlags=20):
    in1 = stats.zscore(in1)
    in2 = stats.zscore(in2)
    corrs = signal.correlate(in2, in1)
    corrs /= in1.size
    lags = signal.correlation_lags(in2.size, in1.size)

    ids = np.where(np.abs(lags) < maxlags)
    lags = lags[ids]
    corrs = corrs[ids]

    return lags, corrs


def main():
    """
    Propagation details are below.

    Graph
    x1 -> x2 -> x3
       -> x4 ->
          x5 ->

    Adjacent matrix for intensity
         x1   x2   x3   x4
    x1  0.0  0.1  0.0  0.1
    x2  0.0  0.0  0.1  0.0
    x3  0.0  0.0  0.0  0.0
    x4  0.0  0.0  0.1  0.0
    x5  0.0  0.0  0.3  0.0

    Adjacent matrix for lag
         x1   x2   x3   x4
    x1    0    5    0    1
    x2    0    0    3    0
    x3    0    0    0    0
    x4    0    0    2    0
    x5    0    0    1    0
    """
    graph = graphprop.Graph()
    graph.add_node("x1", True)
    graph.add_node("x2", False)
    graph.add_node("x3", False)
    graph.add_node("x4", False)
    graph.add_node("x5", True)

    graph.write_node_condition("x1", "x2", 0.1, 5)
    graph.write_node_condition("x2", "x3", 0.1, 3)
    graph.write_node_condition("x4", "x3", 0.1, 2)
    graph.write_node_condition("x2", "x4", 0.1, 1)
    graph.write_node_condition("x5", "x3", 0.2, 1)

    np.random.seed(0)

    def generator_white_noise():
        while 1:
            yield np.random.normal(10, 1)

    graph.set_impact_generator("x1", generator_white_noise)
    graph.set_impact_generator("x5", generator_white_noise)

    num_burnin = 20
    graph.initialize(num_burnin)
    for _ in range(1000):
        graph.update()

    df = graph.realization
    print(df)

    df.plot(subplots=True)
    plt.show()
    plt.close()

    lags, corrs = compute_ccf(df["x1"], df["x3"], 50)
    plt.stem(lags, corrs, markerfmt=" k", linefmt="k")
    uncorr_points = np.repeat(1.96 / np.sqrt(len(df)), len(lags))
    plt.plot(lags, +uncorr_points, color="k", ls="--")
    plt.plot(lags, -uncorr_points, color="k", ls="--")
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()
