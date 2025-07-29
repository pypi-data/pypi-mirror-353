"""Tests for text formatting utilities."""
from src.report_generators.utils.text import format_column_text


def test_format_column_text_none():
    """Test formatting None value."""
    result = format_column_text(None)
    assert result == "Não informado"


def test_format_column_text_short():
    """Test formatting short text that doesn't need wrapping."""
    text = "Short text"
    result = format_column_text(
        text,
        max_col_text_length=20,
        max_col_text_lines=2)
    assert result == text


def test_format_column_text_long():
    """Test formatting long text that needs wrapping."""
    text = "This is a very long text that should be wrapped across multiple lines"
    result = format_column_text(
        text,
        max_col_text_length=20,
        max_col_text_lines=3)
    lines = result.split('\n')
    assert len(lines) <= 3
    assert all(len(line) <= 20 for line in lines)


def test_format_column_text_truncation():
    """Test that very long text gets truncated."""
    text = "x" * 1000
    result = format_column_text(
        text,
        max_col_text_length=10,
        max_col_text_lines=2)
    assert len(result) <= (10 * 2) + 3  # account for newlines and ellipsis
    assert result.endswith("...")
