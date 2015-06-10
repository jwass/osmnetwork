import functools
import itertools

import matplotlib.pyplot as plt
import networkx as nx

from . import utils


# Colorbrewer2: qualitative
_colors = [
    '#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99', '#e31a1c',
    '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a', '#ffff99',
]


class Plot(object):
    def __init__(self, g):
        self.g = g
        self.vias = []
        self.path = []

    def plot(self):
        plt.hold(True)
        colors = itertools.cycle(_colors)
        for n1, n2 in self.plottable_edges():
            lon1, lat1 = self.g.node[n1]['coordinates']
            lon2, lat2 = self.g.node[n2]['coordinates']
            plt.plot([lon1, lon2], [lat1, lat2], color=next(colors))

        coordinates = [self.g.node[n]['coordinates']
                       for n in self.g.nodes_iter()]
        lon, lat = zip(*coordinates)
        plt.scatter(lon, lat, s=0.5, picker=True)

        plt.gcf().canvas.mpl_connect('pick_event', self.on_click)

    def plottable_edges(self):
        """
        If the forward and backward edge are in the graph, only use one

        Use the edge where first node_id is less than the second.

        """
        edges = set(self.g.edges())
        for n1, n2 in edges:
            if n1 < n2 or (n2, n1) not in edges:
                yield n1, n2

    def on_click(self, event):
        ind = event.ind[0]
        node = self.g.nodes()[ind]

        self.add_remove_via(node)
        self.update_path()

        return node

    def add_remove_via(self, node):
        if node in self.vias:
            self.vias.remove(node)
            self.remove_via(node)
        else:
            self.vias.append(node)
            self.add_via(node)
        self.compute_path()

    def remove_via(self, node):
        # Delete
        pass

    def add_via(self, node):
        lon, lat = self.g.node[node]['coordinates']
        plt.scatter(lon, lat, c='k', s=25.0)

    def compute_path(self):
        self.path = []
        if len(self.vias) <= 1:
            return

        for i, (n1, n2) in enumerate(utils.pairwise(self.vias)):
            nodes = nx.shortest_path(self.g, n1, n2, weight='length')
            if i > 0:
                nodes = nodes[1:]
            self.path.extend(nodes)

    def update_path(self):
        coordinates = [self.g.node[n]['coordinates'] for n in self.path]
        if not coordinates:
            return

        lon, lat = zip(*coordinates)
        plt.plot(lon, lat, linewidth=5, color='k')
