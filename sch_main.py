from __future__ import print_function
import sch_config
import os.path
import pandas as pd
import asyncio
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import time
import datetime
import pytz
######################################################################
from os import getenv
from sys import exit
######################################################################
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # БАЗА
from aiogram.dispatcher.filters import Text
from aiogram import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import MessageNotModified
from aiogram.dispatcher import FSMContext
######################################################################
from contextlib import suppress
import atexit
######################################################################



# Configure logging
# filemode = "w"
# logging.basicConfig(filename="logging.log", format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
#                    level=logging.INFO)


bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

SEND_OP = getenv("SEND_OP")
if not SEND_OP:
    exit("Error: no token provided")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = sch_config.SPREADSHEET_ID


def convert_xls_datetime(xls_date):
    return datetime.datetime(1899, 12, 30) + datetime.timedelta(days=xls_date)


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
                # print(result[colorChannel]) Инфо по цветам, RGB с переносом на новую строку
    return result


def getDataFromExcelTable(field):
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
                                 ranges=field, includeGridData=True).execute()

    # result_month = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
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


async def scheduleMonitoring(message: types.Message):
    fields = [sch_config.field_WFM, sch_config.field_monitoring]
    work = [sch_config.WFM, sch_config.Monitoring]
    for field in fields:
        for name in work:
            reply = name
            data = getDataFromExcelTable(field)
            for name in data:
                userName = name
                userData = data[name]
                userInfo = userData["data"]
                reply += "🧑‍💻 " + userName + "  ||  " + userInfo
            #        userColor = userData["color"]
            #    if sch_config.isColorEquals(userColor, sch_config.colorCalls):
            #        reply += " *   👉Роль1* "
            #    elif sch_config.isColorEquals(userColor, sch_config.colorChatterBox):
            #        reply += " *   👉Роль2* "
            #    elif sch_config.isColorEquals(userColor, sch_config.colorWebim):
            #        reply += " *   👉Роль3* "
                reply += "\n"
        await bot.send_message(chat_id=message.chat.id, text=reply, parse_mode='Markdown')
        reply = ""
    print("Расписания отправлены. Включена задержка на 86200 sec.")


@dp.callback_query_handler(Text(equals='infoMonitoring'))
async def infoMonitoring(call: types.CallbackQuery):
    message = call.message
    await bot.send_message(message.chat.id, text=macros.info_Monitoring, parse_mode='Markdown')

tz_Moscow = pytz.timezone('Europe/Moscow')
datetime_Moscow = datetime.datetime.now(tz_Moscow)
print("Moscow time:", datetime_Moscow.strftime("%H:%M:%S"))


@dp.message_handler(commands="loop_activate")
async def time_to_send(message: types.Message):
    while True:
        print("Составляю расписание...")
        if str(datetime_Moscow.strftime("%H:%M:%S")) > "08:00:00":
            await scheduleMonitoring(message)
            await asyncio.sleep(86200)
            print("Составляю расписание...")
        else:
            await asyncio.sleep(25)
            print("Слишком рано. Повторная попытка через 25 sec.")


if __name__ == '__main__':
    executor.start_polling(dp)
