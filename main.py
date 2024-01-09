import random
!pip install deap
from deap import base, creator, tools, algorithms
import networkx as nx
import numpy as np
import math

random.seed(42)

"""
Creating a graph to produce a user-friendly representation of.
It is only necessary to specify the edges of a graph.
"""

a = [ # star graph
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),
    (0, 10), (0, 11), (0, 12), (0, 13), (0, 14), (0, 15), (0, 16)
]

b = [ # square 4x4 grid
    (1, 2), (1, 5), (2, 1), (2, 3), (2, 6),
    (3, 2), (3, 4), (3, 7), (4, 3), (4, 8),
    (5, 1), (5, 6), (5, 9), (6, 2), (6, 5), (6, 7), (6, 10),
    (7, 3), (7, 6), (7, 8), (7, 11), (8, 4), (8, 7), (8, 12),
    (9, 5), (9, 10), (9, 13), (10, 6), (10, 9), (10, 11), (10, 14),
    (11, 7), (11, 10), (11, 12), (11, 15), (12, 8), (12, 11), (12, 16),
    (13, 9), (13, 14), (14, 10), (14, 13), (14, 15),
    (15, 11), (15, 14), (15, 16), (16, 12), (16, 15)
]

c = [ # simple
    (0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 3), (3, 4), (4, 0)
]

d = [ # not so simple
    (4, 13), (13, 9), (9, 5), (9, 11), (11, 6), (6, 0),
    (6, 2), (0, 2), (2, 17), (17, 10), (17, 7), (7, 16),
    (7, 15), (10, 15), (0, 15), (15, 3), (17, 14), (3, 14),
    (1, 3), (1, 14), (1, 12), (1, 8), (12, 13), (8, 13)
]

