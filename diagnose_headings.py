# -*- coding: utf-8 -*-
"""
Diagnose all Heading 1 paragraph styles, font sizes, and spacing differences
"""
import sys
import os
import glob

sys.stdout.reconfigure(encoding='utf-8')

from docx import Document
from docx.oxml.ns import qn

# Find latest fixed docx
files = glob.glob('data/test_已修复_*.docx')
files.sort(key=os.path.getmtime, reverse=True)
latest = files[0]
print(f'Analyzing: {latest}\n')

doc = Document(latest)
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

# Collect all Heading 1 paragraphs
headings = []
for idx, para in enumerate(doc.paragraphs):
    if para.style and 'Heading 1' in para.style.name:
        text = para.text.strip()[:40]
        
        # Font size
        font_size = None
        if para.runs and para.runs[0].font.size:
            font_size = para.runs[0].font.size.pt
        
        # Bold
        bold = None
        if para.runs and para.runs[0].font.bold is not None:
            bold = para.runs[0].font.bold
        
        # Get pPr / w:spacing from XML
        pPr = para._element.find('.//w:pPr', NS)
        spacing = {}
        if pPr is not None:
            wspacing = pPr.find('.//w:spacing', NS)
            if wspacing is not None:
                spacing['before'] = wspacing.get(qn('w:before'))
                spacing['after'] = wspacing.get(qn('w:after'))
                spacing['line'] = wspacing.get(qn('w:line'))
                spacing['lineRule'] = wspacing.get(qn('w:lineRule'))
        
        headings.append({
            'idx': idx,
            'text': text,
            'style': para.style.name,
            'font_size': font_size,
            'bold': bold,
            'spacing': spacing,
            'para': para
        })

print(f'Found {len(headings)} Heading 1 paragraphs\n')
print('=' * 80)

# Display by group
for h in headings:
    print(f"\n[Para {h['idx']}] {h['text']}")
    print(f"  Style: {h['style']}")
    print(f"  Font size: {h['font_size']} pt" if h['font_size'] else "  Font size: (inherit)")
    print(f"  Bold: {h['bold']}")
    
    sp = h['spacing']
    if sp:
        # Show raw XML values (in EMU)
        print(f"  XML spacing (EMU): before={sp.get('before')}, after={sp.get('after')}, line={sp.get('line')}, lineRule={sp.get('lineRule')}")
        
        # Convert to pt (1 pt = 20 EMU)
        before_pt = int(sp['before']) / 20 if sp.get('before') else None
        after_pt = int(sp['after']) / 20 if sp.get('after') else None
        line_pt = int(sp['line']) / 20 if sp.get('line') else None
        
        print(f"  Converted to pt: before={before_pt}pt, after={after_pt}pt, line={line_pt}pt")
        
        # python-docx paragraph_format
        pf = h['para'].paragraph_format
        pf_before = pf.space_before.pt if pf.space_before else None
        pf_after = pf.space_after.pt if pf.space_after else None
        print(f"  python-docx pf: space_before={pf_before}pt, space_after={pf_after}pt, line_spacing={pf.line_spacing}")

print('\n' + '=' * 80)
print('\n=== KEY FINDINGS ===')

print('\n1. Font size comparison:')
chapters_with_size = [h for h in headings if h['font_size'] is not None]
if chapters_with_size:
    sizes = {}
    for h in chapters_with_size:
        key = h['font_size']
        sizes[key] = sizes.get(key, 0) + 1
    for size, count in sorted(sizes.items()):
        print(f'  {size} pt: {count} headings')
else:
    print('  All headings inherit font size from style')

print('\n2. Spacing issues:')
problematic = []
for h in headings:
    sp = h['spacing']
    pf = h['para'].paragraph_format
    
    has_issue = False
    issues = []
    
    # Check XML before value
    if sp.get('before'):
        before_emu = int(sp['before'])
        if before_emu > 0:
            has_issue = True
            issues.append(f'XML before={before_emu}')
    
    # Check python-docx space_before
    if pf.space_before and pf.space_before.pt and pf.space_before.pt > 0:
        has_issue = True
        issues.append(f'python-docx space_before={pf.space_before.pt}pt')
    
    if has_issue:
        problematic.append((h['text'], issues))

if problematic:
    for text, issues in problematic:
        print(f'  [{text}] {", ".join(issues)}')
else:
    print('  No spacing issues found')

print('\n3. Suggested fixes:')
print('  - FixA: Normalize all Heading 1 font sizes')
print('  - FixB: Clear XML w:spacing before/after, ensure 0')
print('  - FixC: For ref/appendix/acknowledgments, keep style consistent while removing numbering')
