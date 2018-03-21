from .base import BaseMsg
class Wechat(BaseMsg):
    def __init__(self):

        print("hello wechat")
    def send(self,subject,body,to,name):
        pass