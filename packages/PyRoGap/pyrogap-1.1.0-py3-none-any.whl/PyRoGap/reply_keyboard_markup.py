import json


class KeyboardButton:
    "https://my.gap.im/doc/botplatform#reply_keyboard-description"
    def __init__(
            self,
            Key : str,
            Value : str
        ):
        self.KeyboardButton = {str(Key) , str(Value)}

    def GetKeyboardButton(self):
        return self.KeyboardButton

class ReplyKeyboardMarkup:
    "https://my.gap.im/doc/botplatform#reply_keyboard-description"
    def __init__(
            self,
            *Rows
        ):
        self.keyboard = []
        
        for Row in Rows:
            NewRow = []
            for Item in Row:
                NewRow.append(Item.GetKeyboardButton())
            self.keyboard.append(NewRow)

    def GetReplyKeyboardMarkup(self):
        return json.dumps({"keyboard" : self.keyboard})

