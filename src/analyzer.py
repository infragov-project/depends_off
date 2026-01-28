from src.terraform_graph import Node, Dependency, ImplicitDependency, ExplicitDependency
from src.graph import DAG, Edge, CycleError

class DependencyAnalyzer:
    """
    Class that creates a dependency graph and finds redundant dependencies.
    """

    def __init__(self, nodes: list[Node], dependencies: list[Dependency]):
        """
        Initialize the dependency graph. An exception is raised if the graph has
        cycles.
        """
        self.nodes = nodes
        self.dependencies = dependencies
        self.id_to_node = {node.id: node for node in nodes}
        self.id_to_dependency = {dependency.id: dependency for dependency in dependencies}

        self.graph = DAG()
        for node in self.nodes:
            self.graph.node(node.id)

        # Dependencies are added as type 0 edges. Spurious dependencies ar
        # eadded as type 1 edges. Spurious dependencies are dependencies that
        # are not real but could be mistakenly identified, such as the one
        # presented in the readme. They are created when the dependency
        # declaration place is different from the dependee.
        # https://github.com/infragov-project/depends_off/?tab=readme-ov-file#on-redundant-dependencies

        for dependency in self.dependencies:
            try: self.graph.edge(Edge(dependency.id, 0, dependency.dependee.id, dependency.depended.id))
            except CycleError: raise DependencyAnalyzerError(
                f'the dependency graph has a cycle: cycle detected while adding {dependency}'
            )

        for dependency in self.dependencies:
            if type(dependency) is ImplicitDependency and dependency.dependee != dependency.declaration:
                try: self.graph.edge(Edge(dependency.id, 1, dependency.declaration.id, dependency.depended.id))
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

        # Check if any of the explicit dependencies is redundant
        explicit_dependencies.sort(key = self._dependency_to_key)
        redundant_dependencies: list[tuple[ExplicitDependency, list[Dependency]]] = list()
        possibly_redundant_dependencies: list[tuple[ExplicitDependency, list[Dependency]]] = list()

        for dependency in explicit_dependencies:

            # Try to find a path using only real dependencies (type 0). In this
            # case, the edge is guarateed to be redundant.
            path = self.graph.path(dependency.dependee.id, dependency.depended.id, [0])
            if path is not None:
                path = [self.id_to_dependency[id] for id in path]
                redundant_dependencies.append((dependency, path))

            else:
                # Try to find a path using real and spurious dependencies (type
                # 0 and 1). In this case, the edge might be redundant.
                path = self.graph.path(dependency.dependee.id, dependency.depended.id, [0, 1])
                if path is not None:
                    path = [self.id_to_dependency[id] for id in path]
                    possibly_redundant_dependencies.append((dependency, path))

            # Add the edge back to the graph once checked, so that it can be
            # used in the paths of subsequent dependencies.
            self.graph.edge(Edge(dependency.id, 0, dependency.dependee.id, dependency.depended.id))

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
