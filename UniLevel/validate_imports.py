import pathlib
import re
import py_compile

root = pathlib.Path('.')
pattern = re.compile(r'^(\s*from\s+)(\.+)([\w\.]*)(\s+import\s+.+)$')
errors = []

for path in sorted(root.rglob('*.py')):
    text = path.read_text(encoding='utf-8')
    for i, line in enumerate(text.splitlines(), 1):
        if pattern.match(line):
            errors.append((path, i, line.strip()))

if errors:
    print('REMAINING_RELATIVE_IMPORTS', len(errors))
    for path, i, line in errors:
        print(f'{path}:{i}: {line}')
else:
    print('NO_REMAINING_RELATIVE_IMPORTS')

failed = []
for path in sorted(root.rglob('*.py')):
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        failed.append((path, str(exc)))
    except Exception as exc:
        failed.append((path, str(exc)))

if failed:
    print('COMPILE_ERRORS', len(failed))
    for path, msg in failed[:20]:
        print(f'{path}: {msg}')
else:
    print('ALL_COMPILED')
