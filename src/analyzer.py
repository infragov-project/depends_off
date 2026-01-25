from src.terraform_graph import Node, Dependency, ExplicitDependency
from src.graph import DAG, CycleError

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
        self.id_to_dependency = {dependency.id: dependency for dependency in dependencies}

        self.graph = DAG()
        for node in self.nodes:
            self.graph.node(node.id)

        for dependency in self.dependencies:
            try: self.graph.edge(dependency.id, dependency.dependee.id, dependency.depended.id, False)
            except CycleError: raise DependencyAnalyzerError(
                f'the dependency graph has a cycle: cycle detected while adding {dependency}'
            )

            if dependency.dependee != dependency.declaration:
                try: self.graph.edge(dependency.id, dependency.declaration.id, dependency.depended.id, True)
                except CycleError:
                    # We ignore this, since the declaration edge is not part of
                    # the actual dependency graph
                    pass

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
            self.graph.remove_edge(dependency.id, dependency.dependee.id)

        for node in self.nodes:
            print(node.id, node)

        # Check if any of the explicit dependencies is redundant
        explicit_dependencies.sort(key = self._dependency_to_key)
        redundant_dependencies: list[tuple[ExplicitDependency, list[Dependency]]] = list()
        possibly_redundant_dependencies: list[tuple[ExplicitDependency, list[Dependency]]] = list()

        for dependency in explicit_dependencies:
            path = self.graph.path(dependency.dependee.id, dependency.depended.id)
            if path is not None:
                used_avoids = path[1]
                path = [self.id_to_dependency[id] for id in path[0]]

                if not used_avoids:
                    redundant_dependencies.append((dependency, path))
                else:
                    possibly_redundant_dependencies.append((dependency, path))

            self.graph.edge(dependency.id, dependency.dependee.id, dependency.depended.id, False)

        return redundant_dependencies, possibly_redundant_dependencies

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
