import re
import hcl2
from typing import Any
from pathlib import Path

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
            
            file_resources, file_dependencies = Parser.parse_file(f'{module_path}/{path.name}')
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

        for data in content['resource']: Parser._resource(data, resources, dependencies)

        return resources, dependencies
    
    @staticmethod
    def _resource(data: Any, resources: list[Resource], dependencies: list[Dependency]):
        rtype, metadata = next(iter(data.items()))
        name, details = next(iter(metadata.items()))

        resource = Resource(rtype, name, Range(
            details['__start_line__'],
            details['__start_column__'],
            details['__end_line__'],
            details['__end_column__']
        ))
        resources.append(resource)

        for attribute, metadata in details.items():
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
    def _dependency(value: str, resource: Resource, metadata: Any, explicit: bool):
        match = re.match(r'^\${(.*)}$', value)
        if not match:
            return None
        
        dependee_name = match.group(1)
        tmp = dependee_name.split('.')
        dependee_type = tmp[0]
        dependee_resource = tmp[1]

        return Dependency(
            f'{dependee_type}.{dependee_resource}',
            f'{resource.type}.{resource.name}',
            explicit,
            Range(
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
        )
