# Google Doc Dates
field_WFM = 'A1:AH20'
field_monitoring = 'A21:AH34'
SPREADSHEET_ID = '1BAIbiDotK1z02ZbraPHBfmK3q0TEq47DqYVGStgrL98'
WFM = "📅 Расписание работы отдела WFM 📅:\n\n"
Monitoring = "📅 Расписание работы отдела Мониторинга 📅:\n\n"


def isColorEquals(firstColor: dict, secondColor: dict):
    if firstColor["red"] == secondColor["red"] and firstColor["blue"] == secondColor["blue"] and firstColor["green"] == secondColor["green"]:
        return True
    return False


# Google Doc Monitoring Colors
colorCalls = {'red': 42, 'green': 157, 'blue': 143}
colorChatterBox = {'red': 233, 'green': 196, 'blue': 106}
colorWebim = {'red': 244, 'green': 162, 'blue': 97}


