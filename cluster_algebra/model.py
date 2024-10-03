from pydantic import BaseModel, Field, field_validator
from typing import Dict, Iterable, List, Optional, Tuple, Union

Point2D = Tuple[float, float]

class Vertex(BaseModel):
    """
    A vertex in a graph.
    """
    x: float = Field(..., description="X coordinate of the vertex")
    y: float = Field(..., description="Y coordinate of the vertex")
    id: int = Field(..., description="Unique identifier, ex: 0, 1, etc.")
    name: str = Field(default=None, description="Name of the vertex, ex: 'v0', 'v1', etc.")
    description: Optional[str] = Field(default=None, description="Description of the vertex")

    def __init__(self, **data):
        super().__init__(**data)
        if self.name is None:
            self.name = f"v_{self.id}"
    
    def __eq__(self, other) -> bool:
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    def to_tuple(self):
        return (self.x, self.y)
    

class Edge(BaseModel):
    """
    An edge in a graph.
    """
    v1: Vertex = Field(..., description="Source vertex of the edge")
    v2: Vertex = Field(..., description="Target vertex of the edge")
    id: int = Field(..., description="Unique identifier, ex: 0, 1, etc.")
    name: str = Field(default=None, description="Name of the edge, ex: 'e_0', 'e_1', etc.")
    description: Optional[str] = Field(default=None, description="Description of the edge")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.name is None:
            self.name = f"e_{self.id}"
    
    def __eq__(self, other) -> bool:
        return self.id == other.id
    
    def __repr__(self):
        return f"{self.name} : {self.v1} -> {self.v2}"
    
    def __str__(self):
        return self.__repr__()
    
    def set_vertices(self, v1: Vertex, v2: Vertex):
        self.v1 = v1
        self.v2 = v2
    
    def get_dividing_point(self, p: float) -> Tuple[float, float]:
        """
        Get the dividing point of the edge.
        """
        return (self.v1.x * p + self.v2.x * (1 - p), self.v1.y * p + self.v2.y * (1 - p))
    
    def get_midpoint(self) -> Tuple[float, float]:
        return self.get_dividing_point(0.5)

class FrozenVariable(Edge):
    """
    A frozen variable in a graph.
    """
    pass

class ClusterVariable(Edge):
    """
    A cluster variable in a graph.
    """
    num_flips: int = Field(default=0, description="Number of flips of the edge")
    
    def __init__(self, **data):
        super().__init__(**data)
    
    def set_vertices(self, v1: Vertex, v2: Vertex):
        self.v1 = v1
        self.v2 = v2
    
    def get_varname(self):
        return "x_{" + str(self.id) + "'" * self.num_flips + "}"
    
    def __repr__(self):
        return self.get_varname()
    
    def __str__(self):
        return self.__repr__()

class Polygon(BaseModel):
    """
    A polygon in a graph.
    """
    vertices: List[Vertex] = Field(..., description="Vertices of the polygon")
    edges: List[Edge] = Field(default=[], description="Edges of the polygon")
    frozens: List[FrozenVariable] = Field(default=[], description="Frozen variables of the polygon")
    id: int = Field(default=0, description="Unique identifier, ex: 0, 1, etc.")
    name: str = Field(default=None, description="Name of the polygon")
    description: Optional[str] = Field(default=None, description="Description of the polygon")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.edges == []:
            self.set_default_edges()
        self.frozens = self.edges
    
    def set_default_edges(self):
        self.edges = [FrozenVariable(v1=self.vertices[i], v2=self.vertices[(i+1)%len(self.vertices)], id=i) for i in range(len(self.vertices))]
    
    @field_validator('edges', mode='before')
    def check_edges(cls, edges, values):
        vertices = values.get('vertices', [])
        for e in edges:
            if e.v1 not in vertices or e.v2 not in vertices:
                raise ValueError(f"Edge {e} is not a valid edge of the polygon. Both endpoints must be in the vertices list.")
        for e in edges:
            if not isinstance(e, FrozenVariable):
                raise ValueError(f"Edge {e} is not a valid edge of the polygon. Frozen variables are allowed only.")
        return edges
    
    def __repr__(self):
        return f"{self.name} : {self.vertices}"

    def __str__(self):
        return self.__repr__()

