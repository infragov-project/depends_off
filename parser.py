from pathlib import Path
import re
import hcl2
from typing import Any
from terraform_graph import Node, Provider, Variable, Resource, Dependency, Range

class Parser:
    def __init__(self):
        self.nodes: list[Node] = list()
        self.dependencies: list[Dependency] = list()

    def parse(self, module_path: str):
        """
        Parse a Terraform module and extract resources and dependencies.
        """
        self.nodes: list[Node] = list()
        self.dependencies: list[Dependency] = list()

        # Terraform modules include only the .tf files in the directory, without
        # recursing into subdirectories
        for path in Path(module_path).iterdir():
            if path.is_dir(): continue
            if not path.name.endswith('.tf'): continue
            
            self.parse_file(str(path))

        return self.nodes, self.dependencies

    def parse_file(self, filename: str):
        """
        Parse a Terraform file and extract resources and dependencies.
        """
        with open(filename, 'r') as f:
            content: Any = hcl2.load(f, with_meta=True) # type: ignore
        if 'variable' in content:
            for data in content['variable']: self._variable(data)

        if 'provider' in content:
            for data in content['provider']: self._provider(data)

        if 'resource' in content:
            for data in content['resource']: self._resource(data)
    
    def _provider(self, data: Any):
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
        self.nodes.append(provider)

        self._dependencies(data, provider)

    def _variable(self, data: Any):
        variable, data = self._extract(data, 'name')

        variable = Variable(variable['name'], Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        self.nodes.append(variable)
    
    def _resource(self, data: Any):
        resource, data = self._extract(data, 'type', 'name')

        resource = Resource(resource['type'], resource['name'], Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        self.nodes.append(resource)

        self._dependencies(data, resource)

    def _dependencies(self, data: Any, origin: Node, explicit: bool = False, metadata: Any = {}):
        # An int has no dependencies
        if type(data) == int:
            pass

        elif type(data) == str:
            self._dependency(data, origin, metadata, explicit)

        elif type(data) == list:
            for value in data: # type: ignore
                self._dependencies(value, origin, explicit, metadata)

        else:
            for attribute, metadata in data.items():
                # Ignore line/column metadata
                if attribute.startswith('__'): continue
                self._dependencies(metadata, origin, explicit or attribute == 'depends_on', data)

    def _dependency(self, value: str, origin: Node, metadata: Any, explicit: bool):
        self._variable_dependency(value, origin, metadata, explicit)
        self._provider_dependency(value, origin, metadata, explicit)
        self._resource_dependency(value, origin, metadata, explicit)

    def _provider_dependency(self, value: str, origin: Node, metadata: Any, explicit: bool):
        match = re.match(r'^\${(.+?)\.(.+?)(\..+)?}$', value)
        if not match:
            return None
        
        provider = match[1]
        alias = match[2]
        provider_name = f'{provider}.{alias}'

        dependee = Provider.get_by_name(provider_name)

        if not dependee: return None

        self.dependencies.append(Dependency(
            origin.id,
            dependee.id,
            explicit,
            Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
        ))
    
    def _variable_dependency(self, value: str, origin: Node, metadata: Any, explicit: bool):
        match = re.match(r'^\${var\.(.+?)(\..+)?}$', value)
        if not match:
            return None
        
        variable_name = match[1]
        dependee = Variable.get_by_name(variable_name)

        if not dependee: return None

        self.dependencies.append(Dependency(
            origin.id,
            dependee.id,
            explicit,
            Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
        ))
    
    def _resource_dependency(self, value: str, origin: Node, metadata: Any, explicit: bool):
        match = re.match(r'^\${(.+?)\.(.+?)(\..+)?}$', value)
        if not match:
            return None
        
        dependee_type = match[1]
        dependee_resource = match[2]
        dependee_name = f'{dependee_type}.{dependee_resource}'

        dependee = Resource.get_by_name(dependee_name)

        if not dependee: return None

        self.dependencies.append(Dependency(
            origin.id,
            dependee.id,
            explicit,
            Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
        ))
    
    def _extract(self, data: dict[Any, Any], *arguments: str):
        result: dict[str, Any] = dict()

        for argument in arguments:
            k, v = next(iter(data.items()))
            result[argument] = k
            data = v

        return result, data
