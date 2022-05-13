import config as config
from enum import Enum


class BotUserType(Enum):
    USER_TYPE_NONE = 1
    USER_TYPE_CC = 2
    USER_TYPE_COURIER = 3
    USER_TYPE_MONITORING = 4
    USER_TYPE_QA = 5
    USER_TYPE_TL = 6


BotUserTypeStrings = {
    BotUserType.USER_TYPE_NONE: "#Unknown",
    BotUserType.USER_TYPE_CC: "#CC",
    BotUserType.USER_TYPE_COURIER: "#COUR",
    BotUserType.USER_TYPE_MONITORING: "#MONITORING",
    BotUserType.USER_TYPE_QA: "#QA",
    BotUserType.USER_TYPE_TL: "#TL",
}


class BotUser:
    __is_admin: bool = False
    __user_name: str = "Unknown"
    __current_user_type: BotUserType = BotUserType.USER_TYPE_NONE
    __user_id: int = -1

    def set_user_id(self, value: int):
        self.__user_id = value

    def get_user_id(self):
        return self.__user_id

    def set_user_name(self, value: str):
        self.__user_name = value

    def get_user_name(self):
        return self.__user_name

    def is_admin(self):
        return self.__is_admin

    def set_is_admin(self, state: bool):
        self.__is_admin = state

    def set_user_type(self, user_type: BotUserType):
        self.__current_user_type = user_type

    def get_user_type(self):
        return self.__current_user_type

    def get_user_type_as_string(self):
        user_type = self.get_user_type()
        return BotUserTypeStrings.get(user_type) or BotUserTypeStrings.get(BotUserType.USER_TYPE_NONE)

    def __determine_user_type_from_data(self, data):
        if data is None or not ("type" in data):
            self.set_user_type(BotUserType.USER_TYPE_NONE)
        else:
            for enumValue in BotUserTypeStrings:
                enumStringValue = BotUserTypeStrings[enumValue]
                if data["type"] == enumStringValue:
                    self.set_user_type(enumValue)
                    return

    def __init__(self, user_id, data):
        user_id = int(user_id)
        self.set_is_admin(config.isadmin(user_id))
        if not ("name" in data) or data["name"] is None:
            self.set_user_name("Unknown")
        else:
            self.set_user_name(data["name"])
        self.set_user_id(user_id)
        self.__determine_user_type_from_data(data)
