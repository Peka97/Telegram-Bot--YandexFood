######################################################################
import asyncio
import logging
import sqlite3
import time

import pymysql
import numpy
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
import GDParsingTL
import config
import keyboard
import macros
import GoogleDocParsing as google
from BotUser import BotUser
from BotUser import BotUserType

######################################################################
######################################################################

# Configure logging
#filemode = "w"
#logging.basicConfig(filename="logging.log", format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
#                    level=logging.INFO)


bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

SEND_OP = getenv("SEND_OP")
if not SEND_OP:
    exit("Error: no token provided")


global BotUsers
BotUsers = {}


# SQL Base
def db_table_update(ID: int, UserName: str, FullName: str, Staff: str, Role: str, Admin: int, ChatMax: int):
    config.cursor.execute('INSERT INTO Users (ID, UserName, FullName, Staff, Role, Admin, ChatMax) VALUES (?, ?, ?, ?, ?, ?, ?)', (ID, UserName, FullName, Staff, Role, Admin, ChatMax))
    config.conn.commit()


# States
class GetData(StatesGroup):
    waiting_for_staff = State()
    waiting_for_role = State()


class GetDataAccess(StatesGroup):
    waiting_for_login = State()
    waiting_for_access = State()


class GetDataChatsMax(StatesGroup):
    waiting_for_logins_max = State()
    waiting_for_logins_min = State()


@dp.message_handler(commands=["menu"])
async def menu(message: types.Message):
    await message.reply("меню мониторинга", reply_markup=keyboard.monitoring_start)



# START
@dp.message_handler(commands=["start"], state='*')
async def get_text_messages(message: types.Message):
    get_id = str(message.from_user.id)
    config.cursor.execute(config.find_id, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_id, (get_id,)).fetchone()
    if str(message.from_user.id) in str(result):
        await message.reply("Ты уже есть в БД. Если нужно заменить какие то данные, воспользуйся соответствующей кнопкой")
    else:
        ID = message.from_user.id
        UserName = "@" + message.from_user.username
        FullName = message.from_user.last_name + " " + message.from_user.first_name
        Staff = config.NULL
        Role = config.NULL
        Admin = 0
        ChatMax = 0
        db_table_update(ID=ID, UserName=UserName, FullName=FullName, Staff=Staff, Role=Role, Admin=Admin, ChatMax=ChatMax)
        await message.reply(f'Привет, *{message.from_user.first_name}*!\n\nНапиши следом свой логин со стаффа (без знака @)', parse_mode='Markdown')
        await GetData.waiting_for_staff.set()


@dp.message_handler(state=GetData.waiting_for_staff)
async def waiting_staff(message: types.Message, state: FSMContext):
    await state.update_data(new_staff=message.text)
    staff_data = await state.get_data()
    find_staff = "SELECT Staff FROM Users WHERE ID = ?"
    get_id = str(message.from_user.id)
    config.cursor.execute(find_staff, (get_id,)).fetchone()
    result = config.cursor.execute(find_staff, (get_id,)).fetchone()
    for row in result:
        if config.NULL in row:
            get_staff = (str(staff_data['new_staff']), str(message.from_user.id))
            config.cursor.execute(config.update_staff, get_staff)
            config.conn.commit()
            data_role = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
            data_role.add(InlineKeyboardButton("L1 Client Calls", callback_data='add_role_L1_Client_Calls'), InlineKeyboardButton("L1 Client Chats", callback_data='add_role_L1_Client_Chats'))
            data_role.add(InlineKeyboardButton("L1 restaurant Calls", callback_data='add_role_L1_Rest_Calls'), InlineKeyboardButton("L1 restaurant Chats", callback_data='add_role_L1_Rest_Chats'))
            data_role.add(InlineKeyboardButton("L1 Courier Calls", callback_data='add_role_L1_Cour_Calls'), InlineKeyboardButton("L1 Courier Chats", callback_data='add_role_L1_Cour_Chats'))
            data_role.add(InlineKeyboardButton("L2", callback_data='add_role_L2'), InlineKeyboardButton("Другая роль", callback_data='add_role_another'))
            await message.reply(f"Ок, твой новый логин со стаффа: " + str(staff_data['new_staff']) + ".\n\nТеперь выбери подходящую роль в КЦ", reply_markup=keyboard.start, parse_mode='Markdown')
        else:
            await message.reply(f"Ваш текущий логин со стаффа: " + str(staff_data['new_staff']) + ".\n\nЖелаете его заменить?", parse_mode='Markdown')
        await state.finish()


# Roles
@dp.callback_query_handler(Text(equals="add_role_L1_Client_Calls"))
async def add_role_L1_Client_Calls(message: types.Message):
    get_id = message.from_user.id
    get_role = config.L1_Client_Calls, str(message.from_user.id)
    config.cursor.execute(config.find_role, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_role, (get_id,)).fetchone()
    for role in result:
        if config.NULL in role:
            config.cursor.execute(config.update_role, get_role)
            config.conn.commit()
            await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваша текущая роль: *{config.L1_Client_Calls}*", parse_mode='Markdown')
        else:
            await bot.send_message(message.from_user.id, f"Ты уже зарегистрирован под этой ролью: *{role}*", parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='add_role_L1_Client_Chats'))
async def add_role_L1_Client_Chats(message: types.Message):
    get_id = message.from_user.id
    get_role = config.L1_Client_Chats, str(message.from_user.id)
    config.cursor.execute(config.find_role, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_role, (get_id,)).fetchone()
    for role in result:
        if config.NULL in role:
            config.cursor.execute(config.update_role, get_role)
            config.conn.commit()
            await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваша текущая роль: *{config.L1_Client_Chats}*",
                                   parse_mode='Markdown')
        else:
            await bot.send_message(message.from_user.id, f"Ты уже зарегистрирован под этой ролью: *{role}*",
                                   parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='add_role_L1_Rest_Calls'))
async def add_role_L1_Rest_Calls(message: types.Message):
    get_id = message.from_user.id
    get_role = config.L1_Rest_Calls, str(message.from_user.id)
    config.cursor.execute(config.find_role, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_role, (get_id,)).fetchone()
    for role in result:
        if config.NULL in role:
            config.cursor.execute(config.update_role, get_role)
            config.conn.commit()
            await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваша текущая роль: *{config.L1_Rest_Calls}*",
                                   parse_mode='Markdown')
        else:
            await bot.send_message(message.from_user.id, f"Ты уже зарегистрирован под этой ролью: *{role}*",
                                   parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='add_role_L1_Rest_Chats'))
