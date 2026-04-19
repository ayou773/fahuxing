"""
PDF生成器服务
使用ReportLab生成法律文书PDF
"""

import os
import tempfile
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors


class PDFGenerator:
    """PDF生成器服务类"""

    def __init__(self):
        self.output_dir = os.getenv('PDF_OUTPUT_DIR', './pdf_outputs')
        self.template_dir = os.getenv('PDF_TEMPLATE_DIR', './templates')

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)

    def generate_lawsuit_pdf(self, lawsuit_content: str, case_info: Dict[str, Any],
                          output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        生成诉状PDF

        Args:
            lawsuit_content: 诉状内容（Markdown或HTML格式）
            case_info: 案件信息
            output_filename: 输出文件名（可选）

        Returns:
            包含文件路径和状态的字典
        """
        try:
            # 生成默认文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"lawsuit_{timestamp}.pdf"

            output_path = os.path.join(self.output_dir, output_filename)

            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # 获取样式
            styles = getSampleStyleSheet()

            # 自定义标题样式
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=30
            )

            # 自定义正文样式
            content_style = ParagraphStyle(
                'Content',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                spaceAfter=10
            )

            # 自定义强调样式
            emphasis_style = ParagraphStyle(
                'Emphasis',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                spaceAfter=10,
                textColor=colors.darkred
            )

            # 构建PDF内容
            story = []

            # 添加标题
            title = case_info.get('title', '民事起诉状')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))

            # 添加原告信息
            plaintiff_info = case_info.get('plaintiff', '')
            if plaintiff_info:
                story.append(Paragraph(f"原告：{plaintiff_info}", content_style))
                story.append(Spacer(1, 8))

            # 添加被告信息
            defendant_info = case_info.get('defendant', '')
            if defendant_info:
                story.append(Paragraph(f"被告：{defendant_info}", content_style))
                story.append(Spacer(1, 8))

            # 添加案由
            case_cause = case_info.get('case_cause', '')
            if case_cause:
                story.append(Paragraph(f"案由：{case_cause}", content_style))
                story.append(Spacer(1, 12))

            # 添加诉讼请求
            story.append(Paragraph("诉讼请求：", title_style))
            requests = case_info.get('requests', [])
            for request in requests:
                story.append(Paragraph(f"• {request}", emphasis_style))
            story.append(Spacer(1, 12))

            # 添加事实与理由
            story.append(Paragraph("事实与理由：", title_style))

            # 处理诉状内容
            content_paragraphs = self._parse_content(lawsuit_content)
            for paragraph in content_paragraphs:
                story.append(Paragraph(paragraph, content_style))
                story.append(Spacer(1, 6))

            # 添加证据清单
            evidence = case_info.get('evidence', [])
            if evidence:
                story.append(Paragraph("证据清单：", title_style))
                for item in evidence:
                    story.append(Paragraph(f"• {item}", content_style))
                story.append(Spacer(1, 12))

            # 添加此致
            story.append(Paragraph("此致", content_style))
            story.append(Paragraph("XX人民法院", content_style))
            story.append(Spacer(1, 20))

            # 添加落款
            story.append(Paragraph("起诉人：", content_style))
            story.append(Paragraph(case_info.get('plaintiff', ''), content_style))
            story.append(Spacer(1, 10))

            current_date = datetime.now().strftime("%Y年%m月%d日")
            story.append(Paragraph(current_date, content_style))

            # 构建表格（如果需要）
            if case_info.get('table_data'):
                table_data = case_info.get('table_data')
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)

            # 生成PDF
            doc.build(story)

            return {
                'success': True,
                'file_path': output_path,
                'file_name': output_filename,
                'message': 'PDF生成成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'PDF生成失败'
            }

    def _parse_content(self, content: str) -> list:
        """
        解析内容为段落列表

        Args:
            content: 原始内容

        Returns:
            段落列表
        """
        # 简单的段落分割逻辑
        paragraphs = []
        lines = content.split('\n')

        current_paragraph = ""
        for line in lines:
            line = line.strip()
            if line:
                if current_paragraph:
                    current_paragraph += " " + line
                else:
                    current_paragraph = line
            else:
                if current_paragraph:
                    paragraphs.append(current_paragraph)
                    current_paragraph = ""

        if current_paragraph:
            paragraphs.append(current_paragraph)

        return paragraphs

    def generate_calculation_report(self, calculation_results: Dict[str, Any],
                                output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        生成计算报告PDF

        Args:
            calculation_results: 计算结果
            output_filename: 输出文件名（可选）

        Returns:
            包含文件路径和状态的字典
        """
        try:
            # 生成默认文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"calculation_report_{timestamp}.pdf"

            output_path = os.path.join(self.output_dir, output_filename)

            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # 获取样式
            styles = getSampleStyleSheet()

            # 自定义标题样式
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=30
            )

            # 自定义副标题样式
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.darkgreen,
                spaceAfter=20
            )

            # 自定义内容样式
            content_style = ParagraphStyle(
                'Content',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                spaceAfter=10
            )

            # 构建PDF内容
            story = []

            # 添加标题
            story.append(Paragraph("劳资计算报告", title_style))
            story.append(Spacer(1, 12))

            # 添加计算结果
            for calc_type, result in calculation_results.items():
                if result.get('success', False):
                    story.append(Paragraph(calc_type, subtitle_style))

                    for key, value in result.items():
                        if key not in ['success']:
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    story.append(Paragraph(f"{sub_key}: {sub_value}", content_style))
                            else:
                                story.append(Paragraph(f"{key}: {value}", content_style))

                    story.append(Spacer(1, 10))

            # 生成PDF
            doc.build(story)

            return {
                'success': True,
                'file_path': output_path,
                'file_name': output_filename,
                'message': '计算报告生成成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '计算报告生成失败'
            }

    def generate_template_pdf(self, template_name: str, data: Dict[str, Any],
                           output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        从模板生成PDF

        Args:
            template_name: 模板名称
            data: 填充数据
            output_filename: 输出文件名（可选）

        Returns:
            包含文件路径和状态的字典
        """
        try:
            # 生成默认文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{template_name}_{timestamp}.pdf"

            output_path = os.path.join(self.output_dir, output_filename)

            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # 获取样式
            styles = getSampleStyleSheet()

            # 自定义标题样式
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.darkblue,
                spaceAfter=30
            )

            # 自定义内容样式
            content_style = ParagraphStyle(
                'Content',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                spaceAfter=10
            )

            # 构建PDF内容
            story = []

            # 添加标题
            story.append(Paragraph(template_name, title_style))
            story.append(Spacer(1, 12))

            # 添加数据
            for key, value in data.items():
                if isinstance(value, dict):
                    story.append(Paragraph(key, content_style))
                    for sub_key, sub_value in value.items():
                        story.append(Paragraph(f"  {sub_key}: {sub_value}", content_style))
                else:
                    story.append(Paragraph(f"{key}: {value}", content_style))
                story.append(Spacer(1, 6))

            # 生成PDF
            doc.build(story)

            return {
                'success': True,
                'file_path': output_path,
                'file_name': output_filename,
                'message': '模板PDF生成成功'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': '模板PDF生成失败'
            }


# 服务实例
pdf_generator = PDFGenerator()