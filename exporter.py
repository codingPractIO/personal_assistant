from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from parser import ReceiptParser
import json



sheet_id = '10s_m17fznodfg0uosbZ0LFbqX8zUxLlMkF__0oOsxpo'

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

SERVICE_ACCOUNT_FILE = '/home/soimimozo/Code/VSCode/reciept_bot/sheetsapi-460823-4a5af45db8a7.json'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=[SCOPES]
)
service = build('sheets', 'v4', credentials=credentials)

sheet = service.spreadsheets()

def export_to_sheet(data):
    """
    Exports the given data to a Google Sheet.
    
    :param data: List of dictionaries containing the data to be exported.
    """
    body = {
        'values': data["items"]
    }
    
    result = sheet.values().update(
        spreadsheetId=sheet_id,
        range='A1',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    print(f"{result.get('updatedCells')} cells updated.")

# Load the JSON file first
# with open("reciept_bot/parsed_data/100065309_17-05-2025.json", encoding="utf-8") as f:
#     parsed_data = json.load(f)

# export_to_sheet(parsed_data)



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
                            "sheetId": 1,
                            "startColumnIndex": 15,
                            "endColumnIndex": 23,
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
                            "columnType": "DROPDOWN",
                            "dataValidationRule": {
                                "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [
                                    {
                                    "userEnteredValue": "Not Started"
                                    },
                                    {
                                    "userEnteredValue": "In Progress"
                                    },
                                    {
                                    "userEnteredValue": "Complete"
                                    }
                                ]
                                }
                            }
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
                        "title": "data_tables"
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

# Example usage:
prepare_sheets()

table_initialization()


