from terraform_graph import Node, Dependency, ExplicitDependency
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
        self.id_to_node = {node.id: node for node in nodes}

        self.graph = DAG()
        for node in self.nodes:
            self.graph.node(node.id)

        for dependency in self.dependencies:
            try: self.graph.edge(dependency.dependee.id, dependency.depended.id)
            except CycleError:
                path = self.graph.path(dependency.depended.id, dependency.dependee.id)
                path = [self.id_to_node[id] for id in path] if path is not None else []
                for p in path:
                    print(f'    {p}')
                raise DependencyAnalyzerError(
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

        explicit_dependencies = [d for d in self.dependencies if type(d) is ExplicitDependency]

        for dependency in explicit_dependencies:
            self.graph.remove_edge(dependency.dependee.id, dependency.depended.id)

        # Check if any of the explicit dependencies is redundant
        explicit_dependencies.sort(key = self._dependency_to_key)
        redundant_dependencies: list[tuple[ExplicitDependency, list[Node]]] = list()

        for dependency in explicit_dependencies:
            path = self.graph.path(dependency.dependee.id, dependency.depended.id)
            if path is not None:
                path = [self.id_to_node[id] for id in path]
                redundant_dependencies.append((dependency, path))
            
            self.graph.edge(dependency.dependee.id, dependency.depended.id)

        return redundant_dependencies

    def _dependency_to_key(self, dependency: ExplicitDependency):
        """
        Transform a dependency into a sorting key, such that the edges can be
        added one by one, and when one edge is inserted all the edges that an
        alternative path might have used have already been added to the graph.
        """

        # An edge X = (a, b) comes before an endge Y = (c, d) if it might be
        # part of a path from c to d. As such, a >= c and b <= d in the
        # topological ordering.

        a = self.graph.order(dependency.dependee.id)
        b = self.graph.order(dependency.depended.id)

        return (-a, b)
    
    def export(self, filename: str):
        """
        Create a DOT file with the dependency graph.
        """

        with open(filename, 'w') as f:
            f.write('digraph G {\n')

            for node in self.nodes:
                f.write(f'    {node.id} [label="{node}"];\n')

            for dependency in self.dependencies:
                style = 'dashed' if type(dependency) is not ExplicitDependency else 'solid'
                f.write(f'    {dependency.dependee.id} -> {dependency.depended.id} [style={style}];\n')

            f.write('}\n')
    
class DependencyAnalyzerError(Exception):
    pass
