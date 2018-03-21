import smtplib
from .base import BaseMsg
from email.mime.text import MIMEText
from email.utils import formataddr


class Email(BaseMsg):
    def __init__(self):
        self.email="hzauqiu@163.com"
        self.user="邱胜彪"
        self.pwd="zyf10086"
        # print("hello email")
    def send(self,subject,body,to,name):
        # print(111)
        # print(subject,body,to,name)
        msg=MIMEText(body,"plain","utf-8") #发送内容
        # print("11")
        msg["From"]=formataddr([self.user,self.email]) #发件人
        # print("22")
        msg["To"]=formataddr([name,to]) #收件人
        # print("33")
        msg["Subject"]=subject #主题
        # print("44")
        server=smtplib.SMTP("smtp.163.com",25) #SMTP服务
        # print("xix")
        print(self.email,self.pwd)
        server.login(self.email,self.pwd)  #邮箱用户名和密码
        print("登陆成功")
        server.sendmail(self.email,[to,],msg.as_string()) #发送者和接收者
        print("邮件发送成功！")
        server.quit()