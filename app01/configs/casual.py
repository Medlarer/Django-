from app01 import models
class single(object):
    """
    单条引入
    """
    users=None
    iter_users=None
    reset_status=False
    rollback_list=[]

    @classmethod
    def fetch_users(cls):
        salers=models.SaleRank.objects.all().order_by("-weight")
        #取到一个权重从大到小的列表
        data=[]
        count=0
        while True:
            flag=False
            for sale in salers:
                if count<sale.num:
                    data.append(sale.user_id)
                    flag=True
                else:
                    flag=False
            count+=1
            if not flag:
                break
        # print(salers)
        # print(data)
        #取到一个按权重分配的有序的销售顾问id的列表
        cls.users=data

    @classmethod
    def get_sale_id(cls):
        if cls.rollback_list:
            return cls.rollback_list.pop()
        if not cls.users:
            cls.fetch_users()
        if not cls.iter_users:
            cls.iter_users=iter(cls.users)
        try:
            user_id=next(cls.iter_users)
        except StopIteration as e:
            if cls.reset_status:
                cls.fetch_users()
                cls.reset_status=False
            cls.iter_users=iter(cls.users)
            user_id=cls.get_sale_id()
        return user_id

    @classmethod
    def reset(cls):
        cls.reset_status=True
    @classmethod
    def rollback(cls,nid):
        cls.rollback_list.insert(0,nid)

