class Edge:
    """
    This class represents a directed edge in a graph, with an associated type.
    """

    def __init__(self, id: int, type: int, origin: int, destination: int):
        self.id = id
        self.type = type
        self.origin = origin
        self.destination = destination

class Graph:
    """
    This class represents a directed graph whose edges have an associated type.
    """

    def __init__(self):
        self.nodes: set[int] = set()
        # edges matches a node to a list of its outgoing edges
        self.edges: dict[int, list[Edge]] = dict()

    def node(self, node: int):
        """
        Add a node to the graph
        """
        self.nodes.add(node)
        self.edges[node] = list()

    def edge(self, edge: Edge):
        """
        Add an edge to the graph
        """
        self.edges[edge.origin].append(edge)

    def remove_edge(self, id: int, u: int):
        """
        Remove the edge from u that has a given id. While not strictly needed,
        the u parameter avoids searching all nodes for the edge.
        """
        self.edges[u] = [edge for edge in self.edges[u] if edge.id != id]

    def path(self, u: int, v: int, allowed: list[int] | None = None):
        """
        Check if there is a path from u to v using the allowed edge types and
        return path edges. If the allowed type list is None, all edges are used.
        """
        return self._dfs(u, v, allowed, set())

    def _dfs(self, u: int, v: int, allowed: list[int] | None, visited: set[int]) -> list[int] | None:
        """
        Depth-first search to find a path from u to v, using the edges whose
        type is allowed. Returns the list of edge ids in the path.
        """

        if u == v: return []

        visited.add(u)

        for edge in self.edges[u]:
            if allowed is not None and edge.type not in allowed: continue

            if edge.destination not in visited:
                path = self._dfs(edge.destination, v, allowed, visited)
                if path is not None:
                    return [edge.id] + path

        return None

class DAG(Graph):
    """
    This class represents a Directed Acyclic Graph whose edges have an
    associated type.
    """

    def edge(self, edge: Edge):
        """
        Add an edge to the graph. If the edge creates a cycle, a CycleError is
        raised.
        """
        if self.path(edge.destination, edge.origin):
            raise CycleError()
        super().edge(edge)

class CycleError(Exception):
    pass
