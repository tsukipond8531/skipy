from __future__ import annotations

import googleapiclient.discovery
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


class SheetService:
    # NOTE:
    # https://googleapis.github.io/google-api-python-client/docs/dyn/sheets_v4.html
    def __init__(self, service_account_file=None, service_account_info=None):
        if service_account_file:
            creds = Credentials.from_service_account_file(
                service_account_file, scopes=SCOPES
            )
        elif service_account_info:
            creds = Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
        else:
            raise ValueError(
                "Either service_account_file or service_account_info must be provided."
            )
        self.client = googleapiclient.discovery.build(
            "sheets", "v4", credentials=creds, cache_discovery=False
        )

    def get_values(
        self, sheet_id: str, ranges: list[str], major_dimension: str = "ROWS"
    ):
        """Get values from a sheet.

        Args:
            sheet_id: Google Spreadsheet ID.
            ranges: list of Ranges.
            major_dimension: Either "ROWS" or "COLUMNS".

        Returns:
            JSON Format response as a dict.

        Examples:
            >>> get_values("sn", "Sheet1!A1:B5", "ROWS")

                [['a1', 'b1'], ['a2', 'b2'], ['a3', 'b3'], ['a4', 'b4'], ['a5', 'b5']]}

            >>> get_values("sn", "Sheet1!A1:B5", "COLUMNS")

                [['a1', 'a2', 'a3', 'a4', 'a5'], ['b1', 'b2', 'b3', 'b4', 'b5']]}

        """
        sheet = self.client.spreadsheets()
        values = (
            sheet.values()
            .batchGet(
                spreadsheetId=sheet_id,
                ranges=ranges,
                majorDimension=major_dimension,
            )
            .execute()
        )

        return values

    def _make_range(
        self, sheet_name: str, values: list, start_row: int, start_col: int
    ):
        end_row = start_row + len(values) - 1
        end_col = start_col + len(values[0]) - 1
        range = f"{sheet_name}!R{start_row}C{start_col}:R{end_row}C{end_col}"
        return range

    def post_values(
        self,
        sheet_id: str,
        values: list,
        sheet_name: str,
        major_dimension: str = "ROWS",
        start_row: int = 0,
        start_col: int = 0,
        range: str | None = None,
    ):
        """Post values to a sheet.

        Args:
            sheet_id: Google Spreadsheet ID.
            values: List of values to be inserted.
            sheet_name: Name of the sheet.
            major_dimension: Either "ROWS" or "COLUMNS".
            start_row: if range is None, start_row is used to make range.
            start_col: if range is None, start_col is used to make range.
            range: Range of the sheet.

        Returns:
            JSON Format response as a dict.

        """
        sheet = self.client.spreadsheets()
        if range is None:
            range = self._make_range(
                sheet_name=sheet_name,
                values=values,
                start_row=start_row,
                start_col=start_col,
            )
        body = {"range": range, "majorDimension": major_dimension, "values": values}
        r = (
            sheet.values()
            .update(
                spreadsheetId=sheet_id,
                body=body,
                range=range,
                valueInputOption="USER_ENTERED",
            )
            .execute()
        )
        return r
