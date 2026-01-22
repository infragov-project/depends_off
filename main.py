from parser import Parser
from analyzer import DependencyAnalyzer
from report import Report
import argparse

argument_parser = argparse.ArgumentParser(usage='%(prog)s [directory]')
argument_parser.add_argument('directory', default='.', nargs='?')
argument_parser.add_argument('--graph')
argument_parser.add_argument('--sarif', action='store_true')
arguments = argument_parser.parse_args()

parser = Parser()
nodes, dependencies = parser.parse(arguments.directory)

analyzer = DependencyAnalyzer(nodes, dependencies)
if arguments.graph: analyzer.export(arguments.graph)
redundant = analyzer.redundant()

report = Report(nodes, dependencies, redundant)
if arguments.sarif: print(report.sarif(), end='')
else: print(report.human_readable(), end='')
