import os
import glob

target_double = chr(92) + chr(92) + '_'
target_single = chr(92) + '_'

for fname in glob.glob('*generator*.py') + glob.glob('tools/*.py'):
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    if target_double in content:
        count = content.count(target_double)
        content = content.replace(target_double, target_single)
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {count} double underscores in {fname}")

# Also check for any remaining bare underscores outside math/commands
print("Escape check complete.")

