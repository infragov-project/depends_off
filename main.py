from parser import Parser
from analyzer import DependencyAnalyzer
import argparse

argument_parser = argparse.ArgumentParser(usage='%(prog)s [directory]')
argument_parser.add_argument('directory', default='.', nargs='?')
argument_parser.add_argument('--graph')
arguments = argument_parser.parse_args()

parser = Parser()
nodes, dependencies = parser.parse(arguments.directory)

analyzer = DependencyAnalyzer(nodes, dependencies)
redundant = analyzer.redundant()

print(f'Total nodes: {len(nodes)}')
print(f'Total dependencies: {len(dependencies)}')
print(f'Redundant dependencies: {len(redundant)}')
for dependency, path in redundant:
    print(f'\t{dependency} via')
    print('\t\t' + ' ->\n\t\t'.join(str(node) for node in path))

if arguments.graph:
    analyzer.export(arguments.graph)
    print(f'Dependency graph exported to {arguments.graph}')
