import json

import networkx as nx


def graph_to_json(g):
    # Compare types directly instead of isinstance because of class hierarchy
    if type(g) == nx.DiGraph:
        _type = 'directed'
    elif type(g) == nx.Graph:
        _type = 'undirected'
    else:
        raise ValueError("Unknown type {}".format(type(g)))

    nodes = g.node
    edges = [{'from': n1, 'to': n2, 'attrs': g[n1][n2]}
             for n1, n2 in g.edges_iter()]

    return json.dumps({
        'type': _type,
        'nodes': nodes,
        'edges': edges,
    })


def json_to_graph(js):
    data = json.loads(js)
    if data['type'] == 'undirected':
        cls = nx.Graph
    elif data['type'] == 'directed':
        cls = nx.DiGraph
    else:
        raise ValueError('Unknown graph type {}'.format(data['type']))

    g = cls()

    for edge_d in data['edges']:
        g.add_edge(edge_d['from'], edge_d['to'], **edge_d['attrs'])
    for node_str, attrs in data['nodes'].iteritems():
        node = int(node_str)
        g.node[node].update(attrs)

    return g
