from django.db.models import Q
from django.shortcuts import HttpResponse,redirect,render,reverse
from django.utils.safestring import mark_safe
from stark.service import v1
from django.conf.urls import url
from app01 import models
from django.forms import fields, widgets, Form, ModelForm
import datetime
from django.db import transaction
from utils import message


class SingleModelForm(ModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant','status','recv_date','last_consult_date']


class CustomerConfig(v1.StarkConfig):

    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return '性别'
        return obj.get_gender_display()

    def display_education(self,obj=None,is_header=False):
        if is_header:
            return '学历'
        return obj.get_education_display()

    def display_course(self,obj=None,is_header=False):
        if is_header:
            return '咨询课程'
        course_list = obj.course.all()
        html = []
        # self.request.GET
        # self._query_param_key
        # 构造QueryDict
        # urlencode()
        for item in course_list:
            temp = "<a style='display:inline-block;padding:3px 5px;border:1px solid blue;margin:2px;' href='/stark/app01/customer/%s/%s/dc/'>%s X</a>" %(obj.pk,item.pk,item.name)
            html.append(temp)

        return mark_safe("".join(html))

    def display_status(self,obj=None,is_header=False):
        if is_header:
            return '状态'
        return obj.get_status_display()

    def record(self,obj=None,is_header=False):
        if is_header:
            return '跟进记录'
        # /stark/crm/consultrecord/?customer=11
        return mark_safe("<a href='/stark/app01/consultrecord/?customer=%s'>查看跟进记录</a>" %(obj.pk,))

    list_display = ['qq','name',display_gender,display_education,display_course,display_status,record]
    edit_link = ['qq']



    def delete_course(self,request,customer_id,course_id):
        """
        删除当前用户感兴趣的课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        """
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        # 跳转回去时，要保留原来的搜索条件
        return redirect(self.get_list_url())
    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/(\d+)/dc/$', self.wrapper(self.delete_course), name="%s_%s_dc" %app_model_name),
            url(r'^public/$', self.wrapper(self.public_view), name="%s_%s_pub" % app_model_name),
            url(r'^(\d+)/competition/$', self.wrapper(self.competition_view), name="%s_%s_competition" % app_model_name),
            url(r'^user/$', self.wrapper(self.user_view), name="%s_%s_user" % app_model_name),
            url(r'^single/$', self.wrapper(self.single_view), name="%s_%s_single" % app_model_name),
        ]
        return patterns

    def public_view(self,request):
        """
        显示公共页面的所有客户
        :param request:
        :return:
        """
        #当前年月日
        current_time=datetime.datetime.now().date()
        #3天以前的时间差
        day_3=current_time-datetime.timedelta(3)
        #15天以前的时间差
        day_15=current_time-datetime.timedelta(15)
        q1=Q()
        q2=Q()
        con=Q()
        q1.connector="OR"
        q1.children.append(("recv_date__lt",day_15))
        q1.children.append(("last_consult_date__lt",day_3))
        q2.connector="AND"
        q2.children.append(("status",2))
        con.add(q1,"AND")
        con.add(q2,"AND")
        customer_list=models.Customer.objects.filter(con)
        # customer_list=models.Customer.objects.filter(Q(recv_date__lt=day_15)|Q(last_consult_date__lt=day_3),status=2)
        return render(request,"public.html",{"customers":customer_list})

    def competition_view(self,request,nid):
        """
        抢单
        :param nid:
        :return:
        """
        current_time = datetime.datetime.now().date()
        # 3天以前的时间差
        day_3 = current_time - datetime.timedelta(3)
        # 15天以前的时间差
        day_15 = current_time - datetime.timedelta(15)
        #通过session取值
        current_user_id = 3
        order = models.Customer.objects.filter(Q(recv_date__lt=day_15) | Q(last_consult_date__lt=day_3),
                                                       status=2,id=nid).exclude(consultant_id=current_user_id).update(
            consultant_id=current_user_id,last_consult_date=current_time,recv_date=current_time
        )
        if not order:
            return HttpResponse("抢单不成功")
        models.CustomerDistribution.objects.create(user_id=current_user_id,customer_id=nid,ctime=current_time)

        return HttpResponse("抢单成功")

    def user_view(self,request):
        """
        当前登录用户的客户
        :param request:
        :return:
        """
        current_user_id=3
        customer_list=models.CustomerDistribution.objects.filter(user_id=current_user_id).order_by("status")
        return render(request,"user.html",{"customers":customer_list})


    def single_view(self,request):
        """
        单条录入客户信息
        :param request:
        :return:
        """
        from .casual import single
        if request.method=="GET":
            form=SingleModelForm()
            return render(request,"single.html",{"form":form})
        else:
            form=SingleModelForm(request.POST)
            if form.is_valid():
                current_time=datetime.datetime.now().date()
                sale_id=single.get_sale_id()
                if not sale_id:
                    return HttpResponse("分配错误,无销售顾问")
                try:
                    with transaction.atomic():
                        form.instance.consultant_id=sale_id
                        form.instance.recv_date=current_time
                        form.instance. last_consult_date=current_time
                        customer_obj=form.save()
                        models.CustomerDistribution.objects.create(user_id=sale_id,
                                                                   customer=customer_obj,
                                                                  ctime=current_time)
                        message.send_message("第一次发邮件","嘻嘻","228341671@qq.com","小海")
                        print("发完了")
                except Exception as e:
                    single.rollback(sale_id)
                    return HttpResponse("录入异常！！！")
                return HttpResponse("录入成功！")
            else:
                return render(request, "single.html", {"form": form})



