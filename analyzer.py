from resources import Resource, Dependency
from graph import DAG

class DependencyAnalyzer:
    """
    Class that creates a dependency graph and finds redundant dependencies.
    """

    def __init__(self, resources: list[Resource], dependencies: list[Dependency]):
        """
        Initialize the dependency graph. A CycleError is raised if any of the
        edges creates a cycle.
        """
        self.resources = resources
        self.dependencies = dependencies

        self.graph = DAG()

        self.resources_to_node: dict[str, int] = dict()
        for i, resource in enumerate(self.resources):
            self.graph.node(i)
            self.resources_to_node[resource.id()] = i

        for dependency in self.dependencies:
            u = self.resources_to_node[dependency.dependee]
            v = self.resources_to_node[dependency.depended]
            self.graph.edge(u, v)

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
            u = self.resources_to_node[dependency.dependee]
            v = self.resources_to_node[dependency.depended]
            self.graph.remove_edge(u, v)

        # Check if any of the explicit dependencies is redundant
        explicit_dependencies.sort(key = self._dependency_to_key)
        redundant_dependencies: list[Dependency] = list()

        for dependency in self.dependencies:
            if not dependency.explicit: continue

            u = self.resources_to_node[dependency.dependee]
            v = self.resources_to_node[dependency.depended]

            if self.graph.path(u, v):
                redundant_dependencies.append(dependency)
            
            self.graph.edge(u, v)

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

        u = self.resources_to_node[dependency.dependee]
        v = self.resources_to_node[dependency.depended]

        a = self.graph.order(u)
        b = self.graph.order(v)

        return (a, -b)
