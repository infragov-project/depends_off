from terraform_graph import Node, Dependency
from graph import DAG, CycleError

class DependencyAnalyzer:
    """
    Class that creates a dependency graph and finds redundant dependencies.
    """

    def __init__(self, nodes: list[Node], dependencies: list[Dependency]):
        """
        Initialize the dependency graph. A CycleError is raised if any of the
        edges creates a cycle.
        """
        self.nodes = nodes
        self.dependencies = dependencies

        self.graph = DAG()
        for node in self.nodes:
            self.graph.node(node.id)

        for dependency in self.dependencies:
            try: self.graph.edge(dependency.dependee_id, dependency.depended_id)
            except CycleError: raise DependencyAnalyzerError(
                f'the dependency graph has a cycle: cycle detected while adding {dependency}'
            )

    def redundant(self):
        """
        Retrieve the redundant explicit dependencies in the graph.
        """

        # Some of the edges will be removed, but we need to keep the original
        # ordering of the graph
        self.graph.toposort()

        # Remove the explicit edges and add them one by one such that, when an edge is
        # added, all the edges that an alternative path might have used have already
        # been added to the graph.

        explicit_dependencies = [d for d in self.dependencies if d.explicit]

        for dependency in explicit_dependencies:
            self.graph.remove_edge(dependency.dependee_id, dependency.depended_id)

        # Check if any of the explicit dependencies is redundant
        explicit_dependencies.sort(key = self._dependency_to_key)
        redundant_dependencies: list[Dependency] = list()

        for dependency in self.dependencies:
            if not dependency.explicit: continue

            if self.graph.path(dependency.dependee_id, dependency.depended_id):
                redundant_dependencies.append(dependency)
            
            self.graph.edge(dependency.dependee_id, dependency.depended_id)

        return redundant_dependencies

    def _dependency_to_key(self, dependency: Dependency):
        """
        Transform a dependency into a sorting key, such that the edges can be
        added one by one, and when one edge is inserted all the edges that an
        alternative path might have used have already been added to the graph.
        """

        # An edge X = (a, b) comes before an endge Y = (c, d) if it might be
        # part of a path from c to d. As such, a <= c and b >= d in the
        # topological ordering.

        a = self.graph.order(dependency.dependee_id)
        b = self.graph.order(dependency.depended_id)

        return (a, -b)
    
class DependencyAnalyzerError(Exception):
    pass
