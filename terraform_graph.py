from __future__ import annotations

class Range:
    def __init__(self, start_line: int, start_column: int, end_line: int, end_column: int):
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

    def __str__(self):
        return f'{self.start_line}:{self.start_column}-{self.end_line}:{self.end_column}'
    
class Node:
    _id_counter = 0

    def __init__(self, name: str, range: Range | None = None):
        self.id = Node._id_counter
        Node._id_counter += 1
        self.name = name
        self.range = range

    def __str__(self):
        return self.name
    
class Provider(Node):
    def __init__(self, name: str, alias: str | None, range: Range):
        if alias: name = f'{name}.{alias}'
        else: name = name

        super().__init__(name, range)
    
class Variable(Node):
    def __init__(self, name: str, range: Range):
        super().__init__(name, range)
    
class Output(Node):
    def __init__(self, name: str, range: Range):
        super().__init__(name, range)

class Resource(Node):
    def __init__(self, type: str, name: str, range: Range):
        super().__init__(f'{type}.{name}', range)
    
class Module():
    def __init__(self, name: str, path: str):
        # Nodes that represent the start and end of the module in the dependency graph
        self.start = Node(f'module.{name} (start)')
        self.end = Node(f'module.{name} (end)')

        self.name = name
        self.path = path

        self.nodes: list[Node] = []
        self.variables: list[Variable] = []
        self.outputs: list[Output] = []
        self.submodules: list[Module] = []
        
class Dependency:
    def __init__(self, dependee: Node, depended: Node, explicit: bool = False, range: Range | None = None):
        self.dependee = dependee
        self.depended = depended
        self.range = range
        self.explicit = explicit
    
    def __str__(self):
        return f'{self.dependee} -> {self.depended} {'(explicit)' if self.explicit else ''}'
