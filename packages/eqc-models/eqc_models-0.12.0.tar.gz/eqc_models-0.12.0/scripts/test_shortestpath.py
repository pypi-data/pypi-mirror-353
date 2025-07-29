import logging
import numpy as np
import networkx as nx
from eqc_models.graph.shortestpath import ShortestPathModel
from eqc_models.solvers import Dirac3DirectSolver, Dirac3ContinuousCloudSolver
from eqc_models.base.results import SolutionResults
logging.basicConfig(level=logging.INFO)
G = nx.DiGraph()
G.add_node("s")
G.add_node("t")
G.add_node("A")
G.add_node("B")
edges = [("s", "A", 10), ("s", "B", 20), ("A", "B", 10),
         ("A", "t", 40), ("B", "t", 5)]
for u, v, cost in edges:
    G.add_edge(u, v, weight=cost)

model = ShortestPathModel(G, "s", "t")
model.penalty_multiplier = 20
model.upper_bound = np.array([1 for x in model.variables])
model.machine_slacks = 1
if False:
    ip_addr = "172.18.41.28"
    port = "50051"
    solver = Dirac3DirectSolver()
    solver.connect(ip_addr=ip_addr, port=port)
    response = solver.solve(model, sum_constraint=4, num_samples=5, relaxation_schedule=1)
    solutions = response["solution"]
else:
    solver = Dirac3ContinuousCloudSolver()
    response = solver.solve(model, sum_constraint=4, num_samples=5, relaxation_schedule=1)
    results = SolutionResults.from_cloud_response(model, response, solver)
    solutions = results.solutions
print(model.variables)
for solution in solutions:
    print(solution)
path = model.decode(solutions[0])
print(path)
