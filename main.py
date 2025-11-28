from parser import Parser

resources, dependencies = Parser.parse('test.tf')

print('resources:')
for resource in resources: print(resource)
print()

print('dependencies:')
for dependency in dependencies: print(dependency)
