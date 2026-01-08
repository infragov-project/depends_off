from pathlib import Path
from parser import Parser
from analyzer import DependencyAnalyzer

count = 0
parsed = 0
analyzed = 0
redundant_count = 0

parser = Parser()

for path in Path('terrads-light').rglob('*'):
    if path.is_file(): continue
    if not path.is_dir(): continue

    file_count = sum(1 for f in path.iterdir() if f.is_file() and f.name.endswith('.tf'))
    if file_count == 0: continue

    count += 1

    try:
        resources, dependencies = parser.parse(str(path))
        print(f'Parsed {str(path)}')
        parsed += 1

        try:
            analyzer = DependencyAnalyzer(resources, dependencies)
            redundant = analyzer.redundant()
            print(f'Analyzed {str(path)}')
            analyzed += 1
            redundant_count += len(redundant)

            if len(redundant) > 0:
                print('Redundant dependencies found:', str(path))
        except Exception as e:
            print(f'Failed to analyze {str(path)}')
    except Exception as e:
        print(f'Failed to parse {str(path)}')

print(f'Parsed {parsed} out of {count} modules successfully.')
print(f'Analyzed {analyzed} out of {count} modules successfully.')
print(f'Total redundant dependencies found: {redundant_count}')
