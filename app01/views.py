from django.shortcuts import render,HttpResponse,redirect
from rbac import models
from rbac.service.init_permission import init_permission
# Create your views here.

def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method=="GET":
        return render(request,"login.html")
    else:
        name=request.POST.get("name")
        pwd=request.POST.get("pwd")
        print(name,pwd)
        user_obj=models.User.objects.filter(username=name,password=pwd).first()
        if user_obj:
            request.session["user_info"]={"user_id":user_obj.id,
                                          "user_name":user_obj.username}
            init_permission(user_obj,request)
            return redirect("/index/")
        return render(request, "login.html")

def index(request):
    return render(request,"index.html")