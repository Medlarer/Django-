from django.conf.urls import url
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.shortcuts import render,HttpResponse,redirect
from django.urls import reverse
from django.forms import ModelForm, ModelChoiceField
from utils.pager import Pagination
from django.http import QueryDict
from django.db.models import ForeignKey,ManyToManyField
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel
import copy,json

class FilterOption(object):
    def __init__(self,field_name,multi=False,condition=None,is_choice=False,
                 text_func_name=None,val_func_name=None):
        """

        :param field_name: 字段名
        :param multi: 是否多选
        :param condition: 搜索条件
        :param is_choice: 是否是choice
        """
        self.field_name=field_name
        self.multi=multi
        self.condition=condition
        self.is_choice=is_choice
        self.text_func_name=text_func_name
        self.val_func_name=val_func_name

    def get_condition(self,field):
        if self.condition:
            return field.rel.to.objects.filter(**self.condition)
        # print(1,field.rel.to.objects.all())
        return field.rel.to.objects.all()

    def get_choice(self,field):
        return field.choices

class FilterRow(object):
    def __init__(self,option,data,request):
        self.option=option
        self.data=data
        self.request=request

    def __iter__(self):
        params=copy.deepcopy(self.request.GET)
        # print(1,params.urlencode())
        params._mutable=True
        current_id=params.get(self.option.field_name)#单选
        current_id_list=params.getlist(self.option.field_name)#多选

        if self.option.field_name in params:
            origin_list=params.pop(self.option.field_name)
            url="{0}?{1}".format(self.request.path_info,params.urlencode())
            # print(url)
            yield mark_safe("<a href='{0}'>全部</a>".format(url))
            params.setlist(self.option.field_name,origin_list)
            # print(3,params.urlencode())
        else:
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe("<a class='active'href='{0}'>全部</a>".format(url))
        for val in self.data:
            if self.option.is_choice:
                pk,text=str(val[0]),val[1]
            else:
                # pk,text=str(val.pk),str(val)
                # print(3,val)
                text=self.option.text_func_name(val) if self.option.text_func_name else str(val)
                pk=str(self.option.val_func_name(val)) if self.option.val_func_name else str(val.pk)
                # print(pk,text)
            if not self.option.multi:
                #单选
                # print(2,params.urlencode())
                params[self.option.field_name]=pk#赋值用这一次取到的值覆盖上一次的值
                # print(3,params.urlencode())
                url="{0}?{1}".format(self.request.path_info,params.urlencode())
                if current_id==pk:
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url,text))
                else:
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url,text))
            else:
                #多选
                clone_params=copy.deepcopy(params)
                id_list=self.request.GET.getlist(self.option.field_name)
                if pk in current_id_list:
                    # print(2,clone_params.urlencode())
                    id_list.remove(pk)
                    # print(id_list)
                    clone_params.setlist(self.option.field_name,id_list)
                    # print(3,clone_params.urlencode())
                    url = "{0}?{1}".format(self.request.path_info, clone_params.urlencode())
                    # print(4,url)
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))
                else:
                    id_list.append(pk)
                    clone_params.setlist(self.option.field_name, id_list)
                    url = "{0}?{1}".format(self.request.path_info, clone_params.urlencode())
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))



