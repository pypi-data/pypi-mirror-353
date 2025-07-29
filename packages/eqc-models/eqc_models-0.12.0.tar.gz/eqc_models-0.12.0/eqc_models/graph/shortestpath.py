r"""
MIP Shortest Path implementation

Given a graph $G$ and nodes $s$ and $t$, find the shortest path
by edge weight between $s$ and $t$. 

$$
\min sum_ij w_ij x_ij
$$
subject to
$$
\sum_{(u,v)\in E} x_{u,v} - \sum{(v,u)\in E} x_{v,u} = 0 \forall u\in N\\{s,t}
$$
and
$$
\sum_{(s,v)\in E} x_{s,v} = 1
$$
and
$$
\sum_{(u,t)\in E} x_{u,t} = 1
$$

"""

from typing import Any, Dict, Tuple
import logging
import numpy as np
import networkx as nx
from eqc_models.graph import EdgeMixin
from eqc_models.base.quadratic import ConstrainedQuadraticModel

log = logging.getLogger(name=__name__)

class ShortestPathModel(EdgeMixin, ConstrainedQuadraticModel):
    """
    ShortestPathModel describes the MIP formulation for the 
    shortest path problem.

    Parameters
    -------------

    G : nx.DiGraph
        A directed graph which is assumed to be connected. A graph
        with disconnected subgraphs may reveal a solution if $s$ and $t$
        are in the same subgraph, but testing for the existence of a path
        between s and t using this model is not recommended. This is 
        due to the difficulty posed by selecting a penalty multiplier 
        large enough to enforce the panalties, which DNE in the infeasible 
        case.
    s : Any
        This is the label for the start node.
    t : Any
        This is the label for the end node.


    """

    def __init__(self, G: nx.DiGraph, s : Any, t : Any):
        self.G = G
        self.s = s
        self.t = t
        self.lhs, self.rhs = self.buildConstraints()
        C, J = self.buildObjective()
        super(ShortestPathModel, self).__init__(C, J, self.lhs, self.rhs)

    def buildConstraints(self) -> Tuple[np.ndarray,np.ndarray]:
        """
        Constraints: 
        $$
        sum_j x[i,l] - sum_j x[j,l] = c for all l
        $$
        $c$ is -1, 1 or 0 for $i=t$, $s$ or all others
        
        """
        log.info("Building constraints to find path from %s to %s", self.s, self.t)
        variables = self.variables
        nodes = [n for n in self.G.nodes]
        m = len(nodes)
        n = len(variables)
        _cons = np.zeros((m, n), dtype=np.int8)
        _rhs = np.zeros((m, 1), dtype=np.int8)
        for node_index, k in enumerate(nodes):
            if k == self.s:
                _rhs[node_index, 0] = 1
            elif k == self.t:
                _rhs[node_index, 0] = -1
        for l, (i, j) in enumerate(variables):
            if i == j:
                # self loops are not allowed
                raise ValueError("Self loops are not allowed in ShortestPathModel")
            # # ignore these edges because we can't go back to s or leave t
            elif j == self.s:
                continue
            elif i == self.t:
                continue
            i_index = nodes.index(i)
            j_index = nodes.index(j)
            _cons[i_index, l] = 1
            _cons[j_index, l] = -1
        log.info("LHS shape %s RHS shape %s", _cons.shape, _rhs.shape)
        log.info("checksum %f min %f", np.sum(_cons), np.min(_cons))
        assert np.sum(_rhs) == 0
        return _cons, np.squeeze(_rhs)

    def buildObjective(self) -> Tuple[np.ndarray, np.ndarray]:
        r"""
        Objective:
        $\min sum_ij w_ij x_ij$

        """
        variables = self.variables
        G = self.G
        nodes = G.nodes
        m, n = len(nodes), len(variables)
        _obj = [0 for i in range(n)]
        for index, name in enumerate(variables):
            i, j = name
            _obj[index] = v = G.get_edge_data(i, j)["weight"]
            assert not np.isnan(v), f"Got a NaN at {i, j}"
        J = np.zeros((n, n))
        return np.array(_obj), J

    def decode(self, solution : np.ndarray) -> Dict:
        """ 
        Convert a solution to this model into a path, which is
        a dictionary with each edge described by key, value pairs.

        """
        variables = self.variables

        lhs, rhs = self.constraints
        upper_thresh = max(solution)
        lower_thresh = 0
        while upper_thresh - lower_thresh > 1e-6:
            log.info("Lower Value: %f Upper Value %f", lower_thresh, upper_thresh)
            thresh = (lower_thresh + upper_thresh) / 2
            nx_path = None
            G = nx.DiGraph()
            for (i, j), value in zip(variables, solution):
                if value > thresh:
                    G.add_edge(i, j)
            path = {}
            try:
                nx_path = nx.shortest_path(G, self.s, self.t)
                upper_thresh = thresh
                lower_thresh = thresh
            except (nx.exception.NodeNotFound, nx.NetworkXAlgorithmError) as err:
                lower_thresh = thresh
        if nx_path is None:
            raise RuntimeError(f"Solution does not describe path from {self.s} to {self.t}")
        path = {}
        for i, v in enumerate(nx_path):
            path[nx_path[i-1]] = v
        if self.t in path:
            del path[self.t]
        return path

