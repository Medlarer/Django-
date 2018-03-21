import importlib
from django.conf import settings

def send_message(subject,body,to,name):
    for path_class in settings.INSTALL_MSGS:
        # print(path_class)
        path,cls=path_class.rsplit(".",maxsplit=1)
        str_class=importlib.import_module(path)
        obj=getattr(str_class,cls)()
        # print(obj)
        obj.send(subject,body,to,name)



