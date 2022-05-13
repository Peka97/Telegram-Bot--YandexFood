import sqlite3

# SQL commands
conn = sqlite3.connect('Data.db', check_same_thread=False)
cursor = conn.cursor()
find_id = "SELECT ID FROM Users WHERE ID = ?"
find_id_staff = "SELECT ID FROM Users WHERE Staff = ?"
find_id_role = "SELECT ID FROM Users WHERE Role = ?"
find_staff = "SELECT Staff FROM Users WHERE ID = ?"
find_role = "SELECT Role FROM Users WHERE ID = ?"
find_fullname = "SELECT FullName FROM Users WHERE Staff = ?"
find_username = "SELECT UserName FROM Users WHERE Staff = ?"
find_username_id = "SELECT UserName FROM Users WHERE ID = ?"
find_admin = "SELECT Admin FROM Users WHERE ID = ?"
update_admin = "UPDATE Users SET Admin = ? WHERE Staff = ?"
update_staff = "UPDATE Users SET Staff = ? WHERE ID = ?"
update_role = "UPDATE Users SET Role = ? WHERE ID = ?"
update_username = "UPDATE Users SET UserName = ? WHERE ID = ?"
update_chat_max = "UPDATE Users SET ChatMax = ? WHERE Staff = ?"
get_chat_max = "SELECT ChatMax FROM Users WHERE Staff = ?"

### SQL Macros
NULL = "NULL"
monitoring = "Monitoring"
TL = "TL"
QA = "QA"
L1_Client_Calls = "Client Calls"
L1_Client_Chats = "Client Chats"
L1_Rest_Calls = "Rest Calls"
L1_Rest_Chats = "Rest Chats"
L1_Cour_Calls = "Cour Calls"
L1_Cour_Chats = "Cour Chats"
L1_Client_Tickets = "Client Tickets"
L1_Rest_Tickets = "Rest Tickets"
admin = 5
roles = [monitoring, TL, QA]

# Google Doc Dates
month = 'A24:AH37'
month_TL = 'A2:BS95'


def isColorEquals(firstColor: dict, secondColor: dict):
    if firstColor["red"] == secondColor["red"] and firstColor["blue"] == secondColor["blue"] and firstColor["green"] == secondColor["green"]:
        return True
    return False


# Google Doc Monitoring Colors
colorCalls = {'red': 42, 'green': 157, 'blue': 143}
colorChatterBox = {'red': 233, 'green': 196, 'blue': 106}
colorWebim = {'red': 244, 'green': 162, 'blue': 97}

# Google Doc TL Colors
colorUnderworking = {'red': 180, 'green': 198, 'blue': 231}  #темносиний
colorDutyEvening = {'red': 170, 'green': 238, 'blue': 236}  #голубой
colorDutyMorning = {'red': 255, 'green': 230, 'blue': 153}  #светложелтый
colorLearning = {'red': 217, 'green': 217, 'blue': 217}  #серый
nocolor = {'red': 255, 'green': 255, 'blue': 255} #белый
emojiTL = "🧑‍💻"
time = "Время"

# Google Doc TL Roles
ClientCalls = str("#ClientCalls")
ClientChats = str("#ClientChats")
OutgoingCalls = str("#OutgoingCalls")
ClientChatsAndTickets = str("#ClientChatsAndTickets")
Night = str("#Night")
L2 = str("#L2")
CourCalls = str("#CourCalls")
CourChats = str("#CourChats")
ProActive = str("#ProActiv")
RestCalls = str("#RestCalls")
RestChats = str("#RestChats")
RetailTickets = str("#RetailTickets")
Donov = str("#1.5")
ZRKC = str("ЗРКЦ")
ZRKC_all = str("🏠     #*ЗРКЦ*                 ")
######################################################################
###################################################################### РАБОЧИЙ КОД НА ЭТОМ ЗАКОНЧЕН
######################################################################
