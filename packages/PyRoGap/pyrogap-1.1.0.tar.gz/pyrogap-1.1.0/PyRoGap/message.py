import requests

class Message:
    "یک شیء از یک پیام کانال"
    def __init__(
            self,
            Data : dict
        ):
        self.DataDict = dict(Data)
        self.id = Data["id"]
        self.link = Data["link"]
        self.date = Data["date"]

        try:
            self.image = Data["image"]
        except:
            self.image = None

        try:
            self.video = Data["video"]
        except:
            self.video = None

        try:
            self.poll = Data["poll"]
        except:
            self.poll = None

        try:
            self.location = Data["location"]
        except:
            self.location = None

        try:
            self.audio = Data["audio"]
        except:
            self.audio = None

        try:
            self.file_name = Data["file_name"]
        except:
            self.file_name = None

        try:
            self.live_video = Data["live_video"]
        except:
            self.live_video = None

        try:
            self.text = Data["text"]
        except:
            self.text = None

        try:
            self.contact = Data["contact"]
        except:
            self.contact = None

    def SaveImage(self):
        "برای ذخیره سازی تصویر دریافت شده به کار می رود"
        return requests.get(
            str(self.image)
        ).content

    def SaveAudio(self):
        "برای ذخیره سازی صوت دریافت شده به کار می رود"
        return requests.get(
            str(self.audio)
        ).content
    
    def SaveVideo(self):
        "برای ذخیره سازی ویدیو دریافت شده به کار می رود"
        return requests.get(
            str(self.video)
        ).content
    
    def SaveContact(self):
        vcard = (
            "BEGIN:VCARD\n"
            "VERSION:3.0\n"
            f"N:{self.contact["name"]};;;\n"
            f"FN:{self.contact["name"]}\n"
            f"TEL;TYPE=CELL:{self.contact["phone"]}\n"
            "END:VCARD\n"
        )
        return vcard