async def add_role_L1_Rest_Chats(message: types.Message):
    get_id = message.from_user.id
    get_role = config.L1_Rest_Calls, str(message.from_user.id)
    config.cursor.execute(config.find_role, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_role, (get_id,)).fetchone()
    for role in result:
        if config.NULL in role:
            config.cursor.execute(config.update_role, get_role)
            config.conn.commit()
            await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваша текущая роль: *{config.L1_Rest_Calls}*",
                                   parse_mode='Markdown')
        else:
            await bot.send_message(message.from_user.id, f"Ты уже зарегистрирован под этой ролью: *{role}*",
                                   parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='add_role_L1_Cour_Calls'))
async def add_role_L1_Cour_Calls(message: types.Message):
    get_id = message.from_user.id
    get_role = config.L1_Cour_Calls, str(message.from_user.id)
    config.cursor.execute(config.find_role, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_role, (get_id,)).fetchone()
    for role in result:
        if config.NULL in role:
            config.cursor.execute(config.update_role, get_role)
            config.conn.commit()
            await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваша текущая роль: *{config.L1_Cour_Calls}*",
                                   parse_mode='Markdown')
        else:
            await bot.send_message(message.from_user.id, f"Ты уже зарегистрирован под этой ролью: *{role}*",
                                   parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='add_role_L1_Cour_Chats'))
async def add_role_L1_Cour_Chats(message: types.Message):
    get_id = message.from_user.id
    get_role = config.L1_Cour_Calls, str(message.from_user.id)
    config.cursor.execute(config.find_role, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_role, (get_id,)).fetchone()
    for role in result:
        if config.NULL in role:
            config.cursor.execute(config.update_role, get_role)
            config.conn.commit()
            await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваша текущая роль: *{config.L1_Cour_Calls}*",
                                   parse_mode='Markdown')
        else:
            await bot.send_message(message.from_user.id, f"Ты уже зарегистрирован под этой ролью: *{role}*",
                                   parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='add_role_L2'))
async def add_role_L2(message: types.Message):
    get_id = message.from_user.id
    get_role = config.L1_Cour_Calls, str(message.from_user.id)
    config.cursor.execute(config.find_role, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_role, (get_id,)).fetchone()
    for role in result:
        if config.NULL in role:
            config.cursor.execute(config.update_role, get_role)
            config.conn.commit()
            await bot.send_message(message.from_user.id, f"Регистрация прошла успешно! Ваша текущая роль: *{config.L1_Cour_Calls}*",
                                   parse_mode='Markdown')
        else:
            await bot.send_message(message.from_user.id, f"Ты уже зарегистрирован под этой ролью: *{role}*",
                                   parse_mode='Markdown')


@dp.message_handler(Text(equals="a4NQm5puAl9jTVlx6Qjm4TmXCe7jtK2tkJL9BlU5"))
async def waiting_role(message: types.Message):
    get_role = config.monitoring, str(message.from_user.id)
    config.cursor.execute(config.update_role, get_role)
    config.conn.commit()
    await message.reply(f"Регистрация прошла успешно! Ваша текущая роль: *{config.monitoring}*", parse_mode='Markdown')


@dp.message_handler(Text(equals="wLJDzdHm7StnCGk4koCTfzkm4SqgWGj9egISynnm"))
async def waiting_role(message: types.Message):
    get_role = config.TL, str(message.from_user.id)
    config.cursor.execute(config.update_role, get_role)
    config.conn.commit()
    await message.reply(f"Регистрация прошла успешно! Ваша текущая роль: *{config.TL}*", parse_mode='Markdown')


# КОМАНДА HELP
@dp.message_handler(commands=['help'], state=None)
async def cmd_help(message: types.Message):
    await bot.send_message(message.chat.id, f"Я - бот отдела мониторинга. Все функциональные клавиши отображаются снизу согласно выбранному тобой отдела.\n\n Если у тебя возникли трудности или вопросы, можешь задать их моему создателю @loner97", reply_markup=keyboard.start, parse_mode='Markdown')


# Access
@dp.message_handler(Text(equals="Выдать доступ"), state="*")
async def give_access_step_1(message: types.Message):
    get_id = message.from_user.id
    config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    if config.admin in result:
        await message.reply(f"Укажите логин агента со стафф, доступ которому нужно выдать", parse_mode='Markdown')
        await GetDataAccess.waiting_for_login.set()


@dp.message_handler(state=GetDataAccess.waiting_for_login)
async def give_access_step_2(message: types.Message, state: FSMContext):
    await state.update_data(state_staff=message.text)
    await message.reply(f"Укажите уровень доступа от 1 до 5", parse_mode='Markdown')
    await GetDataAccess.waiting_for_access.set()


@dp.message_handler(state=GetDataAccess.waiting_for_access)
async def give_access_step_3(message: types.Message, state: FSMContext):
    await state.update_data(state_access=message.text)
    get_data = await state.get_data()
    agent = (int(get_data['state_access'])), str(get_data['state_staff'])
    config.cursor.execute(config.update_admin, agent)
    config.conn.commit()
    await message.reply(f"Агенту *{get_data['state_staff']}* выдан доступ *{get_data['state_access']}-го уровня*", parse_mode='Markdown')
    await state.finish()


@dp.message_handler(Text(equals="📞КЦ L1📞"))
async def cc_start_panel(message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        user.set_user_type(BotUserType.USER_TYPE_CC)
        await bot.send_message(message.chat.id, f"Давай начнём! Что случилось?",
                               reply_markup=keyboard.CC_start, parse_mode='Markdown')
    elif user.get_user_type() != BotUserType.USER_TYPE_NONE:
        await bot.send_message(message.chat.id,
                               f"Ты уже есть в базе под ролью *{user.get_user_type_as_string()}* Уверен в своём выборе?",
                               reply_markup=keyboard.choose_role_cc,
                               parse_mode='Markdown')
    else:
        user.set_user_type(BotUserType.USER_TYPE_CC)
        await bot.send_message(message.chat.id, f"Давай начнём! Что случилось?",
                               reply_markup=keyboard.CC_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='yes_сс'))
