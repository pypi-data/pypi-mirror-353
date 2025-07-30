"""Tests for the CSV report generator."""
import csv
from io import StringIO
from src.report_generators.csv.generator import BaseCSVReportsGenerator


def test_csv_generator_init(base_generator):
    """Test CSV generator initialization."""
    generator = BaseCSVReportsGenerator("Test Report", base_generator)
    assert generator.worksheet.title == "Test Report"


def test_csv_generator_generate(base_generator, mock_data):
    """Test generating a complete CSV report."""
    generator = BaseCSVReportsGenerator("Test Report", base_generator)
    csv_buffer = generator.generate(mock_data)

    # Check that it's a StringIO buffer
    assert isinstance(csv_buffer, StringIO)

    # Read CSV content
    csv_buffer.seek(0)
    reader = csv.reader(csv_buffer)
    rows = list(reader)

    # Check headers
    assert rows[0] == ["Name", "Age", "Email"]

    # Check data
    assert rows[1] == ["John Doe", "30", "john@example.com"]
    assert rows[2] == ["Jane Smith", "25", "jane@example.com"]


def test_csv_generator_with_header_columns(base_generator, mock_data):
    """Test generating CSV report with additional header columns."""
    generator = BaseCSVReportsGenerator("Test Report", base_generator)
    header_columns = [("Header 1", 15), ("Header 2", 15)]

    csv_buffer = generator.generate(mock_data, header_columns=header_columns)

    # Read CSV content
    csv_buffer.seek(0)
    reader = csv.reader(csv_buffer)
    rows = list(reader)

    # Check headers (ignore empty cells)
    header_row = [cell for cell in rows[0] if cell]
    assert header_row == ["Header 1", "Header 2"]
    # Skip blank row (row 1)
    assert rows[2] == ["Name", "Age", "Email"]
    # Check data
    assert rows[3] == ["John Doe", "30", "john@example.com"]
    assert rows[4] == ["Jane Smith", "25", "jane@example.com"]
