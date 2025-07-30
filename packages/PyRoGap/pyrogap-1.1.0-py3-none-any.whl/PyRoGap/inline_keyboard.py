import json


class InlineKeyboardButton:
    "https://my.gap.im/doc/botplatform#inline_keyboard-description"
    def __init__(
            self,
            Text : str,
            **Data
        ):
        self.InlineKeyboardButton = {
            "text" : str(Text)
        }
        for Key , Value in Data.items():
            self.InlineKeyboardButton.update({
                str(Key) : Value
            })

    def GetInlineKeyboardButton(self):
        return self.InlineKeyboardButton

class InlineKeyboard:
    "https://my.gap.im/doc/botplatform#inline_keyboard-description"
    def __init__(
            self,
            *Rows
        ):
        self.InlineKeyboard = []
        for Row in Rows:
            NewRow = []
            for Item in Row:
                NewRow.append(Item.GetInlineKeyboardButton())
            self.InlineKeyboard.append(NewRow)

    def GetInlineKeyboard(self):
        return json.dumps(self.InlineKeyboard)


