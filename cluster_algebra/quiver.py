import sympy as sp
from functools import reduce
from itertools import combinations
from collections import defaultdict
from typing import List, Tuple
import pandas as pd


class Quiver:
    def __init__(self, 
                 vertices: List[int] = [], 
                 clusters: List[Tuple[int, int]] = [],
                 laminations: List[List[Tuple[int, int]]] = [],
                 is_principal: bool = False
                 ):
        self.n = len(vertices)
        self.vertices = vertices
        self.frozens = [(i, (i+1)%self.n) for i in range(self.n)]
        self.clusters = clusters
        self.cluster_names = [str(i) for i in range(1, len(clusters)+1)]
        
        if is_principal:
            laminations = [
                [(self.get_previous_vertex(p), self.get_previous_vertex(q))]
                for p, q in self.clusters
            ] + laminations
        
        self.laminations = laminations
        self.lamination_names = [str(i) for i in range(1, len(laminations)+1)]
        self.x = [
            [sp.symbols(f"""x_{{{i}{"'"*j}}}""") for j in range(self.n)]
            for i in range(1, len(clusters)+1)
        ]
        self.u = [
            sp.symbols(f"""u_{{{i}}}""") for i in range(1, len(laminations)+1)
        ]

    def get_adjacent_edges(self, edge: Tuple[int, int]):
        p, q = edge
        r = []
        all_edges = self.frozens + self.clusters
        for i in range(self.n):
            if (p, i) in all_edges or (i, p) in all_edges:
                if (q, i) in all_edges or (i, q) in all_edges:
                    r.append(i)
        return r


    def get_next_vertex(self, k: int):
        return (k+1)%self.n
    
    def get_previous_vertex(self, k: int):
        return (k-1)%self.n

    
    def flip(self, edge: Tuple[int, int]):
        if edge not in self.clusters:
            raise ValueError("Edge is not a cluster edge")
        idx = self.clusters.index(edge)
        p, q = edge
        r = self.get_adjacent_edges(edge)
        self.clusters[idx] = (r[0], r[1])
        self.cluster_names[idx] += "'"
        return self
    
    def is_in_frozens(self, edge: Tuple[int, int]):
        p, q = edge
        return (p, q) in self.frozens or (q, p) in self.frozens
    
    def is_in_clusters(self, edge: Tuple[int, int]):
        p, q = edge
        return (p, q) in self.clusters or (q, p) in self.clusters
        
    def is_in_edges(self, edge: Tuple[int, int]):
        return self.is_in_frozens(edge) or self.is_in_clusters(edge)
    
    def get_cluster_index_by_edge(self, edge: Tuple[int, int]):
        p, q = edge
        if (p, q) in self.clusters:
            return self.clusters.index((p, q))
        elif (q, p) in self.clusters:
            return self.clusters.index((q, p))
        else:
            raise ValueError("Edge is not a cluster edge")

    def get_all_triangles(self):
        for a, b, c in combinations(range(self.n), 3):
            if self.is_in_edges((a, b)) and self.is_in_edges((b, c)) and self.is_in_edges((c, a)):
                yield (a, b, c)
    
    def get_intersecting_clusters(self, start: int, end: int):
        s, e = start, end
        s += 0.5
        e += 0.5
        
        def between(a, b, c):
            return a < b < c or c < b < a
        
        intersecting_clusters = []
        for p, q in self.clusters:
            if between(s, p, e) ^ between(s, q, e):
                intersecting_clusters.append((p, q))
        
        intersecting_clusters.sort(key=lambda x: ((x[0]-start)%self.n, -(x[1]-start)%self.n))
        return intersecting_clusters
    
    def get_shear_coordinates(self, start: int, end: int):
        intersecting_clusters = []
        intersecting_clusters.append((start, self.get_next_vertex(start)))
        intersecting_clusters.extend(self.get_intersecting_clusters(start, end))
        intersecting_clusters.append((end, self.get_next_vertex(end)))
        
        c = defaultdict(int)
        for p, q in intersecting_clusters:
            c[p] += 1
            c[q] += 1
        
        r = []
        r.append((start, self.get_next_vertex(start)))
        r += [(p, q) for p, q in intersecting_clusters if c[p] >= 2 and c[q] >= 2]
        r.append((end, self.get_next_vertex(end)))
        
        if len(r) <= 2:
            return []
        
        if (c[start] >= 2 and start in r[1]) or (c[end] >= 2 and end in r[1]):
            return [(p, q, (-1)**(i+1)) for i, (p, q) in enumerate(r[1:-1])]
        else:
            return [(p, q, (-1)**i) for i, (p, q) in enumerate(r[1:-1])]

    
    def get_exchange_matrix(self):
        n = len(self.clusters)  # Number of mutable vertices
        m = len(self.laminations)
        
        # Initialize empty matrix with n+m rows and n columns
        matrix = [[0 for _ in range(n)] for _ in range(n+m)]
        
        for a, b, c in self.get_all_triangles():
            if self.is_in_clusters((a, b)) and self.is_in_clusters((b, c)):
                idx1 = self.get_cluster_index_by_edge((a, b))
                idx2 = self.get_cluster_index_by_edge((b, c))
                matrix[idx1][idx2] -= 1
                matrix[idx2][idx1] += 1
            if self.is_in_clusters((b, c)) and self.is_in_clusters((c, a)):
                idx1 = self.get_cluster_index_by_edge((b, c))
                idx2 = self.get_cluster_index_by_edge((c, a))
                matrix[idx1][idx2] -= 1
                matrix[idx2][idx1] += 1
            if self.is_in_clusters((c, a)) and self.is_in_clusters((a, b)):
                idx1 = self.get_cluster_index_by_edge((c, a))
                idx2 = self.get_cluster_index_by_edge((a, b))
                matrix[idx1][idx2] -= 1
                matrix[idx2][idx1] += 1
        
        for i, lamination in enumerate(self.laminations):
            for x, y in lamination:
                for p, q, sign in self.get_shear_coordinates(x, y):
                    matrix[n+i][self.get_cluster_index_by_edge((p, q))] = sign
            
        
        
        # Create column index for clusters
        col_index = [f'x_{i}' for i in self.cluster_names]
        
        # Create row index for clusters and laminations
        row_index = [f'x_{i}' for i in self.cluster_names] + [f'u_{i}' for i in self.lamination_names]
        
        return pd.DataFrame(matrix, index=row_index, columns=col_index)
    
    def flip(self, 
             edge: Tuple[int, int] = None,
             index: int = None):
        if index is not None:
            edge = self.clusters[index-1]
        elif not self.is_in_clusters(edge):
            raise ValueError("Edge is not a cluster edge")
        
        p, q = self.get_adjacent_edges(edge)
        x, y = edge
        
        idx = self.get_cluster_index_by_edge(edge)
        self.clusters[idx] = (p, q)
        self.cluster_names[idx] += "'"
        return self
    
    def get_var_index(self, name: str):
        if name.startswith("x_"):
            base = int(name.split('_')[1].rstrip("'"))
            primes = name.count("'")
            return base-1, primes
        elif name.startswith("u_"):
            return int(name.split('_')[1])-1
        else:
            raise ValueError("Variable name is not valid")
    
    def get_var_by_rowname(self, rowname: str):
        if rowname.startswith("x_"):
            # Extract base number and count primes
            base = int(rowname.split('_')[1].rstrip("'"))
            primes = rowname.count("'")
            return self.x[base-1][primes]
        elif rowname.startswith("u_"):
            return self.u[int(rowname.split('_')[1])-1]
        else:
            raise ValueError("Column name is not valid")
    
    
    def express_target(self, start: int, end: int):
        from copy import deepcopy
        q = deepcopy(self)
        
        relations = []
        expressions = []
        
        for e in q.get_intersecting_clusters(start, end):
            B = q.get_exchange_matrix()
            
            idx = q.get_cluster_index_by_edge(e)
            col = B[f'x_{q.cluster_names[idx]}']
            pos_vars = [q.get_var_by_rowname(B.index[i]) for i,v in enumerate(col) if v == 1]
            neg_vars = [q.get_var_by_rowname(B.index[i]) for i,v in enumerate(col) if v == -1]
            
            pos_term = reduce(lambda x, y: x*y, pos_vars, 1)
            neg_term = reduce(lambda x, y: x*y, neg_vars, 1)
            
            base, primes = q.get_var_index(B.columns[idx])
            
            relations.append(sp.Eq(q.x[base][primes] * q.x[base][primes+1], pos_term + neg_term))
            expressions.append(sp.Eq(q.x[base][primes+1], (pos_term + neg_term) / q.x[base][primes]))
            
            q.flip(edge=e)
        q.relations = relations
        q.expressions = expressions
        
        for i in range(len(q.expressions)-1):
            for j in range(i+1, len(q.expressions)):
                q.expressions[j] = q.expressions[j].subs(q.expressions[i].lhs, q.expressions[i].rhs).expand().simplify()
        
        # Expand only numerators of expressions
        for i in range(len(q.expressions)):
            expr = q.expressions[i]
            if isinstance(expr.rhs, sp.Mul):
                num, den = expr.rhs.as_numer_denom()
                q.expressions[i] = sp.Eq(expr.lhs, (num.expand() / den))

        return q
