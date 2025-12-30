from pathlib import Path
from parser import Parser
from analyzer import DependencyAnalyzer

count = 0
parsed = 0
analyzed = 0
redundant_count = 0

for path in Path('terrads-light').rglob('*'):
    if path.is_file(): continue
    if not path.is_dir(): continue

    file_count = sum(1 for f in path.iterdir() if f.is_file() and f.name.endswith('.tf'))
    if file_count == 0: continue

    count += 1

    try:
        resources, dependencies = Parser.parse(str(path))
        print(f'Parsed {str(path)}')
        parsed += 1

        try:
            analyzer = DependencyAnalyzer(resources, dependencies)
            redundant = analyzer.redundant()
            print(f'Analyzed {str(path)}: {len(redundant)} redundant dependencies')
            analyzed += 1
            redundant_count += len(redundant)
        except Exception as e:
            print(f'Failed to analyze {str(path)}')
    except Exception as e:
        print(f'Failed to parse {str(path)}')

print(f'Parsed {parsed} out of {count} modules successfully.')
print(f'Analyzed {analyzed} out of {count} modules successfully.')
print(f'Total redundant dependencies found: {redundant_count}')
