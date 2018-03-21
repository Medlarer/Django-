from django.conf import settings

def init_permission(user,request):
    """
    初始化权限信息，获取权限信息并放置到session中。
    :param user:
    :param request:
    :return:
    """
    permission_list = user.roles.values("permission__id",
                                      "permission__title",
                                      "permission__url",
                                      "permission__code",
                                      "permission__menu_gp_id",
                                      "permission__group_id",
                                      "permission__group__menu_id",
                                      "permission__group__menu__title").distinct()
    #菜单相关（以后再匹配）
    sub_permission_list=[]
    for item in permission_list:
        tpl={
            "id":item["permission__id"],
            "title":item["permission__title"],
            "url":item["permission__url"],
            "menu_gp_id":item["permission__menu_gp_id"],
            "menu_id":item["permission__group__menu_id"],
            "menu_title":item["permission__group__menu__title"],
        }
        sub_permission_list.append(tpl)
    request.session[settings.PERMISSION_MENU_KEY]=sub_permission_list
    # print(1111)
    #权限相关
    result={}
    for item in permission_list:
        group_id =item["permission__group_id"]
        code=item["permission__code"]
        url=item["permission__url"]
        if group_id in result:
            result[group_id]["code"].append(code)
            result[group_id]["urls"].append(url)
        else:
            result[group_id]={
                "code":[code,],
                "urls":[url,]
            }
    # print(result)
    request.session[settings.PERMISSION_URL_DICT_KEY] = result