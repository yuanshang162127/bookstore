from django.shortcuts import redirect
from django.core.urlresolvers import reverse

# 登录判断装饰器
def login_required(view_func):
    def wrapper(request,*view_args,**view_kargs):
        if request.session.has_key('islogin'):
            # 用户已登录
            return view_func(request,*view_args,**view_kargs)
        else:
            # 跳转到登录界面
            return redirect(reverse('users:login'))
    return wrapper