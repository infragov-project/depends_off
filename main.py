from parser import Parser
from analyzer import DependencyAnalyzer, DependencyAnalyzerError

# Parse the Terraform file

resources, dependencies = Parser.parse('test.tf')

print('resources:')
for resource in resources: print(resource)
print()
print('dependencies:')
for dependency in dependencies: print(dependency)
print()

# Search for redundant dependencies

try: analyzer = DependencyAnalyzer(resources, dependencies)
except DependencyAnalyzerError as e:
    print(e)
    exit(1)

redundant_dependencies = analyzer.redundant()

if len(redundant_dependencies) == 0:
    print('no redundant dependencies found')
for dependency in redundant_dependencies:
    print(f'redundant dependency found: {dependency}')
