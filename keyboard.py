from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

###################################################### ПАНЕЛИ КНОПОК
start = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
CC_start = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
CC_COUR_start = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
monitoring_start = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
QA_start = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
TL_start = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
###
diz_p = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
cc_p = types.ReplyKeyboardMarkup(resize_keyboard=True)
###
problems_panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
devices_panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_oktell_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_chatterbox = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_webim = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_devices = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_admin_panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_apps = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_logic = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_compendium = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_oktell_instal_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_oktell_work_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_oktell_error_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
admin_panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_apps_panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
problems_apps_client_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_apps_rest_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_apps_cour_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_chatterbox_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_webim_panel = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
problems_devices_panel = types.ReplyKeyboardMarkup(resize_keyboard=True)
scheduleСС_panel = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
###################################################### КНОПКИ
CC = types.KeyboardButton("📞КЦ L1📞")
CC_Cour = types.KeyboardButton("🚴🏻КЦ Курьерка🚴🏻")
Monitoring = types.KeyboardButton("🖥Monitoring🖥")
main_menu = types.KeyboardButton("🏠Главное меню🏠")
###
dateMonitoring = types.KeyboardButton("📅Расписание мониторинга📅")
dateTL = types.KeyboardButton("📅Расписание КЦ📅")
diz_b = types.KeyboardButton("🧯Дизастеры🧯")
mailing = types.KeyboardButton("✉️Рассылка✉️")
role = types.KeyboardButton("🔄Сменить роль🔄")
###
schedule_duty_TL = types.KeyboardButton("🧑‍💻Дежурные TL🧑‍💻")
schedule_all = types.KeyboardButton("Все TL")
schedule_ZRKC = types.KeyboardButton("ЗРКЦ")
schedule_client_calls = types.KeyboardButton("TL Клиентские звонки")
schedule_client_chats_and_tickets = types.KeyboardButton("TL Клиентские чаты и тикеты")
schedule_rest_calls = types.KeyboardButton("TL Ресторанные звонки")
schedule_rest_chats_and_tickets = types.KeyboardButton("TL Ресторанные чаты и тикеты")
schedule_cour_calls = types.KeyboardButton("TL Курьерские звонки")
schedule_cour_chats = types.KeyboardButton("TL Курьерские чаты")
schedule_night = types.KeyboardButton("TL Ночной")
schedule_outgoing_calls = types.KeyboardButton("TL Исходящие звонки")
schedule_proactive = types.KeyboardButton("TL Проактив")
schedule_L2 = types.KeyboardButton("TL L2")
schedule_retail_tickets = types.KeyboardButton("TL Ретейл тикеты")
###
problems = types.KeyboardButton("Проблемы")
problems_oktell = types.KeyboardButton("Oktell")
problems_chatterbox = types.KeyboardButton("ChatterBox")
problems_webim = types.KeyboardButton("Webim")
problems_devices = types.KeyboardButton("Оборудование")
problems_access = types.KeyboardButton("🔐Доступы🔐")
problems_admin = types.KeyboardButton("Админка")
problems_apps = types.KeyboardButton("Приложения")
problems_logic = types.KeyboardButton("Логика")
problems_compendium = types.KeyboardButton("Компендиум")
### Oktell
problems_oktell_instal = types.KeyboardButton("Запуск/установка/обновление")
problems_oktell_work = types.KeyboardButton("Некорректная работа")
problems_oktell_error = types.KeyboardButton("Появляется ошибка")
### Oktell - Запуск/установка/обновление
problems_oktell_instal_instr = types.KeyboardButton("Инструкция по установке")
problems_oktell_instal_close = types.KeyboardButton("Oktell не открывается, циклично крутится курсор")
problems_oktell_instal_update = types.KeyboardButton("Не устанавливаются обновления")
### Oktell - Некорректная работа
problems_oktell_work_panel_1 = types.KeyboardButton("Принимает звонок и меняет статус на \"Отсутствующий\"")
problems_oktell_work_panel_2 = types.KeyboardButton("Меня не слышат/слышно")
problems_oktell_work_panel_3 = types.KeyboardButton("Проблемы с карточкой")
problems_oktell_work_panel_4 = types.KeyboardButton("Звонок не принимается")
problems_oktell_work_panel_5 = types.KeyboardButton("Звонок принимается очень быстро")
problems_oktell_work_panel_6 = types.KeyboardButton("Не могу дозвониться до L2")
### Oktell - Появляется ошибка
problems_oktell_error_panel_1 = types.KeyboardButton("Отсутствует доступ к собственному каталогу для записи")
problems_oktell_error_panel_2 = types.KeyboardButton("Пользователь уже зарегистрирован")
problems_oktell_error_panel_3 = types.KeyboardButton("Пользователь не найден")
problems_oktell_error_panel_4 = types.KeyboardButton("Программа уже запущена")
problems_oktell_error_panel_5 = types.KeyboardButton("Сервис автодозвона")
problems_oktell_error_panel_6 = types.KeyboardButton("Свободное пространство на диске заканчивается")
###
### Крутилка
problems_chatterbox_panel_1 = types.KeyboardButton("Не поступают чаты в крутилке")
problems_chatterbox_panel_2 = types.KeyboardButton("Отображается некорректное кол-во тикетов в линиях")
problems_chatterbox_panel_3 = types.KeyboardButton("Не поступают тикеты в нужную линию")
problems_chatterbox_panel_4 = types.KeyboardButton("Обращения (чаты/тикеты) приходят с опозданием")
problems_chatterbox_panel_5 = types.KeyboardButton("Ошибка в тикете")
###
### Webim
problems_webim_panel_1 = types.KeyboardButton("Не приходят сообщения от пользователей")
problems_webim_panel_2 = types.KeyboardButton("Не отправляется сообщение пользователю")
problems_webim_panel_3 = types.KeyboardButton("Не закрывается чат")
problems_webim_panel_4 = types.KeyboardButton("Не открываются вложения/фотографии")
problems_webim_panel_5 = types.KeyboardButton("Не загружается вкладка \"Рабочее место\"")
problems_webim_panel_6 = types.KeyboardButton("Не может войти в аккаунт")
problems_webim_panel_7 = types.KeyboardButton("Причины обращений")
###
### Админка
problems_admin_panel_1 = types.KeyboardButton("Не загружается страница/выдает ошибку 504")
problems_admin_panel_2 = types.KeyboardButton("Заказы не поступают в ресторан (приложение/вендорка)")
problems_admin_panel_3 = types.KeyboardButton("Заказы не поступают в ресторан (интеграция)")
problems_admin_panel_4 = types.KeyboardButton("Не сохраняются данные об изменении заказа")
problems_admin_panel_5 = types.KeyboardButton("Пропала история заказов/общие изменения")
problems_admin_panel_6 = types.KeyboardButton("Проблема с выдачей компенсации (Возникшие проблемы)")
problems_admin_panel_7 = types.KeyboardButton("Курьеры Я.Такси/наши курьеры не назначаются на заказ")
###
### Приложение
problems_apps_client = types.KeyboardButton("Клиентское приложение")
problems_apps_rest = types.KeyboardButton("Ресторанное приложение")
problems_apps_cour = types.KeyboardButton("Курьерское приложение")
###
problems_apps_client_panel_1 = types.KeyboardButton("Не может изменить адрес")
problems_apps_client_panel_2 = types.KeyboardButton("Не проходит оплата/не может перейти к оплате")
problems_apps_client_panel_3 = types.KeyboardButton("Не отображаются рестораны")
problems_apps_client_panel_4 = types.KeyboardButton("При вводе адреса не отображаются рестораны")
problems_apps_client_panel_5 = types.KeyboardButton("Не загружается список ресторанов (висит колесо загрузки)")
problems_apps_client_panel_6 = types.KeyboardButton("Промокоды не срабатывают/не применяются")
###
problems_apps_rest_panel_1 = types.KeyboardButton("Не могут проставить стоп-лист")
problems_apps_rest_panel_2 = types.KeyboardButton("Не могут редактировать меню")
problems_apps_rest_panel_3 = types.KeyboardButton("Не приходят уведомления о заказах")
problems_apps_rest_panel_4 = types.KeyboardButton("Не могут войти в приложение")
###
problems_apps_cour_panel_1 = types.KeyboardButton("Не могут выбирать слоты")
problems_apps_cour_panel_2 = types.KeyboardButton("Не могут проставить статус в приложениии")
problems_apps_cour_panel_3 = types.KeyboardButton("Не может начать слот")
problems_apps_cour_panel_4 = types.KeyboardButton("Не идёт рассчёт времени маршрута")
problems_apps_cour_panel_5 = types.KeyboardButton("Проблема с Яндекс.Про")
problems_apps_cour_panel_6 = types.KeyboardButton("Некорректные отчёты/не пришли отчёты")
###

