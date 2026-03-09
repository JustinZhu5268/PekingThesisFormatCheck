# -*- coding: utf-8 -*-
"""检查Word文档的numbering.xml定义"""
import zipfile
import xml.etree.ElementTree as ET

# Word文档是zip文件，打开numbering.xml
docx_path = 'data/test.docx'

with zipfile.ZipFile(docx_path, 'r') as z:
    # 读取numbering.xml
    try:
        numbering_xml = z.read('word/numbering.xml')
        
        # 解析XML
        root = ET.fromstring(numbering_xml)
        
        # 定义命名空间
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        print("=" * 70)
        print("Word numbering.xml 结构分析")
        print("=" * 70)
        
        # 查找所有num元素（编号定义）
        num_elements = root.findall('.//w:num', ns)
        print(f"\n找到 {len(num_elements)} 个num元素（编号定义）\n")
        
        for num in num_elements:
            num_id = num.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numId')
            print(f"numId: {num_id}")
            
            # 查找abstractNumId
            abstractNum = num.find('.//w:abstractNumId', ns)
            if abstractNum is not None:
                abstract_id = abstractNum.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                print(f"  abstractNumId: {abstract_id}")
            
            # 查找lvl（级别定义）
            lvl_elements = num.findall('.//w:lvl', ns)
            for lvl in lvl_elements:
                lvl_text = lvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
                print(f"    lvl (ilvl): {lvl_text}")
                
                # 查找numFmt（编号格式）
                numFmt = lvl.find('.//w:numFmt', ns)
                if numFmt is not None:
                    fmt = numFmt.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    print(f"      numFmt: {fmt}")
                
                # 查找levelText（级别文本，如"第%1章"）
                levelText = lvl.find('.//w:levelText', ns)
                if levelText is not None:
                    val = levelText.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    print(f"      levelText: {val}")
                
                # 查找suffix（后缀）
                suffix = lvl.find('.//w:suffix', ns)
                if suffix is not None:
                    suf_val = suffix.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    print(f"      suffix: {suf_val}")
            
            print()
        
    except KeyError:
        print("未找到numbering.xml")
