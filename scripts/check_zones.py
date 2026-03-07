# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')
from docx import Document
from emba_checker.zone_detector import detect_zones

doc = Document('D:/Projects/ThesisFormatCheck/emba_checker/tests/test_full_compliant.docx')
zones = detect_zones(doc)

# 查看每个区域的实际文本
from collections import defaultdict
zone_texts = defaultdict(list)

for i, p in enumerate(doc.paragraphs):
    z = zones.get(i, 'unknown')
    zone_texts[z].append(p.text)

# 查看 copyright 区域
print('=== copyright 区域 ===')
for t in zone_texts.get('copyright', []):
    print(t[:100])
print()

# 查看 cover 区域
print('=== cover 区域 ===')
for t in zone_texts.get('cover', []):
    print(t[:100])
print()

# 检查关键词是否存在
print('关键词检查:')
print('  收存 in copyright:', any('收存' in t for t in zone_texts.get('copyright', [])))
print('  原创性 in copyright:', any('原创性' in t for t in zone_texts.get('copyright', [])))
print('  授权 in copyright:', any('授权' in t for t in zone_texts.get('copyright', [])))
print('  承诺书 in copyright:', any('承诺书' in t for t in zone_texts.get('copyright', [])))
print('  图 in body:', any('图' in t for t in zone_texts.get('body_chapter', [])))