incorrect_status = types.KeyboardButton("Некорректные статусы")
underworking = types.KeyboardButton("Подработки")
ticket = types.KeyboardButton("Не помогло?")
chose_role = types.KeyboardButton("Выбор роли")
###
cc_b = types.KeyboardButton("КЦ")
cc_calls = types.KeyboardButton("📞Звонки📞")
cc_calls_l2 = types.KeyboardButton("📞Звонки L2📞")
cc_calls_l2_night = types.KeyboardButton("🌙Звонки L2 Ночь🌙")
cc_calls_l2_stop = types.KeyboardButton("🔥L2 — STOP🔥")
cc_chats = types.KeyboardButton("💬Чаты💬")
cc_tech_error = types.KeyboardButton("🚧Тех. сбой🚧")
cc_pay = types.KeyboardButton("💳Оплата💳")
cc_chatterbox_crit = types.KeyboardButton("💻ChatterBox Crit💻")
###
cour = types.KeyboardButton("Курьерка")
cour_max = types.KeyboardButton("Включить макс. кол-во чатов")
cour_min = types.KeyboardButton("Выключить макс. кол-во чатов")
###################################################### ДОБАВЛЕНИЕ КНОПОК НА ПАНЕЛИ
start.add(CC, CC_Cour, Monitoring)
CC_start.add(dateMonitoring, dateTL, problems, underworking, role)
CC_COUR_start.add(dateMonitoring, dateTL, problems, underworking, role)
QA_start.add(dateMonitoring, dateTL, problems, underworking)
TL_start.add(dateMonitoring,schedule_duty_TL, dateTL, problems, underworking)
monitoring_start.add(diz_b, mailing, schedule_duty_TL, dateMonitoring, dateTL, role)
scheduleСС_panel.add(schedule_all, schedule_ZRKC, schedule_client_calls, schedule_client_chats_and_tickets, schedule_rest_calls, schedule_rest_chats_and_tickets, schedule_cour_calls, schedule_cour_chats, schedule_night, schedule_L2, schedule_retail_tickets, schedule_outgoing_calls, schedule_proactive, main_menu)
diz_p.add(cc_b, cour, incorrect_status, main_menu)
cc_p.add(cc_calls, cc_calls_l2, cc_calls_l2_night, cc_calls_l2_stop, cc_chats, cc_tech_error, cc_pay, cc_chatterbox_crit, main_menu)
problems_panel.add(problems_oktell, problems_chatterbox, problems_webim, problems_devices, problems_access, problems_admin, problems_apps, problems_logic, problems_compendium,  main_menu)
problems_oktell_panel.add(problems_oktell_instal, problems_oktell_work, problems_oktell_error, main_menu)
problems_oktell_instal_panel.add(problems_oktell_instal_instr, problems_oktell_instal_close, problems_oktell_instal_update, main_menu)
problems_oktell_work_panel.add(problems_oktell_work_panel_1, problems_oktell_work_panel_2, problems_oktell_work_panel_3, problems_oktell_work_panel_4, problems_oktell_work_panel_5, problems_oktell_work_panel_6, main_menu)
problems_oktell_error_panel.add(problems_oktell_error_panel_1, problems_oktell_error_panel_2, problems_oktell_error_panel_3, problems_oktell_error_panel_4, problems_oktell_error_panel_5, problems_oktell_error_panel_6, main_menu)
problems_chatterbox_panel.add(problems_chatterbox_panel_1, problems_chatterbox_panel_2, problems_chatterbox_panel_3, problems_chatterbox_panel_4, problems_chatterbox_panel_5, main_menu)
problems_webim_panel.add(problems_webim_panel_1, problems_webim_panel_2, problems_webim_panel_3, problems_webim_panel_4, problems_webim_panel_5, problems_webim_panel_6, problems_webim_panel_7, main_menu)
admin_panel.add(problems_admin_panel_1, problems_admin_panel_2, problems_admin_panel_3, problems_admin_panel_4, problems_admin_panel_5, problems_admin_panel_6, problems_admin_panel_7, main_menu)
problems_apps_panel.add(problems_apps_client, problems_apps_rest, problems_apps_cour, main_menu)
problems_apps_client_panel.add(problems_apps_client_panel_1, problems_apps_client_panel_2, problems_apps_client_panel_3, problems_apps_client_panel_4, problems_apps_client_panel_5, problems_apps_client_panel_6, main_menu)
problems_apps_rest_panel.add(problems_apps_rest_panel_1, problems_apps_rest_panel_2, problems_apps_rest_panel_3, problems_apps_rest_panel_4, main_menu)
problems_apps_cour_panel.add(problems_apps_cour_panel_1, problems_apps_cour_panel_2, problems_apps_cour_panel_3, problems_apps_cour_panel_4, problems_apps_cour_panel_5, problems_apps_cour_panel_6, main_menu)
############################################################################################################
on = f'🟢 Включить 🟢'
off = f'🔴 Отключить 🔴'
chatterbox_crit_on = f'🟢 Включить 🟢'
chatterbox_crit_off = f'🔴 Отключить 🔴'
send = f'Отправить'
tct = f'Не помогло'
yes = f'Да'
no = f'Нет'
infoMonitoring = f'Информация по обозначениям'
infoTL = f'Информация по обозначениям'
###
calls = InlineKeyboardMarkup()    # ОСНОВА INLINE КНОПКИ
calls.add(InlineKeyboardButton(on, callback_data='calls_on'))  #КОЛЛБЭК
calls.add(InlineKeyboardButton(off, callback_data='calls_off'))
###
calls_l2 = InlineKeyboardMarkup()
calls_l2.add(InlineKeyboardButton(on, callback_data='l2_on'))
calls_l2.add(InlineKeyboardButton(off, callback_data='l2_off'))
###
calls_l2_night = InlineKeyboardMarkup()
calls_l2_night.add(InlineKeyboardButton(on, callback_data='l2_night_on'))
calls_l2_night.add(InlineKeyboardButton(off, callback_data='l2_night_off'))
###
calls_l2_stop = InlineKeyboardMarkup()
calls_l2_stop.add(InlineKeyboardButton(on, callback_data='l2_stop_on'))
calls_l2_stop.add(InlineKeyboardButton(off, callback_data='l2_stop_off'))
###
chatterbox_crit = InlineKeyboardMarkup()
chatterbox_crit.add(InlineKeyboardButton(chatterbox_crit_on, callback_data='chatterbox_crit_on'))
chatterbox_crit.add(InlineKeyboardButton(chatterbox_crit_off, callback_data='chatterbox_crit_off'))
###
chats = InlineKeyboardMarkup()
chats.add(InlineKeyboardButton(on, callback_data='chats_on'))
chats.add(InlineKeyboardButton(off, callback_data='chats_off'))
###
tech_error = InlineKeyboardMarkup()
tech_error.add(InlineKeyboardButton(on, callback_data='tech_error_on'))
tech_error.add(InlineKeyboardButton(off, callback_data='tech_error_off'))
###
pay = InlineKeyboardMarkup()
pay.add(InlineKeyboardButton(on, callback_data='pay_on'))
pay.add(InlineKeyboardButton(off, callback_data='pay_off'))
###
cour_max = InlineKeyboardMarkup()
cour_max.add(InlineKeyboardButton(send, callback_data='cour_max'))
###
cour_min = InlineKeyboardMarkup()
cour_min.add(InlineKeyboardButton(send, callback_data='cour_min'))
###
ticket = InlineKeyboardMarkup()
ticket.add(InlineKeyboardButton(tct, callback_data='ticket'))
###
choose_role_cc = InlineKeyboardMarkup()
choose_role_cc.add(InlineKeyboardButton(yes, callback_data='yes_сс'))
choose_role_cc.add(InlineKeyboardButton(no, callback_data='no_сс'))
###
chose_role_cour = InlineKeyboardMarkup()
chose_role_cour.add(InlineKeyboardButton(yes, callback_data='yes_cour'))
chose_role_cour.add(InlineKeyboardButton(no, callback_data='no_cour'))
###
incorrect_status_panel = InlineKeyboardMarkup()
incorrect_status_panel.add(InlineKeyboardButton(f'☎️Перезвон☎️', callback_data='chime'))
incorrect_status_panel.add(InlineKeyboardButton(f'🍽Перед обедом🍽', callback_data='before_lunch'))
###
info_panelMonitoring = InlineKeyboardMarkup()
info_panelMonitoring.add(InlineKeyboardButton(infoMonitoring, callback_data='infoMonitoring'))
###
info_panelTL = InlineKeyboardMarkup()
info_panelTL.add(InlineKeyboardButton(infoTL, callback_data='infoTL'))
############################################################################################################
headphones = InlineKeyboardMarkup()
headphones.add(InlineKeyboardButton(f'Во всех', callback_data='hp.yes'))
headphones.add(InlineKeyboardButton(f'Иногда', callback_data='hp.no'))
######################################################################
###################################################################### РАБОЧИЙ КОД НА ЭТОМ ЗАКОНЧЕН
######################################################################



