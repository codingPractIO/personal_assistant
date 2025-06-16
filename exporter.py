from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env

sheet_id = os.getenv("GOOGLE_SHEET_KEY")

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

SERVICE_ACCOUNT_FILE = 'google_service.json'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=[SCOPES]
)
service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()

def table_initialization():
    """
    Initializes the Google Sheet by clearing existing data and setting up headers.
    """
    # Clear existing data
    sheet.values().clear(spreadsheetId=sheet_id, range='A1').execute()
    

    
    body = {

            
        "requests": [
           {

                "addTable": {
                    "table": {
                        "name": "Item data",
                        "tableId": "item_data",
                        "range": {
                            "sheetId": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 8,
                            "startRowIndex": 0,
                            "endRowIndex": 5,
                        },
                    "columnProperties": [
                        {
                            "columnIndex": 0,
                            "columnName": "Item",
                            "columnType": "TEXT"
                        },
                        {
                            "columnIndex": 1,
                            "columnName": "Price",
                            "columnType": "CURRENCY",
                        },
                          {
                            "columnIndex": 2,
                            "columnName": "Amount",
                            "columnType": "CURRENCY",
                        },
                          {
                            "columnIndex": 3,
                            "columnName": "Total",
                            "columnType": "CURRENCY",
                        },
                          {
                            "columnIndex": 4,
                            "columnName": "Reciept #",
                            "columnType": "TEXT",
                        },
                          {
                            "columnIndex": 5,
                            "columnName": "Vendor",
                            "columnType": "TEXT",
                        },
                          {
                            "columnIndex": 6,
                            "columnName": "Date",
                            "columnType": "DATE",
                        },
                          {
                            "columnIndex": 7,
                            "columnName": "Time",
                            "columnType": "TIME",
                        }
                    ],
                    }
                }
            },
            {

                "addTable":     {
                    "table": {
                        "name": "Coupon data",
                        "tableId": "coupon_data",
                        "range": {
                            "sheetId": 2,
                            "startColumnIndex": 0,
                            "endColumnIndex": 6,
                            "startRowIndex": 0,
                            "endRowIndex": 6,
                        },
                    "columnProperties": [
                        {
                            "columnIndex": 0,
                            "columnName": "Reciept",
                            "columnType": "TEXT"
                        },
                        {
                            "columnIndex": 1,
                            "columnName": "Place",
                            "columnType": "TEXT",
                           
                        },
                        {
                            "columnIndex": 2,
                            "columnName": "Voucher date",
                            "columnType": "DATE",
                        },
                        {
                            "columnIndex": 3,
                            "columnName": "Voucher time",
                            "columnType": "TIME",
                        },
                        {
                            "columnIndex": 4,
                            "columnName": "Total Amount Paid",
                            "columnType": "CURRENCY",
                           
                        },
                        {
                            "columnIndex": 5,
                            "columnName": "Voucher Value",
                            "columnType": "CURRENCY",
                           
                        }
                    ],
                    }
                }
            }
        ],
        "includeSpreadsheetInResponse": False,
        "responseRanges": [
            "A1"
        ],
        "responseIncludeGridData": False
    }

            
   

    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=body
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
    body = {
        "requests": [
             
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": 0,  # First/default sheet
                        "title": "Graphs"
                    },
                    "fields": "title"
                }
            },
            
            {
                "addSheet": {
                    "properties": {
                        "sheetId": 1,
                        "title": "item_table"
                    }
                }
            },

            {
                "addSheet": {
                    "properties": {
                        "sheetId": 2,
                        "title": "voucher_table"
                    }
                }
            }
            
        ]
    }
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=body
    ).execute()
    print(f"New sheet created.")
    return response

def append_cell_request(data):


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


