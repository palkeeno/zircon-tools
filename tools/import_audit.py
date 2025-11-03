import ast
import os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

ignore_dirs = {"__pycache__", "venv", ".venv", "env", ".env"}

py_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip ignored dirs
    parts = dirpath.split(os.sep)
    if any(p in ignore_dirs for p in parts):
        continue
    for fn in filenames:
        if fn.endswith('.py'):
            py_files.append(os.path.join(dirpath, fn))

unused_imports = []
styles = defaultdict(set)  # package -> set of styles seen

def name_from_alias(alias):
    return alias.asname if alias.asname else alias.name

for fpath in sorted(py_files):
    try:
        with open(fpath, 'r', encoding='utf8') as f:
            src = f.read()
        tree = ast.parse(src, filename=fpath)
    except Exception as e:
        print(f"[PARSE ERROR] {fpath}: {e}")
        continue

    # collect imported symbols and their local names
    imports = []  # tuples (module, name, asname, lineno, is_from)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name  # e.g. 'config.config'
                local = name_from_alias(alias)
                imports.append((module, None, local, node.lineno, False))
                # style: 'import <module> as <local>' or 'import <module>'
                if '.' in module:
                    root = module.split('.')[0]
                else:
                    root = module
                styles[root].add(f"import {module} as {local}" if alias.asname else f"import {module}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                name = alias.name
                local = name_from_alias(alias)
                imports.append((module, name, local, node.lineno, True))
                root = module.split('.')[0] if module else ''
                styles[root].add(f"from {module} import {name} as {local}" if alias.asname else f"from {module} import {name}")

    # find used names in file
    used = set()
    for node in ast.walk(tree):
        # Name nodes represent variable/identifier usage
        if isinstance(node, ast.Name):
            used.add(node.id)
        # Attribute uses like config.CWD will have Name node for 'config'
        # so above captures it

    # identify unused imports (simple heuristic)
    for module, name, local, lineno, is_from in imports:
        if local not in used:
            unused_imports.append((fpath, lineno, module, name, local, is_from))

# Print summary
print('=== IMPORT AUDIT REPORT ===')
print(f'Files scanned: {len(py_files)}')
print('\n-- Packages import style summary --')
for pkg in sorted(styles.keys()):
    if not pkg:
        continue
    vals = styles[pkg]
    if len(vals) > 1:
        print(f"[INCONSISTENT] {pkg}: styles={sorted(vals)}")
    else:
        print(f"{pkg}: {next(iter(vals)) if vals else ''}")

print('\n-- Possibly UNUSED imports (heuristic) --')
if not unused_imports:
    print('No suspicious unused imports found by heuristic')
else:
    for fpath, lineno, module, name, local, is_from in unused_imports:
        if is_from:
            print(f"{fpath}:{lineno} - from {module} import {name} as {local} (unused={local})")
        else:
            print(f"{fpath}:{lineno} - import {module} as {local} (unused={local})")

print('\nNote: This is a heuristic AST-based check. "Unused" may be false-positive if imports are used dynamically or in __all__ or in type comments. Review before removing.')
