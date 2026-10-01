import os
import sys
from pathlib import Path
import openpyxl

"""
This script processes Excel files (.xlsx) in a specified directory.
For each Excel file, it scans each sheet row by row and column by column.
If a cell contains only 'x' or 'X', it extracts the value two columns to the left of that cell.
The extracted values are saved to a .txt file with the same name as the Excel file.

It is used to get the choices of the user or selections marked with 'x' in the Excel sheets.
"""

def process_excel_file(excel_path: Path) -> None:
    """Reads an Excel file, extracts the value 2 columns to the left of any cell

    containing only 'x' or 'X' (scanned row by row, then column by column),
    and saves the extracted text lines to a .txt file.
    """
    txt_path = excel_path.with_suffix(".txt")
    extracted_lines = []

    try:
        # Load workbook (data_only=True evaluates formulas to their resulting values)
        wb = openpyxl.load_workbook(excel_path, data_only=True)

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]

            # Horizontal scan: row by row, left to right
            for row in ws.iter_rows(values_only=False):
                for cell in row:
                    val = cell.value

                    # Check if the cell contains strictly 'x' or 'X' (ignoring whitespace)
                    if val is not None and str(val).strip().lower() == "x":
                        col_index = cell.column  # 1-based index (e.g., A=1, B=2, C=3)
                        row_index = cell.row

                        # Ensure there are at least 2 columns to the left
                        if col_index > 2:
                            target_cell = ws.cell(
                                row=row_index, column=col_index - 2
                            )
                            target_val = target_cell.value

                            # Convert value to string (or empty string if None)
                            text = (
                                str(target_val) if target_val is not None else ""
                            )
                            extracted_lines.append(text)

        # Write results to the output .txt file
        with open(txt_path, "w", encoding="utf-8") as f:
            for line in extracted_lines:
                f.write(f"{line}\n")

        # Print a report line.
        # OK if we got 24 lines extracted exactly, ERROR otherwise
        if len(extracted_lines) == 24:
            print(f"[OK] Converted: {excel_path.name} -> {txt_path.name} ({len(extracted_lines)} line(s) extracted)")
        else:
            print(f"[ERROR] Conversion issue: {excel_path.name} -> {txt_path.name} ({len(extracted_lines)} line(s) extracted, expected 24)")

    except Exception as e:
        print(f"[ERROR] Failed to process {excel_path.name}: {e}")


def process_directory(root_dir: str) -> None:
    """Recursively finds and processes all .xlsx files in the target folder."""
    directory = Path(root_dir)

    if not directory.exists():
        print(f"Error: The path '{root_dir}' does not exist.")
        sys.exit(1)

    excel_files = list(directory.rglob("*.xlsx"))

    if not excel_files:
        print("No .xlsx files found in the specified path.")
        return

    print(
        f"Processing {len(excel_files)} Excel file(s) in '{directory}'...\n"
    )

    for excel_file in excel_files:
        # Skip Excel temporary files (~$...)
        if excel_file.name.startswith("~$"):
            continue
        process_excel_file(excel_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_excel.py <folder_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    process_directory(input_path)
