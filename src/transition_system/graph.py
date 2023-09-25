# A representation of a directed, edge labeled graph.
# Made with the help of Adam Vandervorst

from bisect import bisect_right

EL = any


class DirectedGraph:
    """
    Represent a directed, edge labeled graph with an adjacency matrix. In the adjacency matrix, for each node a list
    of integers indicates with what other nodes it is connected.
    """
    def __init__(self, adjacency_graph: list[list[int], list[EL]] = None):
        if adjacency_graph:
            for ns, ls in adjacency_graph:
                assert(len(ns) == len(ls))      # the number of edges and edge labels needs to be the same
            self.adj = adjacency_graph
        else:
            self.adj = list[list[int], list[EL]]()

    def size(self) -> int:
        """
        :return: the number of nodes the graph has
        """
        return len(self.adj)

    def grow(self) -> int:
        """
        Add a node to the graph
        :return: The index of the new node
        """
        self.adj.append((list[int](), list[EL]()))
        return len(self.adj) - 1

    def nbs(self, i: int) -> list[int]:
        """
        :param i: Node index
        :return: All neighbours of node i
        """
        assert(i < len(self.adj))
        return self.adj[i][0]

    def add(self, i: int, j: int, l: EL) -> bool:
        """
        Add an edge between two nodes
        :param i: the node from which to draw an edge
        :param j: the node to which to draw an edge
        :param l: the edge label
        :return: False if the connection already existed, else True
        """
        assert(i < len(self.adj))
        existing = self.adj[i]
        j_idx = bisect_right(existing[0], j)
        if existing[0]:
            if existing[0][j_idx - 1] == j:
                return False
        existing[0].insert(j_idx, j)
        existing[1].insert(j_idx, l)
        return True

    def show(self, statelabels=None) -> str:
        """
        Generate the graphviz code of the graph which can be used to make an image of the graph.
        :param statelabels: Optional a label can be added for each state
        :return: Graphviz code as a string
        """
        trans = ""
        if not statelabels:
            statelabels = [i for i in range(self.size())]
        for n, (ts, ls) in enumerate(self.adj):
            for t in ts:
                trans = trans + f"{statelabels[n]} -> {statelabels[t]}; \n"

        return trans

