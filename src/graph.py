class Graph:
    """
    Simple directed graph
    """

    def __init__(self):
        self.nodes: set[int] = set()
        # edges matches a node to a list of its outgoing edges
        self.edges: dict[int, list[tuple[int, int]]] = dict()

    def node(self, node: int):
        """
        Add a node to the graph
        """
        self.nodes.add(node)
        self.edges[node] = list()
    
    def edge(self, id: int, u: int, v: int):
        """
        Add an edge from u to v
        """
        self.edges[u].append((id, v))
    
    def remove_edge(self, id: int, u: int):
        """
        Remove the edge from u to v
        """
        self.edges[u] = [edge for edge in self.edges[u] if edge[0] != id]
    
    def path(self, u: int, v: int):
        """
        Check if there is a path from u to v and return path edges.
        """
        return self._dfs(u, v, set())

    def _dfs(self, u: int, v: int, visited: set[int]) -> list[int] | None:
        """
        Depth-first search to find a path from u to v and return path edges.
        """
        if u == v: return []

        visited.add(u)
        for edge in self.edges[u]:
            if edge[1] not in visited:
                path = self._dfs(edge[1], v, visited)
                if path is not None:
                    return [edge[0]] + path
        return None
    
class DAG(Graph):
    """
    Simple directed acyclic graph
    """

    def edge(self, id: int, u: int, v: int):
        """
        Add an edge from u to v. If the edge creates a cycle, a CycleError is
        raised.
        """
        if self.path(v, u):
            raise CycleError()
        super().edge(id, u, v)

    def toposort(self):
        """
        Perform a topological sort of the graph. The order of a vertex can be
        found using the order() method after the topological sort.
        """

        # Topological sort is done using DFS. A DFS is made for each unvisited
        # node, and the nodes visited in the DFS are recorded. In each of those
        # segments, a node comes before all of its children. This segment is
        # thus in reverse topological order. If a node was not visited once a
        # new segment starts, none of the previous nodes points to it, but it
        # may point to one of them. As such, each new segment comes after all
        # previous ones in the topological sort.
        visited: set[int] = set()
        sorted: list[int] = list()

        for node in self.nodes:
            if node not in visited:
                segment: list[int] = list()
                self._toposort_dfs(node, visited, segment)
                sorted += segment
        
        sorted.reverse()
        self.topo_order = {node: i for i, node in enumerate(sorted)}
    
    def order(self, u: int):
        """
        Get the order of a node in the last topological sort
        """
        return self.topo_order[u]
    
    def _toposort_dfs(self, u: int, visited: set[int], segment: list[int]):
        visited.add(u)

        for edge in self.edges[u]:
            if edge[1] not in visited:
                self._toposort_dfs(edge[1], visited, segment)

        segment.append(u)
        return segment

class CycleError(Exception):
    pass
