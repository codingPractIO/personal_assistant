# table creation template

TABLE_CREATION_BODY = {

            
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
                            "columnName": "Receipt #",
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
                            "columnName": "Receipt",
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