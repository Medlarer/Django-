class BaseMsg(object):
    def send(self,subject,body,to,name):
        raise NotImplementedError("未实现send方法")