"""Helpers for exporting parsed data to Google Sheets."""
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import logging
from templates.table_creation_template import TABLE_CREATION_BODY
from templates.sheets_preparation_template import SHEETS_PREPARATION_BODY
from templates.graph_creation_template import GRAPH_CREATION_BODY
from .config import SERVICE_ACCOUNT_FILE, SCOPES

logger = logging.getLogger(__name__)

_service = None


def get_service():
    """Return an authorized Google Sheets service instance."""
    global _service
    if _service is None:
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=[SCOPES]
        )
        _service = build("sheets", "v4", credentials=credentials)
    return _service

def initialize_tables(sheet_id: str):
    """Initialize a Google Sheet with headers."""
    service = get_service()
    sheet = service.spreadsheets()
    # Clear existing data
    sheet.values().clear(spreadsheetId=sheet_id, range='A1').execute()

    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=TABLE_CREATION_BODY
    ).execute()
    
    logger.info("Sheet initialized with headers.")


def reset_sheets(sheet_id: str):
    """Reset the spreadsheet to a single empty sheet."""
    service = get_service()
    sheet = service.spreadsheets()
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

    logger.info("Spreadsheet reset: only one empty sheet with id 0 remains.")


def prepare_sheets(sheet_id: str):
    """Create a new sheet (tab) in the Google Spreadsheet."""

    service = get_service()
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=SHEETS_PREPARATION_BODY
    ).execute()
    logger.info("New sheet created.")
    return response


def initialize_graphs(sheet_id: str):
    """Create pivot tables and charts for analytics."""

    service = get_service()
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=GRAPH_CREATION_BODY,
    ).execute()

    logger.info("Graphs initialized.")


def append_item_data(sheet_id: str, data):
    body = {
        'values': data["items"]
    }

    service = get_service()
    sheet = service.spreadsheets()
    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range='item_table!A1',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    logger.info("%s cells appended.", result.get('updates', {}).get('updatedCells', 0))

def append_voucher_data(sheet_id: str, data):
    body = {
        'values': data["voucher_data"]
    }

    service = get_service()
    sheet = service.spreadsheets()
    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range='voucher_table!A1',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    logger.info("%s cells appended.", result.get('updates', {}).get('updatedCells', 0))


