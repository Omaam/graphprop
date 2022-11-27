"""
"""
import numpy as np
import pandas as pd


class Graph:
    """Graph.
    """
    def __init__(self):
        self.nodes = dict()
        self.time = None

    def add_node(self, name: str, is_origin: bool):
        self.nodes[name] = Node(name, is_origin)

    def initialize(self, maxlag: int):
        for node in self.nodes.values():
            node.values.extend(maxlag * [0.0])

        self.maxlag = maxlag
        self.time = maxlag
        for _ in range(maxlag):
            self.update()

    def update(self):

        if self.time is None:
            raise AttributeError(
                "You must initialize before first update."
            )

        self.time += 1
        for node in self.nodes.values():
            if node.is_origin:
                value = np.random.normal(10, 1)
                node.values.append(value)
            else:
                total_value = 0
                for cond in node.prop_conds:
                    target_node = self.nodes[cond["from"]]
                    value = target_node.values[self.time - cond["lag"] - 1]
                    total_value += cond["intensity"] * value
                node.values.append(total_value)

    def write_node_condition(self, target: str, prop_from: str,
                             intensity: float, lag: int):
        self.nodes[target].add_condition(prop_from, intensity, lag)

    @property
    def realization(self):
        names = []
        realizations = []
        for name, node in self.nodes.items():
            names.append(name)
            realizations.append(node.values[2*self.maxlag:])
        realizations = pd.DataFrame(realizations, index=names).T
        return realizations


class Node:

    def __init__(self, name: str, is_origin: bool):
        self.name = name
        self.prop_conds = []
        self.values = []
        self.is_origin = is_origin

    def add_condition(self, prop_from: str, intensity: float,
                      lag: int):
        prop_cond = {
            "from":      prop_from,
            "intensity": intensity,
            "lag":       lag
        }
        self.prop_conds.append(prop_cond)