class ChangList(object):
    def __init__(self,config,queryset=None):
        self.config=config
        self.list_display=config.get_list_display()
        self.model_class=config.model_class
        self.request=config.request
        self.show_add_btn=config.get_show_add_btn()
        self.data_list=queryset
        self.actions=config.get_actions()
        self.com_filter=config.get_com_filter()
        self.edit_link=config.get_edit_link()
        self.show_com_filter=config.get_show_com_filter()
    #搜索
    def show_search_form(self):
        return self.config.show_search_form
    def show_search_form_val(self):
        return self.request.GET.get(self.config.search_key,"")

    #组合搜索

    def get_comb_filter(self):
        data_list = []
        for option in self.com_filter:
            field=self.model_class._meta.get_field(option.field_name)
            # print(field)
            if isinstance(field,ForeignKey):
                # data_list.append(field.rel.to.objects.all())
                # print(2,option.get_condition(field))
                row=FilterRow(option,option.get_condition(field),self.request)
                # print(row)
            elif isinstance(field,ManyToManyField):
                # data_list.append(field.rel.to.objects.all())
                row=FilterRow(option, option.get_condition(field), self.request)
            else:
                # data_list.append(field.choices)
                row=FilterRow(option,option.get_choice(field),self.request)
            yield row


    #下拉框批量操作
    def show_actions(self):
        return self.config.get_show_actions()
    def modify_actions(self):
        result=[]
        for func in self.actions:
            # print(111)
            temp={"name":func.__name__,"text":func.short_desc}
            # print(temp)
            result.append(temp)
            # print(result)
        return result
    def add_url(self):
        return self.config.get_add_url()

    def head_data(self):
        # 先处理表头
        result = []
        for field_name in self.list_display:
            if isinstance(field_name, str):
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self.config,is_header=True,)
            result.append(verbose_name)
        return result
    def body_data(self):
        # total_count = self.model_class.objects.all().count()
        # current_page = self.request.GET.get("page", 1)
        # page_obj=Pagination(current_page,total_count,self.request.path_info,self.request.GET,per_page_num=2)
        page_obj=self.page()
        data_list = self.data_list[page_obj.start:page_obj.end]
        # 处理表身
        new_data_list = []
        for data in data_list:
            tem = []
            for field_name in self.list_display:
                if isinstance(field_name, str):
                    col = getattr(data, field_name)
                else:
                    # print(field_name,self.config,data)
                    col = field_name(self.config,data,)
                if field_name in self.edit_link:
                    col=self.get_edit_link(data.pk,col)
                tem.append(col)
            new_data_list.append(tem)
        # print(new_data_list)
        return new_data_list

    def get_edit_link(self,pk,text):
        """
        点击生成的数据跳转到编辑页面修改数据
        :param pk: 要被修改对象的id
        :param text:要被修改对象的字段名
        :return:带有其他条件的编辑页面的url
        """
        query_str = self.request.GET.urlencode()
        if query_str:
            params = QueryDict(mutable=True)
            params[self.config.list_filter] = query_str
            return mark_safe("<a href='%s?%s'>%s</a>" % (self.config.get_edit_url(pk,), params.urlencode(),text))
        return mark_safe("<a href='%s'>%s</a>" % (self.config.get_edit_url(pk,),text))


    def page(self):
        total_count = self.model_class.objects.all().count()
        current_page = self.request.GET.get("page", 1)
        page_obj = Pagination(current_page, total_count, self.request.path_info, self.request.GET, per_page_num=5)
        self.page_obj=page_obj
        return self.page_obj

