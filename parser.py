import re
import hcl2

from resources import Resource, Dependency, Range

class Parser:
    @staticmethod
    def parse(filename):
        with open(filename, 'r') as f:
            content = hcl2.load(f, with_meta=True)
        
        resources = list()
        dependencies = list()

        for data in content['resource']: Parser.resource(data, resources, dependencies)

        return (resources, dependencies)
    
    @staticmethod
    def resource(data, resources, dependencies):
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
                for v in value:
                    dependency = Parser.dependency(v, resource, metadata, attribute == 'depends_on')
                    if dependency: dependencies.append(dependency)
            else:
                dependency = Parser.dependency(value, resource, metadata, attribute == 'depends_on')
                if dependency: dependencies.append(dependency)
    
    @staticmethod
    def dependency(value, resource, metadata, explicit):
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
