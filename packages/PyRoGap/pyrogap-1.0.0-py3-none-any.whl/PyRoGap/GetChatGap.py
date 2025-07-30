import requests
from bs4 import BeautifulSoup
import time

from .Message import Message





class GetChatGap:
    "یک شیء برای دریافت اطلاعات یک چت"
    def __init__(
            self,
            UserName : str
        ):
        self.UserName = str(UserName)
        self.soup = BeautifulSoup(
            requests.get(
                f"https://gap.im/{str(UserName).replace('@', '')}",
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                },
                proxies={}
            ).text,
            "html.parser"
        )

    def GetName(
            self,
            get_new_data : bool = False
        ):
        "برای دریافت نام استفاده می شود"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            if self.soup.find("div" , class_="info").find("h1" , class_="name"):
                return str(self.soup.find("div" , class_="info").find("h1" , class_="name").text).strip()
            else:
                return None
        except:
            return None
        
    def GetAbout(
            self,
            get_new_data : bool = False
        ):
        "برای دریافت توضیحات استفاده می شود"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            if self.soup.find("div" , class_="item bio").find("div" , class_="inf"):
                return str(self.soup.find("div" , class_="item bio").find("div" , class_="inf").text).strip()
            else:
                return None
        except:
            return None
    
    def GetAvatar(
            self,
            get_new_data : bool = False
        ):
        "برای دریافت تصویر پروفایل چت استفاده می شود"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            if self.soup.find("div" , class_="avatar").find("img" , class_="pic"):
                return str(self.soup.find("div" , class_="avatar").find("img" , class_="pic").get("src"))
            else:
                return None
        except:
            return None
        
    def SaveAvatar(
            self,
            get_new_data : bool = False
        ):
        "برای ذخیره سازی تصویر پروفایل چت استفاده می شود"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            if self.soup.find("div" , class_="avatar").find("img" , class_="pic"):
                return requests.get(
                    str(self.soup.find("div" , class_="avatar").find("img" , class_="pic").get("src")),
                    headers={
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                    },
                    proxies={}
                ).content
            else:
                return None
        except:
            return None

    def GetLink(self):
        "برای دریافت لینک چت استفاده می شود"
        try:
            return f"https://gap.im/{self.UserName.replace('@', '')}"
        except:
            return None
        
    def GetLinkWeb(
            self,
            get_new_data : bool = False
        ):
        "برای دریافت لینک وب چت استفاده می شود"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            
            if self.soup.find("a" , class_="btn web"):
                return str(self.soup.find("a" , class_="btn web").get("href"))
            else:
                return None
        except:
            return None

    def GetMemberCount(
            self,
            get_new_data : bool = False
        ):
        "برای دریافت تعداد اعضا استفاده می شود"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            if self.soup.find("div" , class_="info").find("div" , class_="no"):
                return str(self.soup.find("div" , class_="info").find("div" , class_="no").text).strip()
            else:
                return None
        except:
            return None
    
    def GetLatestMessages(
            self,
            get_new_data : bool = False
        ):
        "برای دریافت آخرین پیام های کانال استفاده می شود"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            ListMessages_BeautifulSoup = self.soup.find_all("article" , class_="post_box")
            Messages = []

            for Message in ListMessages_BeautifulSoup:
                MessageData = {}

                MessageData.update({
                    "id" : str(Message.get("post_id")),
                    "link" : f"https://gap.im{str(Message.find("div" , class_="meta").find("span" , class_="link").find("a").get("href"))}",
                    "date" : str(Message.find("div" , class_="meta").find("span" , class_="date").text).strip(),
                    "likes" : int(Message.find("div" , class_="meta").find("span" , class_="likes").text)
                })

                if Message.find("img"):
                    if str(Message.find("img").get("src")).startswith("https://cdn.gaplication.com/o/"):
                        MessageData.update({
                            "image" : str(Message.find("img").get("src"))
                        })

                if Message.find("video"):
                    if Message.find("video").find("source"):
                        if str(Message.find("video").find("source").get("src")).startswith("https://cdn.gaplication.com/o/"):
                            MessageData.update({
                                "video" : {
                                    "url" : str(Message.find("video").find("source").get("src")),
                                    "video_width" : int(Message.find("video").get("width")),
                                    "video_height" : int(Message.find("video").get("height")),
                                    "poster" : str(Message.find("video").get("poster")),
                                }
                            })
                    elif Message.find("video" , id="live-video"):
                        MessageData.update({
                            "live_video" : {
                                "url" : str(Message.find("video" , id="live-video").get("src")),
                                "video_width" : int(Message.find("video" , id="live-video").get("width")),
                                "video_height" : int(Message.find("video" , id="live-video").get("height")),
                                "data_live" : str(Message.find("video" , id="live-video").get("data-live")),
                            }
                        })

                if Message.find("div" , class_="msgpoll"):
                    options = []
                    for option in Message.find("div" , class_="msgpoll").find_all("label" , class_="msgpoll__option"):
                        options.append(str(option.text).strip())
                    
                    MessageData.update({
                        "poll" : {
                            "title" : str(Message.find("div" , class_="msgpoll").find("h3" , class_="msgpoll__title").text).strip(),
                            "options" : options
                        }
                    })

                if Message.find("a").find("img" , alt="icon location" , src="/img/icon-location.png"):
                    MessageData.update({
                        "location" : str(Message.find("a").get("href"))
                    })

                if Message.find("audio"):
                    MessageData.update({
                        "audio" : str(Message.find("audio").find("source").get("src"))
                    })

                if Message.find("a").find("img" , src="/img/icon-download.png" , alt="icon download"):
                    MessageData.update({
                        "file_name" : str(Message.find("a").text).strip()
                    })

                if Message.find("p"):
                    contact_name = Message.find("p").find("b", class_="contact-name")
                    contact_phone = Message.find("p").find("span", class_="contact-phone")
                    if contact_name and contact_phone:
                        MessageData.update({
                            "contact": {
                                "name": str(contact_name.text).strip(),
                                "phone": str(contact_phone.text).strip()
                            }
                        })

                if Message.find("p"):
                    if Message.find("p").find("b", class_="contact-name") and Message.find("p").find("span", class_="contact-phone"):
                        if len(Message.find_all("p")) > 1:
                            MessageData.update({
                                "text" : str(Message.find_all("p")[-1].text)
                            })
                    else:
                        MessageData.update({
                            "text" : str(Message.find_all("p")[-1].text)
                        })
                    

                Messages.append(MessageData)
            return Messages
        except:
            return None

    def isChannelVerified(
            self,
            get_new_data : bool = False
        ):
        "بررسی می کند که آیا چت مورد نظر تیک تایید دارد یا خیر"
        try:
            if get_new_data == True:
                self.soup = BeautifulSoup(
                    requests.get(
                        f"https://gap.im/{str(self.UserName).replace('@', '')}",
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                        },
                        proxies={}
                    ).text,
                    "html.parser"
                )
            if self.soup.find("div" , class_="info").find("h1" , class_="name").find("div" , class_="icon-official"):
                return True
            else:
                return False
        except:
            return None
    
    def GetMessagesAfter(
            self,
            last_id : str | int
        ):
        "از این متد برای دریافت پیام های بعد از شناسه ای که به متد می دهید استفاده می شود"
        try:
            GetMessages = GetChatGap.GetLatestMessages(self , True)
            MessagesAfter = []
            for msg in GetMessages:
                if int(last_id) < int(msg["id"]):
                    MessagesAfter.append(msg)
        
            return MessagesAfter[::-1]
        except:
            return None
        
    def Run(
            self,
            last_id : str | int,
            function,
            commands : dict = {},
            sleep_time : float = 0.1
        ):
        "از این متد برای دریافت همیشگی پیام های چت استفاده می شود و هر پیامی که در چت بیاید به صورت یک شیء ای از مسیج به تابع مورد نظر فراخوانی می شود"
        while True:
            try:
                NewMessages = GetChatGap.GetMessagesAfter(self , last_id)
                if NewMessages != None:
                    for msg in NewMessages:
                        last_id = int(msg["id"])
                        if "text" in commands.keys():
                            if str(msg["text"]) in commands.keys():
                                commands[str(msg["text"])](
                                    Message(
                                        msg
                                    )
                                )
                            else:
                                function(
                                    Message(
                                        msg
                                    )
                                )
                        else:
                            function(
                                Message(
                                    msg
                                )
                            )
                    time.sleep(sleep_time)
            except:
                continue




