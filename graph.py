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

class CycleError(Exception):
    pass
