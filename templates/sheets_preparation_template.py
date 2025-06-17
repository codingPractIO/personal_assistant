#sheets preparation body template

SHEETS_PREPARATION_BODY = {
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