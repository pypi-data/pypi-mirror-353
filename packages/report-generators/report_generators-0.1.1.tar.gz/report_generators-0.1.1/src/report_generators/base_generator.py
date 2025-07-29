from typing import List

from abc import ABC, abstractmethod
from typing import Tuple, List, Any

COLUMNS_TYPE = List[Tuple[str, int]]


class BaseGenerator(ABC):
    @abstractmethod
    def get_columns(self) -> List[COLUMNS_TYPE]:
        """Get the column definitions for the report."""
        pass

    @abstractmethod
    def generate_row_fn(self, item: Any) -> list:
        """Generate a row of data from an item."""
        pass
