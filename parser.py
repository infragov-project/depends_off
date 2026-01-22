from pathlib import Path
import re
import hcl2
from typing import Any
from terraform_graph import Node, Provider, Variable, Output, Resource, Dependency, ExplicitDependency, Range, Module

class Parser:
    def parse(self, path: str):
        """
        Parse the dependency graph of a Terraform module and the modules it
        depends on.
        """

        # Parsing is divided into two passes. In the first pass, all the nodes
        # in the dependency graph are parse. Potential dependencies are also
        # listed, but not resolved, since the dependee node might not have been
        # parsed yet. In the second pass, all the potential dependencies are
        # resolved.

        self.nodes: list[Node] = list()
        self.dependencies: list[Dependency] = list()
        self.node_map: dict[str, Node] = dict()

        # A list of dependencies to consider in the second pass. Contains tuples
        # of the form (dependent, is explicit, dependency declaration range,
        # dependency string, module where the dependency was declared)
        self.potential_dependencies: list[tuple[Node, bool, Range, str, Module]] = list()

        # First pass
        self._parse_module_nodes('root', path)

        # Second pass
        self._parse_dependencies()

        return self.nodes, self.dependencies

    def _parse_module_nodes(self, name: str, path: str):
        """
        Parse the nodes in the dependency graph of a Terraform module and its
        submodules.
        """
        
        module = Module(name, path)
        self.nodes.append(module.expand)
        self.nodes.append(module.close)

        # Terraform modules include only the .tf files in the directory, without
        # recursing into subdirectories
        if Path(path).exists():
            for p in Path(path).iterdir():
                if p.is_dir(): continue
                if not p.name.endswith('.tf'): continue
                
                self._parse_file_nodes(module, str(p))

        # All nodes depend on the start of the module's expand node
        for node in module.nodes:
            self.dependencies.append(Dependency(node, module.expand))
            
        # The module's close node depends on all nodes
        for node in module.nodes:
            self.dependencies.append(Dependency(module.close, node))

        return module
    
    def _parse_file_nodes(self, module: Module, filename: str):
        """
        Parse the nodes in a Terraform file.
        """

        with open(filename, 'r') as f:
            try:
                content: Any = hcl2.load(f, with_meta=True) # type: ignore
            except Exception as e:
                raise ParserError(f'HCL2 parsing error in {filename}: {str(e)}')

        if 'module' in content:
            for data in content['module']: self._module_block(module, filename, data)

        if 'variable' in content:
            for data in content['variable']: self._variable(module, filename, data)

        if 'output' in content:
            for data in content['output']: self._output(module, filename, data)

        if 'provider' in content:
            for data in content['provider']: self._provider(module, filename, data)

        if 'resource' in content:
            for data in content['resource']: self._resource(module, filename, data)
    
    def _parse_dependencies(self):
        """
        Resolve all potential dependencies in the dependency graph.
        """
        for dependent, explicit, range, string, module in self.potential_dependencies:
            dependee = self._find_node(module, string)
            
            if dependee is None: continue
            if dependee == dependent: continue # ignore self-references

            if explicit: self.dependencies.append(ExplicitDependency(
                dependent,
                dependee,
                range
            ))

            else: self.dependencies.append(Dependency(
                dependent,
                dependee,
                range
            ))

    def _module_block(self, module: Module, filename: str, data: Any):
        """
        Parse a module block in a Terraform file.
        """
        name, data = self._extract(data, 'name')
        source = data['source']['value']

        path = module.path + '/' + source
        submodule = self._parse_module_nodes(f'{module.name}.{name['name']}', path)
        module.submodules.append(submodule)
        
        self.dependencies.append(Dependency(module.close, submodule.close))
        self.dependencies.append(Dependency(submodule.expand, module.expand))

        self._dependencies(module, filename, data, submodule.expand)
    
    def _provider(self, module: Module, filename: str, data: Any):
        """
        Parse a provider block in a Terraform file.
        """
        provider, data = self._extract(data, 'name')

        if 'alias' in data:
            alias = data['alias']['value']
        else :
            alias = None

        provider = Provider(provider['name'], alias, Range(
            filename,
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(provider)
        self.nodes.append(provider)
        self.node_map[f'{module.name}.provider.{provider.name}'] = provider

        self._dependencies(module, filename, data, provider)

    def _variable(self, module: Module, filename: str, data: Any):
        """
        Parse a variable block in a Terraform file.
        """
        variable, data = self._extract(data, 'name')

        variable = Variable(variable['name'], Range(
            filename,
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(variable)
        module.variables.append(variable)
        self.nodes.append(variable)
        self.node_map[f'{module.name}.{variable.name}'] = variable
        
        module.variables.append(variable)

    def _output(self, module: Module, filename: str, data: Any):
        """
        Parse an output block in a Terraform file.
        """
        output, data = self._extract(data, 'name')

        output = Output(output['name'], Range(
            filename,
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(output)
        module.outputs.append(output)
        self.nodes.append(output)
        self.node_map[f'{module.name}.{output.name}'] = output

        self._dependencies(module, filename, data, output)
    
    def _resource(self, module: Module, filename: str, data: Any):
        """
        Parse a resource block in a Terraform file.
        """
        resource, data = self._extract(data, 'type', 'name')

        resource = Resource(resource['type'], resource['name'], Range(
            filename,
            data['__start_line__'],
            data['__start_column__'],
            data['__end_line__'],
            data['__end_column__']
        ))
        module.nodes.append(resource)
        self.nodes.append(resource)
        self.node_map[f'{module.name}.resource.{resource.name}'] = resource

        self._dependencies(module, filename, data, resource)

    def _dependencies(self, module: Module, filename: str, data: Any, origin: Node, explicit: bool = False, metadata: Any = {}):
        """
        Recursively parse potential dependencies in a Terraform block's data.
        """

        # Ints and bools have no dependencies
        if type(data) == int or type(data) == bool:
            pass

        # Strings can contain dependencies
        elif type(data) == str:
            range = Range(
                filename,
                metadata['__start_line__'],
                metadata['__start_column__'],
                metadata['__end_line__'],
                metadata['__end_column__']
            )
            for match in re.finditer(r'\${(.+?)}', data):   
                self.potential_dependencies.append((origin, explicit, range, match[1], module))
            else:
                # In explicit dependencies, the whole string may be a dependency
                if explicit:
                    self.potential_dependencies.append((origin, explicit, range, data, module))

        # Recursively parse lists
        elif type(data) == list:
            for value in data: # type: ignore
                self._dependencies(module, filename, value, origin, explicit, metadata)

        # Recursively parse dictionaries
        elif type(data) == dict:
            for attribute, metadata in data.items():
                # Ignore line/column metadata
                if attribute.startswith('__'): continue
                self._dependencies(module, filename, metadata, origin, explicit or attribute == 'depends_on', data)
        
        else:
            raise ParserError(f'Unsupported data type: {type(data)}')

    def _find_node(self, module: Module, string: str) -> Node | None:
        """
        Find a node in the dependency graph based on a dependency string.
        """
        return self._find_var(module, string) or self._find_module_output(module, string) or self._find_provider(module, string) or self._find_resource(module, string)
    
    def _find_provider(self, module: Module, string: str) -> Node | None:
        """
        Find a provider node based on a dependency string.
        """
        match = re.match(r'(.+?)\.(.+?)(\..+)?$', string)
        if not match: return None

        provider = match[1]
        alias = match[2]
        return self.node_map.get(f'{module.name}.provider.{provider}.{alias}')
    
    def _find_var(self, module: Module, string: str) -> Node | None:
        """
        Find a variable node based on a dependency string.
        """
        if string[:4] != "var.": return None
        
        name = string.split('.')[1]
        return self.node_map.get(f'{module.name}.var.{name}')
    
    def _find_module_output(self, module: Module, string: str) -> Node | None:
        """
        Find a module output node based on a dependency string.
        """
        match = re.match(r'module\.(.+?)\.(.+?)(\..+)?$', string)
        if not match: return None

        module_name = f'{module.name}.{match[1]}'
        output_name = f'output.{match[2]}'

        m = next((m for m in module.submodules if m.name == module_name), None)
        if m is None: return None
        
        o = next((o for o in m.outputs if o.name == output_name), None)

        return o
    
    def _find_resource(self, module: Module, string: str) -> Node | None:
        """
        Find a resource node based on a dependency string.
        """
        match = re.match(r'(.+?)\.(.+?)(\..+)?$', string)
        if not match: return None

        type = match[1]
        name = match[2]
        return self.node_map.get(f'{module.name}.resource.{type}.{name}')
    
    def _extract(self, data: dict[Any, Any], *arguments: str):
        result: dict[str, Any] = dict()

        for argument in arguments:
            k, v = next(iter(data.items()))
            result[argument] = k
            data = v

        return result, data

class ParserError(Exception):
    pass
