from typing import TextIO
from pathlib import Path
from src.parser import Parser
from src.analyzer import DependencyAnalyzer

ROOT = Path('dataset')
OUTPUT = Path('output.txt')

parsed = 0
analyzed = 0
redundant_count = 0
failed = 0
parser = Parser()

def process_directory(directory: Path, out: TextIO):
    global parsed, analyzed, redundant_count, failed

    if not directory.is_dir(): return
    if not has_tf_files(directory):
        # This is not a Terraform module directory, search deeper
        for subdirectory in directory.iterdir():
            process_directory(subdirectory, out)
        return
    
    try:
        resources, dependencies = parser.parse(str(directory))
        parsed += 1
    except Exception as e:
        out.write(f'Error parsing {directory}.\n')
        failed += 1
        print_progress(parsed, analyzed, redundant_count, failed)
        return

    try:
        analyzer = DependencyAnalyzer(resources, dependencies)
        redundant = analyzer.redundant()
        analyzed += 1
        redundant_count += len(redundant)

        if redundant:
            out.write(f'Found {len(redundant)} redundant dependencies in {directory}:\n')
            for dependency, path in redundant:
                out.write(f'\t{dependency} via' + '\n')
                out.write('\t\t' + '\n\t\t'.join(str(dependency) for dependency in path) + '\n')

    except Exception as e:
        out.write(f'Error analyzing {directory}.\n')
        failed += 1

    print_progress(parsed, analyzed, redundant_count, failed)

def print_progress(parsed, analyzed, redundant, failed):
    print(f'\rParsed: {parsed}\tAnalyzed: {analyzed}\tFailed: {failed}\tRedundant dependencies: {redundant}', end='')

def has_tf_files(directory: Path) -> bool:
    return any(p.suffix == '.tf' for p in directory.iterdir() if p.is_file())

with OUTPUT.open('w') as out:
    process_directory(ROOT, out)

print('\nDetailed feedback available in output.txt')
