from __future__ import annotations

class Range:
    """
    Represents a range in a source file.
    """

    def __init__(self, filename: str, start_line: int, start_column: int, end_line: int, end_column: int):
        self.filename = filename
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

    def __str__(self):
        return f'{self.filename} ({self.start_line}:{self.start_column}-{self.end_line}:{self.end_column})'
    
class Node:
    """
    Represents a generic node in the dependency graph.
    """

    _id_counter = 0

    def __init__(self, name: str, range: Range | None = None):
        self.id = Node._id_counter
        Node._id_counter += 1
        self.name = name
        self.range = range

    def __str__(self):
        return self.name
    
class Provider(Node):
    """
    Represents a provider node in the dependency graph.
    """
    def __init__(self, name: str, alias: str | None, range: Range):
        if alias: name = f'{name}.{alias}'
        else: name = name

        super().__init__(name, range)
    
class Variable(Node):
    """
    Represents a variable node in the dependency graph.
    """
    def __init__(self, name: str, range: Range):
        super().__init__(f'var.{name}', range)
    
class Output(Node):
    """
    Represents an output node in the dependency graph.
    """
    def __init__(self, name: str, range: Range):
        super().__init__(f'output.{name}', range)

class Data(Node):
    """
    Represents a data node in the dependency graph.
    """
    def __init__(self, type: str, name: str, range: Range):
        super().__init__(f'data.{type}.{name}', range)

class Local(Node):
    """
    Represents a local node in the dependency graph.
    """
    def __init__(self, name: str, range: Range):
        super().__init__(f'local.{name}', range)

class Resource(Node):
    """
    Represents a resource node in the dependency graph.
    """
    def __init__(self, type: str, name: str, range: Range):
        super().__init__(f'{type}.{name}', range)
    
class Module():
    """
    Container for a module in the dependency graph. This includes the module's
    nodes, submodules and expand and close nodes.
    """
    def __init__(self, name: str, path: str):
        # Nodes that represent the start and end of the module in the dependency graph
        self.expand = Node(f'module.{name} (expand)')
        self.close = Node(f'module.{name} (close)')

        self.name = name
        self.path = path

        self.nodes: list[Node] = []
        self.variables: list[Variable] = []
        self.outputs: list[Output] = []
        self.submodules: list[Module] = []
        
class Dependency:
    """
    Represents a dependency between two nodes in the dependency graph.
    """
    def __init__(self, dependee: Node, depended: Node, declaration: Node, range: Range | None = None):
        self.dependee = dependee
        self.depended = depended
        self.declaration = declaration
        self.range = range
    
    def __str__(self):
        return f'{self.dependee} -> {self.depended}'
    
class ExplicitDependency(Dependency):
    """
    Represents an explicit dependency between two nodes in the dependency graph.
    """
    def __init__(self, dependee: Node, depended: Node, declaration: Node, range: Range):
        super().__init__(dependee, depended, declaration, range)
        self.range = range
