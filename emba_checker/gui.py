# -*- coding: utf-8 -*-
"""
EMBA 论文格式审查工具 - GUI 模块
基于 Tkinter 的极简图形界面
"""

import os
import sys
import threading
import queue
import shutil
from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, List, Any

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)


class EMBAcheckerGUI:
    """
    北大光华 EMBA 论文格式审查工具 - GUI
    
    界面规格：
    ┌──────────────────────────────────────────────────────────┐
    │  北大光华 EMBA 论文格式审查工具 v1.0                     │
    ├──────────────────────────────────────────────────────────┤
    │                                                          │
    │  论文文件：  [________________________] [选择文件...]     │
    │  MD规则文件：[________________________] [选择文件...]     │
    │                                                          │
    │  检查级别：                                               │
    │    ○ 仅 ★★★★★ 必须项                                    │
    │    ○ ★★★★☆ 以上                                         │
    │    ● 全部 164 条规则                                      │
    │                                                          │
    │  □ 启用 AI 辅助审查（需 Claude API Key）                  │
    │  API Key：[__________________________________________]    │
    │                                                          │
    │  [          开 始 审 查          ]                        │
    │                                                          │
    │  ┌─ 审查进度 ──────────────────────────────────────────┐ │
    │  │ ████████████████████░░░░░░░░ 62% (102/164)          │ │
    │  │ 当前：Group 2 — 正在检查正文段落格式...              │ │
    │  └────────────────────────────────────────────────────┘ │
    │                                                          │
    │  ┌─ 审查结果摘要 ──────────────────────────────────────┐ │
    │  │  发现 47 个问题：                                    │ │
    │  │    格式类: 23  │ 标点类: 8  │ 参考文献类: 12        │ │
    │  │  覆盖率核对：164/164 规则已检查 ✓                    │ │
    │  └────────────────────────────────────────────────────┘ │
    │                                                          │
    │  ┌─ 运行日志（实时滚动）─────────────────────────────┐  │
    │  │ [14:30:01] 加载规则库：164条规则                   │  │
    │  └──────────────────────────────────────────────────┘  │
    │                                                          │
    │  输出文件：                                              │
    │  📄 论文_审查结果_20260303_143016.docx    [打开文件]     │
    │  📄 论文_审查报告_20260303_143016.txt     [打开文件]     │
    └──────────────────────────────────────────────────────────┘
    """
    
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("北大光华 EMBA 论文格式审查工具 v1.0")
        self.root.geometry("700x750")
        self.root.resizable(False, False)
        
        # 变量
        self.doc_path = StringVar()
        self.rules_path = StringVar()
        self.check_level = StringVar(value="all")
        self.enable_ai = BooleanVar(value=False)
        self.api_key = StringVar()
        
        # 审查结果
        self.output_docx = ""
        self.output_report = ""
        self.issues: List[Any] = []
        
        # 进度队列
        self.progress_queue = queue.Queue()
        
        # 创建界面
        self._create_widgets()
        
        # 启动进度更新
        self._update_progress()
        
        # 加载默认规则路径
        default_rules = os.path.join(BASE_DIR, "rules_registry.json")
        if os.path.exists(default_rules):
            self.rules_path.set(default_rules)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=BOTH, expand=True)
        
        # ===== 标题 =====
        title_label = ttk.Label(
            main_frame, 
            text="北大光华 EMBA 论文格式审查工具 v1.0",
            font=("微软雅黑", 16, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # ===== 文件选择区域 =====
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=X, pady=(0, 10))
        
        # 论文文件
        doc_frame = ttk.Frame(file_frame)
        doc_frame.pack(fill=X, pady=3)
        ttk.Label(doc_frame, text="论文文件：").pack(side=LEFT)
        ttk.Entry(doc_frame, textvariable=self.doc_path, width=45).pack(side=LEFT, padx=5)
        ttk.Button(doc_frame, text="选择文件...", command=self._select_doc_file).pack(side=LEFT)
        
        # 规则文件
        rules_frame = ttk.Frame(file_frame)
        rules_frame.pack(fill=X, pady=3)
        ttk.Label(rules_frame, text="规则文件：").pack(side=LEFT)
        ttk.Entry(rules_frame, textvariable=self.rules_path, width=45).pack(side=LEFT, padx=5)
        ttk.Button(rules_frame, text="选择文件...", command=self._select_rules_file).pack(side=LEFT)
        
        # ===== 检查级别 =====
        level_frame = ttk.LabelFrame(main_frame, text="检查级别", padding="10")
        level_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Radiobutton(
            level_frame, 
            text="仅 ★★★★★ 必须项", 
            variable=self.check_level, 
            value="critical"
        ).pack(anchor=W, pady=2)
        ttk.Radiobutton(
            level_frame, 
            text="★★★★☆ 以上", 
            variable=self.check_level, 
            value="important"
        ).pack(anchor=W, pady=2)
        ttk.Radiobutton(
            level_frame, 
            text="全部 164 条规则", 
            variable=self.check_level, 
            value="all"
        ).pack(anchor=W, pady=2)
        
        # ===== AI 设置 =====
        ai_frame = ttk.LabelFrame(main_frame, text="AI 辅助", padding="10")
        ai_frame.pack(fill=X, pady=(0, 10))
        
        ai_check = ttk.Checkbutton(
            ai_frame,
            text="启用 AI 辅助审查（需 Claude API Key）",
            variable=self.enable_ai,
            command=self._toggle_api_key
        )
        ai_check.pack(anchor=W)
        
        api_frame = ttk.Frame(ai_frame)
        api_frame.pack(fill=X, pady=(5, 0))
        ttk.Label(api_frame, text="API Key：").pack(side=LEFT)
        self.api_key_entry = ttk.Entry(
            api_frame, 
            textvariable=self.api_key, 
            width=40,
            show="*"
        )
        self.api_key_entry.pack(side=LEFT, padx=5)
        
        # 默认禁用 API Key 输入
        self.api_key_entry.config(state=DISABLED)
        
        # ===== 开始审查按钮 =====
        self.start_button = ttk.Button(
            main_frame,
            text="开始审查",
            command=self._start_check,
            style="Accent.TButton"
        )
        self.start_button.pack(pady=10)
        
        # ===== 进度条 =====
        progress_frame = ttk.LabelFrame(main_frame, text="审查进度", padding="10")
        progress_frame.pack(fill=X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=100
        )
        self.progress_bar.pack(fill=X)
        
        self.progress_label = ttk.Label(
            progress_frame,
            text="就绪",
            font=("微软雅黑", 9)
        )
        self.progress_label.pack(pady=(5, 0))
        
        # ===== 结果摘要 =====
        summary_frame = ttk.LabelFrame(main_frame, text="审查结果摘要", padding="10")
        summary_frame.pack(fill=X, pady=(0, 10))
        
        self.summary_text = Text(
            summary_frame,
            height=5,
            font=("微软雅黑", 9),
            state=DISABLED,
            wrap=WORD
        )
        self.summary_text.pack(fill=X)
        
        # ===== 运行日志 =====
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        self.log_text = Text(
            log_frame,
            height=10,
            font=("Consolas", 9),
            state=DISABLED
        )
        self.log_text.pack(fill=BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # ===== 输出文件 =====
        output_frame = ttk.LabelFrame(main_frame, text="输出文件", padding="10")
        output_frame.pack(fill=X)
        
        self.output_label = ttk.Label(
            output_frame,
            text="尚未生成审查结果",
            font=("微软雅黑", 9)
        )
        self.output_label.pack()
        
        self.open_docx_btn = ttk.Button(
            output_frame,
            text="打开文档",
            command=self._open_docx,
            state=DISABLED
        )
        self.open_docx_btn.pack(side=LEFT, padx=5)
        
        self.open_report_btn = ttk.Button(
            output_frame,
            text="打开报告",
            command=self._open_report,
            state=DISABLED
        )
        self.open_report_btn.pack(side=LEFT, padx=5)
    
    def _toggle_api_key(self):
        """切换 API Key 输入框状态"""
        if self.enable_ai.get():
            self.api_key_entry.config(state=NORMAL)
        else:
            self.api_key_entry.config(state=DISABLED)
            self.api_key.set("")
    
    def _select_doc_file(self):
        """选择论文文件"""
        filename = filedialog.askopenfilename(
            title="选择论文文件",
            filetypes=[("Word 文档", "*.docx"), ("所有文件", "*.*")]
        )
        if filename:
            self.doc_path.set(filename)
    
    def _select_rules_file(self):
        """选择规则文件"""
        filename = filedialog.askopenfilename(
            title="选择规则文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            self.rules_path.set(filename)
    
    def _log(self, message: str):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
    
    def _update_progress(self):
        """更新进度条"""
        try:
            while True:
                current, total, message = self.progress_queue.get_nowait()
                
                if total > 0:
                    percentage = int(current / total * 100)
                    self.progress_bar['value'] = percentage
                    self.progress_label.config(
                        text=f"{message} ({current}/{total}) - {percentage}%"
                    )
                else:
                    self.progress_label.config(text=message)
                    
        except queue.Empty:
            pass
        
        # 继续监听
        self.root.after(100, self._update_progress)
    
    def _start_check(self):
        """开始审查"""
        # 验证输入
        doc_path = self.doc_path.get().strip()
        if not doc_path:
            messagebox.showerror("错误", "请选择论文文件")
            return
        
        if not os.path.exists(doc_path):
            messagebox.showerror("错误", "论文文件不存在")
            return
        
        rules_path = self.rules_path.get().strip()
        if not rules_path or not os.path.exists(rules_path):
            messagebox.showerror("错误", "规则文件不存在")
            return
        
        # 获取 API Key
        api_key = None
        if self.enable_ai.get():
            api_key = self.api_key.get().strip()
            if not api_key:
                messagebox.showerror("错误", "请输入 API Key")
                return
        
        # 禁用开始按钮
        self.start_button.config(state=DISABLED)
        
        # 清空日志
        self.log_text.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)
        
        self._log("开始审查...")
        
        # 在后台线程中运行审查
        thread = threading.Thread(
            target=self._run_check_thread,
            args=(doc_path, rules_path, api_key)
        )
        thread.daemon = True
        thread.start()
    
    def _run_check_thread(self, doc_path: str, rules_path: str, api_key: Optional[str]):
        """后台审查线程"""
        try:
            # 报告进度
            self.progress_queue.put((0, 100, "加载规则库..."))
            self._log("加载规则库...")
            
            # 导入模块（在线程中导入以避免阻塞）
            from emba_checker.main_engine import MainEngine
            
            # 进度回调
            def progress_callback(source, message, current, total):
                self.progress_queue.put((current, total, message))
                self._log(f"[{source}] {message}")
            
            # 创建引擎
            engine = MainEngine(
                doc_path,
                rules_path,
                api_key,
                progress_callback
            )
            
            # 运行审查
            self.progress_queue.put((10, 100, "开始检查..."))
            self._log("开始检查...")
            
            enable_claude = api_key is not None
            self.issues = engine.run(enable_claude=enable_claude)
            
            # 获取摘要
            summary = engine.get_summary()
            
            # 报告完成
            self.progress_queue.put((100, 100, "审查完成"))
            self._log("审查完成!")
            
            # 生成输出文件
            self._log("生成输出文件...")
            self.output_docx, self.output_report = self._generate_output(
                doc_path, self.issues
            )
            
            # 更新结果摘要
            self.root.after(0, lambda: self._update_summary(summary))
            
            # 更新输出文件显示
            self.root.after(0, lambda: self._update_output_display())
            
            self._log(f"输出文件: {os.path.basename(self.output_docx)}")
            self._log(f"报告文件: {os.path.basename(self.output_report)}")
            
        except Exception as e:
            self._log(f"错误: {str(e)}")
            messagebox.showerror("错误", f"审查失败: {str(e)}")
        
        finally:
            # 恢复开始按钮
            self.root.after(0, lambda: self.start_button.config(state=NORMAL))
    
    def _generate_output(self, doc_path: str, issues: List[Any]) -> tuple:
        """生成输出文件"""
        from emba_checker.safe_annotator import annotate_document, generate_report
        from docx import Document
        
        # 复制原文件并标注
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        basename = os.path.splitext(os.path.basename(doc_path))[0]
        
        output_docx = f"{basename}_审查结果_{timestamp}.docx"
        output_report = f"{basename}_审查报告_{timestamp}.docx"
        
        # 复制并标注文档
        shutil.copy2(doc_path, output_docx)
        doc = Document(output_docx)
        
        # 直接使用 issues 列表（来自 MainEngine.run()，已是 CheckIssue 对象）
        # 不做 isinstance 检查，因为模块导入路径不同会导致检查失败
        check_issues = issues
        
        # 标注
        from emba_checker.safe_annotator import SafeAnnotator
        annotator = SafeAnnotator(doc, check_issues, output_docx)
        annotator.annotate_all()
        doc.save(output_docx)
        
        # 生成报告
        output_report_txt = output_report.replace('.docx', '.txt')
        generate_report(doc_path, check_issues, output_report_txt)
        
        return output_docx, output_report_txt
    
    def _update_summary(self, summary: dict):
        """更新结果摘要"""
        self.summary_text.config(state=NORMAL)
        self.summary_text.delete(1.0, END)
        
        lines = []
        lines.append(f"发现问题总数: {summary['total_issues']}")
        lines.append(f"  ★★★★★ 错误: {summary['error_count']}")
        lines.append(f"  ★★★★☆ 警告: {summary['warning_count']}")
        lines.append(f"  ★★★☆☆ 信息: {summary['info_count']}")
        lines.append("")
        lines.append(f"确定性检查: {summary['docx_engine_issues']} 条")
        lines.append(f"AI 语义检查: {summary['claude_engine_issues']} 条")
        lines.append(f"去重合并: {summary['deduplicated']} 条")
        lines.append(f"总耗时: {summary['total_time']:.2f} 秒")
        
        self.summary_text.insert(1.0, "\n".join(lines))
        self.summary_text.config(state=DISABLED)
    
    def _update_output_display(self):
        """更新输出文件显示"""
        self.output_label.config(
            text=f"📄 {os.path.basename(self.output_docx)}\n"
                 f"📄 {os.path.basename(self.output_report)}"
        )
        self.open_docx_btn.config(state=NORMAL)
        self.open_report_btn.config(state=NORMAL)
    
    def _open_docx(self):
        """打开输出的 Word 文档"""
        if self.output_docx and os.path.exists(self.output_docx):
            os.startfile(self.output_docx)
    
    def _open_report(self):
        """打开输出的报告文件"""
        if self.output_report and os.path.exists(self.output_report):
            os.startfile(self.output_report)


def main():
    """主入口"""
    root = Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置 Accent 按钮样式
    style.configure(
        "Accent.TButton",
        font=("微软雅黑", 11, "bold"),
        padding=10
    )
    
    # 创建应用
    app = EMBAcheckerGUI(root)
    
    # 运行
    root.mainloop()


if __name__ == "__main__":
    main()
