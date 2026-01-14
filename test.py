from pathlib import Path
from parser import Parser
from analyzer import DependencyAnalyzer

ROOT = Path('terrads-light')
OUTPUT = Path('output.txt')

def print_progress(parsed, analyzed, redundant, failed):
    print(f'\rParsed: {parsed}\tAnalyzed: {analyzed}\tFailed: {failed}\tRedundant dependencies: {redundant}', end='')

def has_tf_files(directory: Path) -> bool:
    return any(p.suffix == '.tf' for p in directory.iterdir() if p.is_file())

parsed = 0
analyzed = 0
redundant_count = 0
failed = 0
parser = Parser()

with OUTPUT.open('w') as out:
    for path in ROOT.rglob('*'):
        if not path.is_dir() or not has_tf_files(path):
            continue

        try:
            resources, dependencies = parser.parse(str(path))
            parsed += 1
        except Exception as e:
            out.write(f'Error parsing {path}.\n')
            failed += 1
            print_progress(parsed, analyzed, redundant_count, failed)
            continue

        try:
            analyzer = DependencyAnalyzer(resources, dependencies)
            redundant = analyzer.redundant()
            analyzed += 1
            redundant_count += len(redundant)

            if redundant:
                out.write(f'Found {len(redundant)} redundant dependencies in {path}:\n')
                for r in redundant:
                    out.write(f'\t{r}\n')

        except Exception as e:
            out.write(f'Error analyzing {path}.\n')
            failed += 1

        print_progress(parsed, analyzed, redundant_count, failed)

print('\nDetailed feedback available in output.txt')
