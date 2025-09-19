"""Template for setting up charts on the Graphs sheet."""

GRAPH_CREATION_BODY = {
    "requests": [
        {
            "addPivotTable": {
                "pivotTable": {
                    "source": {
                        "sheetId": 1,
                        "startRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8,
                    },
                    "rows": [
                        {
                            "sourceColumnOffset": 0,
                            "sortOrder": "DESCENDING",
                            "showTotals": False,
                        }
                    ],
                    "values": [
                        {
                            "summarizeFunction": "SUM",
                            "sourceColumnOffset": 3,
                            "name": "Total Spend",
                        }
                    ],
                    "valueLayout": "HORIZONTAL",
                    "sortSpecs": [
                        {
                            "measureOffset": 0,
                            "sortOrder": "DESCENDING",
                        }
                    ],
                },
                "destination": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "startColumnIndex": 0,
                },
            }
        },
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Top Items by Total Spend",
                        "basicChart": {
                            "chartType": "BAR",
                            "legendPosition": "RIGHT_LEGEND",
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 1,
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1,
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 1,
                                                    "startColumnIndex": 1,
                                                    "endColumnIndex": 2,
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS",
                                }
                            ],
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Items"},
                                {"position": "LEFT_AXIS", "title": "Total Spend"},
                            ],
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": 0,
                                "rowIndex": 0,
                                "columnIndex": 5,
                            },
                            "offsetXPixels": 0,
                            "offsetYPixels": 0,
                            "widthPixels": 600,
                            "heightPixels": 400,
                        }
                    },
                }
            }
        },
        {
            "addPivotTable": {
                "pivotTable": {
                    "source": {
                        "sheetId": 1,
                        "startRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8,
                    },
                    "rows": [
                        {
                            "sourceColumnOffset": 5,
                            "showTotals": False,
                        }
                    ],
                    "values": [
                        {
                            "summarizeFunction": "SUM",
                            "sourceColumnOffset": 3,
                            "name": "Total Spend",
                        }
                    ],
                },
                "destination": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "startColumnIndex": 12,
                },
            }
        },
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Spending by Vendor",
                        "pieChart": {
                            "legendPosition": "RIGHT_LEGEND",
                            "domain": {
                                "sourceRange": {
                                    "sources": [
                                        {
                                            "sheetId": 0,
                                            "startRowIndex": 1,
                                            "startColumnIndex": 12,
                                            "endColumnIndex": 13,
                                        }
                                    ]
                                }
                            },
                            "series": {
                                "sourceRange": {
                                    "sources": [
                                        {
                                            "sheetId": 0,
                                            "startRowIndex": 1,
                                            "startColumnIndex": 13,
                                            "endColumnIndex": 14,
                                        }
                                    ]
                                }
                            },
                        },
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": 0,
                                "rowIndex": 15,
                                "columnIndex": 5,
                            },
                            "offsetXPixels": 0,
                            "offsetYPixels": 0,
                            "widthPixels": 500,
                            "heightPixels": 400,
                        }
                    },
                }
            }
        },
        {
            "addPivotTable": {
                "pivotTable": {
                    "source": {
                        "sheetId": 1,
                        "startRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 8,
                    },
                    "rows": [
                        {
                            "sourceColumnOffset": 6,
                            "showTotals": False,
                            "sortOrder": "ASCENDING",
                            "groupRule": {
                                "dateTimeRule": {
                                    "type": "YEAR_MONTH",
                                }
                            },
                        }
                    ],
                    "values": [
                        {
                            "summarizeFunction": "SUM",
                            "sourceColumnOffset": 3,
                            "name": "Total Spend",
                        }
                    ],
                    "filterSpecifications": [
                        {
                            "filterCriteria": {
                                "condition": {
                                    "type": "DATE_AFTER_RELATIVE",
                                    "values": [
                                        {"relativeDate": "PAST_SIX_MONTHS"}
                                    ],
                                }
                            },
                            "sourceColumnOffset": 6,
                        }
                    ],
                },
                "destination": {
                    "sheetId": 0,
                    "startRowIndex": 20,
                    "startColumnIndex": 0,
                },
            }
        },
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Monthly Spending (Last 6 Months)",
                        "basicChart": {
                            "chartType": "COLUMN",
                            "legendPosition": "RIGHT_LEGEND",
                            "domains": [
                                {
                                    "domain": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 21,
                                                    "startColumnIndex": 0,
                                                    "endColumnIndex": 1,
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            "series": [
                                {
                                    "series": {
                                        "sourceRange": {
                                            "sources": [
                                                {
                                                    "sheetId": 0,
                                                    "startRowIndex": 21,
                                                    "startColumnIndex": 1,
                                                    "endColumnIndex": 2,
                                                }
                                            ]
                                        }
                                    },
                                    "targetAxis": "LEFT_AXIS",
                                }
                            ],
                            "axis": [
                                {"position": "BOTTOM_AXIS", "title": "Month"},
                                {"position": "LEFT_AXIS", "title": "Total Spend"},
                            ],
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": 0,
                                "rowIndex": 20,
                                "columnIndex": 5,
                            },
                            "offsetXPixels": 0,
                            "offsetYPixels": 0,
                            "widthPixels": 600,
                            "heightPixels": 400,
                        }
                    },
                }
            }
        },
    ]
}
