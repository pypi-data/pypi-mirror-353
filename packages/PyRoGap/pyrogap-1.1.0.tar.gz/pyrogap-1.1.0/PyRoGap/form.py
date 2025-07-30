import json


class FormItem:
    "https://my.gap.im/doc/botplatform#form-description"
    def __init__(
            self,
            **Data
        ):
        self.Data = dict(Data)

    def GetFormItem(self):
        return self.Data

class Form:
    "https://my.gap.im/doc/botplatform#form-description"
    def __init__(
            self,
            *Items
        ):
        self.FormItems = []
        for Item in Items:
            self.FormItems.append(Item.GetFormItem())


    def GetForm(self):
        return json.dumps(self.FormItems)
