from bisect import bisect_right

EL = any


class DirectedGraph:
    def __init__(self, adjacency_graph: list[list[int], list[EL]] = None):
        if adjacency_graph:
            for ns, ls in adjacency_graph:
                assert(len(ns) == len(ls))
            self.adj = adjacency_graph
        else:
            self.adj = list[list[int], list[EL]]()

    def size(self) -> int:
        return len(self.adj)

    def grow(self) -> int:
        self.adj.append((list[int](), list[EL]()))
        return len(self.adj) - 1

    def nbs(self, i: int) -> list[int]:
        assert(i < len(self.adj))
        return self.adj[i][0]

    def add(self, i: int, j: int, l: EL) -> bool:
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
        trans = ""
        if not statelabels:
            statelabels = [i for i in range(self.size())]
        for n, (ts, ls) in enumerate(self.adj):
            for t in ts:
                trans = trans + f"{statelabels[n]} -> {statelabels[t]}; \n"

        return trans

