from typing import Any, List, Optional
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Table, SimpleDocTemplate, TableStyle, Paragraph

from ..base_generator import BaseGenerator
from ..utils import format_column_text


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
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])

    def _get_title_style(self):
        return ParagraphStyle(
            name='TitleStyle',
            fontSize=36,
            alignment=1,
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

    def _generate_pdf(self, items_data: List[list]):
        buffer = BytesIO()
        custom_page_size = (self.custom_page_width, self.custom_page_height)

        title_style = self._get_title_style()
        header_cell_style = self._get_header_cell_style()
        data_cell_style = self._get_data_cell_style()

        title_paragraph = Paragraph(self.title, title_style)

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
        story = [title_paragraph, table]
        pdf_doc.build(story)

        buffer.seek(0)
        return buffer

    def generate(self, items: List[Any]) -> BytesIO:
        items_data_rows = []
        for item in items:
            row = self.base_generator.generate_row_fn(item=item)
            items_data_rows.append(row)
        pdf_buffer = self._generate_pdf(items_data_rows)

        return pdf_buffer
