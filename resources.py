class Range:
    def __init__(self, start_line: int, start_column: int, end_line: int, end_column: int):
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

    def __str__(self):
        return f'{self.start_line}:{self.start_column}-{self.end_line}:{self.end_column}'

class Resource:
    def __init__(self, type: str, name: str, range: Range):
        self.type = type
        self.name = name
        self.range = range

    def id(self):
        return f'{self.type}.{self.name}'

    def __str__(self):
        return f'{self.type}.{self.name} ({self.range})'

class Dependency:
    def __init__(self, dependee: str, depended: str, explicit: bool, range: Range):
        self.dependee = dependee
        self.depended = depended
        self.range = range
        self.explicit = explicit
    
    def __str__(self):
        return f'{self.depended} -> {self.dependee} ({self.range}{', explicit' if self.explicit else ''})'
