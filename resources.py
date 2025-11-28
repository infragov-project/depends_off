class Resource:
    def __init__(self, type, name, range):
        self.type = type
        self.name = name
        self.range = range

    def __str__(self):
        return f'{self.type}.{self.name} ({self.range})'

class Dependency:
    def __init__(self, dependee, depended, explicit, range):
        self.dependee = dependee
        self.depended = depended
        self.range = range
        self.explicit = explicit
    
    def __str__(self):
        return f'{self.depended} -> {self.dependee} ({self.range}{', explicit' if self.explicit else ''})'

class Range:
    def __init__(self, start_line, start_column, end_line, end_column):
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

    def __str__(self):
        return f'{self.start_line}:{self.start_column}-{self.end_line}:{self.end_column}'
