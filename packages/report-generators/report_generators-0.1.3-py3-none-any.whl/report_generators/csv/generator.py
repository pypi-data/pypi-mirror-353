from io import StringIO
from typing import List, Any, Optional

from ..base_generator import BaseGenerator
from ..utils import COLUMNS_TYPE, workbook_to_csv_buffer
from ..xlsx.generator import BaseXLSXReportsGenerator


class BaseCSVReportsGenerator(BaseXLSXReportsGenerator):
    """Base class for generating CSV reports."""

    def __init__(self, title: str, base_generator: BaseGenerator):
        super().__init__(title, base_generator)

    def _save_csv_file(self, csv_data: StringIO, filepath: str) -> None:
        with open(filepath, "w") as f:
            f.write(csv_data.getvalue())

    def generate(
        self, items: List[Any], header_columns: Optional[COLUMNS_TYPE] = None,
        save_file_path: Optional[str] = None
    ) -> StringIO:
        """
        Generate a CSV report from the items.

        Args:
            items: List of items to include in the report
            header_columns: Optional header columns to add at the top

        Returns:
            StringIO buffer containing the CSV data
        """
        workbook = super().generate(items, header_columns)
        csv_buffer = workbook_to_csv_buffer(workbook)

        if save_file_path is not None:
            self._save_csv_file(csv_data=csv_buffer, filepath=save_file_path)

        return csv_buffer
