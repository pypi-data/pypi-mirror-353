"""Tests for the XLSX report generator."""
import pytest
from openpyxl.workbook import Workbook
from src.report_generators.xlsx.generator import BaseXLSXReportsGenerator


def test_xlsx_generator_init(base_generator):
    """Test XLSX generator initialization."""
    generator = BaseXLSXReportsGenerator("Test Report", base_generator)
    assert isinstance(generator.workbook, Workbook)
    assert generator.worksheet.title == "Test Report"


def test_xlsx_generator_assign_cell_titles(base_generator):
    """Test assigning column titles to worksheet."""
    generator = BaseXLSXReportsGenerator("Test Report", base_generator)
    columns = base_generator.get_columns()
    generator.assign_cell_titles(columns)

    for col_num, (title, _) in enumerate(columns, 1):
        cell = generator.worksheet.cell(row=1, column=col_num)
        assert cell.value == title


def test_xlsx_generator_assign_cell_data(base_generator):
    """Test assigning row data to worksheet."""
    generator = BaseXLSXReportsGenerator("Test Report", base_generator)
    row_data = ["John Doe", 30, "john@example.com"]
    generator.assign_cell_data(row_data, row_num=2)

    for col_num, value in enumerate(row_data, 1):
        cell = generator.worksheet.cell(row=2, column=col_num)
        assert cell.value == value


def test_xlsx_generator_generate(base_generator, mock_data):
    """Test generating a complete XLSX report."""
    generator = BaseXLSXReportsGenerator("Test Report", base_generator)
    workbook = generator.generate(mock_data)

    # Check that it's a workbook
    assert isinstance(workbook, Workbook)

    worksheet = workbook.active
    # Check headers
    headers = [cell.value for cell in worksheet[1]]
    expected_headers = ["Name", "Age", "Email"]
    assert headers[0:3] == expected_headers

    # Check data
    data_row = [cell.value for cell in worksheet[2]]
    assert data_row[0:3] == ["John Doe", 30, "john@example.com"]


def test_xlsx_generator_with_header_columns(base_generator, mock_data):
    """Test generating XLSX report with additional header columns."""
    generator = BaseXLSXReportsGenerator("Test Report", base_generator)
    header_columns = [("Header 1", 15), ("Header 2", 15)]

    workbook = generator.generate(mock_data, header_columns=header_columns)
    worksheet = workbook.active

    # Check header row
    header_row = [cell.value for cell in worksheet[1]]
    assert header_row[0:2] == ["Header 1", "Header 2"]        # Check column headers (row 3)
    column_headers = [cell.value for cell in worksheet[3]]
    assert column_headers[0:3] == ["Name", "Age", "Email"]
    
    # Check data (row 4)
    data_row = [cell.value for cell in worksheet[4]]
    assert data_row[0:3] == ["John Doe", 30, "john@example.com"]
