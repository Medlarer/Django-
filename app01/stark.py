from django.shortcuts import HttpResponse,redirect,render,reverse
from django.utils.safestring import mark_safe
from stark.service import v1
from django.conf.urls import url
from app01 import models
from django.forms import fields,widgets,Form
from app01.configs import customer,student

class DepartmentConfig(v1.StarkConfig):
    # 1部门表
    list_display = ["title","code"]

    edit_link = ["title",]

v1.site.register(models.Department,DepartmentConfig)


class UserInfoConfig(v1.StarkConfig):
    """
    用户表
    """
    list_display = ["name","username","email","depart"]
    edit_link = ["name","username"]
    com_filter = [v1.FilterOption("depart",text_func_name=lambda x: str(x),
                                  val_func_name=lambda x:x.code)]
    search_fields = ["name__contains","email__contains"]
    show_search_form = True
    show_com_filter = True
v1.site.register(models.UserInfo,UserInfoConfig)

class CourseConfig(v1.StarkConfig):
    """
    课程名称
    """
    list_display = ["name"]
    edit_link = ["name"]
v1.site.register(models.Course,CourseConfig)

class SchoolConfig(v1.StarkConfig):
    """
    校区名字
    """
    list_display = ['title']
    edit_link = ['title',]
v1.site.register(models.School,SchoolConfig)

class ClassListConfig(v1.StarkConfig):
    """
    班级名称
    """
    list_display =["school","course","semester","start_date"]
    com_filter = [v1.FilterOption("teachers", text_func_name=lambda x: str(x),
                                  val_func_name=lambda x: x.teach_classes), ]
    show_com_filter = True
v1.site.register(models.ClassList,ClassListConfig)


v1.site.register(models.Customer,customer.CustomerConfig)







class ConsultRecordConfig(v1.StarkConfig):
    list_display = ['customer','consultant','date']

    comb_filter = [
        v1.FilterOption('customer')
    ]

    def changelist_view(self,request,*args,**kwargs):
        customer = request.GET.get('customer')
        # session中获取当前用户ID
        current_login_user_id = 6
        ct = models.Customer.objects.filter(consultant=current_login_user_id,id=customer).count()
        if not ct:
            return HttpResponse('别抢客户呀...')

        return super(ConsultRecordConfig,self).edit(request,*args,**kwargs)

v1.site.register(models.ConsultRecord,ConsultRecordConfig)


#  上课记录
class CourseRecordConfig(v1.StarkConfig):
    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url_patterns = [
            url(r"^(\d+)/score/$", self.wrapper(self.score_list), name="%s_%s_score" % (app_model_name)),
        ]
        return url_patterns

    def score_list(self,request,record_id):
        if request.method=="GET":
            study_record_list=models.StudyRecord.objects.filter(course_record_id=record_id)
            data=[]
            for obj in study_record_list:
                TestForm=type("TestForm",(Form,),{
                    "score_%s" %obj.pk:fields.ChoiceField(models.StudyRecord.score_choices),
                    "homework_note_%s" %obj.pk:fields.CharField(widget=widgets.Textarea())
                })
                data.append({"obj":obj,"form":TestForm(initial={"score_%s" %obj.pk:obj.score,
                                                                "homework_note_%s" %obj.pk:obj.homework_note})})
            return render(request,"score_list.html",{"data":data})
        else:
            record_dict = {}
            for key,values in request.POST.items():
                if key == "csrfmiddlewaretoken":
                    continue
                name,id=key.rsplit("_",1)
                if id in record_dict:
                    record_dict[id][name]=values
                else:
                    record_dict[id]={name:values}
            for rid,com_dict in record_dict.items():
                models.StudyRecord.objects.filter(id=rid).update(**com_dict)
            return redirect("/stark/app01/courserecord/")
    def attend(self,obj=None,is_header=False):
        if is_header:
            return "考勤"
        return mark_safe("<a href='/stark/app01/studyrecord/?course_record=%s'>考勤管理</a>" %(obj.pk,))

    def display_score_list(self, obj=None, is_header=False):
        if is_header:
            return '成绩录入'
        from django.urls import reverse
        rurl = reverse("stark:app01_courserecord_score", args=(obj.pk,))
        return mark_safe("<a href='%s'>成绩录入</a>" % rurl)

    list_display = ['class_obj','day_num',attend,display_score_list]

    def multi_init(self,request):
        """
        自定义批量初始化方法
        :param request:
        :return:
        """
        #上课记录ID列表
        pk_list=request.POST.getlist("choice")
        #上课记录对象
        record_list=models.CourseRecord.objects.filter(id__in=pk_list)
        for record in record_list:
            #上课记录对象
            #第一天，第二天
            exists=models.StudyRecord.objects.filter(course_record=record).exists()
            if exists:
                continue
            student_list=models.Student.objects.filter(class_list=record.class_obj)
            bulk_list=[]
            for student in student_list:
                #为每一个学生创建每一天的学习记录
                bulk_list.append(models.StudyRecord(student=student,course_record=record))
            models.StudyRecord.objects.bulk_create(bulk_list)
        return HttpResponse("添加成功")
    multi_init.short_desc="批量初始化"
    actions=[multi_init]
    show_action = True
v1.site.register(models.CourseRecord,CourseRecordConfig)


class StudyRecordConfig(v1.StarkConfig):

    def display_record(self,obj=None,is_header=False):
        if is_header:
            return '出勤'
        return obj.get_record_display()

    list_display = ['course_record','student',display_record]

    comb_filter = [
        v1.FilterOption('course_record')
    ]

    def action_checked(self,request):
        pass
    action_checked.short_desc= "签到"

    def action_vacate(self,request):
        pass
    action_vacate.short_desc= "请假"

    def action_late(self,request):
        pass
    action_late.short_desc= "迟到"

    def action_noshow(self,request):
        pk_list = request.POST.getlist('choice')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='noshow')
    action_noshow.short_desc= "缺勤"

    def action_leave_early(self,request):
        pass
    action_leave_early.short_desc= "早退"

    actions = [action_checked,action_vacate, action_late,action_noshow,action_leave_early]

    show_actions = True

    show_add_btn = False


v1.site.register(models.StudyRecord,StudyRecordConfig)

v1.site.register(models.Student,student.StudentConfig)





