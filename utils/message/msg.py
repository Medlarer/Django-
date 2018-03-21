from .base import BaseMsg
class Message(BaseMsg):
    def __init__(self):
        print("hello message")
    def send(self,subject,body,to,name):
        pass