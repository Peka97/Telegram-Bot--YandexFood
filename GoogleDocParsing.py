from __future__ import print_function
import config
import datetime
import os.path
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BAIbiDotK1z02ZbraPHBfmK3q0TEq47DqYVGStgrL98'
SAMPLE_RANGE_NAME_MONTH = config.month

def convert_xls_datetime(xls_date):
    return (datetime.datetime(1899, 12, 30) + datetime.timedelta(days=xls_date))

def getColumnValueIfPossible(data):
    if "formattedValue" in data:
        return data["formattedValue"]
    return ""

def getCellColorIfPossible(data):
    result = {"red": 0, "green": 0, "blue": 0}
    if "userEnteredFormat" in data and "backgroundColor" in data["userEnteredFormat"]:
        for colorChannel in result:
            if colorChannel in data["userEnteredFormat"]["backgroundColor"]:
                result[colorChannel] = round(data["userEnteredFormat"]["backgroundColor"][colorChannel] * 255)
                #print(result[colorChannel]) Инфа по цветам, RGB с переносом на новую строку
    return result

def getDataFromExcelTable():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result_grid_data = sheet.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                         ranges=SAMPLE_RANGE_NAME_MONTH, includeGridData=True).execute()

    #result_month = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                                     ranges=SAMPLE_RANGE_NAME_MONTH).execute()
    result = result_grid_data['sheets'][0]['data'][0]['rowData']
    rowIndex = -1
    dateColumnIndex = -1
    date_now = datetime.datetime.now().date()
    parseResult = {}
    lastAddedElement = None
    for row in result:
        rowIndex = rowIndex + 1
        columnIndex = -1
        if 'values' in row:
            for values in row['values']:
                columnIndex = columnIndex + 1
                if rowIndex == 0:
                    if "userEnteredValue" in values and "numberValue" in values["userEnteredValue"]:
                        rowDate = convert_xls_datetime(values["userEnteredValue"]["numberValue"]).date()
                        if rowDate == date_now and dateColumnIndex < 0:
                            dateColumnIndex = columnIndex
                else:
                    if dateColumnIndex < 0:
                        break
                    if columnIndex == 0:
                        lastAddedElement = getColumnValueIfPossible(values)
                        parseResult[lastAddedElement] = {}
                    if columnIndex == dateColumnIndex:
                        parseResult[lastAddedElement]["data"] = getColumnValueIfPossible(values)
                        parseResult[lastAddedElement]["color"] = getCellColorIfPossible(values)
                        if len(parseResult[lastAddedElement]["data"]) == 0:
                            del parseResult[lastAddedElement]
                            continue
    return parseResult