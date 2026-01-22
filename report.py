from terraform_graph import Dependency, Node

class Report:
    """
    Class that represents the result of a redundant dependency analysis.
    """

    def __init__(self, nodes: list[Node], dependencies: list[Dependency], redundant_dependencies: list[tuple[Dependency, list[Node]]]):
        """
        Initialize the report with the given redundant dependencies.
        """
        self.nodes = nodes
        self.dependencies = dependencies
        self.redundant_dependencies = redundant_dependencies

    def human_readable(self):
        """
        Generate a human-readable report of redundant dependencies.
        """

        result = str()
        result += 'Redundant Dependencies Report\n\n'
        result += f'Total nodes: {len(self.nodes)}\n'
        result += f'Total dependencies: {len(self.dependencies)}\n'

        if (len(self.redundant_dependencies) == 0): result += 'No redundant dependencies found.\n'
        else:
            result += 'Redundant dependencies:\n'
            for dependency, path in self.redundant_dependencies:
                result += f'\t{dependency}\n\tvia\t'
                result += ' ->\n\t\t'.join(str(node) for node in path) + '\n'

        return result 
