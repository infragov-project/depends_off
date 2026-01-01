from pathlib import Path
import re
import hcl2
from typing import Any
from terraform_graph import Node, Provider, Variable, Output, Resource, Dependency, Range, Module

class Parser:
    def parse(self, path: str):
        """
        Parse a Terraform module located at the given path and the modules it
        depends on.
        """

        # A list of modules yet to be parsed
        self.modules_to_parse = [('root', path)]
        
        modules: list[Module] = []
        while self.modules_to_parse:
            name, path = self.modules_to_parse.pop()
            modules.append(self._parse_module(name, path))

        return modules

    def _parse_module(self, name: str, path: str):
        """
        Parse a Terraform module and extract resources and dependencies.
        """
        
        module = Module(name, path)

        # A list of dependencies to consider in the second pass. Contains tuples
        # of the form (dependent, is explicit, dependency declaration range,
        # dependency string)
        self.potential_dependencies: list[tuple[Node, bool, Range, str]] = list()

        # Terraform modules include only the .tf files in the directory, without
        # recursing into subdirectories
        for p in Path(path).iterdir():
            if p.is_dir(): continue
            if not p.name.endswith('.tf'): continue
            
            self._parse_file(module, str(p))

        for (dependent, explicit, range, string) in self.potential_dependencies:
            dependee = self._find_node(string)
            if dependee:
                module.dependencies.append(Dependency(
                    dependent.id,
                    dependee.id,
                    explicit,
                    range
                ))

        for node in module.nodes:
            module.dependencies.append(Dependency(node.id, module.start.id, False, module.start.range))
            
        for node in module.nodes:
            module.dependencies.append(Dependency(module.end.id, node.id, False, module.end.range))

        return module


    def _parse_file(self, module: Module, filename: str):
        """
        Parse a Terraform file and extract resources and dependencies.
        """
        with open(filename, 'r') as f:
            content: Any = hcl2.load(f, with_meta=True) # type: ignore

        if 'variable' in content:
            for data in content['variable']: self._variable(module, data)

        if 'output' in content:
            for data in content['output']: self._output(module, data)

        if 'provider' in content:
            for data in content['provider']: self._provider(module, data)

        if 'resource' in content:
            for data in content['resource']: self._resource(module, data)
    
    def _provider(self, module: Module, data: Any):
        provider, data = self._extract(data, 'name')

        if 'alias' in data:
            alias = data['alias']['value']
        else :
            alias = None

        provider = Provider(provider['name'], alias, Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(provider)

        self._dependencies(data, provider)

    def _variable(self, module: Module, data: Any):
        variable, data = self._extract(data, 'name')

        variable = Variable(variable['name'], Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(variable)
        
        module.variables.append(variable)

    def _output(self, module: Module, data: Any):
        output, data = self._extract(data, 'name')

        output = Output(output['name'], Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(output)

        self._dependencies(data, output)
    
    def _resource(self, module: Module, data: Any):
        resource, data = self._extract(data, 'type', 'name')

        resource = Resource(resource['type'], resource['name'], Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(resource)

        self._dependencies(data, resource)

    def _dependencies(self, data: Any, origin: Node, explicit: bool = False, metadata: Any = {}):
        # An int has no dependencies
        if type(data) == int:
            pass

        elif type(data) == str:
            range = Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
            for match in re.finditer(r'\${(.+?)}', data):   
                self.potential_dependencies.append((origin, explicit, range, match[1]))

        elif type(data) == list:
            for value in data: # type: ignore
                self._dependencies(value, origin, explicit, metadata)

        else:
            for attribute, metadata in data.items():
                # Ignore line/column metadata
                if attribute.startswith('__'): continue
                self._dependencies(metadata, origin, explicit or attribute == 'depends_on', data)

    def _find_node(self, string: str) -> Node | None:
        return self._find_var(string) or self._find_provider(string) or self._find_resource(string)
    
    def _find_provider(self, string: str) -> Node | None:
        match = re.match(r'(.+?)\.(.+?)(\..+)?$', string)
        if not match: return None

        provider = match[1]
        alias = match[2]
        return Provider.get_by_name(f'{provider}.{alias}')
    
    def _find_var(self, string: str) -> Node | None:
        if string[:4] != "var.": return None
        
        name = string.split('.')[1]
        return Variable.get_by_name(name)
    
    def _find_resource(self, string: str) -> Node | None:
        match = re.match(r'(.+?)\.(.+?)(\..+)?$', string)
        if not match: return None

        type = match[1]
        name = match[2]
        return Resource.get_by_name(f'{type}.{name}')
    
    def _extract(self, data: dict[Any, Any], *arguments: str):
        result: dict[str, Any] = dict()

        for argument in arguments:
            k, v = next(iter(data.items()))
            result[argument] = k
            data = v

        return result, data
