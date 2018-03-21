import copy
class Pagination(object):
    def __init__(self, current_page,total_count,base_url,params,per_page_num=10,max_page_code=11):
        """
        自定义分页
        :param current_page:
        :param page_num:
        :param base_url:
        :param params:
        :param per_page_num:
        :param max_page_code:
        """
        try:
            current_page=int(current_page)
            if current_page < 1:
                current_page = 1
            self.current_page = current_page
        except Exception as e:
            current_page=1

        #总数据数
        self.total_count=total_count
        # URL前缀
        self.base_url=base_url
        #每页显示的最大数
        self.per_page_num=per_page_num
        #每页显示的最大页码
        self.max_page_code=max_page_code
        #最大页码
        page_num,remainder=divmod(self.total_count,self.per_page_num)
        if remainder:
            page_num=page_num+1
        self.page_num=page_num
        params=copy.deepcopy(params)
        params._mutable=True
        self.params=params

    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_num

    @property
    def end(self):
        return self.current_page * self.per_page_num

    def page_html(self):
        page_html_list = []
        self.params["page"]=1
        first = "<a class='active' href='%s?%s'>首页</a>" %(self.base_url,self.params.urlencode())
        self.half_page_code = (self.max_page_code - 1) / 2
        if self.page_num < self.max_page_code:
            page_start = 1
            page_end = self.page_num
        # elif self.page_num < 2:
        #     page_start=1
        #     page_end=1
        else:
            if self.current_page < self.half_page_code:
                page_start = 1
                page_end = page_start + self.max_page_code
            elif (self.half_page_code + self.current_page) > self.page_num:
                page_end = self.page_num
                page_start = self.page_num - self.max_page_code + 1
            else:
                page_start = self.current_page - self.half_page_code
                page_end =self.current_page + self.half_page_code
        page_html_list.append(first)
        self.params["page"]=self.current_page
        if self.current_page > 1:
            last = "<a class='active' href='%s?%s'>上一页</a>" % (self.base_url,self.current_page - 1,)
        else:
            last = "<a class='active' href='host/?page=1'>上一页</a>"
        page_html_list.append(last)
        for i in range(int(page_start), int(page_end)+1):
            self.params["page"] = i
            if i == self.current_page:
                temp = "<a class='active' href='%s?%s'>%s</a>" % (self.base_url, self.params.urlencode(),i)
            else:
                temp = "<a href='%s?%s'>%s</a>" % (self.base_url, self.params.urlencode(),i)
            page_html_list.append(temp)
        self.params["page"]=self.page_num
        end = "<a class='active' href='%s?%s'>尾页</a>" % (self.base_url,self.params.urlencode(),)
        if self.current_page < self.page_num:
            next = "<a class='active' href='%s?%s'>下一页</a>" % (self.base_url,self.current_page + 1,)
        else:
            next = "<a class='active' href='%s?%s'>下一页</a>" % (self.base_url,self.page_num,)
        page_html_list.append(next)
        page_html_list.append(end)
        page_html = "".join(page_html_list)
        return page_html

    def page_bootstrap_html(self):
        page_html_list = []
        self.params["page"]=1
        first = "<li><a class='active' href='%s?%s'>首页</a></li>" %(self.base_url,self.params.urlencode())
        self.half_page_code = (self.max_page_code - 1) / 2
        if self.page_num < self.max_page_code:
            page_start = 1
            page_end = self.page_num
        else:
            if self.current_page < self.half_page_code:
                page_start = 1
                page_end = page_start + self.max_page_code
            elif (self.half_page_code + self.current_page) > self.page_num:
                page_end = self.page_num
                page_start = self.page_num - self.max_page_code + 1
            else:
                page_start = self.current_page - self.half_page_code
                page_end =self.current_page + self.half_page_code
        page_html_list.append(first)
        if self.current_page > 1:
            self.params["page"] = self.current_page-1
            last = "<li><a  href='%s?%s'>上一页</a></li>" % (self.base_url,self.params.urlencode(),)
        else:
            self.params["page"] =  1
            last = "<li><a  href='%s?%s'>上一页</a></li>" %(self.base_url,self.params.urlencode())
        page_html_list.append(last)
        for i in range(int(page_start), int(page_end)+1):
            self.params["page"] = i
            if i == self.current_page:
                temp = "<li class='active'><a href='%s?%s'>%s</a></li>" % (self.base_url, self.params.urlencode(),i)
            else:
                temp = "<li><a href='%s?%s'>%s</a></li>" % (self.base_url, self.params.urlencode(),i)
            page_html_list.append(temp)
        self.params["page"]=self.page_num
        end = "<li><a href='%s?%s'>尾页</a></li>" % (self.base_url,self.params.urlencode(),)
        if self.current_page < self.page_num:
            self.params["page"]=self.current_page+1
            next = "<li><a href='%s?%s'>下一页</a></li>" % (self.base_url,self.params.urlencode(),)
        else:
            self.params["page"] = self.page_num
            next = "<li><a href='%s?%s'>下一页</a></li>" % (self.base_url,self.params.urlencode(),)
        page_html_list.append(next)
        page_html_list.append(end)
        page_html = "".join(page_html_list)
        return page_html

    # isinstance()