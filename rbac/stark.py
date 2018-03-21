from stark.service import v1
from . import models

class UserConfig(v1.StarkConfig):
    list_display = ["id","username","email"]
    edit_link = ["username"]
v1.site.register(models.User,UserConfig)

class PermissionConfig(v1.StarkConfig):
    list_display = ["id","title","url","code"]
    edit_link = ["title"]
v1.site.register(models.Permission,PermissionConfig)


class RoleConfig(v1.StarkConfig):
    list_display = ["id","title"]
    edit_link = ["title"]
v1.site.register(models.Role,RoleConfig)


class GroupConfig(v1.StarkConfig):
    list_display = ["id","caption"]
    edit_link = ["caption"]
v1.site.register(models.Group,GroupConfig)


class MenuConfig(v1.StarkConfig):
    list_display = ["id","title"]
    edit_link = ["title"]
v1.site.register(models.Menu,MenuConfig)