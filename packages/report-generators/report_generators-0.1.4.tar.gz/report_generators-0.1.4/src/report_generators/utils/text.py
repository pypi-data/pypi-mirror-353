"""Text formatting utilities for report generators."""
from textwrap import wrap
from typing import Optional


def format_column_text(
        text: Optional[str], max_col_text_length: int = 40,
        max_col_text_lines: int = 7
) -> str:
    """
    Format text for column display in reports with line breaks and truncation.

    Args:
        text: The text to format
        max_col_text_length: Maximum characters per line
        max_col_text_lines: Maximum number of lines

    Returns:
        Formatted text with line breaks
    """
    if text is None:
        # TODO refact for idioms
        return "Não informado"

    max_chars = max_col_text_length * max_col_text_lines
    if len(text) > max_chars:
        text = text[:max_chars - 3] + "..."

    lines = wrap(
        text, width=max_col_text_length, max_lines=max_col_text_lines,
        break_long_words=False
    )

    return "\n".join(lines)