async def calls_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    user.set_user_type(BotUserType.USER_TYPE_COURIER)
    await bot.send_message(message.chat.id, f"Твоя текущая роль #CC.\n\n Готов к работе!", reply_markup=keyboard.CC_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='no_сс'))
async def no_cour(call: types.CallbackQuery):
    message = call.message
    await bot.send_message(message.chat.id, f"Хорошо, роль осталась прежней", reply_markup=keyboard.CC_start, parse_mode='Markdown')


@dp.message_handler(Text(equals="🚴🏻КЦ Курьерка🚴🏻"))
async def cc_cour_start_panel(message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        user.set_user_type(BotUserType.USER_TYPE_COURIER)
        await bot.send_message(message.chat.id, f"Давай начнём! Что случилось?",
                               reply_markup=keyboard.CC_COUR_start, parse_mode='Markdown')
    elif user.get_user_type() != BotUserType.USER_TYPE_NONE:
        await bot.send_message(message.chat.id, f"Ты уже есть в базе под ролью *{user.get_user_type_as_string()}* Уверен в своём выборе?", reply_markup=keyboard.choose_role_cc,
                               parse_mode='Markdown')
    else:
        user.set_user_type(BotUserType.USER_TYPE_COURIER)
        await bot.send_message(message.chat.id, f"Давай начнём! Что случилось?",
                               reply_markup=keyboard.CC_COUR_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='yes_сour'))
async def yes_cour(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    user.set_user_type(BotUserType.USER_TYPE_CC)
    await bot.send_message(message.chat.id, f"Твоя текущая роль #COUR.\n\n Готов к работе!", reply_markup=keyboard.CC_COUR_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='no_сour'))
async def no_cour(call: types.CallbackQuery):
    message = call.message
    await bot.send_message(message.chat.id, f"Хорошо, роль осталась прежней", reply_markup=keyboard.CC_COUR_start, parse_mode='Markdown')


@dp.message_handler(Text(equals="🖥Мониторинг🖥"))
async def monitoring_start_panel(message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        user.set_user_type(BotUserType.USER_TYPE_MONITORING)
        await bot.send_message(message.chat.id, f"*{message.from_user.first_name},* я тебя узнал. Готов вкалывать!",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
    else:
        await bot.send_message(message.chat.id, f"Отказано. Обратись к @loner97 для выдачи доступа",
                               parse_mode='Markdown')

# Доступ QA
@dp.message_handler(Text(equals="fds556ds6fds4564ds6f44f864ds6f4sd5f"))
async def QA_start_panel(message):
    user = BotUsers.get(message.from_user.id)
    user.set_user_type(BotUserType.USER_TYPE_QA)
    await bot.send_message(message.chat.id, f"*{message.from_user.first_name},* похоже ты знаешь волшебное слово. Готов вкалывать!",
                               reply_markup=keyboard.QA_start, parse_mode='Markdown')

# Доступ TL
@dp.message_handler(Text(equals="f564dsf564ds88asd684sa5g6465f4ds56f"))
async def TL_start_panel(message):
    user = BotUsers.get(message.from_user.id)
    user.set_user_type(BotUserType.USER_TYPE_TL)
    await bot.send_message(message.chat.id, f"*{message.from_user.first_name},* похоже ты знаешь волшебное слово. Готов вкалывать!",
                           reply_markup=keyboard.TL_start, parse_mode='Markdown')


# КНОПКИ
@dp.message_handler(Text(equals="🧯Дизастеры🧯"))
async def diz_b(message: types.Message):
    get_id = message.from_user.id
    config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    if config.admin in result:
        await message.answer("Выбери канал рассылки", reply_markup=keyboard.diz_p)


@dp.message_handler(Text(equals="КЦ"))
async def cc_b(message: types.Message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        await message.answer("Выбери дизастер", reply_markup=keyboard.cc_p)


@dp.message_handler(Text(equals="Проблемы"))
async def problems_panel(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_panel)


@dp.message_handler(Text(equals="🔄Сменить роль🔄"))
async def role(message):
    await bot.send_message(message.chat.id, f"Выбери нужную роль", reply_markup=keyboard.start,
                               parse_mode='Markdown')


# ЗВОНКИ
@dp.message_handler(Text(equals="📞Звонки📞"))
async def calls(message: types.Message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.calls,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='calls_on'))
async def calls_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_on,
                                           parse_mode='Markdown')
                    receive_users += 1
                except Exception:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='calls_off'))
async def calls_off(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_off,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


# ЗВОНКИ L2
@dp.message_handler(Text(equals="📞Звонки L2📞"))
async def without_puree(message: types.Message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.calls_l2,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='l2_on'))
async def l2_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_l2_on,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='l2_off'))
async def l2_off(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_l2_off,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.message_handler(Text(equals="🌙Звонки L2 Ночь🌙"))
async def calls_l2_night(message: types.Message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.calls_l2_night,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='l2_night_on'))
async def l2_night_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_l2_night_on,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='l2_night_off'))
async def l2_night_off(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_l2_night_off,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.message_handler(Text(equals="🔥L2 — STOP🔥"))
async def diz_l2_stop(message: types.Message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.calls_l2_stop,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='l2_stop_on'))
async def l2_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_l2_stop_on,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='l2_stop_off'))
async def l2_off(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_call_l2_stop_off,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')

# ЧАТЫ
@dp.message_handler(Text(equals="💻ChatterBox Crit💻"))
async def chatterbox_crit(message: types.Message):
    user = BotUsers.get(message.from_user.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text=macros.diz_chatterbox_crit_confirm,
                               reply_markup=keyboard.chatterbox_crit,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='chatterbox_crit_on'))
async def chatterbox_crit_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_chatterbox_crit_on,
                                           parse_mode='Markdown')
                    receive_users += 1
                except Exception:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='chatterbox_crit_off'))
