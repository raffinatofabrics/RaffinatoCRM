# customers/services/pdf_generator.py

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os

# 注册中文字体（首选微软雅黑，备选黑体）
CHINESE_FONT = 'Helvetica'
try:
    # 首选：微软雅黑
    font_path = "C:/Windows/Fonts/msyh.ttc"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('MicrosoftYaHei', font_path))
        print("中文字体 MicrosoftYaHei 注册成功")
        CHINESE_FONT = 'MicrosoftYaHei'
    else:
        # 备选：黑体
        font_path = "C:/Windows/Fonts/simhei.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('SimHei', font_path))
            print("中文字体 SimHei 注册成功")
            CHINESE_FONT = 'SimHei'
        else:
            print("未找到中文字体，使用默认字体")
except Exception as e:
    print(f"字体注册失败: {e}")


class PDFGenerator:
    """外贸单据 PDF 生成器"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def _get_style(self, name, fontSize=10, fontName=None):
        """获取样式（支持中文）"""
        if fontName is None:
            fontName = CHINESE_FONT
        try:
            return ParagraphStyle(name, parent=self.styles['Normal'], fontSize=fontSize, fontName=fontName)
        except:
            return self.styles['Normal']
    
    def _get_bold_style(self, name, fontSize=10, fontName=None):
        """获取粗体样式"""
        if fontName is None:
            fontName = CHINESE_FONT
        try:
            return ParagraphStyle(name, parent=self.styles['Normal'], fontSize=fontSize, fontName=fontName, fontWeight='bold')
        except:
            return self.styles['Normal']
    
    def _get_items(self, order):
        """获取订单明细（兼容 list 格式）"""
        if hasattr(order, 'items') and isinstance(order.items, list):
            return order.items
        return []
    
    def _add_logo_and_title(self, elements, title_text):
        """添加 Logo 和标题（Logo靠左，标题居中）"""
        # Logo 路径
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'invoicelogo.png')
        
        # 创建标题样式（居中，使用中文字体）
        title_style = ParagraphStyle(
            'Title', 
            parent=self.styles['Heading1'], 
            fontSize=16, 
            alignment=1,
            fontName=CHINESE_FONT
        )
        
        # 1. 添加 Logo（左对齐）
        try:
            if os.path.exists(logo_path):
                # 保持 3:1 比例（原图 750x250 = 3:1）
                logo_width = 40 * mm
                logo_height = logo_width / 3
                logo_img = Image(logo_path, width=logo_width, height=logo_height)
                logo_img.hAlign = 'LEFT'
                elements.append(logo_img)
                elements.append(Spacer(1, 5))
        except Exception as e:
            print(f"Logo 加载失败: {e}")
        
        # 2. 添加标题（居中）
        title = Paragraph(title_text, title_style)
        title.hAlign = 'CENTER'
        elements.append(title)
        elements.append(Spacer(1, 10))
    
    def generate_quotation(self, order, customer, company_info):
        """生成报价单 PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        
        # 添加 Logo 和标题
        self._add_logo_and_title(elements, "报价单 / QUOTATION")
        
        # 公司信息
        info_style = self._get_style('Info', 9)
        elements.append(Paragraph(f"{company_info.get('name', '')}", info_style))
        elements.append(Paragraph(f"地址: {company_info.get('address', '')}", info_style))
        elements.append(Paragraph(f"电话: {company_info.get('phone', '')}", info_style))
        elements.append(Spacer(1, 10))
        
        # 客户信息
        customer_style = self._get_style('Customer', 10)
        elements.append(Paragraph(f"致: {customer.company_name}", customer_style))
        if customer.contact_person:
            elements.append(Paragraph(f"联系人: {customer.contact_person}", customer_style))
        elements.append(Spacer(1, 10))
        
        # 单据信息
        info_style = self._get_style('Info', 10)
        elements.append(Paragraph(f"报价单号: Q-{order.order_no}", info_style))
        elements.append(Paragraph(f"日期: {datetime.now().strftime('%Y-%m-%d')}", info_style))
        elements.append(Spacer(1, 10))
        
        # 产品表格
        data = [['序号', '产品名称', '规格', '数量', '单位', '单价', '总价']]
        
        items = self._get_items(order)
        if items:
            for i, item in enumerate(items, 1):
                data.append([
                    str(i),
                    item.get('product_name', '-'),
                    item.get('specification', '-'),
                    str(item.get('quantity', '-')),
                    item.get('unit', '-'),
                    f"{item.get('unit_price', 0):.2f}",
                    f"{item.get('amount', 0):.2f}",
                ])
        else:
            data.append(['1', '-', '-', '1', '件', '-', '-'])
        
        # 添加合计行
        total_amount = float(order.total_cost) if order.total_cost else 0
        data.append(['', '', '', '', '', '合计:', f"{total_amount:.2f}"])
        
        table = Table(data, colWidths=[25, 100, 70, 45, 40, 65, 65])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 1), (0, -2), 'CENTER'),
            ('ALIGN', (1, 1), (4, -2), 'LEFT'),
            ('ALIGN', (5, 1), (6, -2), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('TOPPADDING', (0, 1), (-1, -2), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F7F7F7')]),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F0FE')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, -1), (4, -1), 'RIGHT'),
            ('ALIGN', (5, -1), (6, -1), 'RIGHT'),
            ('TOPPADDING', (0, -1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#4472C4')),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # 备注
        if order.notes:
            notes_style = self._get_style('Notes', 9)
            elements.append(Paragraph(f"备注: {order.notes}", notes_style))
        
        # 签名
        elements.append(Spacer(1, 30))
        sign_style = self._get_style('Sign', 10)
        elements.append(Paragraph("授权签字: ___________________", sign_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_invoice(self, order, customer, company_info, invoice_type='commercial'):
        """生成发票 (商业发票/形式发票)"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        
        # 标题映射
        title_map = {
            'commercial': '商业发票 / COMMERCIAL INVOICE',
            'proforma': '形式发票 / PROFORMA INVOICE'
        }
        title_text = title_map.get(invoice_type, '发票 / INVOICE')
        
        # 添加 Logo 和标题
        self._add_logo_and_title(elements, title_text)
        
        # 公司信息
        info_style = self._get_style('Info', 9)
        elements.append(Paragraph(f"{company_info.get('name', '')}", info_style))
        elements.append(Paragraph(f"地址: {company_info.get('address', '')}", info_style))
        elements.append(Paragraph(f"电话: {company_info.get('phone', '')}", info_style))
        elements.append(Spacer(1, 10))
        
        # 买卖双方信息
        party_style = self._get_style('Party', 10)
        elements.append(Paragraph(f"卖方: {company_info.get('name', '')}", party_style))
        elements.append(Paragraph(f"买方: {customer.company_name}", party_style))
        if customer.country:
            elements.append(Paragraph(f"目的地: {customer.country}", party_style))
        elements.append(Spacer(1, 10))
        
        # 单据信息
        info_style = self._get_style('Info', 10)
        elements.append(Paragraph(f"发票号: INV-{order.order_no}", info_style))
        elements.append(Paragraph(f"日期: {datetime.now().strftime('%Y-%m-%d')}", info_style))
        elements.append(Spacer(1, 10))
        
        # 产品表格
        data = [['序号', '产品名称', '规格', '数量', '单位', '单价', '总价']]
        
        items = self._get_items(order)
        if items:
            for i, item in enumerate(items, 1):
                data.append([
                    str(i),
                    item.get('product_name', '-'),
                    item.get('specification', '-'),
                    str(item.get('quantity', '-')),
                    item.get('unit', '-'),
                    f"{item.get('unit_price', 0):.2f}",
                    f"{item.get('amount', 0):.2f}",
                ])
        else:
            data.append(['1', '-', '-', '1', '件', '-', '-'])
        
        total_amount = float(order.total_cost) if order.total_cost else 0
        data.append(['', '', '', '', '', '合计:', f"{total_amount:.2f}"])
        
        table = Table(data, colWidths=[25, 100, 70, 45, 40, 65, 65])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 1), (0, -2), 'CENTER'),
            ('ALIGN', (1, 1), (4, -2), 'LEFT'),
            ('ALIGN', (5, 1), (6, -2), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('TOPPADDING', (0, 1), (-1, -2), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F7F7F7')]),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F0FE')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, -1), (4, -1), 'RIGHT'),
            ('ALIGN', (5, -1), (6, -1), 'RIGHT'),
            ('TOPPADDING', (0, -1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#4472C4')),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # 备注
        if order.notes:
            notes_style = self._get_style('Notes', 9)
            elements.append(Paragraph(f"备注: {order.notes}", notes_style))
        
        # 签名
        elements.append(Spacer(1, 30))
        sign_style = self._get_style('Sign', 10)
        elements.append(Paragraph("授权签字: ___________________", sign_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_packing_list(self, order, customer, company_info):
        """生成装箱单 PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        
        # 添加 Logo 和标题
        self._add_logo_and_title(elements, "装箱单 / PACKING LIST")
        
        # 公司信息
        info_style = self._get_style('Info', 9)
        elements.append(Paragraph(f"{company_info.get('name', '')}", info_style))
        elements.append(Spacer(1, 10))
        
        # 客户信息
        customer_style = self._get_style('Customer', 10)
        elements.append(Paragraph(f"客户: {customer.company_name}", customer_style))
        elements.append(Spacer(1, 10))
        
        # 单据信息
        info_style = self._get_style('Info', 10)
        elements.append(Paragraph(f"装箱单号: PL-{order.order_no}", info_style))
        elements.append(Paragraph(f"日期: {datetime.now().strftime('%Y-%m-%d')}", info_style))
        elements.append(Spacer(1, 10))
        
        # 装箱表格
        data = [['序号', '产品名称', '规格', '数量', '单位', '箱数']]
        
        items = self._get_items(order)
        if items:
            for i, item in enumerate(items, 1):
                data.append([
                    str(i),
                    item.get('product_name', '-'),
                    item.get('specification', '-'),
                    str(item.get('quantity', '-')),
                    item.get('unit', '-'),
                    '1',
                ])
        else:
            data.append(['1', '-', '-', '1', '件', '1'])
        
        table = Table(data, colWidths=[25, 110, 80, 50, 50, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (4, -1), 'LEFT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F7F7')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # 总件数
        total_style = self._get_bold_style('Total', 10)
        elements.append(Paragraph(f"总件数: {len(items) if items else 1} 件", total_style))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer