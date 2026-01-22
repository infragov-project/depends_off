from parser import Parser
from analyzer import DependencyAnalyzer
from report import Report
import argparse

argument_parser = argparse.ArgumentParser(usage='%(prog)s [directory]')
argument_parser.add_argument('directory', default='.', nargs='?')
argument_parser.add_argument('--graph')
arguments = argument_parser.parse_args()

parser = Parser()
nodes, dependencies = parser.parse(arguments.directory)

analyzer = DependencyAnalyzer(nodes, dependencies)
redundant = analyzer.redundant()

report = Report(nodes, dependencies, redundant)
print(report.human_readable(), end='')

if arguments.graph:
    analyzer.export(arguments.graph)
    print(f'Dependency graph exported to {arguments.graph}')
