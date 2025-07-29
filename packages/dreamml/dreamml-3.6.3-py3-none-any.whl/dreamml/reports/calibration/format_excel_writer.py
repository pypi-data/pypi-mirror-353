import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
from typing import Tuple


class FormatExcelWriter:
    """
    Interface implementation for writing DataFrames to an Excel workbook with formatting.

    Args:
        writer (pd.ExcelWriter, optional): Excel writer object for writing.
            It is assumed that the Excel file is created outside the class.
    """

    def __init__(self, writer: pd.ExcelWriter = None):
        self.writer = writer
        self.workbook = self.writer.book
        self.formats = {}

        # Add a header format.
        self.header_format = self.workbook.add_format(
            {
                "bold": True,
                "text_wrap": False,
                "valign": "top",
                "fg_color": "#BFBFBF",
                "center_across": True,
                "border": 1,
            }
        )

        # Format sets for conditional formatting and traffic lights
        self.format_green = self.workbook.add_format(
            {"bg_color": "#C6EFCE", "font_color": "#006100"}
        )
        self.format_red = self.workbook.add_format(
            {"bg_color": "#FFC7CE", "font_color": "#9C0006"}
        )
        self.format_yellow = self.workbook.add_format(
            {"bg_color": "#FFFFCC", "font_color": "#CC9900"}
        )

        self.format_blind_red = self.workbook.add_format({"bg_color": "FDE9D9"})

    def _print_header(self, df: pd.DataFrame, pos: tuple, sheet: str):
        """
        Writes the table header in a specified format at the given position.

        Args:
            df (pd.DataFrame): DataFrame whose header is to be written.
            pos (tuple): Tuple containing the row and column indices for the header's starting position.
            sheet (str): Name of the sheet where the header will be written.
        """
        rows, cols = pos

        # Write header elements
        for col_num, value in enumerate(df.columns.values):
            self.worksheet.write(rows, cols + col_num, value, self.header_format)

    def _print_data(self, df: pd.DataFrame, pos: tuple, sheet: str):
        """
        Writes the DataFrame's data to the Excel sheet.

        Args:
            df (pd.DataFrame): DataFrame to be written.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            sheet (str): Name of the sheet where the data will be written.
        """
        rows, cols = pos

        for row_num, row in enumerate(df.values):
            for col_num, val in enumerate(row):
                # xlsxwriter cannot write lists or tuples, only strings or numerics
                if isinstance(val, list) or isinstance(val, tuple):
                    print_val = str(val)
                elif pd.isnull(val):
                    print_val = " "
                else:
                    print_val = val

                cell = xl_rowcol_to_cell(rows + row_num + 1, cols + col_num)

                # Apply format if exists for the cell
                if cell in self.formats.keys():
                    fmt = self.workbook.add_format(self.formats[cell])
                    self.worksheet.write(cell, print_val, fmt)
                else:
                    self.worksheet.write(cell, print_val)

    def _reset_format(self):
        """
        Resets the formats dictionary after formats have been applied.
        """
        self.formats = {}

    def merge_cells(
        self,
        df: pd.DataFrame,
        pos: Tuple,
        col_start: str,
        col_end: str,
        row_start: int,
        row_end: int,
    ):
        """
        Merges cells in the Excel sheet.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            pos (Tuple): Tuple containing the row and column indices for the top-left corner of the table.
            col_start (str): Starting column name for merging.
            col_end (str): Ending column name for merging.
            row_start (int): Starting row index for merging.
            row_end (int): Ending row index for merging.
        """
        merge_format = self.workbook.add_format(
            {
                "align": "center",
                "valign": "vcenter",
                "font_color": "#BFBFBF",
                "text_wrap": True,
            }
        )

        row, col = pos
        first_col = df.columns.get_loc(col_start) + col
        last_col = df.columns.get_loc(col_end) + col

        if row_start == 0:
            merge_format.set_top(5)
        if row_end == df.shape[0] - 1:
            merge_format.set_bottom(5)
        if first_col == 0:
            merge_format.set_left(5)
        if last_col == df.shape[1] - 1:
            merge_format.set_right(5)

        self.worksheet.merge_range(
            first_row=row_start + row + 1,
            first_col=first_col,
            last_row=row_end + row + 1,
            last_col=last_col,
            data=df[col_start][row_start],
            cell_format=merge_format,
        )

    def _add_cell_format(self, cell: str, format_name: str, format_value):
        """
        Adds a format to the formats dictionary for a specific cell.

        Args:
            cell (str): Cell address (e.g., 'A1').
            format_name (str): Name of the format attribute.
            format_value: Value of the format attribute.
        """
        format_dict = {format_name: format_value}

        if cell in self.formats.keys():
            tmp = self.formats[cell]
            tmp[format_name] = format_value
            self.formats[cell] = tmp
        else:
            self.formats[cell] = {format_name: format_value}

    def _add_column_format(
        self, df: pd.DataFrame, pos: tuple, col_name: str, format_name: str, format_value
    ):
        """
        Adds a format to each cell in a specified column.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            col_name (str): Name of the column to format.
            format_name (str): Name of the format attribute.
            format_value: Value of the format attribute.
        """
        rows, cols = pos
        col_num = df.columns.get_loc(col_name)

        for row_num in range(df.shape[0]):
            cell = xl_rowcol_to_cell(rows + row_num + 1, cols + col_num)
            self._add_cell_format(cell, format_name, format_value)

    def _add_row_format(
        self, df: pd.DataFrame, pos: tuple, row_num: int, format_name: str, format_value
    ):
        """
        Adds a format to each cell in a specified row.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            row_num (int): Index of the row to format.
            format_name (str): Name of the format attribute.
            format_value: Value of the format attribute.
        """
        rows, cols = pos

        for col_num in range(df.shape[1]):
            cell = xl_rowcol_to_cell(rows + row_num + 1, cols + col_num)
            self._add_cell_format(cell, format_name, format_value)

    def _add_bold_border(self, df: pd.DataFrame, pos: tuple, thickness: int):
        """
        Adds bold borders around the table with specified thickness.

        Args:
            df (pd.DataFrame): DataFrame for which the bold border is added.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            thickness (int): Thickness of the border.
        """
        rows, cols = pos
        # Top and bottom borders
        for col_num in range(df.shape[1]):
            top_cell = xl_rowcol_to_cell(rows + 1, cols + col_num)
            self._add_cell_format(top_cell, format_name="top", format_value=thickness)

            bottom_cell = xl_rowcol_to_cell(rows + df.shape[0], cols + col_num)
            self._add_cell_format(
                bottom_cell, format_name="bottom", format_value=thickness
            )

        # Left and right borders
        for row_num in range(df.shape[0]):
            left_cell = xl_rowcol_to_cell(rows + row_num + 1, cols)
            self._add_cell_format(left_cell, format_name="left", format_value=thickness)

            right_cell = xl_rowcol_to_cell(rows + row_num + 1, cols + df.shape[1] - 1)
            self._add_cell_format(
                right_cell, format_name="right", format_value=thickness
            )

    def set_width(self, df: pd.DataFrame, width: int, pos: tuple):
        """
        Sets the width of each column in the Excel sheet.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            width (int): Width to set for each column.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
        """
        rows, cols = pos
        for num, col in enumerate(df.columns):
            self.worksheet.set_column(cols + num, cols + num, width)

    def set_height(self, df: pd.DataFrame, height: int, pos: tuple):
        """
        Sets the height of each row in the Excel sheet.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            height (int): Height to set for each row.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
        """
        rows, cols = pos
        for row in range(df.shape[0]):
            self.worksheet.set_row(row + rows + 1, height)

    def _set_cells_width(self, df: pd.DataFrame, pos: tuple, sheet: str):
        """
        Sets the width of each column based on the maximum length of the data or header.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            sheet (str): Name of the sheet where the widths will be set.
        """
        rows, cols = pos
        for num, column in enumerate(df.columns):
            column_len = df[column].astype("str").str.len().max()
            column_len = max(column_len, len(column)) + 2
            self.worksheet.set_column(num + cols, num + cols, column_len)

    @staticmethod
    def define_auto_formats(df: pd.DataFrame) -> dict:
        """
        Automatically defines the formatting for the DataFrame based on data types and value ranges.

        Rules:
            - Integers: "## ##0"
            - Floats > 10: "## ##0.00"
            - Floats ≤ 10: "## ##0.0000"

        Args:
            df (pd.DataFrame): Original DataFrame to define formats for.

        Returns:
            dict: Dictionary containing format definitions.
        """
        # Base formats
        int_number = "## ##0"
        float_number_high = "## ##0.00"
        float_number_low = "## ##0.0000"
        int_percentage = "0%"
        float_percentage = "0.00%"

        # Data types
        integers = ["int16", "int32", "int64"]
        floats = ["float16", "float32", "float64"]

        high_floats = []
        low_floats = []
        ints = []

        for col in df.columns:
            if df[col].dtype in floats and df[col].max() > 10:
                high_floats.append(col)
            elif df[col].dtype in floats and df[col].max() <= 10:
                low_floats.append(col)
            elif df[col].dtype in integers:
                ints.append(col)

        formats = {
            "num_format": {
                int_number: ints,
                float_number_high: high_floats,
                float_number_low: low_floats,
                int_percentage: [],
                float_percentage: [],
            }
        }
        return formats

    def set_cell_cond_format(
        self,
        df: pd.DataFrame,
        pos: tuple,
        col_name: str,
        row_num: int,
        upper,
        lower,
        order: str,
    ):
        """
        Sets conditional formatting on a specific cell in the Excel sheet based on value ranges.

        Args:
            df (pd.DataFrame): Original DataFrame containing the data.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            col_name (str): Name of the column for which the cell is formatted.
            row_num (int): Row index of the cell to format.
            upper: Upper threshold for formatting.
            lower: Lower threshold for formatting.
            order (str): Ordering of thresholds. 
                - "straight": 
                    - Between lower and upper: yellow
                    - Below lower: green
                    - Above upper: red
                - "reverse": 
                    - Between upper and lower: yellow
                    - Above lower: green
                    - Below upper: red
        """
        rows, cols = pos

        col_num = df.columns.get_loc(col_name)

        fmt_start = xl_rowcol_to_cell(rows + row_num + 1, cols + col_num)
        fmt_end = xl_rowcol_to_cell(rows + row_num + 1, cols + col_num)

        if order == "straight":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "between",
                    "minimum": lower,
                    "maximum": upper,
                    "format": self.format_yellow,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "<",
                    "value": lower,
                    "format": self.format_green,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": ">",
                    "value": upper,
                    "format": self.format_red,
                },
            )

        elif order == "reverse":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "between",
                    "minimum": upper,
                    "maximum": lower,
                    "format": self.format_yellow,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": ">",
                    "value": lower,
                    "format": self.format_green,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "<",
                    "value": upper,
                    "format": self.format_red,
                },
            )

    def set_col_cond_format_tail(
        self, df: pd.DataFrame, pos: tuple, col_name: str, upper, lower, order: str
    ):
        """
        Sets one-sided conditional formatting on a column in the Excel sheet.

        Args:
            df (pd.DataFrame): Original DataFrame containing the data.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            col_name (str): Name of the column for which the formatting is applied.
            upper: Upper threshold for formatting.
            lower: Lower threshold for formatting.
            order (str): Ordering of thresholds.
                - "straight":
                    - Below lower: green
                    - Above or equal to upper: red
                - "reverse":
                    - Above lower: green
                    - Below or equal to upper: red
        """
        rows, cols = pos
        col_num = df.columns.get_loc(col_name)

        fmt_start = xl_rowcol_to_cell(rows + 1, cols + col_num)
        fmt_end = xl_rowcol_to_cell(rows + df.shape[0], cols + col_num)

        if order == "straight":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "<",
                    "value": lower,
                    "format": self.format_green,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": ">=",
                    "value": upper,
                    "format": self.format_red,
                },
            )

        elif order == "reverse":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": ">",
                    "value": lower,
                    "format": self.format_green,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "<=",
                    "value": upper,
                    "format": self.format_red,
                },
            )

    def set_simple_cond_format(
        self, df: pd.DataFrame, pos: tuple, col_name: str, boundary, order: str
    ):
        """
        Sets simple conditional formatting on a column in the Excel sheet.

        Args:
            df (pd.DataFrame): Original DataFrame containing the data.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            col_name (str): Name of the column for which the formatting is applied.
            boundary: Boundary value for formatting.
            order (str): Ordering of the boundary.
                - "straight": 
                    - Less than or equal to boundary: light red
                - "reverse": 
                    - Greater than or equal to boundary: light red
        """
        rows, cols = pos
        col_num = df.columns.get_loc(col_name)

        fmt_start = xl_rowcol_to_cell(rows + 1, cols + col_num)
        fmt_end = xl_rowcol_to_cell(rows + df.shape[0], cols + col_num)

        if order == "straight":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "<=",
                    "value": boundary,
                    "format": self.format_blind_red,
                },
            )

        elif order == "reverse":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": ">=",
                    "value": boundary,
                    "format": self.format_blind_red,
                },
            )

    def set_col_cond_format(
        self, df: pd.DataFrame, pos: tuple, col_name: str, upper, lower, order: str
    ):
        """
        Sets two-sided conditional formatting on a column in the Excel sheet.

        Args:
            df (pd.DataFrame): Original DataFrame containing the data.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            col_name (str): Name of the column for which the formatting is applied.
            upper: Upper threshold for formatting.
            lower: Lower threshold for formatting.
            order (str): Ordering of thresholds.
                - "straight":
                    - Below lower: green
                    - Between lower and upper: yellow
                    - Above upper: red
                - "reverse":
                    - Above lower: green
                    - Between upper and lower: yellow
                    - Below upper: red
        """
        rows, cols = pos
        col_num = df.columns.get_loc(col_name)

        fmt_start = xl_rowcol_to_cell(rows + 1, cols + col_num)
        fmt_end = xl_rowcol_to_cell(rows + df.shape[0], cols + col_num)

        if order == "straight":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "between",
                    "minimum": lower,
                    "maximum": upper,
                    "format": self.format_yellow,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "<",
                    "value": lower,
                    "format": self.format_green,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": ">",
                    "value": upper,
                    "format": self.format_red,
                },
            )

        elif order == "reverse":
            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "between",
                    "minimum": upper,
                    "maximum": lower,
                    "format": self.format_yellow,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": ">",
                    "value": lower,
                    "format": self.format_green,
                },
            )

            self.worksheet.conditional_format(
                f"{fmt_start}:{fmt_end}",
                {
                    "type": "cell",
                    "criteria": "<",
                    "value": upper,
                    "format": self.format_red,
                },
            )

    def write_data_frame(
        self,
        df: pd.DataFrame,
        pos: tuple,
        sheet: str,
        formats: dict = None,
        row_formats: dict = None,
    ):
        """
        Writes a DataFrame to an Excel sheet with specified formatting.

        Args:
            df (pd.DataFrame): Original DataFrame to write.
            pos (tuple): Tuple containing the row and column indices for the top-left corner of the table.
            sheet (str): Name of the sheet where the DataFrame will be written.
            formats (dict, optional): Dictionary of formats to apply to columns.
            row_formats (dict, optional): Dictionary of formats to apply to rows.

        Raises:
            ValueError: If the sheet name exceeds Excel's 31-character limit.
        """
        # Excel sheet name length limitation
        worksheet = sheet[:31]
        df_empty = pd.DataFrame()
        # Write an empty DataFrame to Excel to ensure the sheet is created correctly
        df_empty.to_excel(
            excel_writer=self.writer,
            sheet_name=worksheet,
            startrow=0,
            index=False,
            header=False,
            engine="OpenPyXL",
        )

        self.worksheet = self.writer.sheets[worksheet]

        # Write the formatted table header
        self._print_header(df=df, pos=pos, sheet=worksheet)
        if formats is None:
            formats = self.define_auto_formats(df)

        # Add formats for columns
        for fmt_name, fmt in formats.items():
            for value, cols in fmt.items():
                for col in cols:
                    if col in df.columns:
                        self._add_column_format(
                            df=df,
                            pos=pos,
                            col_name=col,
                            format_name=fmt_name,
                            format_value=value,
                        )
        if row_formats is not None:
            # Add formats for rows
            for fmt_name, fmt in row_formats.items():
                for value, rows in fmt.items():
                    for row in rows:
                        self._add_row_format(
                            df=df,
                            pos=pos,
                            row_num=row,
                            format_name=fmt_name,
                            format_value=value,
                        )

        # Add a bold border around the table
        self._add_bold_border(df=df, pos=pos, thickness=5)

        # Write the formatted table data
        self._print_data(df=df, pos=pos, sheet=worksheet)

        # Set column widths
        self._set_cells_width(df=df, pos=pos, sheet=worksheet)

        self._reset_format()