import itertools
import math


def assign_weights(g, f, attr='weight'):
    for n1, n2 in g.edges_iter():
        edge = g[n1][n2]
        edge[attr] = f(g, n1, n2)


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)

    return itertools.izip(a, b)


def distance(c1, c2):
    lon1, lat1 = c1[0], c1[1]
    lon2, lat2 = c2[0], c2[1]

    r = 6371000.0
    rlat1 = math.radians(lat1)
    rlat2 = math.radians(lat2)
    lat_sin = math.sin((rlat2 - rlat1) / 2.0)
    lon_sin = math.sin(math.radians(lon2 - lon1) / 2.0)
    a = (lat_sin * lat_sin + 
         math.cos(rlat1) * math.cos(rlat2) * lon_sin * lon_sin)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    d = r * c # Distance in m

    return d


