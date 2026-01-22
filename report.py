import json
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
                result += f'\t{dependency} at {dependency.range} \n\tvia\t'
                result += ' ->\n\t\t'.join(str(node) for node in path) + '\n'

        return result
    
    def sarif(self):
        """
        Generate a SARIF report of redundant dependencies.
        """

        report = {
            "version": "2.1.0",
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json",
            "runs": [
                {
                "tool": {
                    "driver": {
                    "name": "terraform-3d"
                    }
                },
                "results": [
                    self._sarif_result(dependency, path) for dependency, path in self.redundant_dependencies
                    ]
                }
            ]
        }

        return json.dumps(report, indent=4) + '\n'
    
    def _sarif_result(self, dependency: Dependency, path: list[Node]):
        """
        Generate a SARIF result for a redundant dependency.
        """

        result = {
            "ruleId": "no-redundant-dependencies",
            "level": "warning",
            "message": {
                "text": f'Redundant dependency found: {dependency} via\n\t' + ' ->\n\t'.join(str(node) for node in path)
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": dependency.range.filename
                    },
                    "region": {
                        "startLine": dependency.range.start_line,
                        "startColumn": dependency.range.start_column,
                        "endLine": dependency.range.end_line,
                        "endColumn": dependency.range.end_column
                    }
                }
            }]
        }

        return result
