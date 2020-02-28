from django.db import models
from db.base_model import BaseModel
from util.get_hash import get_hash
# Create your models here.

class PassportManager(models.manager.Manager):
    def add_one_passport(self,username,password,email):
        '''添加一个用户信息'''
        passport = self.create(username=username,password=get_hash(password),email=email)
        print('注册成功')
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

    # # 用户的表管理器
    # objects = PassportManager()

    class Meta:
        db_table = 's_user_account'

class AddressManager(models.manager.Manager):
    '''地址模型类管理类'''
    def get_default_address(self,passport_id):
        '''查询指定账户的默认收获地址'''
        try:
            addr = self.get(passport_id=passport_id,is_default=True)
        except Exception as e:
            # 没有默认收货地址
            addr = None

    def add_one_address(self,passport_id,recipient_name,recipient_addr,zip_code,recipient_phone):
        '''添加收获地址'''
        # 判断用户是否有默认收货地址
        addr = self.get_default_address(passport_id=passport_id)
        if addr:
            is_default = False
        else:

            is_default = True

        # 添加一个地址
        addr = self.create(
            passport_id = passport_id,
            recipient_name = recipient_name,
            recipient_addr = recipient_addr,
            recipient_phone = recipient_phone,
            zip_code = zip_code,
            is_default = is_default
        )

        return  addr




class Address(BaseModel):
    '''地址模型类'''
    recipient_name = models.CharField(max_length=20,verbose_name='收件人')
    recipient_addr = models.CharField(max_length=256,verbose_name='收件地址')
    zip_code = models.IntegerField(verbose_name='邮政编码')
    recipient_phone = models.CharField(max_length=11,verbose_name='联系电话')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')
    passport = models.ForeignKey('Passport',verbose_name='账户')

    objects = AddressManager()

    class Meta:
        db_table = 's_user_address'

