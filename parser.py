from pathlib import Path
import re
import hcl2
from typing import Any

from resources import Resource, Dependency, Range

class Parser:
    @staticmethod
    def parse(module_path: str):
        """
        Parse a Terraform module and extract resources and dependencies.
        """
        resources: list[Resource] = list()
        dependencies: list[Dependency] = list()

        # Terraform modules include only the .tf files in the directory, without
        # recursing into subdirectories
        for path in Path(module_path).iterdir():
            if path.is_dir(): continue
            if not path.name.endswith('.tf'): continue
            
            file_resources, file_dependencies = Parser.parse_file(str(path))
            resources.extend(file_resources)
            dependencies.extend(file_dependencies)

        return resources, dependencies

    @staticmethod
    def parse_file(filename: str):
        """
        Parse a Terraform file and extract resources and dependencies.
        """
        with open(filename, 'r') as f:
            content: Any = hcl2.load(f, with_meta=True) # type: ignore
        
        resources: list[Resource] = list()
        dependencies: list[Dependency] = list()

        if 'resource' in content:
            for data in content['resource']: Parser._resource(data, resources, dependencies)

        return resources, dependencies
    
    @staticmethod
    def _resource(data: Any, resources: list[Resource], dependencies: list[Dependency]):
        resource, content = Parser._extract(data, 'type', 'name')

        resource = Resource(resource['type'], resource['name'], Range(
            content['__start_line__'],
            content['__start_column__'],
            content['__end_line__'],
            content['__end_column__']
        ))
        resources.append(resource)

        for attribute, metadata in content.items():
            # Ignore line/column metadata
            if attribute.startswith('__'):
                continue

            value = metadata['value']

            if type(value) == list:
                for v in value: # type: ignore
                    dependency = Parser._resource_dependency(v, resource, metadata, attribute == 'depends_on') # type: ignore
                    if dependency: dependencies.append(dependency)
            else:
                dependency = Parser._resource_dependency(value, resource, metadata, attribute == 'depends_on')
                if dependency: dependencies.append(dependency)
    
    @staticmethod
    def _resource_dependency(value: str, origin: Resource, metadata: Any, explicit: bool):
        match = re.match(r'^\${(.+?)\.(.+?)(\..+)?}$', value)
        if not match:
            return None
        
        dependee_type = match[1]
        dependee_resource = match[2]

        return Dependency(
            f'{dependee_type}.{dependee_resource}',
            f'{origin.type}.{origin.name}',
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
