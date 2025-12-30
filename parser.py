from pathlib import Path
import re
import hcl2
from typing import Any
from terraform_graph import Node, Provider, Variable, Resource, Dependency, Range

class Parser:
    @staticmethod
    def parse(module_path: str):
        """
        Parse a Terraform module and extract resources and dependencies.
        """
        nodes: list[Node] = list()
        dependencies: list[Dependency] = list()

        # Terraform modules include only the .tf files in the directory, without
        # recursing into subdirectories
        for path in Path(module_path).iterdir():
            if path.is_dir(): continue
            if not path.name.endswith('.tf'): continue
            
            file_resources, file_dependencies = Parser.parse_file(str(path))
            nodes.extend(file_resources)
            dependencies.extend(file_dependencies)

        return nodes, dependencies

    @staticmethod
    def parse_file(filename: str):
        """
        Parse a Terraform file and extract resources and dependencies.
        """
        with open(filename, 'r') as f:
            content: Any = hcl2.load(f, with_meta=True) # type: ignore
        
        nodes: list[Node] = list()
        dependencies: list[Dependency] = list()

        if 'provider' in content:
            for data in content['provider']: Parser._provider(data, nodes)

        if 'variable' in content:
            for data in content['variable']: Parser._variable(data, nodes)

        if 'resource' in content:
            for data in content['resource']: Parser._resource(data, nodes, dependencies)

        return nodes, dependencies
    
    @staticmethod
    def _provider(data: Any, nodes: list[Node]):
        provider, data = Parser._extract(data, 'name')

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
        nodes.append(provider)

    @staticmethod
    def _variable(data: Any, nodes: list[Node]):
        variable, data = Parser._extract(data, 'name')

        variable = Variable(variable['name'], Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        nodes.append(variable)
    
    @staticmethod
    def _resource(data: Any, nodes: list[Node], dependencies: list[Dependency]):
        resource, data = Parser._extract(data, 'type', 'name')

        resource = Resource(resource['type'], resource['name'], Range(
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        nodes.append(resource)

        for attribute, metadata in data.items():
            # Ignore line/column metadata
            if attribute.startswith('__'):
                continue

            value = metadata['value']

            if type(value) == list:
                for v in value: # type: ignore
                    dependency = Parser._dependency(v, resource, metadata, attribute == 'depends_on') # type: ignore
                    if dependency: dependencies.append(dependency)
            else:
                dependency = Parser._dependency(value, resource, metadata, attribute == 'depends_on')
                if dependency: dependencies.append(dependency)

    @staticmethod
    def _dependency(value: str, origin: Node, metadata: Any, explicit: bool):
        dependency = Parser._variable_dependency(value, origin, metadata, explicit)
        if dependency:
            return dependency

        dependency = Parser._provider_dependency(value, origin, metadata, explicit)
        if dependency:
            return dependency
        
        dependency = Parser._resource_dependency(value, origin, metadata, explicit)
        if dependency:
            return dependency
        
        return None

    @staticmethod
    def _provider_dependency(value: str, origin: Node, metadata: Any, explicit: bool):
        match = re.match(r'^\${(.+?)\.(.+?)(\..+)?}$', value)
        if not match:
            return None
        
        provider = match[1]
        alias = match[2]
        provider_name = f'{provider}.{alias}'

        dependee = Provider.get_by_name(provider_name)

        if not dependee: return None

        return Dependency(
            origin.id,
            dependee.id,
            explicit,
            Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
        )
    
    @staticmethod
    def _variable_dependency(value: str, origin: Node, metadata: Any, explicit: bool):
        match = re.match(r'^\${var\.(.+?)(\..+)?}$', value)
        if not match:
            return None
        
        variable_name = match[1]

        dependee = Variable.get_by_name(variable_name)

        if not dependee: return None

        return Dependency(
            origin.id,
            dependee.id,
            explicit,
            Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
        )
    
    @staticmethod
    def _resource_dependency(value: str, origin: Node, metadata: Any, explicit: bool):
        match = re.match(r'^\${(.+?)\.(.+?)(\..+)?}$', value)
        if not match:
            return None
        
        dependee_type = match[1]
        dependee_resource = match[2]
        dependee_name = f'{dependee_type}.{dependee_resource}'

        dependee = Resource.get_by_name(dependee_name)

        if not dependee: return None

        return Dependency(
            origin.id,
            dependee.id,
            explicit,
            Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
        )
    
    @staticmethod
    def _extract(data: dict[Any, Any], *arguments: str):
        result: dict[str, Any] = dict()

        for argument in arguments:
            k, v = next(iter(data.items()))
            result[argument] = k
            data = v

        return result, data
