import requests
import json



from .inline_keyboard import InlineKeyboard
from .reply_keyboard_markup import ReplyKeyboardMarkup
from .form import Form


class GapBot:
    "برای ساخت یک شیء از ربات پیام رسان گپ به کار می رود"
    def __init__(
            self,
            Token : str,
            Proxies = {},
            base_url : str = "https://api.gap.im"
        ):
        self.token = str(Token)
        self.proxies = Proxies
        self.base_url = str(base_url)

    def sendMessage(
            self,
            chat_id : str | int,
            text : str,
            inline_keyboard : InlineKeyboard = None,
            reply_keyboard : ReplyKeyboardMarkup = None,
            form : Form = None,
        ):
        "برای ارسال پیام به کار می رود"
        DataRequests = {
            "chat_id" : chat_id,
            "type" : "text",
            "data" : str(text)
        }
        if inline_keyboard != None:
            DataRequests.update({
                "inline_keyboard" : inline_keyboard.GetInlineKeyboard()
            })
        
        if reply_keyboard != None:
            DataRequests.update({
                "reply_keyboard" : reply_keyboard.GetReplyKeyboardMarkup()
            })

        if form != None:
            DataRequests.update({
                "form" : form.GetForm()
            })

        return requests.post(
            f"{self.base_url}/sendMessage",
            data=DataRequests,
            headers={
                "token" : self.token
            },
            proxies=self.proxies
        ).json()
    
    def sendLocation(
            self,
            chat_id : str | int,
            lat : float | int | str,
            long : float | int | str,
            desc : str,
            inline_keyboard : InlineKeyboard = None,
            reply_keyboard : ReplyKeyboardMarkup = None,
            form : Form = None
        ):
        "برای ارسال موقعیت جغرافیایی به کار می رود"
        DataRequests = {
            "chat_id" : chat_id,
            "type" : "location",
            "data" : json.dumps({
                "lat" : float(lat),
                "long" : float(long),
                "desc" : str(desc)
            })
        }
        if inline_keyboard != None:
            DataRequests.update({
                "inline_keyboard" : inline_keyboard.GetInlineKeyboard()
            })
        
        if reply_keyboard != None:
            DataRequests.update({
                "reply_keyboard" : reply_keyboard.GetReplyKeyboardMarkup()
            })

        if form != None:
            DataRequests.update({
                "form" : form.GetForm()
            })

        return requests.post(
            f"{self.base_url}/sendMessage",
            data=DataRequests,
            headers={
                "token" : self.token
            },
            proxies=self.proxies
        ).json()
    
    def sendInvoice(
            self,
            chat_id : str | int,
            amount : int,
            description : str,
            expire_time : int = 86400,
            currency : str = "IRR"
        ):
        "برای ارسال یک پرداخت به کار می رود"
        return requests.post(
            f"{self.base_url}/invoice",
            data={
                "chat_id" : chat_id,
                "amount" : int(amount),
                "description" : str(description),
                "expire_time" : int(expire_time),
                "currency" : str(currency)
            },
            headers={
                "token" : self.token
            },
            proxies=self.proxies
        ).json()

    def sendInvoiceAndText(
            self,
            chat_id : str | int,
            text : str,
            text_button : str,
            amount : int,
            ref_id : str,
            description : str,
            currency : str = "IRR"
        ):
        "برای ارسال یک پرداخت به کار می رود"
        return requests.post(
            f"{self.base_url}/sendMessage",
            data={
                "chat_id" : chat_id,
                "type" : "text",
                "data" : str(text),
                "inline_keyboard" : json.dumps([
                    [{"text" : str(text_button) , "amount" : int(amount) , "currency" : str(currency) , "ref_id" : str(ref_id) , "desc" : str(description)}]
                ])
            },
            headers={
                "token" : self.token
            },
            proxies=self.proxies
        ).json()

    def sendContact(
            self,
            chat_id : str | int,
            phone : str | int,
            name : str,
            inline_keyboard : InlineKeyboard = None,
            reply_keyboard : ReplyKeyboardMarkup = None,
            form : Form = None
        ):
        "برای ارسال یک مخاطب به کار می رود"
        DataRequests = {
            "chat_id" : chat_id,
            "type" : "contact",
            "data" : json.dumps({
                "phone" : str(phone),
                "name" : str(name)
            })
        }
        if inline_keyboard != None:
            DataRequests.update({
                "inline_keyboard" : inline_keyboard.GetInlineKeyboard()
            })
        
        if reply_keyboard != None:
            DataRequests.update({
                "reply_keyboard" : reply_keyboard.GetReplyKeyboardMarkup()
            })

        if form != None:
            DataRequests.update({
                "form" : form.GetForm()
            })

        return requests.post(
            f"{self.base_url}/sendMessage",
            data=DataRequests,
            headers={
                "token" : self.token
            },
            proxies=self.proxies
        ).json()
    
    def sendAction(
            self,
            chat_id : str | int,
            action : str = "typing"
        ):
        "برای ارسال یک وضعیت به ربات استفاده می شود"
        return requests.post(
            f"{self.base_url}/sendAction",
            headers={
                "token" : self.token
            },
            data={
                "chat_id" : chat_id,
                "type" : str(action)
            },
            proxies=self.proxies
        ).json()
    
    def editMessage(
            self,
            chat_id : str | int,
            message_id : str | int,
            text : str,
            inline_keyboard : InlineKeyboard = None
        ):
        "برای ویرایش یک پیام به کار می رود"
        DataRequests = {
            "chat_id" : chat_id,
            "message_id" : int(message_id),
            "data" : str(text)
        }

        if inline_keyboard != None:
            DataRequests.update({
                "inline_keyboard" : inline_keyboard.GetInlineKeyboard()
            })
        
        return requests.post(
            f"{self.base_url}/editMessage",
            data=DataRequests,
            headers={
                "token" : self.token
            },
            proxies=self.proxies
        ).json()
    
    def deleteMessage(
            self,
            chat_id : str | int,
            message_id : str | int,
        ):
        "برای حذف یک پیام به کار می رود"
        return requests.post(
            f"{self.base_url}/deleteMessage",
            headers={
                "token" : self.token
            },
            data={
                "chat_id" : chat_id,
                "message_id" : int(message_id),
            },
            proxies=self.proxies
        ).json()
    
    def answerCallbackQuery(
            self,
            chat_id : str | int,
            callback_id : int,
            text : str,
            show_alert : bool = False
        ):
        "برای نمایش یک پیام به صورت آلرت یا پاپاپ به کار می رود"
        return requests.post(
            f"{self.base_url}/answerCallback",
            headers={
                "token" : self.token
            },
            data={
                "chat_id" : chat_id,
                "callback_id" : int(callback_id),
                "text" : str(text),
                "show_alert" : bool(show_alert)
            },
            proxies=self.proxies
        ).json()
    



