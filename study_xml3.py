# -*- coding: utf-8 -*-
"""深入研究Word Heading编号的XML结构"""
from docx import Document
from docx.oxml import OxmlElement

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

output = []

doc = Document('data/test.docx')

output.append("=" * 70)
output.append("检查前面章节的Heading 1 - 查看完整XML")
output.append("=" * 70)

# 检查前面章节的Heading 1 (第一章到第七章)
for i in range(200, 220):
    para = doc.paragraphs[i]
    style_name = para.style.name if para.style else 'None'
    if 'Heading 1' in style_name:
        text = para.text.strip()
        output.append(f"\n段落 {i}: [{style_name}]")
        output.append(f"  文本: {text[:50]}")
        
        # 获取完整XML
        para_xml = para._element.xml
        # 查找numPr
        if 'numPr' in para_xml:
            output.append(f"  包含numPr!")
        else:
            output.append(f"  无numPr")
        
        # 检查w:pPr
        pPr = para._element.find('.//w:pPr', NS)
        if pPr is not None:
            output.append(f"  有pPr元素")
            # 打印pPr下的所有子元素
            for child in pPr:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                output.append(f"    {tag}: {dict(child.attrib)}")
        break  # 只看一个例子

output.append("\n" + "=" * 70)
output.append("检查末尾Heading 1 - 参考文献/附录/致谢")
output.append("=" * 70)

# 检查末尾章节
for i in range(1010, 1070):
    para = doc.paragraphs[i]
    style_name = para.style.name if para.style else 'None'
    text = para.text.strip()
    if 'Heading 1' in style_name and ('参考文献' in text or '附录' in text or '致谢' in text):
        output.append(f"\n段落 {i}: [{style_name}]")
        output.append(f"  文本: {text[:60]}")
        
        # 获取完整XML
        para_xml = para._element.xml
        if 'numPr' in para_xml:
            output.append(f"  包含numPr!")
        else:
            output.append(f"  无numPr")
        
        # 检查w:pPr
        pPr = para._element.find('.//w:pPr', NS)
        if pPr is not None:
            output.append(f"  有pPr元素")
            for child in pPr:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                output.append(f"    {tag}: {dict(child.attrib)}")
        
        # 打印rPr (段落标记属性)
        rPr = para._element.find('.//w:rPr', NS)
        if rPr is not None:
            output.append(f"  有rPr元素")

# 检查document.xml中的numbering定义
output.append("\n" + "=" * 70)
output.append("检查文档样式定义")
output.append("=" * 70)

# 检查样式
styles = doc.styles
for style in styles:
    if style.name and 'Heading 1' in style.name:
        output.append(f"样式: {style.name}, 类型: {style.type}")
        # 检查样式的XML
        try:
            style_xml = style._element.xml
            if 'numPr' in style_xml:
                output.append(f"  包含numPr定义!")
                # 查找ilvl和numId
                import re
                ilvl = re.search(r'<w:ilvl.*?w:val="(\d+)".*?/>', style_xml)
                numId = re.search(r'<w:numId.*?w:val="(\d+)".*?/>', style_xml)
                if ilvl: output.append(f"    ilvl: {ilvl.group(1)}")
                if numId: output.append(f"    numId: {numId.group(1)}")
        except:
            pass

# 保存到文件
with open('study_output2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("已保存到 study_output2.txt")