e = [ # K 4,7 graph (18 edge crossings)
    (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
    (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
    (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
    (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10),
]

edges = e
nodes = set(node for edge in edges for node in edge)
n = len(nodes)

def graph_layout(ind):
  """
  Creates a dictionary with node numbers as keys and x, y node coordinates as values.
  Node coords are retrieved from an individual that stores them in a flat list: [x1, y1, x2, y2, ...].
  """

  node_coords = [(ind[i], ind[i+1]) for i in range(0, len(ind), 2)]
  layout_dict = {node: coords for node, coords in zip(nodes, node_coords)}
  return layout_dict

def ccw(A,B,C):
	return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0]) # 0 <-> x, 1 <-> y

def _intersect(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def intersect(x1, y1, x2, y2, x3, y3, x4, y4):
  """
  Return true if line segments 12 and 34 intersect.
  """
  return _intersect((x1, y1), (x2, y2), (x3, y3), (x4, y4))

def edge_crossings(ind):
  """
  Returns the number of edge crossings in a graph.
  """

  layout_dict = graph_layout(ind)
  crossings = 0

  checked_edges = []

  for edge1 in edges:
        x1, y1 = layout_dict[edge1[0]]
        x2, y2 = layout_dict[edge1[1]]

        for edge2 in edges:
            if edge1 != edge2 and set([edge1, edge2]) not in checked_edges: # in - problem?
                nodes = set([*edge1, *edge2])
                if len(nodes) != 4: continue # explain

                x3, y3 = layout_dict[edge2[0]]
                x4, y4 = layout_dict[edge2[1]]

                checked_edges.append(set([edge1, edge2]))

                if intersect(x1, y1, x2, y2, x3, y3, x4, y4):
                  # print(edge1, edge2)
                  crossings += 1

  return crossings

def edge_length_var(ind):
  """
  Returns the variance of the lengths of graph edges.
  """

  layout_dict = graph_layout(ind)
  edge_lengths = []

  for edge in edges:
    x1, y1 = layout_dict[edge[0]]
    x2, y2 = layout_dict[edge[1]]
    len = ((x1-x2)**2 + (y1-y2)**2)**0.5
    edge_lengths.append(len)

  return np.var(edge_lengths)

def node_node_dist(ind):
  """
  Returns the variance of the distances between nodes and
  returns the minimal distance between nodes.
  """

  layout_dict = graph_layout(ind)
  dists = []

  for node1 in nodes:
    x1, y1 = layout_dict[node1]
    for node2 in nodes:
      if node1 != node2:
        x2, y2 = layout_dict[node2]
        dist = ((x1-x2)**2 + (y1-y2)**2)**0.5
        dists.append(dist)

  return np.var(dists), min(dists) # idk if both are necessary but I think so, they are responsible for different things

def distance_to_edge(node_coords, edge_coords):
    """
    Returns the distance from a node to its nearest point on an edge (at 90 degrees).
    """

    x0, y0 = node_coords
    x1, y1 = edge_coords[0]
    x2, y2 = edge_coords[1]

    # calculate coords of a point that's in the middle of the edge
    mx = (x1+x2)/2
    my = (y1+y2)/2

    # calculate the distance between the node and the middle of the edge
    dist = ((x0-mx)**2 + (y0-my)**2)**0.5
    return dist

def node_edge_dist(ind):
  """
  Returns the minimum distance between the nodes and the edges.
  """

  layout_dict = graph_layout(ind)
  dists = []

  for node, coords in layout_dict.items():
    # find the nearest edge for each node
    nearest_edge_distance = min(distance_to_edge(coords, (layout_dict[edge[0]], layout_dict[edge[1]])) for edge in edges)
    dists.append(nearest_edge_distance)

  return min(dists)

def calculate_angle(nbr1, nbr2, node):
  """
  Calculates the angle between 3 2d points, node being the center one.
  """

  ang = math.degrees(math.atan2(nbr2[1]-node[1], nbr2[0]-node[0]) - math.atan2(nbr1[1]-node[1], nbr1[0]-node[0]))
  return ang + 360 if ang < 0 else ang

def neighbors(node):
  """
  Returns a list of neighbors of a given node.
  """

  nbrs = set()
  for edge in edges:
      if node in edge:
          nbrs.update(edge)

  nbrs.remove(node)  # remove the original node from the neighbors
  return list(nbrs)

def edge_angle_var(ind):
  """
  Returns the variance of the angles between graph edges.
  """

  layout_dict = graph_layout(ind)
  angles = []

  for node in nodes:
    nbrs = neighbors(node)
    if len(nbrs) >= 2:
      for nbr1, nbr2 in zip(nbrs, nbrs[1:]):
        angles.append(calculate_angle(layout_dict[nbr1], layout_dict[nbr2], layout_dict[node]))
        # tutaj dodac do jakichs temp angles, z nich usunac max i potem dodac reszte do angles?? moze (i jeszcze dodac kat pierwszego z ostatnim)

  return np.var(angles)

def evaluate(ind):
  """
  Returns the fitness of an individual (a graph). It consists of 6 heuristic parameters, that is:
    1. the number of edge crossings
    2. the variance of the edge lengths
    3. the minimal distance of nodes to the nearest edge
    4. the variance of the inter-node distance
    5. the minimal distance between nodes
    6. the variance of the edge angles at every node

  While creating fitness, I specified that I want to minimize the first two parameters and maximize the third one. We want
  a minimal number of edge crossings. The variance of the edge lengths should be fairly low as well in order for the graph
  to look nice - if the lengths vary a lot, the graph will be hard to read. The goal of maximizing the third parameter is increasing
  the distance between nodes and the nearest edge - it should make the graph more readable.

  Later, I decided to add the 4th parameter which is the variance of the inter-node distance. The resulting graphs were
  already looking quite good but the nodes were often crammed together too much. This parameter will focus on achieving
  a more uniform distribution of distances between nodes. We will of course want to minimize it.

  5th parameter is quite similar to the 4th parameter (same function computes it). We will want to maximize the minimal distance between nodes
  so that the nodes aren't crammed together too much.

  6th parameter is very important as well. By minimizing the variance of the edge angles at every node, the graph will become much more readable
  because the angles will be more uniform.
  """

  return edge_crossings(ind), edge_length_var(ind), node_edge_dist(ind), node_node_dist(ind)[0], node_node_dist(ind)[1], edge_angle_var(ind) # ordering DOES matter! + normalize??

"""
Creates:
  -fitness that minimizes the first two objectives and maximize the third one
  -individual that's a simple list of floats (x, y coords of a node)
"""

creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -10.0, 10.0, -10.0, 10.0, -0.001)) # weights don't work with some selection operators??
creator.create("Individual", list, fitness=creator.FitnessMulti)

"""
Create the initializers for individuals containing random floating point numbers and for a population that contains them.
"""

IND_SIZE = n * 2 # x, y coords of each node

toolbox = base.Toolbox()
toolbox.register("attribute", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# # test
# ind1 = toolbox.individual()
# print(ind1)
# print(ind1.fitness.valid)

# # test 2
# ind1.fitness.values = evaluate(ind1)
# print(ind1.fitness.valid)
# print(ind1.fitness)

layout = graph_layout(ind1)

g = nx.Graph()
g.add_nodes_from(nodes)
g.add_edges_from(edges)
nx.draw(g, pos=layout, with_labels=True)

toolbox.register("mate", tools.cxUniform, indpb=0.2) # blend (alpha=0.2 - why? what is even that?), uniform, onepoint, twopoint
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2) # ?
toolbox.register("select", tools.selNSGA2, nd="standard") # some Pareto stuff + https://groups.google.com/g/deap-users/c/d9vi86HpypU + need eaMuPlusLambda?
toolbox.register("evaluate", evaluate)

NGEN = 30
MU = 500
LAMBDA = 2000
CXPB = 0.5 # SWITCH THEM BACK LATER! (or maybe not lol)
MUTPB = 0.5

# experiment with different orderings of the objectives + maybe run more gens once and that's it I think

pop = toolbox.population(n=MU)
hof = tools.ParetoFront()
algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, halloffame=hof, verbose=True);

best_individual = hof.items[0]
best_layout = graph_layout(best_individual)

G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

nx.draw(G, pos=best_layout, with_labels=True)
print(best_individual.fitness)

#=============================================================#