class StarkConfig(object):
    list_display = []
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site
        self.request=None
        self.list_filter="_list_filter"
        self.search_key="q"

    show_add_btn=True
    def get_show_add_btn(self):
        return self.show_add_btn

    show_com_filter=False
    def get_show_com_filter(self):
        return self.show_com_filter

    search_fields=[]
    def get_search_fields(self):
        list=[]
        if self.search_fields:
            list.extend(self.search_fields)
        return list
    #组合搜索
    com_filter=[]
    def get_com_filter(self):
        result=[]
        if self.com_filter:
            result.extend(self.com_filter)
        return result

    edit_link=[]
    def get_edit_link(self):
        result=[]
        if self.edit_link:
            result.extend(self.edit_link)
        return result

    def wrapper(self,views_func):
        def inner(request,*args,**kwargs):
            self.request=request
            return views_func(request,*args,**kwargs)
        return inner

    def checkbok(self, obj=None,is_header=False):
        if is_header:
            return "选择"
        return mark_safe("<input name='choice' value='%s' type='checkbox'/>" % (obj.id,))

    def edit(self, obj=None, is_header=False):
        if is_header:
            return "编辑"
        # name="stark:%s_%s_edit" %(self.model_class._meta.app_label,self.model_class._meta.model_name)
        # url=reverse(name,args=(obj.id,))
        query_str=self.request.GET.urlencode()
        # print(self)
        # print(query_str)
        if query_str:
            params=QueryDict(mutable=True)
            params[self.list_filter]=query_str
            return mark_safe("<a href='%s?%s'>编辑</a>" % (self.get_edit_url(obj.id,),params.urlencode()))
        return mark_safe("<a href='%s'>编辑</a>" %(self.get_edit_url(obj.id,)))

    def delete(self,obj=None, is_header=False):
        if is_header:
            return "删除"
        return mark_safe("<a href='%s'>删除</a>" % (self.get_delete_url(obj.id)))

    def get_urls(self):
        app_model_name=(self.model_class._meta.app_label,self.model_class._meta.model_name)
        url_patterns=[
            url(r"^$", self.wrapper(self.list_view),name="%s_%s_list" %(app_model_name)),
            url(r"^add/$", self.wrapper(self.add_view),name="%s_%s_add" %(app_model_name)),
            url(r"^(\d+)/edit/$", self.wrapper(self.edit_view),name="%s_%s_edit" %(app_model_name)),
            url(r"^(\d+)/delete/$", self.wrapper(self.delete_view),name="%s_%s_delete" %(app_model_name)),
        ]
        url_patterns.extend(self.extra_url())
        return url_patterns

    def extra_url(self):
        url_list=[]
        return url_list

    @property
    def urls(self):
        return self.get_urls()

    def get_edit_url(self,nid):
        name = "stark:%s_%s_edit" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url = reverse(name, args=(nid,))
        return url
    def get_delete_url(self,nid):
        name = "stark:%s_%s_delete" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url = reverse(name, args=(nid,))
        return url
    def get_add_url(self):
        name = "stark:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url = reverse(name)
        return url
    def get_list_url(self):
        name = "stark:%s_%s_list" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url = reverse(name)
        # page=self.request.GET.get("page")
        # print(page)
        # if page:
        #     url="%s?page=%s" %(url,page)
        return url

    show_search_form=False
    def get_show_search_form(self):
        return self.show_search_form

    show_action=False
    def get_show_actions(self):
        return self.show_action

    actions=None
    def get_actions(self):
        result=[]
        if self.actions:
            result.extend(self.actions)
        return result

    model_form_class=None
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class

        # class AddForm(ModelForm):
        #     class Meta:
        #         model = self.model_class
        #         fields = "__all__"
        meta=type("Meta",(object,),{"model":self.model_class,"fields":"__all__"})
        AddForm=type("AddForm",(ModelForm,),{"Meta":meta})
        return AddForm
    def get_list_display(self):
        data=[]
        if self.list_display:
            data.extend(self.list_display)
            # data.append(StarkConfig.edit)
            data.append(StarkConfig.delete)
        #也可以写成self,写成self就是实例化的对象调用，成方法了，
            data.insert(0,StarkConfig.checkbok)
        return data
    def get_search_condition(self):
        search_key=self.request.GET.get(self.search_key)
        # print(search_key)
        search_fields=self.get_search_fields()
        condition=Q()
        condition.connector = "or"
        if search_key and self.get_show_search_form():
            for field in search_fields:
                condition.children.append((field,search_key))
                # print(condition)
        return condition




    def list_view(self,request,*args,**kwargs):
        head_list = []
        # 先处理表头
        # print(self)
        if request.method == "GET":
            comb_condition = {}
            option_list = self.get_com_filter()
            # print(option_list)

            for key in request.GET.keys():
                value_list = request.GET.getlist(key)
                #他取到的是一个列表，不是只有一个值
                flag = False
                for option in option_list:
                    if option.field_name == key:
                        flag = True
                        break
                if flag:
                    comb_condition["%s__in" %key] = value_list
            # print(comb_condition)
            queryset=self.model_class.objects.filter(self.get_search_condition()).filter(**comb_condition).distinct()
            # print(queryset)
            # print(queryset.query)
            # print(self)
            cls_obj=ChangList(self,queryset)
            return render(request, "stark/list.html", {"cls": cls_obj})
        else:
            func_str=self.request.POST.get("list_action")
            func=getattr(self,func_str)
            ret=func(request)
            if ret:
                return ret

        # total_count=self.model_class.objects.all().count()
        # current_page=request.GET.get("page",1)
        # page_obj=Pagination(current_page,total_count,request.path_info,request.GET,per_page_num=2)
        # for field_name in self.get_list_display():
        #     if isinstance(field_name, str):
        #         verbose_name = self.model_class._meta.get_field(field_name).verbose_name
        #     else:
        #         verbose_name = field_name(self, is_header=True)
        #     head_list.append(verbose_name)
        # data_list=self.model_class.objects.all()[page_obj.start:page_obj.end]
        # #处理表身
        # new_data_list=[]
        # for obj in data_list:
        #     tem = []
        #     for field_name in self.get_list_display():
        #         if isinstance(field_name,str):
        #             col=getattr(obj,field_name)
        #         else:
        #             col=field_name(self,obj)
        #         tem.append(col)
        #     new_data_list.append(tem)
        # print(new_data_list)
        # print(head_list)
        # return render(request,
        #               "stark/list.html",
        #               {"head_list":head_list,
        #                "data_list":new_data_list,
        #                "show_add_btn":self.get_show_add_btn(),
        #                "add_url":self.get_add_url(),
        #                "page_obj":page_obj})

    def add_view(self,request,*args,**kwargs):
        AddForm=self.get_model_form_class()
        tag_id = request.GET.get("tag_id")
        if request.method == "GET":
            forms=AddForm()
            # if tag_id:
            #     model_class_name=self
            #     print(model_class_name)
            #     return render(request, "stark/add.html", {"forms": forms, "config": model_class_name})
            return render(request, "stark/add.html", {"forms": forms,"config":self})
            #自定义标签

            # from django.forms.boundfield import BoundField
            # from django.db.models import QuerySet
            # from django.forms import ModelChoiceField
            # new_forms=[]
            # for field_name in forms:
            #     temp={"is_pop":False,"url":None,"field_name":field_name}
            #     if isinstance(field_name.field,ModelChoiceField):
            #         # print(field_name.field, type(field_name.field))
            #         related_class=field_name.field.queryset.model
            #         if related_class in site._registry:
            #             app_model_name=(related_class._meta.app_label,related_class._meta.model_name)
            #             base_url=reverse("stark:%s_%s_add" %(app_model_name))
            #             pop_url="%s?tag_id=%s" %(base_url,field_name.auto_id)
            #             temp["is_pop"]=True
            #             temp["url"]=pop_url
            #     new_forms.append(temp)
            # print(type(forms))

        else:
            forms=AddForm(data=request.POST)
            if forms.is_valid():
                obj = forms.save()
                # print(obj)
                if tag_id:
                    #判断是不是popup函数
                    response={"obj_pk":None,"text":None,"tag_id":tag_id}
                    get_model_name=request.GET.get("model_name")
                    get_related_name=request.GET.get("related_name")
                    # print('dsad',get_related_name,get_model_name)
                    # print(obj._meta.related_objects)
                    for related_obj in obj._meta.related_objects:
                        #新创建的班级的类
                        model_name=related_obj.field.model._meta.model_name
                        related_name=related_obj.related_name
                        # print(1,model_name,related_name)
                        if (type(related_obj)== ManyToOneRel):
                            field_name=related_obj.field_name
                            # print(field_name)
                        else:
                            field_name="pk"
                        limit_choices_to = related_obj.limit_choices_to
                        # print(type(get_related_name))
                        # print(model_name,"2",get_model_name)
                        # print(related_name,"3",get_related_name)
                        if model_name==get_model_name and get_related_name==str(related_name):
                            # print(4)
                            if self.model_class.objects.filter(**limit_choices_to,pk=obj.pk).exists():
                                response["obj_pk"]=getattr(obj,field_name)
                                response["text"]=str(obj)
                                response["tag_id"]=tag_id
                                # pop_reponse = json.dumps(response, ensure_ascii=False)
                                return render(request, "stark/pop_response.html", {"json_dict": json.dumps(response, ensure_ascii=False)})
                    return render(request, "stark/pop_response.html",
                                  {"json_dict": json.dumps(response, ensure_ascii=False)})
                #注意不要逻辑错误，如果return 在for循环里面，就只会执行一次for循环
                else:
                    # print(1111)
                    return redirect(self.get_list_url())
            else:
                return render(request, "stark/add.html", {"forms": forms,"config":self})

    def edit_view(self,request,nid,*args,**kwargs):
        obj=self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_list_url())
        EditForm = self.get_model_form_class()
        if request.method=="GET":
            forms=EditForm(instance=obj)
            return render(request,"stark/edit.html",{"forms":forms})
        else:
            forms=EditForm(instance=obj,data=request.POST)
            if forms.is_valid():
                forms.save()
                query_str=self.request.GET.get(self.list_filter)
                list_url="%s?%s" %(self.get_list_url(),query_str)
                return redirect(list_url)
            else:
                return render(request, "stark/edit.html", {"forms": forms,"config":self})
    def delete_view(self,request,nid,*args,**kwargs):
        self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_list_url())

class StarkSite(object):
    def __init__(self):
        self._registry={}

    def register(self,model_class,stark_config_class=None):
        if not stark_config_class:
            stark_config_class=StarkConfig
        self._registry[model_class]=stark_config_class(model_class,self)

    def get_urls(self):
        url_patterns =[]
        for modle_class,stark_config_obj in self._registry.items():
            app_name=modle_class._meta.app_label
            modle_name=modle_class._meta.model_name
            # print(app_name,modle_name)
            curd_url=url(r"^%s/%s/" %(app_name,modle_name),(stark_config_obj.urls,None,None))
            # print(curd_url)
            url_patterns.append(curd_url)

        # print(url_patterns)
        return url_patterns
    @property
    def urls(self):
        return (self.get_urls(),None,'stark')

site=StarkSite()