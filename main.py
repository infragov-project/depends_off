"""
A tool that detects redundant Terraform dependencies.

To parse the dependency graph of a given module and detect redundancies, provide
the tool with the path to the directory containing the module (or leave empty
for the current directory). The `--graph` command can be used to to output the
inferred dependency graph in DOT format, and the `--sarif` flag generate SARIF
output.

```
$ python3 main.py [directory] [--graph path.dot] [--sarif]
```
"""

import argparse
from src.parser import Parser
from src.analyzer import DependencyAnalyzer
from src.report import Report

argument_parser = argparse.ArgumentParser(usage='%(prog)s [directory]')
argument_parser.add_argument('directory', default='.', nargs='?')
argument_parser.add_argument('--graph')
argument_parser.add_argument('--sarif', action='store_true')
arguments = argument_parser.parse_args()

parser = Parser()
nodes, dependencies = parser.parse(arguments.directory)

analyzer = DependencyAnalyzer(nodes, dependencies)
if arguments.graph: analyzer.export(arguments.graph)
redundant, possibly_redundant = analyzer.redundant()

report = Report(nodes, dependencies, redundant, possibly_redundant)
if arguments.sarif: print(report.sarif(), end='')
else: print(report.human_readable(), end='')
