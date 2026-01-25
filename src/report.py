import json
from src.terraform_graph import Node, Dependency, ExplicitDependency

type RedundantList = list[tuple[ExplicitDependency, list[Dependency]]]

class Report:
    """
    Class that represents the result of a redundant dependency analysis.
    """

    def __init__(self, nodes: list[Node], dependencies: list[Dependency], redundant: RedundantList, possibly_redundant: RedundantList):
        """
        Initialize the report with the given redundant dependencies.
        """
        self.nodes = nodes
        self.dependencies = dependencies
        self.redundant_dependencies = redundant
        self.possibly_redundant_dependencies = possibly_redundant

    def human_readable(self):
        """
        Generate a human-readable report of redundant dependencies.
        """

        result = str()
        result += f'Total nodes: {len(self.nodes)}\n'
        result += f'Total dependencies: {len(self.dependencies)}\n'

        if (len(self.redundant_dependencies) == 0): result += 'No redundant dependencies found.\n'
        else:
            result += 'Redundant dependencies:\n'
            for dependency, path in self.redundant_dependencies:
                result += f'\t{dependency} at {dependency.range} \n\tvia\t'
                result += '\n\t\t'.join(str(dependency) for dependency in path) + '\n'

        if (len(self.possibly_redundant_dependencies) == 0): result += 'No possibly redundant dependencies found.\n'
        else:
            result += 'Possibly redundant dependencies:\n'
            for dependency, path in self.possibly_redundant_dependencies:
                result += f'\t{dependency} at {dependency.range}\n\tvia\t'
                result += '\n\t\t'.join(str(dependency) for dependency in path) + '\n'

        return result
    
    def sarif(self):
        """
        Generate a SARIF report of redundant dependencies.
        """

        report = {
            'version': '2.1.0',
            '$schema': 'https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/schemas/sarif-schema-2.1.0.json',
            'runs': [{
                'tool': {
                    'driver': {
                        'name': 'depends_off',
                        'version': '1.0.0',
                        'informationUri': 'https://github.com/infragov-project/depends_off'
                    }
                },
                'results': [
                    self._sarif_result(dependency, path) for dependency, path in self.redundant_dependencies
                ]
            }]
        }

        return json.dumps(report, indent=4) + '\n'
    
    def _sarif_result(self, dependency: ExplicitDependency, path: list[Dependency]):
        """
        Generate a SARIF result for a redundant dependency.
        """

        result = {
            'ruleId': 'no-redundant-dependencies',
            'level': 'warning',
            'message': {
                'text': f'Redundant dependency found: {dependency} via\n\t' + '\n\t'.join(str(dependency) for dependency in path)
            },
            'locations': [{
                'physicalLocation': {
                    'artifactLocation': {
                        'uri': dependency.range.filename
                    },
                    'region': {
                        'startLine': dependency.range.start_line,
                        'startColumn': dependency.range.start_column,
                        'endLine': dependency.range.end_line,
                        'endColumn': dependency.range.end_column
                    }
                }
            }]
        }

        return result
