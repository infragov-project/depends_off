from parser import Parser
from graph import DAG, CycleError


# Parse the Terraform file

resources, dependencies = Parser.parse('test.tf')

print('resources:')
for resource in resources: print(resource)
print()

print('dependencies:')
for dependency in dependencies: print(dependency)
print()


# Build the full dependency graph and get its topological order

graph = DAG()

resources_to_node = dict()
for i, resource in enumerate(resources):
    graph.node(i)
    resources_to_node[resource.id()] = i

for dependency in dependencies:
    u = resources_to_node[dependency.dependee]
    v = resources_to_node[dependency.depended]

    try: graph.edge(u, v)
    except CycleError:
        print(f'the dependency graph has a cycle: cycle detected on {dependency}')
        exit(1)

order = graph.toposort()


# Remove the explicit edges and add them one by one such that, when an edge is
# added, all the edges that an alternative path might have used have already
# been used.

explicit_dependencies = [d for d in dependencies if d.explicit]

for dependency in explicit_dependencies:
    u = resources_to_node[dependency.dependee]
    v = resources_to_node[dependency.depended]
    graph.remove_edge(u, v)

# We'll order the edges such that they can be added one by one, respecting the
# property above. An edge X = (a, b) comes before an endge Y = (c, d) if it
# might be part of a path from c to d. As such, a <= c and b >= d in the
# topological ordering.

def dependency_to_key(dependency):
    u = resources_to_node[dependency.dependee]
    v = resources_to_node[dependency.depended]

    a = graph.order(u)
    b = graph.order(v)

    return (a, -b)

explicit_dependencies.sort(key = dependency_to_key)

# Check if any of the explicit dependencies is redundant

redundant_dependencies = list()

for dependency in dependencies:
    if not dependency.explicit: continue

    u = resources_to_node[dependency.dependee]
    v = resources_to_node[dependency.depended]

    if graph.path(u, v):
        redundant_dependencies.append(dependency)
    
    graph.edge(u, v)

if len(redundant_dependencies) == 0:
    print('no redundant dependencies found')

for dependency in redundant_dependencies:
    print(f'redundant dependency found: {dependency}')
