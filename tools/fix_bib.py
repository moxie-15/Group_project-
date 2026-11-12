import re

# Read chapter_six_and_backmatter_generator.py
with open('chapter_six_and_backmatter_generator.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix the broken \texttt{... in bibliography
# In bibliography, titles were like: ``Title,'' or \texttt{Title,'' or }\texttt{Title,''
# Let's replace any `\texttt{ or }\texttt{ in the bibliography section with "
bib_idx = text.find(r'\begin{thebibliography}')
if bib_idx != -1:
    bib_part = text[bib_idx:]
    front_part = text[:bib_idx]
    
    # Replace broken texttt patterns
    bib_part = bib_part.replace('}\\texttt{', '"')
    bib_part = bib_part.replace('`\\texttt{', '"')
    bib_part = bib_part.replace('\\texttt{', '"')
    # Replace '' with "
    bib_part = bib_part.replace("''", '"')
    # Replace `` with "
    bib_part = bib_part.replace('``', '"')
    
    text = front_part + bib_part

with open('chapter_six_and_backmatter_generator.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed bibliography in chapter_six_and_backmatter_generator.py")