async def chatterbox_crit_off(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_chatterbox_crit_off,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.message_handler(Text(equals="💬Чаты💬"))
async def cc_chats(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.chats,
                               parse_mode='Markdown')


class DataChats(StatesGroup):
    waiting_for_message_on = State()
    waiting_for_message_off = State()


@dp.callback_query_handler(Text(equals="chats_on"), state='*')
async def cc_chats_max_mailing_start(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, "Введите список агентов или нажмите /cancel для отмены действия")
        await DataChats.waiting_for_message_on.set()


@dp.message_handler(commands="cancel", state="*")
async def mailing_cancel(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, "Действие отменено", reply_markup=keyboard.monitoring_start,
                               parse_mode="Markdown")
        await state.finish()


@dp.message_handler(state=DataChats.waiting_for_message_on)
async def cc_chats_max_mailing_end(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await state.update_data(choosen_operators=message.text)
        operators_data = await state.get_data()
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(),
                                           f"Включено максимальное количество чатов:\n{operators_data['choosen_operators']}",
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
        await state.finish()


@dp.callback_query_handler(Text(equals="chats_off"), state='*')
async def cc_chats_min_mailing_start(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await message.answer("Введите список агентов или нажмите /cancel для отмены действия")
        await DataChats.waiting_for_message_off.set()


@dp.message_handler(state=DataChats.waiting_for_message_off)
async def cc_chats_min_mailing_end(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await state.update_data(choosen_operators=message.text)
        operators_data = await state.get_data()
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(),
                                           f"Выключено максимальное количество чатов:\n{operators_data['choosen_operators']}",
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
        await state.finish()


# ТЕХ СБОЙ
@dp.message_handler(Text(equals="🚧Тех. сбой🚧"))
async def without_puree(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.tech_error,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='tech_error_on'))
async def tech_error_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_tech_error_on,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='tech_error_off'))
async def tech_error_off(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_tech_error_off,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


# ОПЛАТА
@dp.message_handler(Text(equals="💳Оплата💳"))
async def without_puree(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.pay,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='pay_on'))
async def pay_on(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_pay_on,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='pay_off'))
async def pay_off(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.diz_pay_off,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')

    # КУРЬЕРКА


@dp.message_handler(Text(equals="Курьерка"))
async def cour(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Включить макс. кол-во чатов", "Выключить макс. кол-во чатов", "🏠Главное меню🏠"]
    keyboard.add(*buttons)
    await message.answer("Выбери нужное", reply_markup=keyboard)


class DataCour(StatesGroup):
    waiting_for_message_max = State()
    waiting_for_message_min = State()


@dp.message_handler(Text(equals="Включить макс. кол-во чатов"), state="*")
async def max_chats_step_1(message: types.Message):
    get_id = message.from_user.id
    config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    if config.admin in result:
        await message.reply(f"Укажите логины агентов", parse_mode='Markdown')
        await GetDataChatsMax.waiting_for_logins_max.set()


@dp.message_handler(commands="cancel", state="*")
async def mailing_cancel(message: types.Message, state: FSMContext):
    get_id = message.from_user.id
    config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    result = config.cursor.execute(config.find_admin, (get_id,)).fetchone()
    if config.admin in result:
        await bot.send_message(message.chat.id, "Действие отменено", reply_markup=keyboard.monitoring_start, parse_mode="Markdown")
        await state.finish()


@dp.message_handler(state=DataCour.waiting_for_message_max)
async def cour_max_chats_mailing_end(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await state.update_data(choosen_operators=message.text)
        operators_data = await state.get_data()
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(),
                                           f"Включено максимальное количество чатов:\n{operators_data['choosen_operators']}",
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
        await state.finish()


@dp.message_handler(state=GetDataChatsMax.waiting_for_logins_min)
async def max_chats_step_2(message: types.Message, state: FSMContext):
    await state.update_data(logins=message.text, logins_2=message.text)
    get_data = await state.get_data()
    data = get_data['logins'].split()
    data_2 = get_data['logins_2'].split()
    index_state = -1
    for get_data['logins'] in data:
        index_state = index_state + 1
        if index_state < len(data):
            set_chat_max = (1), data[index_state]
            config.cursor.execute(config.update_chat_max, set_chat_max)
            print(config.cursor.execute(config.update_chat_max, set_chat_max))
            config.conn.commit()
        else:
            break
    index_state_2 = -1
    reply = ""
    for get_data['logins_2'] in data_2:
        index_state_2 = index_state_2 + 1
        if index_state_2 < len(data_2):
            config.cursor.execute(config.find_fullname, (data[index_state_2],)).fetchone()
            config.cursor.execute(config.find_username, (data[index_state_2],)).fetchone()
            config.conn.commit()
            for names in config.cursor.execute(config.find_fullname, (data[index_state_2],)).fetchone():
                reply += names + " "
            for telegram in config.cursor.execute(config.find_username, (data[index_state_2],)).fetchone():
                reply += telegram + "\n"
        else:
            break
    reply += f"\n\nИнициатор: @{message.from_user.username}"
    await message.reply(f"Включено максимальное количество чатов:\n\n{reply}", parse_mode='Markdown')
    await state.finish()


@dp.message_handler(state=GetDataChatsMax.waiting_for_logins_max)
async def max_chats_step_0(message: types.Message, state: FSMContext):
    print("Start")
    await state.update_data(logins=message.text, logins_2=message.text)
    get_data = await state.get_data()
    data = get_data['logins'].split()
    data_2 = get_data['logins_2'].split()
    index_state = -1
    receive_users, block_users = 0, 0
    index_role = 0
    message_id_list = []
    while index_role < 3:
        print(index_role)
        config.cursor.execute(config.find_id_role, (config.roles[index_role],)).fetchone()
        print(config.cursor.execute(config.find_id_role, (config.roles[index_role],)).fetchone())
        for ID in config.cursor.execute(config.find_id_role, (config.roles[index_role],)).fetchone():
            if ID is not None:
                print(ID)
                message_id_list.append(ID)
        index_role += 1
    for get_data['logins'] in data:
        index_state = index_state + 1
        if index_state < len(data):
            set_chat_max = (1), data[index_state]
            config.cursor.execute(config.update_chat_max, set_chat_max)
            config.conn.commit()
            receive_users += 1
        else:
            block_users += 1
    index_state_2 = -1
    reply = ""
    for get_data['logins_2'] in data_2:
        index_state_2 = index_state_2 + 1
        if index_state < len(data_2):
            config.cursor.execute(config.find_fullname, (data[index_state_2],)).fetchone() # сделать обработку исключений
            config.cursor.execute(config.find_username, (data[index_state_2],)).fetchone()
            config.cursor.execute(config.find_id_staff, (data[index_state_2],)).fetchone()
            config.conn.commit()
            for names in config.cursor.execute(config.find_fullname, (data[index_state_2],)).fetchone():
                reply += names + " "
            for telegram in config.cursor.execute(config.find_username, (data[index_state_2],)).fetchone():
                reply += telegram + "\n"
        else:
            break
    reply += f"\n\nИнициатор: @{message.from_user.username}"
    for ID in message_id_list:
        print("Sending...")
        await bot.send_message(ID, f"Включено максимальное количество чатов:\n\n{reply}", parse_mode='Markdown')
    await state.finish()


@dp.message_handler(Text(equals="Выключить макс. кол-во чатов"), state='*')
async def cour_min_chats_mailing_start(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await message.answer("Введите список агентов или нажмите /cancel для отмены действия")
        await DataCour.waiting_for_message_min.set()


@dp.message_handler(state=DataCour.waiting_for_message_min)
async def cour_min_chats_mailing_end(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await state.update_data(choosen_operators=message.text)
        operators_data = await state.get_data()
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(),
                                           f"Выключено максимальное количество чатов:\n{operators_data['choosen_operators']}",
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
        await state.finish()


@dp.message_handler(Text(equals="Некорректные статусы"))
async def incorrect_status(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Выбери нужное",
                               reply_markup=keyboard.incorrect_status_panel,
                               parse_mode='Markdown')


@dp.callback_query_handler(Text(equals="chime"))
async def incorrect_status_chime(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.incorrect_status_chime,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals="before_lunch"))
async def incorrect_status_before_lunch(call: types.CallbackQuery):
    message = call.message
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(), text=macros.incorrect_status_before_lunch,
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили сообщение: *{receive_users}*\n",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')


@dp.message_handler(Text(equals="✉️Рассылка✉️"))
async def cour(message: types.Message):
    keyboard.mailing = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["На КЦ", "На курьерку", "Всем", "🏠Главное меню🏠"]
    keyboard.mailing.add(*buttons)
    await message.answer("Выбери нужное", reply_markup=keyboard.mailing)


class DataMailing(StatesGroup):
    waiting_for_message_cc = State()
    waiting_for_message_cour = State()
    waiting_for_message_all = State()


@dp.message_handler(Text(equals="На КЦ"), state='*')
async def mailing_wait_cc(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await message.answer("Введите сообщение или нажмите /cancel для отмены действия")
        await DataMailing.waiting_for_message_cc.set()


@dp.message_handler(state=DataMailing.waiting_for_message_cc)
async def mailing_start_cc(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await state.update_data(msg=message.text)
        message_data = await state.get_data()
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(),
                                           f"{message_data['msg']}",
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
        await state.finish()


@dp.message_handler(Text(equals="На курьерку"), state='*')
async def mailing_wait_cour(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await message.answer("Введите список агентов или нажмите /cancel для отмены действия")
        await DataMailing.waiting_for_message_cour.set()


@dp.message_handler(state=DataMailing.waiting_for_message_cour)
async def mailing_start_cour(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await state.update_data(msg=message.text)
        message_data = await state.get_data()
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(),
                                           f"{message_data['msg']}",
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
        await state.finish()


@dp.message_handler(Text(equals="Всем"), state='*')
async def mailing_wait_all(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await message.answer("Введите список агентов или нажмите /cancel для отмены действия")
        await DataMailing.waiting_for_message_all.set()


@dp.message_handler(state=DataMailing.waiting_for_message_all)
async def mailing_start_all(message: types.Message, state: FSMContext):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await state.update_data(msg=message.text)
        message_data = await state.get_data()
        await bot.send_message(message.chat.id, f"*Рассылка началась \nБот оповестит когда рассылку закончит*",
                               parse_mode='Markdown')
        receive_users, block_users = 0, 0
        for userID in BotUsers:
            botUser = BotUsers[userID]
            if botUser.get_user_type() == BotUserType.USER_TYPE_COURIER or botUser.get_user_type() == BotUserType.USER_TYPE_CC or botUser.get_user_type() == BotUserType.USER_TYPE_MONITORING or botUser.get_user_type() == BotUserType.USER_TYPE_QA or botUser.get_user_type() == BotUserType.USER_TYPE_TL:  # добавлять через or
                try:
                    await bot.send_message(botUser.get_user_id(),
                                           f"{message_data['msg']}",
                                           parse_mode='Markdown')
                    receive_users += 1
                except:
                    block_users += 1
        await bot.send_message(message.chat.id, f"*Рассылка была завершена *\n"
                                                f"получили: *{receive_users}*\n"
                                                f"не получили: *{block_users}*",
                               reply_markup=keyboard.monitoring_start, parse_mode='Markdown')
        await state.finish()


# ГЛАВНОЕ МЕНЮ
@dp.message_handler(Text(equals="🏠Главное меню🏠"))
async def main_menu(message: types.Message):
    user = BotUsers.get(message.chat.id)
    if user.is_admin():
        await bot.send_message(message.chat.id, text="Главное меню", reply_markup=keyboard.monitoring_start,
                               parse_mode='Markdown')
    if not user.is_admin():
        await bot.send_message(message.chat.id, text="Главное меню", reply_markup=keyboard.CC_start,
                               parse_mode='Markdown')


# КНОПКИ ДЛЯ L1
@dp.message_handler(commands="scheduleMonitoring")
@dp.message_handler(Text(equals="📅Расписание мониторинга📅"))
async def scheduleMonitoring(message: types.Message):
    reply = "Расписание работы отдела мониторинга:\n"
    data = google.getDataFromExcelTable()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        userColor = userData["color"]
        reply += userName + " " + userInfo
        if config.isColorEquals(userColor, config.colorCalls):
            reply += " *   👉Calls* "
        elif config.isColorEquals(userColor, config.colorChatterBox):
            reply += " *   👉ChatterBox/Tickets* "
        elif config.isColorEquals(userColor, config.colorWebim):
            reply += " *   👉Feedbacks/L2️* "
        reply += "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelMonitoring, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='infoMonitoring'))
async def infoMonitoring(call: types.CallbackQuery):
    message = call.message
    await bot.send_message(message.chat.id, text=macros.info_Monitoring, parse_mode='Markdown')


@dp.message_handler(commands="scheduleСС")
@dp.message_handler(Text(equals="📅Расписание КЦ📅"))
async def scheduleTL(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.scheduleСС, reply_markup=keyboard.scheduleСС_panel, parse_mode='Markdown')


@dp.message_handler(Text(equals="Все TL"))
async def scheduleTL(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        userColor = userData["color"]
        reply += userName + " *//* " + userInfo
        if config.Donov in userName:
            break
        elif config.isColorEquals(userColor, config.colorDutyMorning):
            reply += " * // 👉Утренний мониторинг* "
        elif config.isColorEquals(userColor, config.colorDutyEvening):
            reply += " * // 👉Вечерний мониторинг* "
        elif config.isColorEquals(userColor, config.colorUnderworking):
            reply += " * // 👉Подработки️* "
        elif config.isColorEquals(userColor, config.colorLearning):
            reply += " * // 👉Кейсы+Обучение* "
        reply += "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="ЗРКЦ"))
async def scheduleZRKC(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.ZRKC_all in userName:
            reply += userName + "\n"
        elif config.ZRKC in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals='infoTL'))
async def infoTL(call: types.CallbackQuery):
    message = call.message
    await bot.send_message(message.chat.id, text=macros.info_TL, parse_mode='Markdown')


@dp.message_handler(Text(equals="🧑‍💻Дежурные TL🧑‍💻"))
async def scheduleTLduty(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        userColor = userData["color"]
        if userColor != config.nocolor:
            if config.isColorEquals(userColor, config.colorDutyMorning):
                reply += config.emojiTL + userName + " *//* " + userInfo + " * // 👉Утренний мониторинг* " + "\n\n"
            elif config.isColorEquals(userColor, config.colorDutyEvening):
                reply += config.emojiTL + userName + " *//* " + userInfo + " * // 👉Вечерний мониторинг* " + "\n\n"
            elif config.isColorEquals(userColor, config.colorUnderworking):
                reply += config.emojiTL + userName + " *//* " + userInfo + " * // 👉Подработки️* " + "\n\n"
            elif config.isColorEquals(userColor, config.colorLearning):
                reply += config.emojiTL + userName + " *//* " + userInfo + " * // 👉Кейсы+Обучение* " + "\n\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Клиентские звонки"))
async def scheduleTLClientCalls(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.ClientCalls in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Ресторанные звонки"))
async def scheduleTLRestCalls(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.RestCalls in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Клиентские чаты и тикеты"))
async def scheduleTLСlientChats(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.ClientChats in userName or config.ClientChatsAndTickets in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Ресторанные чаты и тикеты"))
async def scheduleTLRestChats(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.RestChats in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Курьерские звонки"))
async def scheduleTLCourCalls(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.CourCalls in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Курьерские чаты"))
async def scheduleTLCourChats(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.CourChats in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL L2"))
async def scheduleTLL2(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.L2 in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Проактив"))
async def scheduleTLProactive(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.ProActive in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Ночной"))
async def scheduleTLNight(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.Night in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')


@dp.message_handler(Text(equals="TL Исходящие звонки"))
async def scheduleTLOutgoingCalls(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        print(userInfo)
        if len(userInfo) < 6:
            print("empty")
            await bot.send_message(message.chat.id, text=macros.missing_reply, reply_markup=keyboard.CC_start,
                                   parse_mode='Markdown')
            break
        else:
            if config.Donov in userName:
                print("Donov")
                break
            elif config.OutgoingCalls in userName:
                print("start")
                reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
            else:
                print(321)
                await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')
            break


@dp.message_handler(Text(equals="TL Ретейл тикеты"))
async def scheduleTLRetailTickets(message: types.Message):
    reply = "Расписание работы TL:\n"
    data = GDParsingTL.getDataFromExcelTableTL()
    for name in data:
        userName = name
        userData = data[name]
        userInfo = userData["data"]
        if config.Donov in userName:
            break
        elif config.RetailTickets in userName:
            reply += config.emojiTL + userName + " *//* " + userInfo + "\n"
    await message.reply(reply, reply_markup=keyboard.info_panelTL, parse_mode='Markdown')



@dp.message_handler(Text(equals="Доступ"))
async def access(message: types.Message):
    await bot.send_message(message.chat.id, text="Обратись к любому тимлидеру. Расписание TL можешь получить нажав на команду /scheduleTL", reply_markup=keyboard.CC_start, parse_mode='Markdown')


# ПОМОЩЬ L1
@dp.message_handler(filters.Text(contains=['интернет', "наушник", 'доступ'], ignore_case=True))
async def headphones(message: types.Message):
    await bot.send_message(message.chat.id, text="Интернет и наушники?",
                           reply_markup=keyboard.headphones, parse_mode='Markdown')


@dp.message_handler(filters.Text(contains='Наушники', ignore_case=True))
async def headphones(message: types.Message):
    await bot.send_message(message.chat.id, text="Проблема фиксируется во всех звонках или через раз?",
                           reply_markup=keyboard.headphones, parse_mode='Markdown')


@dp.message_handler(filters.Text(contains='интернет', ignore_case=True))
async def headphones(message: types.Message):
    await bot.send_message(message.chat.id, text="Интернет?",
                           reply_markup=keyboard.headphones, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals="hp.yes"))
async def yes(call: types.CallbackQuery):
    message = call.message
    await bot.send_message(message.chat.id,
                           text="Хмм, попробуй проверить настройки звука системы и Oktell, выбери нужное устройство и проверь всё ли теперь в порядке?🤔",
                           reply_markup=keyboard.CC_start, parse_mode='Markdown')


@dp.callback_query_handler(Text(equals="hp.no"))
async def no(call: types.CallbackQuery):
    message = call.message
    await bot.send_message(message.chat.id,
                           text="Давай проверим скорость твоего интернета, заходи на 2ip.ru и запускай тест. \nСкриншот результата отправь в форме моим коллегам, они всё проверят, вот ссылка: https://forms.yandex-team.ru/surveys/65718/",
                           reply_markup=keyboard.CC_start, parse_mode='Markdown')


user_data = {}


@dp.message_handler(lambda message: message.text == "Подработки")
async def underworking(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Менее 4 ч.", "4-5 ч.", "6 ч.", "7-8 ч.", "9-11 ч.", "12-14 ч.", "15 ч. и более",
               "🏠Главное меню🏠"]
    keyboard.add(*buttons)
    await message.answer("Выбери количество часов", reply_markup=keyboard)


@dp.message_handler(Text(equals="Менее 4 ч."))
async def underworking_loss(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.underworking_loss, reply_markup=keyboard.start,
                           parse_mode='Markdown')


@dp.message_handler(Text(equals="4-5 ч."))
async def underworking_4_5_hours(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.underworking_4_5_hours, reply_markup=keyboard.start,
                           parse_mode='Markdown')


@dp.message_handler(Text(equals="6 ч."))
async def underworking_6_hours(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.underworking_6_hours, reply_markup=keyboard.start,
                           parse_mode='Markdown')


@dp.message_handler(Text(equals="7-8 ч."))
async def underworking_7_8_hours(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.underworking_7_8_hours, reply_markup=keyboard.start,
                           parse_mode='Markdown')


@dp.message_handler(Text(equals="9-11 ч."))
async def underworking_9_11_hours(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.underworking_9_11_hours, reply_markup=keyboard.start,
                           parse_mode='Markdown')


@dp.message_handler(Text(equals="12-14 ч."))
async def underworking_12_14_hours(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.underworking_12_14_hours, reply_markup=keyboard.start,
                           parse_mode='Markdown')


@dp.message_handler(Text(equals="15 ч. и более"))
async def underworking_15_and_more_hours(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.underworking_15_and_more_hours, reply_markup=keyboard.start,
                           parse_mode='Markdown')


# РАЗДЕЛ С ПРОБЛЕМАМИ
@dp.message_handler(Text(equals="Oktell"))
async def problems_oktell_panel(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_oktell_panel)


@dp.message_handler(Text(equals="ChatterBox"))
async def problems_chatterbox(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_chatterbox_panel)


@dp.message_handler(Text(equals="Webim"))
async def problems_webim(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_webim_panel)


@dp.message_handler(Text(equals="Оборудование"))
async def problems_devices(message: types.Message):
    await message.answer(text=macros.problems_oktell_error_panel_2_macr, reply_markup=keyboard.problems_devices_panel)


@dp.message_handler(Text(equals="🔐Доступы🔐"))
async def problems_access(message: types.Message):
    await message.answer("Проблемы с доступами решаются через Тимлидеров, обратись к любому на смене",
                         reply_markup=keyboard.problems_panel)


@dp.message_handler(Text(equals="Админка"))
async def admin_panel(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.admin_panel)


@dp.message_handler(Text(equals="Приложения"))
async def apps_panel(message: types.Message):
    await message.answer("Выбери тип приложения, в котором что-то не так", reply_markup=keyboard.problems_apps_panel)


@dp.message_handler(Text(equals="Логика"))
async def logic_panel(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_panel)


@dp.message_handler(Text(equals="Компендиум"))
async def compendium_panel(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_panel)


@dp.message_handler(Text(equals="problems_panel_back"))
async def problems_panel_back(message):
    await bot.send_message(message.chat.id,
                           text="Попробуем ещё раз. С чем связана проблема?",
                           reply_markup=keyboard.CC_start, parse_mode='Markdown')


@dp.message_handler(Text(equals="Клиентское приложение"))
async def app_panel_client(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_apps_client_panel)


@dp.message_handler(Text(equals="Ресторанное приложение"))
async def app_panel_rest(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_apps_rest_panel)


@dp.message_handler(Text(equals="Курьерское приложение"))
async def app_panel_cour(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_apps_cour_panel)


######################################################################################
### Oktell

@dp.message_handler(Text(equals="Запуск/установка/обновление"))
async def problems_oktell_panel_instal(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_oktell_instal_panel)


@dp.message_handler(Text(equals="Некорректная работа"))
async def problems_oktell_panel_work(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_oktell_work_panel)


@dp.message_handler(Text(equals="Принимает звонок и меняет статус на \"Отсутствующий\""))
async def problems_oktell_work_panel_1(message: types.Message):
    await bot.send_photo(message.chat.id, open("Yandex Oktell VPN bat.png", 'rb'))
    await message.answer(text=macros.problems_oktell_work_panel_1_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')



@dp.message_handler(Text(equals="Меня не слышат/слышно"))
async def problems_oktell_work_panel_2(message: types.Message):
    await message.answer(text=macros.problems_oktell_work_panel_2_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Проблемы с карточкой"))
async def problems_oktell_work_panel_3(message: types.Message):
    await message.answer(text=macros.problems_oktell_work_panel_3_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Звонок не принимается"))
async def problems_oktell_work_panel_4(message: types.Message):
    await message.answer(text=macros.problems_oktell_work_panel_4_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Звонок принимается очень быстро"))
async def problems_oktell_work_panel_5(message: types.Message):
    await message.answer(text=macros.problems_oktell_work_panel_5_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не могу дозвониться до L2"))
async def problems_oktell_work_panel_6(message: types.Message):
    await message.answer(text=macros.problems_oktell_work_panel_6_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Появляется ошибка"))
async def problems_oktell_error_panel(message: types.Message):
    await message.answer("С чем связана проблема?", reply_markup=keyboard.problems_oktell_error_panel)


@dp.message_handler(Text(equals="Отсутствует доступ к собственному каталогу для записи"))
async def problems_oktell_error_panel_1(message: types.Message):
    await message.answer(text=macros.problems_oktell_error_panel_1_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Пользователь уже зарегистрирован"))
async def problems_oktell_error_panel_2(message: types.Message):
    await message.answer(text=macros.problems_oktell_error_panel_2_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Пользователь не найден"))
async def problems_oktell_error_panel_3(message: types.Message):
    await message.answer(text=macros.problems_oktell_error_panel_3_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Программа уже запущена"))
async def problems_oktell_error_panel_4(message: types.Message):
    await message.answer(text=macros.problems_oktell_error_panel_4_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Сервис автодозвона"))
async def problems_oktell_error_panel_5(message: types.Message):
    await message.answer(text=macros.problems_oktell_error_panel_5_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Свободное пространство на диске заканчивается"))
async def problems_oktell_error_panel_6(message: types.Message):
    await message.answer(text=macros.problems_oktell_error_panel_6_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Инструкция по установке"))
async def problems_oktell_panel_instal(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_oktell_instal_instr_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Oktell не открывается, циклично крутится курсор"))
async def problems_oktell_panel_work(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_oktell_instal_close_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не устанавливаются обновления"))
async def problems_oktell_panel_update(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_oktell_instal_update_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


#############
### Крутилка

@dp.message_handler(Text(equals="Не поступают чаты в крутилке"))
async def problems_chatterbox_panel_1(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_chatterbox_panel_1_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Отображается некорректное кол-во тикетов в линиях"))
async def problems_chatterbox_panel_2(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_chatterbox_panel_2_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не поступают тикеты в нужную линию"))
async def problems_chatterbox_panel_3(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_chatterbox_panel_3_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Обращения (чаты/тикеты) приходят с опозданием"))
async def problems_chatterbox_panel_4(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_chatterbox_panel_4_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Ошибка в тикете"))
async def problems_chatterbox_panel_5(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_chatterbox_panel_5_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


#############
### Webim

@dp.message_handler(Text(equals="Не приходят сообщения от пользователей"))
async def problems_webim_panel_1(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_webim_panel_1_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не отправляется сообщение пользователю"))
async def problems_webim_panel_2(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_webim_panel_2_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не закрывается чат"))
async def problems_webim_panel_3(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_webim_panel_3_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не открываются вложения/фотографии"))
async def problems_webim_panel_4(message: types.Message):
    await bot.send_photo(message.chat.id, open("Advertisement off.jpg", 'rb'))
    await bot.send_message(message.chat.id, text=macros.problems_webim_panel_4_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')



@dp.message_handler(Text(equals='Не загружается вкладка \"Рабочее место\"'))
async def problems_webim_panel_5(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_webim_panel_5_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не может войти в аккаунт"))
async def problems_webim_panel_6(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_webim_panel_6_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Причины обращений"))
async def problems_webim_panel_7(message: types.Message):
    await bot.send_message(message.chat.id, text=macros.problems_webim_panel_6_macr,
                           reply_markup=keyboard.ticket, parse_mode='Markdown')


#############
### Админка

@dp.message_handler(Text(equals="Не загружается страница/выдает ошибку 504"))
async def problems_admin_panel_1_macr(message: types.Message):
    await message.answer(text=macros.problems_admin_panel_1_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Заказы не поступают в ресторан (приложение/вендорка)"))
async def problems_admin_panel_2_macr(message: types.Message):
    await message.answer(text=macros.problems_admin_panel_2_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Заказы не поступают в ресторан (интеграция)"))
async def problems_admin_panel_3_macr(message: types.Message):
    await message.answer(text=macros.problems_admin_panel_3_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не сохраняются данные об изменении заказа"))
async def problems_admin_panel_4_macr(message: types.Message):
    await message.answer(text=macros.problems_admin_panel_4_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Пропала история заказов/общие изменения"))
async def problems_admin_panel_5_macr(message: types.Message):
    await message.answer(text=macros.problems_admin_panel_5_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Проблема с выдачей компенсации (Возникшие проблемы)"))
async def problems_admin_panel_6_macr(message: types.Message):
    await message.answer(text=macros.problems_admin_panel_6_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Курьеры Я.Такси/наши курьеры не назначаются на заказ"))
async def problems_admin_panel_7_macr(message: types.Message):
    await message.answer(text=macros.problems_admin_panel_7_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


################################################################################
### Приложение - Клиенты

@dp.message_handler(Text(equals="Не может изменить адрес"))
async def problems_apps_client_panel_1_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_client_panel_1_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не проходит оплата/не может перейти к оплате"))
async def problems_apps_client_panel_2_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_client_panel_2_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не отображаются рестораны"))
async def problems_apps_client_panel_3_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_client_panel_3_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="При вводе адреса не отображаются рестораны"))
async def problems_apps_client_panel_4_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_client_panel_4_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не загружается список ресторанов (висит колесо загрузки)"))
async def problems_apps_client_panel_5_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_client_panel_5_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Промокоды не срабатывают/не применяются"))
async def problems_apps_client_panel_6_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_client_panel_6_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


###########################
### Приложение - Рестораны

@dp.message_handler(Text(equals="Не могут проставить стоп-лист"))
async def problems_apps_rest_panel_1_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_rest_panel_1_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не могут редактировать меню"))
async def problems_apps_rest_panel_2_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_rest_panel_2_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не приходят уведомления о заказах"))
async def problems_apps_rest_panel_3_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_rest_panel_3_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не могут войти в приложение"))
async def problems_apps_rest_panel_4_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_rest_panel_4_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


###########################
### Приложение - Курьеры

@dp.message_handler(Text(equals="Не могут выбирать слоты"))
async def problems_apps_cour_panel_1_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_cour_panel_1_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не могут проставить статус в приложениии"))
async def problems_apps_cour_panel_2_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_cour_panel_2_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не может начать слот"))
async def problems_apps_cour_panel_3_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_cour_panel_3_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Не идёт рассчёт времени маршрута"))
async def problems_apps_cour_panel_4_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_cour_panel_4_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Проблема с Яндекс.Про"))
async def problems_apps_cour_panel_5_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_cour_panel_5_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


@dp.message_handler(Text(equals="Некорректные отчёты/не пришли отчёты"))
async def problems_apps_cour_panel_6_macr(message: types.Message):
    await message.answer(text=macros.problems_apps_cour_panel_6_macr,
                         reply_markup=keyboard.ticket, parse_mode='Markdown')


#############
### Логика

@dp.message_handler(Text(equals="Логика"))
async def problems_logic(message: types.Message):
    await message.answer(text=macros.problems_logic_macr, reply_markup=keyboard.problems_panel, parse_mode='Markdown')


#############
### Эскалация в тикет

@dp.callback_query_handler(Text(equals='ticket'))
async def ticket(call: types.CallbackQuery):
    await call.answer(text=macros.ticket, show_alert=True)


if __name__ == '__main__':
    executor.start_polling(dp)


######################################################################
#####################################################################РАБОЧИЙ КОД НА ЭТОМ ЗАКОНЧЕН
#####################################################################
