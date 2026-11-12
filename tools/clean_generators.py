import os
import re

def fix_text(s):
    # Replace markdown backticks with \texttt{...} and escape underscores inside
    def repl(m):
        content = m.group(1)
        content_escaped = content.replace('_', r'\_').replace('&', r'\&').replace('%', r'\%')
        return r'\texttt{' + content_escaped + '}'
    
    # We use regex with chr(96) to avoid backtick issues in python
    bt = chr(96)
    pattern = bt + r'([^' + bt + r']+)' + bt
    s = re.sub(pattern, repl, s)
    return s

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = fix_text(content)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {path}")
    else:
        print(f"No changes in {path}")

for fname in ['chapter_three_generator.py', 'chapter_four_generator.py', 'chapter_five_generator.py']:
    if os.path.exists(fname):
        clean_file(fname)

# Now specifically handle chapter_six_and_backmatter_generator.py
path6 = 'chapter_six_and_backmatter_generator.py'
with open(path6, 'r', encoding='utf-8') as f:
    text6 = f.read()

# 1. Remove CRediT Author Statement chapter
credit_start = text6.find(r'\chapter*{CRediT Author Statement}')
if credit_start != -1:
    disclosures_start = text6.find(r'\chapter*{Disclosures and AI Assistance Statement}')
    if disclosures_start != -1:
        text6 = text6[:credit_start] + text6[disclosures_start:]
        print("Removed CRediT Author Statement from chapter_six_and_backmatter_generator.py")

# 2. Fix backticks
text6 = fix_text(text6)

with open(path6, 'w', encoding='utf-8') as f:
    f.write(text6)
print("Updated chapter_six_and_backmatter_generator.py")

