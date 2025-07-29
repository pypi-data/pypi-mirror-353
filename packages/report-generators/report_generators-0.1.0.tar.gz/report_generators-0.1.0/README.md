# Report Generators

This Python package provides a flexible and extensible framework for generating reports in multiple formats, including XLSX (Excel), CSV, and PDF.

## Features
- Generate tabular reports in XLSX, CSV, and PDF formats
- Easily extendable for new report types and formats
- Utilities for formatting text and converting workbooks to CSV
- Base classes to help you implement custom report generators

## Structure
- `src/report_generators/xlsx/` – XLSX (Excel) report generator
- `src/report_generators/csv/` – CSV report generator (inherits from XLSX generator)
- `src/report_generators/pdf/` – PDF report generator
- `src/report_generators/utils/` – Shared utilities (text formatting, type definitions, workbook-to-CSV conversion)
- `src/report_generators/base_generator.py` – Base class for custom report logic

## Usage Example
```python
from src.report_generators.csv.generator import BaseCSVReportsGenerator
from src.report_generators.xlsx.generator import BaseXLSXReportsGenerator
from src.report_generators.pdf.generator import BasePDFReportsGenerator

# Implement your own BaseGenerator subclass for your data
base_generator = YourCustomBaseGenerator()

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

## Installation
Install the required dependencies:
```bash
pip install -r requirements.txt
```

## License
MIT License

---
Feel free to extend or customize the generators for your own reporting needs!
