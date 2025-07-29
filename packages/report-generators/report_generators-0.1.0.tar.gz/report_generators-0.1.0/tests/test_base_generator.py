"""Tests for the BaseGenerator class."""
import pytest
from src.report_generators.base_generator import BaseGenerator


def test_base_generator_is_abstract():
    """Test that BaseGenerator cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseGenerator()


def test_mock_generator_get_columns(base_generator):
    """Test that get_columns returns the expected column definitions."""
    columns = base_generator.get_columns()
    assert len(columns) == 3
    assert columns[0] == ("Name", 20)
    assert columns[1] == ("Age", 10)
    assert columns[2] == ("Email", 30)


def test_mock_generator_generate_row(base_generator, mock_data):
    """Test that generate_row_fn returns the expected row data."""
    row = base_generator.generate_row_fn(mock_data[0])
    assert row == ["John Doe", 30, "john@example.com"]
