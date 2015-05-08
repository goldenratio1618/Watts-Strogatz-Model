import random as rand
import matplotlib.pyplot as plt
import sys
import queue as q

class Graph:
    """ Initializes a graph with specified vertices and edges.
    
        The graph is by default undirected. Edges must be ascending (i.e. (2,3)
        is allowed but (3,2) is not); this comes into play later when we're
        randomizing things.
    """
    def __init__(self, num_vertices, edges):
        self.num_vertices = num_vertices
        self.edges = edges
        # Stores which vertices are neighbors of a given vertex
        # E.g. the 5th element of neighbors is a list of all vertices that
        # share an edge with vertex 5.
        self.neighbors = [[] for i in range(self.num_vertices)]
        for e in self.edges:
            self.neighbors[e[0]].append(e[1])
            self.neighbors[e[1]].append(e[0])
            
        self.all_possible_edges = []
        for a in range(num_vertices):
            for b in range(a):
                self.all_possible_edges.append((b,a))
    
    """ Calculates the clustering coefficient of this graph."""
    def clustering_coefficient(self):
        avg_cluster = 0
        for i in range(self.num_vertices):
            for j in range(len(self.neighbors[i])):
                for k in range(j):
                    if self.neighbors[i][k] in self.neighbors[self.neighbors[i][j]]:
                        avg_cluster = (i * avg_cluster + 1) / (i + 1)
                    else:
                        avg_cluster = avg_cluster * i / (i + 1)
        return avg_cluster
    
    """ Determines the lengths of the shortest paths between a given vertex and all other vertices. """
    def shortest_path(self, v1):
        queue = q.Queue()
        # The queue stores vertices, together with how many edges we had
        # to traverse to get to that vertex
        queue.put((v1, 0))
        # dictionary of vertex to its shortest length from this vertex
        # also doubles as a list of vertices we've seen before
        shortest_lengths = {v1: 0}
        while not queue.empty():
            v = queue.get()
            for neighbor in self.neighbors[v[0]]:
                # don't add anything to the queue if we've already seen the vertex
                if not (neighbor in shortest_lengths):
                # increment the length by 1, since we had to travel another edge
                    queue.put((neighbor, v[1] + 1))
                    shortest_lengths[neighbor] = v[1] + 1
        # the graph is disconnected; no path exists
        return shortest_lengths
        
    """ Calculates the average shortest path between any two vertices.
    
        This method is very slow (it has to calculate a shortest path between
        all pairs of vertices).
    """
    def shortest_path_len(self):
        avg = 0
        count = 0
        # number of random trials
        for v1 in range(self.num_vertices):
            sp = self.shortest_path(v1)
            for v2 in range(v1):
                # ignore cases where the graph was not connected
                if v2 in sp:
                    avg = (avg * count + sp[v2]) / (count + 1)
                    count += 1
        return avg
    
    """ Calculates average shortest path based on only 20 starting vertices.
    
        These vertices are chosen randomly. This method is a lot faster,
        due to using only 20 instead of num_vertices vertices. But it's also
        likely slightly less accurate.
    """
    def shortest_path_len_random(self):
        avg = 0
        count = 0
        for i in range(20):
            v1 = rand.randint(0, self.num_vertices - 1)
            sp = self.shortest_path(v1)
            for v2 in range(self.num_vertices):
                # ignore cases where the graph was not connected
                if v2 in sp:
                    avg = (avg * count + sp[v2]) / (count + 1)
                    count += 1
        return avg
        
    """ Each edge is swapped for a completely random edge with probability p.

        A new graph with the new edge set is returned.
    """
    def randomize_graph(self, p):
        new_edges = list(self.edges)
        for i in range(len(self.edges)):
            if rand.random() < p:
                new_edge = self.all_possible_edges[rand.randint(0,len(self.all_possible_edges) - 1)]
                # no duplicate edges
                while new_edge in new_edges:
                    new_edge = self.all_possible_edges[rand.randint(0,len(self.all_possible_edges) - 1)]
                new_edges[i] = new_edge
        return Graph(self.num_vertices, new_edges)
        
        
    """ Makes a geographic graph whereby vertices within a certain distance are
            connected by edges. Assumes separation << num_vertices """
    @staticmethod
    def make_graph(num_vertices, separation):
        edges = []
        for i in range(num_vertices):
            for j in range(i - separation, i):
                if j < 0:
                    edges.append((i, j + num_vertices))
                else:
                    edges.append((i, j))
                    
        return Graph(num_vertices, edges)

        
# initialize 100 graphs, so as to have lower statistical error
graphs = [Graph.make_graph(1000, 5)] * 100
clustering_coeffs = []
avg_shortest_paths = []
num_datapoints = 100
domain = list(map(lambda x : 1.1 ** (x - 99), range(num_datapoints)))
for i in range(num_datapoints):
    print("Datapoint " + str(i))
    sys.stdout.flush()
    new_cc_sum = 0
    new_sp_sum = 0
    count = 0
    for g in graphs:
        print("Graph " + str(count))
        sys.stdout.flush()
        count += 1
        new_g = g.randomize_graph(domain[i])
        new_cc_sum += new_g.clustering_coefficient()
        new_sp_sum += new_g.shortest_path_len_random()
    clustering_coeffs.append(new_cc_sum/len(graphs))
    avg_shortest_paths.append(new_sp_sum/len(graphs))
    
clustering_coeffs = list(map(lambda x : x/clustering_coeffs[0], clustering_coeffs))
avg_shortest_paths = list(map(lambda x : x/avg_shortest_paths[0], avg_shortest_paths))
plt.semilogx(domain, clustering_coeffs)
plt.semilogx(domain, avg_shortest_paths)
plt.show()
