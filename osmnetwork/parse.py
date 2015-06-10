import functools
import itertools
import os
import requests
import tempfile

import imposm.parser
import networkx as nx

from . import utils


def parse_file(filename):
    coords = {}
    nodes = {}
    ways = {}

    coords_cb = functools.partial(coords_callback, coords)
    node_cb = functools.partial(nodes_callback, nodes)
    ways_cb = functools.partial(ways_callback, ways)

    p = imposm.parser.OSMParser(coords_callback=coords_cb,
                                nodes_callback=node_cb,
                                ways_callback=ways_cb)
    p.parse(filename)

    return coords, nodes, ways


def parse_bbox(bbox):
    # Follow the GeoJSON standard

    url = 'http://api.openstreetmap.com/api/0.6/map'
    params = {'bbox': '{0},{1},{2},{3}'.format(*bbox)}

    r = requests.get(url, params=params)
    r.raise_for_status()

    fd, pathname = tempfile.mkstemp(suffix='.osm')
    try:
        os.write(fd, r.content)
        ret = parse_file(pathname)
    finally:
        os.close(fd)
        os.remove(pathname)

    return ret


def coords_callback(d, elements):
    for node_id, lon, lat in elements:
        d[node_id] = (lon, lat)


def nodes_callback(d, elements):
    for node_id, tags, coords in elements:
        d[node_id] = tags


def ways_callback(d, elements):
    highways = itertools.ifilter(lambda e: 'highway' in e[1], elements)
    for way_id, tags, node_ids in highways:
        if tags.get('oneway') == '-1':
            # oneway=-1 means interpret one way as the opposite direction
            # (this is OSM's greatest crime)
            node_ids = list(reversed(node_ids))
            tags['oneway'] = 'yes'
        d[way_id] = (tags, node_ids)


def build_graph(coords, nodes, ways, directed=True):
    if directed:
        g = nx.DiGraph()
    else:
        g = nx.Graph()

    def add_edges(g, node_ids, tags):
        for n1, n2 in utils.pairwise(node_ids):
            g.add_edge(n1, n2, tags=tags)

    for tags, node_ids in ways.values():
        add_edges(g, node_ids, tags)
        if directed and tags.get('oneway') not in {'yes', '1'}:
            add_edges(g, reversed(node_ids), tags)

    for n in g.nodes_iter():
        g.node[n]['coordinates'] = coords[n]

    graph_nodes = set(g.nodes())
    for n, tags in nodes.iteritems():
        if n in graph_nodes:
            g.node[n].update(tags)

    def node_distance(g, n1, n2):
        return utils.distance(g.node[n1]['coordinates'], g.node[n2]['coordinates'])

    utils.assign_weights(g, node_distance, attr='length') 
    return g
