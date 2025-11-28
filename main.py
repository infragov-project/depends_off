import hcl2
import re

with open("test.tf", "r") as f:
    data = hcl2.load(f, with_meta=True)

def get_name(resource):
    return '.'.join(resource.split('.')[0:2])

resources = list()
for resource in data['resource']:
    rtype, content = next(iter(resource.items()))
    name, attributes = next(iter(content.items()))
    print(rtype + "." + name)

for resource in data['resource']:
    rtype, content = next(iter(resource.items()))
    name, attributes = next(iter(content.items()))

    print(rtype + "." + name)
    for attribute_name, attribute in attributes.items():
        if attribute_name.startswith('__'):
            continue
        print("\t" + attribute_name + " = " + str(attribute['value']))

        if type(attribute['value']) == list:
            for value in attribute['value']:
                match = re.match(r'^\${(.*)}$', value)
                if match:
                    print('\t\tdepends on ' + get_name(match.group(1)))
        else:
            match = re.match(r'^\${(.*)}$', attribute['value'])
            if match:
                print('\t\tdepends on ' + get_name(match.group(1)))


#pprint.pprint(resources)
