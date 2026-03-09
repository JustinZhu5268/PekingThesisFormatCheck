# -*- coding: utf-8 -*-
import re

with open('emba_checker/docx_autofixer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并注释掉插入分节符的代码
old_code = '''            # 如果是参考文献，在其之前插入分节符（使用无空格版本比较）
            text_nospace = text.replace(' ', '').replace('\t', '')
            if text_nospace == "参考文献":
                try:
                    self._insert_section_break_before_paragraph(i)
                    print(f"    已插入分节符（参考文献前）")
                except Exception as e:
                    print(f"    插入分节符失败: {e}")'''

new_code = '''            # 注意：不再在参考文献前插入分节符，因为这会导致section过多问题
            # text_nospace = text.replace(' ', '').replace('\t', '')
            # if text_nospace == "参考文献":
            #     try:
            #         self._insert_section_break_before_paragraph(i)
            #         print(f"    已插入分节符（参考文献前）")
            #     except Exception as e:
            #         print(f"    插入分节符失败: {e}")'''

content = content.replace(old_code, new_code)

with open('emba_checker/docx_autofixer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
