# -*- coding: utf-8 -*-
"""
研究Word Heading样式的XML结构，特别是多级列表编号
"""
from docx import Document
from docx.oxml import OxmlElement

# 定义命名空间
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

doc = Document('data/test.docx')

print("=" * 60)
print("查找包含'第八章'/'第九章'/'第十章'的Heading 1段落")
print("=" * 60)

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if ('第八章' in text or '第九章' in text or '第十章' in text or 
        '参考文献' in text or '附录' in text or '致谢' in text):
        style_name = para.style.name if para.style else 'None'
        
        # 获取XML元素
        para_xml = para._element
        
        # 查找 numPr 元素（编号属性）
        numPr = para_xml.find('.//w:numPr', NS)
        
        print(f"\n段落 {i}:")
        print(f"  文本: {text[:60]}")
        print(f"  样式: {style_name}")
        
        if numPr is not None:
            print(f"  有numPr编号元素!")
            # 打印numPr的子元素
            for child in numPr:
                print(f"    {child.tag}: {child.attrib}")
        else:
            print(f"  无numPr编号元素")
        
        # 检查outlineLvl
        outlineLvl = para_xml.find('.//w:outlineLvl', NS)
        if outlineLvl is not None:
            print(f"  outlineLvl: {outlineLvl.attrib}")
