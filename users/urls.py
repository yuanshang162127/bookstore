from django.conf.urls import url
from users import views
app_name = 'users'
urlpatterns = [
    url(r'^register/$',views.register,name='register'),#用户注册
    url(r'^login/$',views.login,name='login'),# 用户登录页面
    url(r'^logout/$',views.logout,name='logout'), # 用户登出
    url(r'^address/$', views.address, name='address'),
    url(r'^order/(?P<page>\d+)?/?$', views.order, name='order'), # 用户中心-订单页  增加分页功能
    url(r'^$', views.user, name='user'), # 用户中心-信息页

]
