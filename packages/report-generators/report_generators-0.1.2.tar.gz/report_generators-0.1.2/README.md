# Report Generators

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/your-username/report-generators)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

This Python package provides a flexible and extensible framework for generating reports in multiple formats, including XLSX (Excel), CSV, and PDF.

## Features

- Generate tabular reports in XLSX, CSV, and PDF formats
- Easily extendable for new report types and formats
- Utilities for formatting text and converting workbooks to CSV
- Base classes to help you implement custom report generators

## Installation

```bash
pip install report-generators
```

Or install from source:

```bash
pip install -e .
```

## Usage Example

```python
from report_generators import (
    BaseCSVReportsGenerator,
    BaseXLSXReportsGenerator,
    BasePDFReportsGenerator,
    BaseGenerator
)

# Implement your own BaseGenerator subclass for your data
class YourCustomGenerator(BaseGenerator):
    def get_columns(self):
        return [
            ("Name", 20),
            ("Age", 10),
            ("Email", 30)
        ]

    def generate_row_fn(self, item):
        return [item["name"], item["age"], item["email"]]

# Create your data
items = [
    {"name": "John Doe", "age": 30, "email": "john@example.com"},
    {"name": "Jane Smith", "age": 25, "email": "jane@example.com"}
]

# Initialize your generator
base_generator = YourCustomGenerator()

# Generate an XLSX report
xlsx_gen = BaseXLSXReportsGenerator("Report Title", base_generator)
xlsx_workbook = xlsx_gen.generate(items)

# Generate a CSV report
csv_gen = BaseCSVReportsGenerator("Report Title", base_generator)
csv_buffer = csv_gen.generate(items)

# Generate a PDF report
pdf_gen = BasePDFReportsGenerator("Report Title", base_generator)
pdf_buffer = pdf_gen.generate(items)
```

## Project Structure

```
report_generators/
├── base_generator.py  # Base class for custom report logic
├── xlsx/             # XLSX (Excel) report generator
├── csv/              # CSV report generator (inherits from XLSX)
├── pdf/              # PDF report generator
└── utils/            # Shared utilities
    ├── text.py          # Text formatting
    ├── types.py         # Type definitions
    └── workbook_to_csv.py
```

## Dependencies

- openpyxl>=3.1.5
- reportlab>=4.4.1
- Python 3.7+

## License

MIT License

---

Feel free to extend or customize the generators for your own reporting needs!
