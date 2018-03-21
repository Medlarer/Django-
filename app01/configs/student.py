from django.db.models import Q
from django.shortcuts import HttpResponse,redirect,render,reverse
from django.utils.safestring import mark_safe
from stark.service import v1
from django.conf.urls import url
from app01 import models
from django.forms import fields,widgets,Form
import datetime,json


class StudentConfig(v1.StarkConfig):
    """
    自定义学生信息表
    """
    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/score/$', self.wrapper(self.score_view), name="%s_%s_sco" % app_model_name),
            url(r'^chart/$', self.wrapper(self.chart_view), name="%s_%s_cha" % app_model_name),
        ]
        return patterns

    def score_view(self,request,nid):
        """
        学生成绩录入
        :param request:
        :param nid:
        :return:
        """
        student_obj=models.Student.objects.filter(id=nid).first()
        if not student_obj:
            return HttpResponse("查无此人")
        class_list=student_obj.class_list.all()
        return render(request,"score_view.html",{"classes":class_list,"sid":nid})

    def chart_view(self,request):
        ret={"status":False,"data":None,"msg":None}
        try:
            sid=request.GET.get("sid")
            cid=request.GET.get("cid")
            record_list=models.StudyRecord.objects.filter(student_id=sid,course_record__class_obj_id=cid).order_by("course_record")
            # data=[
            #     ['day1', 24.25],
            #     ['day2', 23.50],
            #     ['day3', 21.51],
            #     ['day4', 16.78],
            #     ['day5', 16.06],
            #     ['day6', 15.20]
            # ]
            data=[]
            for record in record_list:
                day="day%s" %(record.course_record.day_num,)
                data.append([day,record.score])
            ret["status"]=True
            ret["data"]=data
        except Exception as e:
            ret["msg"]="请求错误"
        return HttpResponse(json.dumps(ret))

    def display_scores(self,obj=None,is_header=False):
        if is_header:
            return "成绩查询"
        surl=reverse("stark:app01_student_sco",args=(obj.id,))
        return mark_safe("<a href='%s'>成绩查询</a>"%(surl,))
    list_display = ['username','emergency_contract',display_scores]

