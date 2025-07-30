import csv
import io
from openpyxl import Workbook


def workbook_to_csv_buffer(workbook: Workbook) -> io.StringIO:
    sheet = workbook.active
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    for row in sheet.iter_rows(values_only=True):
        writer.writerow(row)

    buffer.seek(0)
    return buffer
