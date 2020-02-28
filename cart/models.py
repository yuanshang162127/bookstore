from django.db import models
from db.base_model import BaseModel
from users.models import Passport
from books.models import Books

# Create your models here.

# 购物车条目表
class Cart_item(BaseModel):
    passport_id = models.IntegerField(unique=False)
    books = models.ForeignKey('books.Books',verbose_name='账户')
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 's_cart_item'




