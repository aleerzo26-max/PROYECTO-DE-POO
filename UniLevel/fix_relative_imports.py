import pathlib
import re

root = pathlib.Path('.')
pattern = re.compile(r'^(?P<indent>\s*from\s+)(?P<dots>\.+)(?P<module>[\w\.]*)(?P<rest>\s+import\s+.+)$')
modified = []
changed_imports = 0

for path in sorted(root.rglob('*.py')):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    new_lines = []
    changed = False

    for line in lines:
        m = pattern.match(line)
        if m:
            dots = m.group('dots')
            module = m.group('module')
            module_parts = [] if module == '' else module.split('.')
            depth = len(dots) - 1
            current_dir = path.parent
            target_dir = current_dir
            for _ in range(depth):
                target_dir = target_dir.parent

            if target_dir == root:
                abs_parts = module_parts
            else:
                rel = target_dir.relative_to(root)
                abs_parts = list(rel.parts) + module_parts

            new_module = '.'.join(abs_parts) if abs_parts else ''
            if new_module == '':
                new_module = '.'.join(current_dir.relative_to(root).parts)

            newline = f"{m.group('indent')}{new_module}{m.group('rest')}"
            if newline != line:
                line = newline
                changed = True
                changed_imports += 1
        new_lines.append(line)

    if changed:
        path.write_text('\n'.join(new_lines) + ('\n' if text.endswith('\n') else ''), encoding='utf-8')
        modified.append(str(path))

print('MODIFIED_FILES', len(modified))
for p in modified:
    print(p)
print('CHANGED_IMPORTS', changed_imports)
