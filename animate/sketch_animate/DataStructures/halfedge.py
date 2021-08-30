import numpy as np


class HalfEdge:
    def __init__(self, collection, iself, inext, ivertex, ipair=-1):
        self.collection = collection
        self.iself = iself
        self.inext = inext
        self.ivertex = ivertex
        self.ipair = ipair

    def __repr__(self):
        return 'HalfEdge<index=%d inext=%d ivertex=%d ipair=%d' % \
               (self.iself, self.inext, self.ivertex, self.ipair)

    def prev(self):
        prev = self.collection[self.inext]
        while prev.inext != self.iself:
            prev = self.collection[prev.inext]
        return prev


def build(triangles):
    collection = []
    nTriangles = triangles.shape[0]
    for iTriangle in range(0, nTriangles):
        tri = triangles[iTriangle, :]
        for rotation in range(0, 3):
            rotatedNext = rotation + 1 if rotation < 2 else rotation - 2
            iVertex = tri[rotatedNext]
            iNext = 3 * iTriangle + rotatedNext
            collection.append(HalfEdge(collection, len(collection), iNext, iVertex))
    for me in collection:
        if me.ipair != -1:
            continue
        myPrev = me.prev()
        for pairPrev in collection:
            if pairPrev.ivertex != me.ivertex:
                continue
            pair = collection[pairPrev.inext]
            if pair.ivertex != myPrev.ivertex:
                continue
            pair.ipair = me.iself
            me.ipair = pair.iself
            break
    return collection


def toEdge(halfedges):
    edges = []
    indices = []
    for i in range(0, len(halfedges)):
        he = halfedges[i]
        if he.ipair == -1:
            prev = he.prev()
            edges.append((prev.ivertex, he.ivertex))
            indices.append(i)
        elif he.iself < he.ipair:
            pair = halfedges[he.ipair]
            edges.append((pair.ivertex, he.ivertex))
            indices.append(i)
    return np.asarray(edges, dtype=np.int), indices


if __name__ == '__main__':
    triangles = np.asarray(((0, 3, 1), (0, 2, 3)))
    halfedges = build(triangles)
    print('halfedges=', halfedges)
    print( 'edges=', toEdge(halfedges))
