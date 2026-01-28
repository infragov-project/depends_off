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

        if len(self.redundant_dependencies) + len(self.possibly_redundant_dependencies) == 0: result += 'No redundant dependencies found.\n'
        
        if len(self.redundant_dependencies) > 0:
            result += 'Redundant dependencies:\n'
            for dependency, path in self.redundant_dependencies:
                result += f'\t{dependency.str_with_range()} \n\tvia\t'
                result += '\n\t\t'.join(str(dependency.str_with_range()) for dependency in path) + '\n'

        if len(self.possibly_redundant_dependencies) > 0:
            result += 'Possibly redundant dependencies:\n'
            for dependency, path in self.possibly_redundant_dependencies:
                result += f'\t{dependency.str_with_range()}\n\tvia\t'
                result += '\n\t\t'.join(str(dependency.str_with_range()) for dependency in path) + '\n'

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
                'results':
                    [self._sarif_redundant(dependency, path) for dependency, path in self.redundant_dependencies]
                    + [self._sarif_possibly_redundant(dependency, path) for dependency, path in self.possibly_redundant_dependencies]
            }]
        }

        return json.dumps(report, indent=4) + '\n'
    
    def _sarif_redundant(self, dependency: ExplicitDependency, path: list[Dependency]):
        """
        Generate a SARIF result for a redundant dependency.
        """

        result = {
            'ruleId': 'no-redundant-dependencies',
            'level': 'warning',
            'message': {
                'text': f'Redundant dependency found: {dependency}. There is a dependency chain that implies this dependency, via\n\t' + '\n\t'.join(str(dependency.str_with_range()) for dependency in path)
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
    
    def _sarif_possibly_redundant(self, dependency: ExplicitDependency, path: list[Dependency]):
        """
        Generate a SARIF result for a possibly redundant dependency.
        """

        result = {
            'ruleId': 'possibly-redundant-dependencies',
            'level': 'note',
            'message': {
                'text': f'Possibly redundant dependency found: {dependency}. There is a dependency chain that could imply this dependency, via\n\t' + '\n\t'.join(str(dependency.str_with_range()) for dependency in path)
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
