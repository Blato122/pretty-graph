import random
from deap import base, creator, tools, algorithms
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
import os
import shutil

random.seed(42)

"""
Graphs to produce a user-friendly representation of.
It is only necessary to specify the edges of a graph.
"""
graphs = {
  "triangle8": [ # triangular graph with 8 nodes
    (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),
    (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
    (3, 4), (3, 5), (3, 6), (3, 7), (3, 8),
    (4, 5), (4, 6), (4, 7), (4, 8),
    (5, 6), (5, 7), (5, 8),
    (6, 7), (6, 8),
    (7, 8)
  ],

  "star16": [ # star graph
      (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),
      (0, 10), (0, 11), (0, 12), (0, 13), (0, 14), (0, 15), (0, 16)
  ],

  "square3x3": [ # square 3x3 grid
    (1, 2), (1, 4),
    (2, 1), (2, 3), (2, 5),
    (3, 2), (3, 6),
    (4, 1), (4, 5), (4, 7),
    (5, 2), (5, 4), (5, 6), (5, 8),
    (6, 3), (6, 5), (6, 9),
    (7, 4), (7, 8),
    (8, 5), (8, 7), (8, 9),
    (9, 6), (9, 8)
  ],

  "simple": [ # simple
      (0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 3), (3, 4), (4, 0)
  ],

  "medium": [ # not so simple
      (4, 13), (13, 9), (9, 5), (9, 11), (11, 6), (6, 0),
      (6, 2), (0, 2), (2, 17), (17, 10), (17, 7), (7, 16),
      (7, 15), (10, 15), (0, 15), (15, 3), (17, 14), (3, 14),
      (1, 3), (1, 14), (1, 12), (1, 8), (12, 13), (8, 13)
  ],

  "K47": [ # K 4,7 graph (18 edge crossings)
      (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10),
      (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
      (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
      (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10),
  ],

  "chatgpt": [ # random graph with 25 nodes and 30 edges by chat gpt
    (1, 5), (1, 10), (1, 12), (1, 14), (1, 17), (1, 19), (2, 3), (2, 6),
    (2, 7), (2, 11), (2, 13), (2, 21), (3, 6), (3, 8), (3, 14), (4, 5),
    (4, 8), (4, 10), (4, 11), (4, 15), (5, 9), (5, 12), (5, 20), (6, 8),
    (6, 9), (7, 9), (7, 18), (7, 20), (8, 19)
  ]
}

for key, value in reversed(graphs.items()): # functions and os.makedirs() in that loop??
  print(key)
  edges = value
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
    Returns true if line segments 12 and 34 intersect.
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

    ba = np.array(nbr1) - np.array(node)
    bc = np.array(nbr2) - np.array(node)

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

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

  def edge_angle_min(ind):
    """
    Returns the minimum angle between graph edges.
    """

    layout_dict = graph_layout(ind)
    angles = []

    for node in nodes:
      nbrs = neighbors(node)
      if len(nbrs) >= 2:
        nbrs2 = nbrs[1:] + [nbrs[0]] # !
        for nbr1, nbr2 in zip(nbrs, nbrs2):
          angle = calculate_angle(layout_dict[nbr1], layout_dict[nbr2], layout_dict[node])
          angles.append(angle)
          # print(int(angle), nbr1, node, nbr2)

    return min(angles)

  def evaluate(ind):
    """
    Returns the fitness of an individual (a graph). It consists of 6 heuristic parameters, that is:
      1. the number of edge crossings
      2. the variance of the edge lengths
      3. the minimal distance of nodes to the nearest edge
      4. the variance of the inter-node distance
      5. the minimal distance between nodes
      6. the minimal angle between edges

    While creating fitness, I specified that I want to minimize the first two parameters and maximize the third one. We want
    a minimal number of edge crossings - the most important parameter. The variance of the edge lengths should be fairly low as well 
    in order for the graph to look nice - if the lengths vary a lot, the graph will be hard to read. The goal of maximizing the third 
    parameter is increasing the distance between nodes and the nearest edge - it should make the graph more readable.

    Later, I decided to add the 4th parameter which is the variance of the inter-node distance. The resulting graphs were
    already looking quite good but the nodes were often crammed together too much. This parameter will focus on achieving
    a more uniform distribution of distances between nodes. We will of course want to minimize it.

    5th parameter is quite similar to the 4th parameter (same function computes it). We will want to maximize the minimal distance between nodes
    so that the nodes aren't crammed together too much.

    6th parameter is very important as well. By maximizing the minimal angle between edges, the graph will become much more readable
    because there won't be any very small angles that cause edges to overlap.
    """

    # print(-edge_crossings(ind), node_node_dist(ind)[0], node_node_dist(ind)[1], edge_length_var(ind), node_edge_dist(ind), edge_angle_var(ind))
    return -edge_crossings(ind), -10*node_node_dist(ind)[0]+10*node_node_dist(ind)[1]-10*edge_length_var(ind)+10*node_edge_dist(ind)+5*edge_angle_min(ind), # normalize by assigning weights

  """
  Creates:
    -fitness that minimizes the first two objectives and maximize the third one
    -individual that's a simple list of floats (x, y coords of a node)
  """
  creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
  creator.create("Individual", list, fitness=creator.FitnessMulti)

  """
  Create the initializers for individuals containing random floating point numbers and for a population that contains them.
  """
  IND_SIZE = n*2 # x, y coords of each node
  toolbox = base.Toolbox()
  toolbox.register("attribute", random.random)
  toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)
  toolbox.register("population", tools.initRepeat, list, toolbox.individual)

  # MULTIPROCESSING:
  pool = multiprocessing.Pool()
  toolbox.register("map", pool.map)

  # TEST:
  # subfolder test-results
  ind1 = toolbox.individual()
  ind1.fitness.values = evaluate(ind1)
  print(ind1.fitness)
  layout = graph_layout(ind1)
  g = nx.Graph()
  g.add_nodes_from(nodes)
  g.add_edges_from(edges)
  nx.draw(g, pos=layout, with_labels=True)
  plt.savefig("NEW-RESULTS/test-results/random_" + key + ".png")
  plt.close()

  # TOOLBOX - OPERATORS:
  toolbox.register("mate", tools.cxUniform, indpb=0.2) # blend (alpha=0.2 - why? what is even that?), uniform, onepoint, twopoint
  toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2) # ?
  # toolbox.register("select", tools.selNSGA2, nd="standard") # needs eaMuPlusLambda?
  t = 5
  toolbox.register("select", tools.selTournament, tournsize=t) # back to 3 later?
  toolbox.register("evaluate", evaluate)

  # MAIN:
  NGEN = 10000
  MU = 15
  LAMBDA = 0 # 0 -> eaSimple, not 0 -> eaMuPlusLambda 
  CXPB = 0.2
  MUTPB = 0.7 

  pop = toolbox.population(n=MU)
  hof = tools.ParetoFront()
  algorithms.eaSimple(pop, toolbox, CXPB, MUTPB, NGEN, halloffame=hof, verbose=True);
  # algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, halloffame=hof, verbose=True);

  # kolejne testy:
  # tournsize inne?
  # na koncu, moze troche zmodyfikowac wagi
  # pozostali moze niech wyprobuja inne mate, mutate operatory

  # RESULTS:
  # folder results-ngen8000-x-y-z-...
  subfolder_name = "NEW-RESULTS/results_NGEN-" + str(NGEN) + "_MU-" + str(MU) + ("_LAMBDA-" + str(LAMBDA) + "_CXPB-" if LAMBDA != 0 else "_CXPB-") \
  + str(CXPB) + "_MUTPB-" + str(MUTPB) + ("_TOURNSIZE-" + str(t) + "_CXPB-" if t != 0 else "_NSGA2")
  # if os.path.exists(subfolder_name):
  #   shutil.rmtree(subfolder_name)
  os.makedirs(os.path.join(subfolder_name), exist_ok=True)
  os.makedirs(os.path.join(subfolder_name + "/selbest/"), exist_ok=True)
  os.makedirs(os.path.join(subfolder_name + "/hof/"), exist_ok=True)
  os.makedirs(os.path.join(subfolder_name + "/nx/"), exist_ok=True)


  # subfolder selbest
  best_individual = tools.selBest(pop, 1)[0]
  best_layout = graph_layout(best_individual)
  G = nx.Graph()
  G.add_nodes_from(nodes)
  G.add_edges_from(edges)
  nx.draw(G, pos=best_layout, with_labels=True, node_size=100, font_size=8)
  plt.text(0, 0, best_individual.fitness)
  plt.savefig(subfolder_name + "/selbest/" + key + ".png")
  print(best_individual.fitness)
  plt.close()

  # subfolder hof
  for i in range(0, 3):
      if i < len(hof.items):
        best_individual = hof.items[i]
        best_layout = graph_layout(best_individual)
        nx.draw(G, pos=best_layout, with_labels=True, node_size=100, font_size=8)
        plt.text(0, 0, best_individual.fitness)
        plt.savefig(subfolder_name + "/hof/hof_" + str(i) + "_" + key + ".png")
        print(best_individual.fitness)
        plt.close()


  # subfolder nx
  nx.draw(G, pos=nx.spring_layout(G), with_labels=True, node_size=100, font_size=8)
  plt.savefig(subfolder_name + "/nx/spring_" + key + ".png")
  plt.close()

  # nx.draw(G, pos=nx.spectral_layout(G), with_labels=True, node_size=100, font_size=8)
  # plt.savefig(subfolder_name + "/nx/spectral_" + key + ".png")
  # plt.close()

  # nx.draw(G, pos=nx.kamada_kawai_layout(G), with_labels=True, node_size=100, font_size=8)
  # plt.savefig(subfolder_name + "/nx/kamada_kawai_" + key + ".png")
  # plt.close()

  # try:
  #   nx.draw(G, pos=nx.planar_layout(G), with_labels=True, node_size=100, font_size=8)
  #   plt.savefig(subfolder_name + "/nx/planar_" + key + ".png")
  #   plt.close()
  # except Exception : pass

  # try:
  #   nx.draw(G, pos=nx.circular_layout(G), with_labels=True, node_size=100, font_size=8)
  #   plt.savefig(subfolder_name + "/nx/shell_" + key + ".png")
  #   plt.close()
  # except Exception : pass

  # try:
  #   nx.draw(G, pos=nx.shell_layout(G), with_labels=True, node_size=100, font_size=8)
  #   plt.savefig(subfolder_name + "/nx/shell_" + key + ".png")
  #   plt.close()
  # except Exception : pass

  #=============================================================#
