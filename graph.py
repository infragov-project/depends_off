class Graph:
    def __init__(self):
        self.nodes = set()
        # edges matches a node to a list of its outgoing edges
        self.edges = dict()

    def node(self, node):
        self.nodes.add(node)
        self.edges[node] = list()
    
    def edge(self, u, v):
        self.edges[u].append(v)
    
    def remove_edge(self, u, v):
        self.edges[u].remove(v)
    
    def path(self, u, v):
        return self.dfs(u, v, set())

    def dfs(self, u, v, visited):
        if u == v: return True

        visited.add(u)
        for neighbor in self.edges[u]:
            if neighbor not in visited:
                if self.dfs(neighbor, v, visited):
                    return True
        return False
    
class DAG(Graph):
    def edge(self, u, v):
        if self.path(v, u):
            raise CycleError()
        super().edge(u, v)

    def toposort(self):
        # Topological sort is done using DFS. A DFS is made for each unvisited
        # node, and the nodes visited in the DFS are recorded. In each of those
        # segments, a node comes before all of its children. This segment is
        # thus in reverse topological order. If a node was not visited once a
        # new segment starts, none of the previous nodes points to it, but it
        # may point to one of them. As such, each new segment comes after all
        # previous ones in the topological sort.
        visited = set()
        sorted = list()

        for node in self.nodes:
            if node not in visited:
                segment = list()
                self._toposort_dfs(node, visited, segment)
                sorted += reversed(segment)

        self.topo_order = {node: i for i, node in enumerate(sorted)}
    
    def order(self, u):
        return self.topo_order[u]
    
    def _toposort_dfs(self, u, visited, segment):
        visited.add(u)
        segment.append(u)

        for neighbor in self.edges[u]:
            if neighbor not in visited:
                self._toposort_dfs(neighbor, visited, segment)

        return segment

class CycleError(Exception):
    pass
