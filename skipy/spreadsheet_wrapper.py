import googleapiclient.discovery
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


class SpreadsheetService:
    def __init__(self, service_account_file=None, service_account_info=None):
        if service_account_file:
            creds = Credentials.from_service_account_file(service_account_file, scope=SCOPES)
        if service_account_info:
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        else:
            raise ValueError("Please specify service_account_file or service_account_info")
        self.sheets_service = googleapiclient.discovery.build("sheets", "v4", credentials=creds, cache_discovery=False)

    def get_sheet_values(self, ss_id: str, ss_name: str) -> list:
        ss = self.sheets_service.spreadsheets()
        range_ = f"{ss_name}!A:ZZ"
        dict_ = ss.values().batchGet(spreadsheetId=ss_id, ranges=range_).execute()

        return dict_["valueRanges"][0]["values"]

    def post_values_to_sheet(self, ss_id: str, ss_name: str, values: list, row: int, col: int) -> None:
        ss = self.sheets_service.spreadsheets()
        range_ = f"{ss_name}!R{row}C{col}:R{row + len(values) - 1}C{col + len(values[0]) - 1}"
        body = {"range": range_, "majorDimension": "ROWS", "values": values}
        ss.values().update(
            spreadsheetId=ss_id,
            range=range_,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
