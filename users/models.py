from django.db import models
from db.base_model import BaseModel
from util.get_hash import get_hash
# Create your models here.

class PassportManager(models.manager.Manager):
    def add_one_passport(self,username,password,email):
        '''添加一个用户信息'''
        passport = self.create(username=username,password=get_hash(password),email=email)
        return  passport

    def get_one_passport(self,username,password):
        try:
            passport = self.get(username=username,password=get_hash(password))
        except self.models.DoesNotExist:
            # 账户不存在
            passport = None
        return passport

class Passport(BaseModel):
    '''用户模型类'''
    username = models.CharField(max_length=20,unique=True,verbose_name='用户名称')
    password = models.CharField(max_length=40,verbose_name='用户密码')
    email = models.EmailField(verbose_name='用户邮箱')
    is_active = models.BooleanField(default=True,verbose_name='是否激活')

    # 用户的表管理器
    objects = PassportManager()

    class Meta:
        db_table = 's_user_account'
