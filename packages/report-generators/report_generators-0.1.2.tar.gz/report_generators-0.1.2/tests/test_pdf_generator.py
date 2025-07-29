"""Tests for the PDF report generator."""
import pytest
from io import BytesIO
from src.report_generators.pdf.generator import BasePDFReportsGenerator


def test_pdf_generator_init(base_generator):
    """Test PDF generator initialization."""
    generator = BasePDFReportsGenerator("Test Report", base_generator)
    assert generator.title == "Test Report"
    assert generator.custom_page_width == 2500
    assert generator.custom_page_height == 1700


def test_pdf_generator_table_style(base_generator):
    """Test PDF table style generation."""
    generator = BasePDFReportsGenerator("Test Report", base_generator)
    style = generator._get_table_style()
    commands = style._cmds

    # Check that basic style commands are present
    style_commands = [cmd[0] for cmd in commands]
    assert 'BACKGROUND' in style_commands
    assert 'GRID' in style_commands
    assert 'VALIGN' in style_commands


def test_pdf_generator_format_text(base_generator):
    """Test text formatting in PDF generator."""
    generator = BasePDFReportsGenerator("Test Report", base_generator)

    # Test None value
    assert generator._format_col_text(None) == "Não informado"

    # Test normal text
    text = "Normal text"
    assert generator._format_col_text(text) == text

    # Test long text
    long_text = "This is a very long text that should be wrapped properly across multiple lines"
    formatted = generator._format_col_text(long_text)

    # Check each line length
    lines = formatted.split('\n')
    assert all(len(line) <= generator.max_col_text_length for line in lines)

    # Ensure content is preserved
    assert formatted.replace('\n', ' ').startswith("This is a very long text")


def test_pdf_generator_generate(base_generator, mock_data):
    """Test generating a complete PDF report."""
    generator = BasePDFReportsGenerator("Test Report", base_generator)
    pdf_buffer = generator.generate(mock_data)

    # Check that it's a BytesIO buffer
    assert isinstance(pdf_buffer, BytesIO)

    # Check that buffer contains PDF data
    pdf_data = pdf_buffer.getvalue()
    assert pdf_data.startswith(b'%PDF')  # PDF magic number
    assert len(pdf_data) > 0


def test_pdf_generator_styles(base_generator):
    """Test PDF style generation."""
    generator = BasePDFReportsGenerator("Test Report", base_generator)

    # Test title style
    title_style = generator._get_title_style()
    assert title_style.fontSize == 36
    assert title_style.alignment == 1

    # Test header cell style
    header_style = generator._get_header_cell_style()
    assert header_style.fontSize == 10
    assert header_style.fontName == 'Helvetica-Bold'

    # Test data cell style
    data_style = generator._get_data_cell_style()
    assert data_style.fontSize == 9
    assert data_style.alignment == 1
