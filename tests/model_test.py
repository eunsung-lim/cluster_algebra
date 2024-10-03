import pytest
from cluster_algebra.model import Vertex, Edge, FrozenVariable, ClusterVariable, Polygon, TriangulatedPolygon, SingleLamination, Lamination, Quiver, distance, get_intersection

def test_vertex():
    v = Vertex(x=1.0, y=2.0, id=0)
    assert v.x == 1.0
    assert v.y == 2.0
    assert v.id == 0
    assert v.name == "v_0"
    assert v.to_tuple() == (1.0, 2.0)

def test_edge():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=1.0, id=1)
    e = Edge(v1=v1, v2=v2, id=0)
    assert e.v1 == v1
    assert e.v2 == v2
    assert e.id == 0
    assert e.name == "e_0"
    assert e.get_midpoint() == (0.5, 0.5)

def test_frozen_variable():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=1.0, id=1)
    fv = FrozenVariable(v1=v1, v2=v2, id=0)
    assert isinstance(fv, Edge)
    assert fv.v1 == v1
    assert fv.v2 == v2

def test_cluster_variable():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=1.0, id=1)
    cv = ClusterVariable(v1=v1, v2=v2, id=0)
    assert cv.get_varname() == "x_{0}"
    cv.num_flips = 2
    assert cv.get_varname() == "x_{0''}"

def test_polygon():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=0.0, id=1)
    v3 = Vertex(x=0.5, y=1.0, id=2)
    p = Polygon(vertices=[v1, v2, v3], id=0)
    assert len(p.edges) == 3
    assert all(isinstance(e, Edge) for e in p.edges)
    assert all(isinstance(e, FrozenVariable) for e in p.frozens)
    
def test_triangulated_polygon():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=0.0, id=1)
    v3 = Vertex(x=0.5, y=1.0, id=2)
    v4 = Vertex(x=0.5, y=0.5, id=3)
    tp = TriangulatedPolygon(vertices=[v1, v2, v3, v4], id=0)
    assert len(tp.clusters) == 1
    assert tp.is_connected(v1, v3)
    assert tp.is_connected(v1, v4)
    assert tp.get_triangles(tp.clusters[0]) == [v2, v4]

def test_single_lamination():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=0.0, id=1)
    v3 = Vertex(x=0.5, y=1.0, id=2)
    e1 = FrozenVariable(v1=v1, v2=v2, id=0)
    e2 = FrozenVariable(v1=v2, v2=v3, id=1)
    sl = SingleLamination(start=e1, end=e2, id=0)
    assert sl.start == e1
    assert sl.end == e2
    assert sl.name == "arc_0"

def test_lamination():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=0.0, id=1)
    v3 = Vertex(x=0.5, y=1.0, id=2)
    e1 = FrozenVariable(v1=v1, v2=v2, id=0)
    e2 = FrozenVariable(v1=v2, v2=v3, id=1)
    sl1 = SingleLamination(start=e1, end=e2, id=0)
    sl2 = SingleLamination(start=e2, end=e1, id=1)
    lam = Lamination(arcs=[sl1, sl2], id=0)
    assert len(lam) == 2
    assert lam.name == "lam_0"

def test_quiver():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=1.0, y=0.0, id=1)
    v3 = Vertex(x=0.5, y=1.0, id=2)
    v4 = Vertex(x=0.5, y=0.5, id=3)
    q = Quiver(vertices=[v1, v2, v3, v4], id=0)
    assert len(q.clusters) == 1
    assert len(q.frozens) == 4

def test_distance():
    v1 = Vertex(x=0.0, y=0.0, id=0)
    v2 = Vertex(x=3.0, y=4.0, id=1)
    assert distance(v1, v2) == 5.0
    assert distance((0.0, 0.0), (3.0, 4.0)) == 5.0

def test_get_intersection():
    e1 = Edge(v1=Vertex(x=0.0, y=0.0, id=0), v2=Vertex(x=2.0, y=2.0, id=1), id=0)
    e2 = Edge(v1=Vertex(x=0.0, y=2.0, id=2), v2=Vertex(x=2.0, y=0.0, id=3), id=1)
    intersection = get_intersection(e1, e2)
    assert intersection == (1.0, 1.0)

    e3 = Edge(v1=Vertex(x=0.0, y=0.0, id=4), v2=Vertex(x=1.0, y=1.0, id=5), id=2)
    e4 = Edge(v1=Vertex(x=2.0, y=2.0, id=6), v2=Vertex(x=3.0, y=3.0, id=7), id=3)
    assert get_intersection(e3, e4) is None

if __name__ == "__main__":
    pytest.main()
