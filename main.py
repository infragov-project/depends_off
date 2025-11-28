from parser import Parser
from graph import Graph


# Parse the Terraform file

resources, dependencies = Parser.parse('test.tf')

print('resources:')
for resource in resources: print(resource)
print()

print('dependencies:')
for dependency in dependencies: print(dependency)
print()


# Build a dependency graph using only implicit dependencies

graph = Graph()

resources_to_node = dict()
for i, resource in enumerate(resources):
    graph.node(i)
    resources_to_node[resource.id()] = i

for dependency in dependencies:
    if dependency.explicit: continue

    u = resources_to_node[dependency.dependee]
    v = resources_to_node[dependency.depended]
    graph.edge(u, v)


# Check if any of the explicit dependencies is redundant

redundant_dependencies = list()

for dependency in dependencies:
    if not dependency.explicit: continue

    u = resources_to_node[dependency.dependee]
    v = resources_to_node[dependency.depended]

    if graph.path(u, v):
        redundant_dependencies.append(dependency)

if len(redundant_dependencies) == 0:
    print('No redundant dependencies found.')

for dependency in redundant_dependencies:
    print(f'Redundant dependency found: {dependency}')
