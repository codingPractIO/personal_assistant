from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
from templates.table_creation_template import TABLE_CREATION_BODY
from templates.sheets_preparation_template import SHEETS_PREPARATION_BODY

load_dotenv()  # Loads from .env

sheet_id = os.getenv("GOOGLE_SHEET_KEY")

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

SERVICE_ACCOUNT_FILE = 'google_service.json'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=[SCOPES]
)
service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()

def initialize_tables():
    """
    Initializes the Google Sheet by clearing existing data and setting up headers.
    """
    # Clear existing data
    sheet.values().clear(spreadsheetId=sheet_id, range='A1').execute()

    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=TABLE_CREATION_BODY
    ).execute()
    
    print("Sheet initialized with headers.")


def reset_sheets():
    """
    Resets the spreadsheet to its original state:
    - Ensures only one sheet remains with sheetId 0.
    - Clears all data from the remaining sheet and renames it to 'Sheet1'.
    """
    spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheets = spreadsheet.get('sheets', [])
    sheet_ids = [s['properties']['sheetId'] for s in sheets]

    requests = []

    if 0 not in sheet_ids:
        # Duplicate the first sheet and set its id to 0
        source_sheet_id = sheets[0]['properties']['sheetId']
        requests.append({
            "duplicateSheet": {
                "sourceSheetId": source_sheet_id,
                "insertSheetIndex": 0,
                "newSheetId": 0
            }
        })

    # After duplication, delete all sheets except sheetId 0
    # If we duplicated, the new sheet will be at index 0, so update the list
    # We'll delete all sheets with id != 0
    for s in sheets:
        sid = s['properties']['sheetId']
        if sid != 0:
            requests.append({
                "deleteSheet": {
                    "sheetId": sid
                }
            })

    # Rename sheetId 0 to 'Sheet1'
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": 0,
                "title": "Sheet1"
            },
            "fields": "title"
        }
    })

    # Perform batch update (duplicate if needed, delete, rename)
    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={"requests": requests}
        ).execute()

    # Now clear all data from 'Sheet1'
    sheet.values().clear(spreadsheetId=sheet_id, range='Sheet1').execute()

    print("Spreadsheet reset: only one empty sheet with id 0 remains.")


def prepare_sheets():
    """
    Creates a new sheet (tab) in the Google Spreadsheet.
    :param sheet_name: Name of the new sheet/tab.
    """
    
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=SHEETS_PREPARATION_BODY
    ).execute()
    print(f"New sheet created.")
    return response


def append_item_data(data):
    body = {
        'values': data["items"]
    }

    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range='item_table!A1',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates', {}).get('updatedCells', 0)} cells appended.")

def append_voucher_data(data):
    body = {
        'values': data["voucher_data"]
    }

    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range='voucher_table!A1',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    print(f"{result.get('updates', {}).get('updatedCells', 0)} cells appended.")


