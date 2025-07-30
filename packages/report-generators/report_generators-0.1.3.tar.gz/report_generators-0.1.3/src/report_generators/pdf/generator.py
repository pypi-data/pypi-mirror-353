from typing import Any, List, Optional
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Table, SimpleDocTemplate, TableStyle, Paragraph, Image
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from svglib.svglib import svg2rlg

from ..base_generator import BaseGenerator
from ..utils import format_column_text, COLUMNS_TYPE
import os

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

pdfmetrics.registerFont(
    TTFont('Inter-Regular', os.path.join(current_dir, 'Inter-Regular.ttf'))
)
pdfmetrics.registerFont(
    TTFont('Inter-Bold', os.path.join(current_dir, 'Inter-Bold.ttf'))
)

class BasePDFReportsGenerator:
    """Base class for generating PDF reports."""

    def __init__(self, title: str, base_generator: BaseGenerator):
        self.title = title
        self.custom_page_width = 2500
        self.custom_page_height = 1700
        self.max_col_text_length = 40
        self.max_col_text_lines = 7
        self.base_generator = base_generator

    def _save_pdf_file(self, pdf_data: BytesIO, filepath: str) -> None:
        # Use later for saving files
        with open(filepath, "wb") as f:
            f.write(pdf_data.getvalue())

    def _get_table_style(self):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Inter-Regular'),
            ('FONTNAME', (0, 0), (-1, 0), 'Inter-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 20),
            ('LEADING', (0, 0), (-1, -1), 24),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])

    def _get_title_style(self):
        return ParagraphStyle(
            name='TitleStyle',
            fontSize=36,
            alignment=1,
            fontName='Inter-Bold',
            spaceAfter=50
        )

    def _get_subtitle_style(self):
        return ParagraphStyle(
            name='SubTitleStyle',
            fontSize=24,
            alignment=1,
            fontName='Inter-Regular',
            spaceAfter=50
        )

    def _get_header_cell_style(self):
        return ParagraphStyle(
            name='HeaderCellStyle',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            alignment=1,
            textColor=colors.whitesmoke
        )

    def _get_data_cell_style(self):
        return ParagraphStyle(
            name='DataCellStyle',
            parent=getSampleStyleSheet()['Normal'],
            fontSize=9,
            alignment=1,
            leading=12
        )

    def _format_col_text(self, text: Optional[str]) -> str:
        return format_column_text(
            text,
            max_col_text_length=self.max_col_text_length,
            max_col_text_lines=self.max_col_text_lines
        )
    
    def _process_image(self, image_path: str):
        logo_format = image_path.split('.')[-1]
        if logo_format != 'svg':
            return  Image(image_path, width=4 * inch, height=1 * inch)
        
        drawing = None
        try:
            drawing = svg2rlg(image_path)
            if drawing is not None:
                drawing.hAlign = 'CENTER'

                scale = 0.3
                drawing.scale(scale, scale)
                drawing.width *= scale
                drawing.height *= scale
        except Exception as e:
            print(f"Error converting SVG: {e}")

        return drawing

    def _generate_pdf(
        self, items_data: List[list], logo_path: Optional[str] = None,
        header_columns: Optional[COLUMNS_TYPE] = None, 
    ) -> BytesIO:
        buffer = BytesIO()
        custom_page_size = (self.custom_page_width, self.custom_page_height)
        story = []

        title_style = self._get_title_style()
        header_cell_style = self._get_header_cell_style()
        data_cell_style = self._get_data_cell_style()

        if logo_path is not None:
            space_after_image = Paragraph(
                "<br/>", ParagraphStyle(name='SpaceAfterImage', spaceAfter=30)
            )
            logo_image = self._process_image(image_path=logo_path)

            if logo_image is not None:
                story.extend([logo_image, space_after_image])

        title_paragraph = Paragraph(self.title, title_style)
        story.append(title_paragraph)

        if header_columns is not None:
            subtitle = self._convert_header_columns(header_columns)
            story.append(Paragraph(subtitle, self._get_subtitle_style()))

        column_definitions = self.base_generator.get_columns()
        header_cells = [
            Paragraph(str(col_name), header_cell_style) for col_name,
            _ in column_definitions
        ]

        processed_data_rows = []
        for data_row_values in items_data:
            row_cells = []
            for cell_value in data_row_values:
                text_for_cell = self._format_col_text(
                    str(cell_value) if cell_value is not None else None
                )
                row_cells.append(Paragraph(text_for_cell, data_cell_style))
            processed_data_rows.append(row_cells)

        all_table_content = [header_cells] + processed_data_rows

        table = Table(all_table_content)
        table.setStyle(self._get_table_style())

        pdf_doc = SimpleDocTemplate(buffer, pagesize=custom_page_size)
        story.append(table)
        pdf_doc.build(story)

        buffer.seek(0)
        return buffer
    
    def _convert_header_columns(
        self, header_columns: List[COLUMNS_TYPE]
    ) -> str:
        header_indicators = [value for value, _ in header_columns]
        return " - ".join(header_indicators)

    def generate(
        self, items: List[Any], header_columns: Optional[COLUMNS_TYPE] = None,
        logo_path: Optional[str] = None, save_file_path: Optional[str] = None
    ) -> BytesIO:
        items_data_rows = []
        for item in items:
            row = self.base_generator.generate_row_fn(item=item)
            items_data_rows.append(row)
        pdf_buffer = self._generate_pdf(
            items_data=items_data_rows, header_columns=header_columns,
            logo_path=logo_path
        )

        if save_file_path is not None:
            self._save_pdf_file(
                pdf_data=pdf_buffer, filepath=save_file_path
            )

        return pdf_buffer