class TriangulatedPolygon(Polygon):
    """
    A triangulated polygon in a graph.
    """
    frozens: List[FrozenVariable] = Field(default=[], description="Frozen variables of the polygon")
    clusters: List[ClusterVariable] = Field(default=[], description="Cluster variables of the polygon")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.clusters == []:
            self.set_default_clusters()
        self.frozens = self.edges
    
    def set_default_clusters(self):
        self.clusters = [
            ClusterVariable(
                v1=self.vertices[0], 
                v2=self.vertices[i], 
                id=i-1, 
                name=str(i-1)
            ) for i in range(2, len(self.vertices)-1)]

    def is_connected(self, v1: Vertex, v2: Vertex):
        return any([{v1, v2} == {e.v1, e.v2} for e in self.clusters + self.frozens])
    
    def get_triangles(self, cluster: ClusterVariable):
        v1, v2 = cluster.v1, cluster.v2
        triangles = []
        for v in self.vertices:
            if self.is_connected(v, v1) and self.is_connected(v, v2):
                triangles.append(v)
        return triangles
    
    def flip(self, cluster: ClusterVariable):
        v3, v4 = self.get_triangles(cluster)
        cluster.set_vertices(v3, v4)
        cluster.num_flips += 1

class SingleLamination(BaseModel):
    """
    A single lamination in a graph.
    """
    start: FrozenVariable = Field(..., description="Start of the lamination")
    end: FrozenVariable = Field(..., description="End of the lamination")
    id: int = Field(default=0, description="Unique identifier, ex: 0, 1, etc.")
    name: str = Field(default=None, description="Name of the lamination")
    description: Optional[str] = Field(default=None, description="Description of the lamination")
    
    starting_point: Tuple[float, float] = Field(default=None, description="Starting point of the lamination")
    ending_point: Tuple[float, float] = Field(default=None, description="Ending point of the lamination")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.name is None:
            self.name = f"arc_{self.id}"
    
    def __repr__(self):
        return f"{self.name} : {self.start} -> {self.end}"
    
    def __str__(self):
        return self.__repr__()
    
    def set_starting_point(self, x: float, y: float):
        self.starting_point = (x, y)
    
    def set_ending_point(self, x: float, y: float):
        self.ending_point = (x, y)
    
    def get_midpoint(self) -> Tuple[float, float]:
        if self.starting_point is None:
            self.starting_point = self.start.get_midpoint()
        if self.ending_point is None:
            self.ending_point = self.end.get_midpoint()
        
        return ((self.starting_point[0] + self.ending_point[0]) / 2, (self.starting_point[1] + self.ending_point[1]) / 2)

class Lamination(BaseModel):
    arcs: List[SingleLamination] = Field(default=[], description="Arcs of the lamination")
    id: int = Field(default=0, description="Unique identifier, ex: 0, 1, etc.")
    name: str = Field(default=None, description="Name of the lamination")
    description: Optional[str] = Field(default=None, description="Description of the lamination")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.name is None:
            self.name = f"lam_{self.id}"
    
    def __len__(self):
        return len(self.arcs)

class Shear(BaseModel):
    """
    A shear in a graph.
    """
    pass

class Arrow(BaseModel):
    """
    An arrow in a graph.
    """
    pass

class Quiver(TriangulatedPolygon):
    """
    A quiver in a graph.
    """
    laminations: List[Lamination] = Field(default=[], description="Laminations of the quiver")
    arrows: List[Arrow] = Field(default=[], description="Arrows of the quiver")
    
    def __repr__(self):
        return f"{self.name} : {self.vertices}"
    
    def __str__(self):
        return self.__repr__()

    def get_crossing_clusters(self, target: ClusterVariable):
        crossing_clusters = []
        for cluster in self.clusters:
            if cluster == target:
                continue
            intersection = get_intersection(cluster, target)
            if intersection:
                crossing_clusters.append((cluster, intersection))
        
        # Sort crossing clusters based on distance from target.v1
        crossing_clusters.sort(key=lambda x: distance(target.v1, x[1]))
        
        return [cluster for cluster, _ in crossing_clusters]



def distance(v1: Union[Vertex, Point2D], v2: Union[Vertex, Point2D]):
    if isinstance(v1, Vertex):
        x1, y1 = v1.x, v1.y
    else:
        x1, y1 = v1
    if isinstance(v2, Vertex):
        x2, y2 = v2.x, v2.y
    else:
        x2, y2 = v2
    return ((x1 - x2)**2 + (y1 - y2)**2)**0.5

def get_intersection(e1: Edge, e2: Edge):
    # Check if line segments intersect
    x1, y1 = e1.v1.x, e1.v1.y
    x2, y2 = e1.v2.x, e1.v2.y
    x3, y3 = e2.v1.x, e2.v1.y
    x4, y4 = e2.v2.x, e2.v2.y
    
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return None  # Lines are parallel
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Intersection point
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    
    return None
