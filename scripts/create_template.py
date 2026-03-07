# -*- coding: utf-8 -*-
"""
创建完全合规的测试模板 docx
严格遵循 EMBA 论文格式规范
"""
import sys
sys.path.insert(0, 'D:/Projects/ThesisFormatCheck')

from docx import Document
from docx.shared import Pt, Cm, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def create_compliant_template():
    doc = Document()
    
    # ========== 页面设置 (A4, 页边距上下3.0/2.5, 左右2.6) ==========
    section = doc.sections[0]
    section.page_width = Cm(21.0)   # A4
    section.page_height = Cm(29.7)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.6)
    section.right_margin = Cm(2.6)
    
    # ========== 封面 COVER_01-06 ==========
    # 论文标题 - 黑体26pt加粗居中
    title = doc.add_paragraph()
    run = title.add_run("企业战略管理与组织变革研究")
    run.font.name = "黑体"
    run.font.size = Pt(26)
    run.font.bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()  # 空行
    
    # 学校名称 - 宋体16pt居中
    school = doc.add_paragraph()
    run = school.add_run("北京大学光华管理学院")
    run.font.name = "宋体"
    run.font.size = Pt(16)
    school.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 学位类型 - 宋体16pt居中
    degree = doc.add_paragraph()
    run = degree.add_run("( 学术学位    专业学位 )")
    run.font.name = "宋体"
    run.font.size = Pt(16)
    degree.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # ========== 版权声明 DECL_01-04 ==========
    doc.add_page_break()
    
    # 标题 - 黑体16pt居中
    copyright_title = doc.add_paragraph()
    run = copyright_title.add_run("版权声明")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    copyright_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 正文 - 仿宋16pt
    copyright_text = doc.add_paragraph()
    run = copyright_text.add_run("任何收存和保管本论文各种版本的单位和个人，未经本论文作者书面同意，不得将本论文转借他人并以各种形式复制、传播。")
    run.font.name = "仿宋"
    run.font.size = Pt(16)
    copyright_text.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 原创性声明
    decl1 = doc.add_paragraph()
    run = decl1.add_run("原创性声明")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    decl1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    decl2 = doc.add_paragraph()
    run = decl2.add_run("本人声明：所呈交的学位论文是本人在导师指导下进行的研究工作及取得的研究成果。除了文中特别加以标注和致谢的地方外，论文中不包含其他人已经发表或撰写过的研究成果，也不包含为获得北京大学或其他教育机构的学位或证书而使用过的材料。")
    run.font.name = "仿宋"
    run.font.size = Pt(16)
    
    # 授权说明
    decl3 = doc.add_paragraph()
    run = decl3.add_run("学位论文使用授权说明")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    decl3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    decl4 = doc.add_paragraph()
    run = decl4.add_run("本人完全了解北京大学有关保留、使用学位论文的规定，即：学校有权保留本人的学位论文复印件和电子版，允许论文被查阅和借阅；学校可以公布论文的全部或部分内容。")
    run.font.name = "仿宋"
    run.font.size = Pt(16)
    
    # 承诺书
    decl5 = doc.add_paragraph()
    run = decl5.add_run("提交终版学位论文承诺书")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    decl5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    decl6 = doc.add_paragraph()
    run = decl6.add_run("本人承诺提交的终版学位论文与最终定稿一致，如有虚假愿承担法律责任。")
    run.font.name = "仿宋"
    run.font.size = Pt(16)
    
    # ========== 中文摘要 ABSTRACT_CN_01-14 ==========
    doc.add_page_break()
    
    # 标题 - 黑体16pt居中，段前24磅段后18磅
    abstract_title = doc.add_paragraph()
    run = abstract_title.add_run("摘    要")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    abstract_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    abstract_title.paragraph_format.space_before = Pt(24)
    abstract_title.paragraph_format.space_after = Pt(18)
    
    # 正文 - 宋体14pt，两端对齐，首行缩进2字符，行距20pt
    abstract_text = doc.add_paragraph()
    text = "本论文以某企业为例，探讨了企业战略管理与组织变革之间的关系及其对企业绩效的影响。研究发现，有效的战略管理与组织变革能够显著提升企业的核心竞争力。本文采用案例研究方法，通过对多家企业的调研分析，验证了假设模型的有效性。研究结果表明，企业在实施战略转型时，需要充分考虑组织文化、组织结构、人力资源等多方面因素。本文的创新点在于构建了战略管理与组织变革的整合框架，为企业实践提供了理论指导。本研究的数据来源于对100家企业问卷调查和深度访谈，时间跨度为2023年1月至2024年6月。通过实证分析，本文提出了针对性的管理建议，为企业战略决策提供了参考依据。"
    run = abstract_text.add_run(text)
    run.font.name = "宋体"
    run.font.size = Pt(14)
    abstract_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abstract_text.paragraph_format.first_line_indent = Pt(28)  # 2字符
    abstract_text.paragraph_format.line_spacing_rule = 1  # EXACTLY
    abstract_text.paragraph_format.line_spacing = Pt(20)
    
    # 关键词 - 宋体12pt
    keywords = doc.add_paragraph()
    run = keywords.add_run("关键词：战略管理；组织变革；企业转型；管理创新")
    run.font.name = "宋体"
    run.font.size = Pt(12)
    keywords.paragraph_format.space_after = Pt(0)
    
    # ========== 英文摘要 ABSTRACT_EN_01-05 ==========
    doc.add_page_break()
    
    # 标题 - Arial16pt居中
    abstract_en_title = doc.add_paragraph()
    run = abstract_en_title.add_run("ABSTRACT")
    run.font.name = "Arial"
    run.font.size = Pt(16)
    abstract_en_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    abstract_en_title.paragraph_format.space_before = Pt(24)
    abstract_en_title.paragraph_format.space_after = Pt(18)
    
    # 正文 - Times New Roman12pt，两端对齐，首行缩进
    abstract_en_text = doc.add_paragraph()
    text_en = "This thesis explores the relationship between enterprise strategic management and organizational change and their impact on firm performance. Using case study methodology, this research analyzes multiple companies and verifies the proposed model. The results indicate that effective strategic management and organizational change can significantly enhance core competitiveness. The innovation of this paper lies in constructing an integrated framework for strategic management and organizational change, providing theoretical guidance for enterprise practice."
    run = abstract_en_text.add_run(text_en)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    abstract_en_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abstract_en_text.paragraph_format.first_line_indent = Pt(24)
    abstract_en_text.paragraph_format.line_spacing_rule = 1
    abstract_en_text.paragraph_format.line_spacing = Pt(20)
    abstract_en_text.paragraph_format.space_after = Pt(0)
    
    # Keywords - Arial14pt加粗居中
    keywords_en = doc.add_paragraph()
    run = keywords_en.add_run("Keywords: strategic management; organizational change; enterprise transformation; management innovation")
    run.font.name = "Arial"
    run.font.size = Pt(14)
    run.font.bold = True
    keywords_en.alignment = WD_ALIGN_PARAGRAPH.CENTER
    keywords_en.paragraph_format.space_before = Pt(8)
    keywords_en.paragraph_format.space_after = Pt(6)
    
    # ========== 目录 TOC_01-11 ==========
    doc.add_page_break()
    
    # 标题 - 黑体16pt居中
    toc_title = doc.add_paragraph()
    run = toc_title.add_run("目    录")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 目录内容 - 宋体14pt
    toc_items = [
        ("第一章 绪论", "1"),
        ("1.1 研究背景", "3"),
        ("1.2 研究意义", "5"),
        ("第二章 文献综述", "8"),
        ("2.1 战略管理理论", "8"),
        ("2.2 组织变革理论", "12"),
        ("第三章 研究方法", "18"),
        ("3.1 研究假设", "18"),
        ("3.2 数据来源", "20"),
        ("第四章 案例分析", "22"),
        ("4.1 A公司战略转型", "22"),
        ("4.2 B公司组织变革", "28"),
        ("4.3 比较分析", "32"),
        ("第五章 研究结论", "35"),
        ("5.1 主要结论", "35"),
        ("5.2 政策建议", "37"),
        ("参考文献", "40"),
        ("致谢", "45"),
        ("附录A 调查问卷", "48"),
    ]
    
    for title_text, page_num in toc_items:
        toc_para = doc.add_paragraph()
        run = toc_para.add_run(f"{title_text} ........................................ {page_num}")
        run.font.name = "宋体"
        run.font.size = Pt(14)
    
    # ========== 正文 BODY_01-06 ==========
    doc.add_page_break()
    
    # 第一章 绪论 - 黑体16pt居中
    ch1_title = doc.add_paragraph()
    run = ch1_title.add_run("第一章 绪论")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    ch1_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 1.1 研究背景 - 黑体14pt加粗居左
    ch1_1_title = doc.add_paragraph()
    run = ch1_1_title.add_run("1.1 研究背景")
    run.font.name = "黑体"
    run.font.size = Pt(14)
    run.font.bold = True
    ch1_1_title.paragraph_format.line_spacing_rule = 2  # MULTIPLE
    ch1_1_title.paragraph_format.line_spacing = 1.5
    ch1_1_title.paragraph_format.space_before = Pt(24)
    ch1_1_title.paragraph_format.space_after = Pt(6)
    
    # 正文 - 宋体12pt，两端对齐，首行缩进2字符
    for i in range(50):  # 20000字需要大量段落
        body_text = doc.add_paragraph()
        text = f"随着全球经济一体化进程的加快，企业面临的竞争环境日益复杂多变。在这样的背景下，战略管理与组织变革成为企业获取竞争优势的关键途径。研究表明，有效的战略规划能够帮助企业更好地适应外部环境的变化，而组织变革则是实现战略目标的重要保障。本研究旨在探讨战略管理与组织变革之间的内在关联，以及它们对企业绩效的影响机制。{i}"
        run = body_text.add_run(text)
        run.font.name = "宋体"
        run.font.size = Pt(12)
        body_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        body_text.paragraph_format.first_line_indent = Pt(24)
        body_text.paragraph_format.line_spacing_rule = 2
        body_text.paragraph_format.line_spacing = 1.5
    
    # 1.2 研究意义
    ch1_2_title = doc.add_paragraph()
    run = ch1_2_title.add_run("1.2 研究意义")
    run.font.name = "黑体"
    run.font.size = Pt(14)
    run.font.bold = True
    ch1_2_title.paragraph_format.line_spacing_rule = 2
    ch1_2_title.paragraph_format.line_spacing = 1.5
    ch1_2_title.paragraph_format.space_before = Pt(24)
    ch1_2_title.paragraph_format.space_after = Pt(6)
    
    body_text2 = doc.add_paragraph()
    run = body_text2.add_run("本研究的理论意义在于丰富了战略管理与组织变革的理论框架，为企业管理者提供了科学的决策依据。实践意义在于通过案例分析，为企业实施战略转型提供可借鉴的经验和方法。")
    run.font.name = "宋体"
    run.font.size = Pt(12)
    body_text2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    body_text2.paragraph_format.first_line_indent = Pt(24)
    body_text2.paragraph_format.line_spacing_rule = 2
    body_text2.paragraph_format.line_spacing = 1.5
    
    # 图示例 - 宋体10.5pt居中，段前6磅段后12磅
    fig_para = doc.add_paragraph()
    run = fig_para.add_run("图 1.1 企业战略管理框架")
    run.font.name = "宋体"
    run.font.size = Pt(10.5)
    fig_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fig_para.paragraph_format.space_before = Pt(6)
    fig_para.paragraph_format.space_after = Pt(12)
    
    # 表示例 - 宋体10.5pt居中，段前12磅段后6磅
    table_para = doc.add_paragraph()
    run = table_para.add_run("表 1.1 研究对象基本特征")
    run.font.name = "宋体"
    run.font.size = Pt(10.5)
    table_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table_para.paragraph_format.space_before = Pt(12)
    table_para.paragraph_format.space_after = Pt(6)
    
    # 表格内容
    table = doc.add_table(rows=3, cols=3)
    table.style = 'Table Grid'
    table.cell(0, 0).text = '企业名称'
    table.cell(0, 1).text = '所属行业'
    table.cell(0, 2).text = '员工数量'
    table.cell(1, 0).text = 'A公司'
    table.cell(1, 1).text = '制造业'
    table.cell(1, 2).text = '1000人'
    table.cell(2, 0).text = 'B公司'
    table.cell(2, 1).text = '服务业'
    table.cell(2, 2).text = '500人'
    
    # 公式示例 - 宋体12pt居中
    expr_para = doc.add_paragraph()
    run = expr_para.add_run("式 (1.1) Y = aX + b + c")
    run.font.name = "宋体"
    run.font.size = Pt(12)
    expr_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    expr_para.paragraph_format.line_spacing_rule = 2
    expr_para.paragraph_format.line_spacing = 1.0
    expr_para.paragraph_format.space_before = Pt(6)
    expr_para.paragraph_format.space_after = Pt(6)
    
    # ========== 参考文献 REFERENCES_01-51 ==========
    doc.add_page_break()
    
    # 标题 - 黑体16pt居中
    ref_title = doc.add_paragraph()
    run = ref_title.add_run("参考文献")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    ref_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 参考文献条目 - Times New Roman10.5pt，悬挂缩进
    refs = [
        "[1] 张三. 企业战略管理研究[M]. 北京: 北京大学出版社, 2020.",
        "[2] 李四, 王五. 组织变革与绩效关系研究[J]. 管理世界, 2019, 35(4): 45-58.",
        "[3] ABC Corporation. Annual Report 2021[R]. 2022.",
        "[4] 陈六. 战略管理理论与实践[M]. 上海: 上海财经大学出版社, 2018.",
        "[5] 赵七, 孙八. 企业转型路径研究[J]. 经济管理, 2021, 43(2): 12-25.",
        "[6] Smith J. Strategic Management in Global Context[M]. New York: Springer, 2019.",
        "[7] Johnson M, Williams K. Organizational Change and Performance[J]. Harvard Business Review, 2020, 98(3): 78-85.",
        "[8] 刘九. 管理创新与企业竞争力研究[D]. 北京大学, 2022.",
        "[9] 周十. 组织结构变革对企业绩效的影响机制研究[J]. 南开管理评论, 2018, 21(5): 112-123.",
        "[10] Brown A, Davis P. Strategic Management: Concepts and Cases[M]. London: Pearson, 2021.",
        "[11] 吴一. 企业战略联盟的形成与合作机制研究[J]. 中国工业经济, 2019, 36(7): 89-103.",
        "[12] 郑二. 跨国公司战略管理本土化研究[J]. 管理世界, 2020, 36(8): 156-170.",
        "[13] Wang L, Chen M. Digital Transformation and Strategic Management[J]. Journal of Business Research, 2021, 132: 234-245.",
        "[14] 马三. 企业核心竞争力的构建与提升研究[J]. 经济理论与经济管理, 2018, 38(4): 67-79.",
        "[15] 胡四. 战略人力资源管理与企业绩效关系研究[J]. 外国经济与管理, 2019, 41(9): 45-58.",
    ]
    
    for ref in refs:
        ref_para = doc.add_paragraph()
        run = ref_para.add_run(ref)
        run.font.name = "Times New Roman"
        run.font.size = Pt(10.5)
        ref_para.paragraph_format.first_line_indent = Pt(-21.6)
        ref_para.paragraph_format.left_indent = Pt(21.6)
    
    # ========== 附录 APPENDIX_01-04 ==========
    doc.add_page_break()
    
    # 附录标题 - 黑体16pt居中
    app_title = doc.add_paragraph()
    run = app_title.add_run("附录A    调查问卷")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    run.font.bold = True
    app_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 附录内容 - 宋体12pt
    for i in range(5):
        app_text = doc.add_paragraph()
        run = app_text.add_run(f"以下为本次研究使用的调查问卷第{i+1}部分内容...")
        run.font.name = "宋体"
        run.font.size = Pt(12)
        app_text.paragraph_format.first_line_indent = Pt(24)
    
    # ========== 致谢 ACKNOWLEDGMENT_01-02 ==========
    doc.add_page_break()
    
    # 标题 - 黑体16pt居中
    ack_title = doc.add_paragraph()
    run = ack_title.add_run("致    谢")
    run.font.name = "黑体"
    run.font.size = Pt(16)
    ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 致谢正文 - 宋体12pt，首行缩进
    ack_text = doc.add_paragraph()
    run = ack_text.add_run("感谢我的导师XXX教授的悉心指导，感谢所有帮助过我的老师和同学。感谢北京大学光华管理学院提供的良好学习环境。感谢家人的支持和鼓励。")
    run.font.name = "宋体"
    run.font.size = Pt(12)
    ack_text.paragraph_format.first_line_indent = Pt(24)
    
    return doc

if __name__ == "__main__":
    doc = create_compliant_template()
    output_path = "D:/Projects/ThesisFormatCheck/emba_checker/tests/test_complete_template.docx"
    doc.save(output_path)
    print(f"完全合规测试模板已保存到: {output_path}")
