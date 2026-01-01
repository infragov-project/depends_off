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
    _id_registry: dict[int, Node] = dict()

    def __init__(self, range: Range):
        self.id = Node._id_counter
        Node._id_counter += 1

        self.range = range
        Node._id_registry[self.id] = self

    @staticmethod
    def get(id: int):
        return Node._id_registry[id]
    
class Provider(Node):
    _name_registry: dict[str, Provider] = dict()

    def __init__(self, name: str, alias: str | None, range: Range):
        if alias:
            name = f'{name}.{alias}'
        else:
            name = name

        super().__init__(range)
        self.name = name
        Provider._name_registry[self.name] = self

    @staticmethod
    def get_by_name(name: str):
        return Provider._name_registry.get(name)

    def __str__(self):
        return f'{self.name} ({self.range})'
    
class Variable(Node):
    _name_registry: dict[str, Variable] = dict()

    def __init__(self, name: str, range: Range):
        super().__init__(range)
        self.name = name
        Variable._name_registry[self.name] = self

    @staticmethod
    def get_by_name(name: str):
        return Variable._name_registry.get(name)
    
    def __str__(self):
        return f'var.{self.name} ({self.range})'
    
class Output(Node):
    _name_registry: dict[str, Output] = dict()

    def __init__(self, name: str, range: Range):
        super().__init__(range)
        self.name = name
        Output._name_registry[self.name] = self

    @staticmethod
    def get_by_name(name: str):
        return Output._name_registry.get(name)
    
    def __str__(self):
        return f'output.{self.name} ({self.range})'

class Resource(Node):
    _name_registry: dict[str, Resource] = dict()

    def __init__(self, type: str, name: str, range: Range):
        super().__init__(range)

        self.type = type
        self.name = name
        Resource._name_registry[f'{self.type}.{self.name}'] = self

    @staticmethod
    def get_by_name(name: str):
        return Resource._name_registry.get(name)

    def __str__(self):
        return f'{self.type}.{self.name} ({self.range})'
    
class ModuleNode(Node):
    def __init__(self, name: str, start: bool):
        super().__init__(Range(0, 0, 0, 0))
        self.name = name
        self.start = start
    
    def __str__(self):
        return f'module.{self.name} ({"start" if self.start else "end"})'

    
class Module():
    def __init__(self, name: str, path: str):
        # Nodes that represent the start and end of the module in the dependency graph
        self.start = ModuleNode(name, True)
        self.end = ModuleNode(name, False)

        self.name = name
        self.path = path

        self.nodes: list[Node] = []
        self.variables: list[Variable] = []
        self.outputs: list[Output] = []
        self.dependencies: list[Dependency] = []
        self.submodules: list[Module] = []
        
class Dependency:
    def __init__(self, dependee_id: int, depended_id: int, explicit: bool, range: Range):
        self.dependee_id = dependee_id
        self.depended_id = depended_id
        self.range = range
        self.explicit = explicit
    
    def __str__(self):
        dependee = Node.get(self.dependee_id)
        depended = Node.get(self.depended_id)
        return f'{dependee} -> {depended} ({self.range}{', explicit' if self.explicit else ''})'
