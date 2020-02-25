from django.conf.urls import url
from users import views

urlpatterns = [
    url(r'^registers/$',views.register,name='register'),#用户注册
]
