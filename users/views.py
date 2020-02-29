from django.shortcuts import render,redirect,reverse
from users.models import Passport, Address
from util.decorators import login_required
from util.get_hash import get_hash
from django.http import JsonResponse, HttpResponseRedirect
import re

# Create your views here.
def register(request):
    '''显示用户注册页面'''
    if request.method == 'GET':
        return render(request,'users/register.html')
    elif request.method == 'POST':
        # 接收数据
        # print(request)
        username = request.POST.get('user_name','')
        password = request.POST.get('pwd','')
        cpassword = request.POST.get('cpwd','')
        email = request.POST.get('email','')
        print(username,password,email)
        # 数据校验
        if not all([username, password, email]):
            # 有数据为空
            return render(request, 'users/register.html', {'errmsg': '参数不能为空'})
        # 判断邮箱是否合法
        if not re.match(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            # 邮箱不合法
            return render(request, 'users/register.html', {'errmsg': '邮箱不合法'})
        if password != cpassword:
            return render(request, 'users/register.html', {'errmsg': '两次输入密码不一致'})
        # 校验用户是否存在
        user = Passport.objects.filter(username=username)
        if user:
            return render(request, 'users/register.html', {'errmsg': '用户名已存在'})
        user = Passport.objects.filter(email=email)
        if user:
            return render(request, 'users/register.html', {'errmsg': '此邮箱已被注册'})
        # 校验所有数据合法，增加新账户
        try:
            password = Passport.objects.create(
                username=username,
                password=password,
                email=email
            )
        except Exception as e:
            return render(request, 'users/register.html', {'errmsg': '注册失败'})
        print('注册成功')
    # 注册完，返回注册页
    return  redirect(reverse('books:index'))

def login(request):
    if request.method == 'GET':
        request.session['login_from'] = request.META.get('HTTP_REFERER', '/')
        if request.COOKIES.get('username'):
            username = request.COOKIES.get("username")
            checked = 'checked'
        else:
            username = ''
            checked = ''
        context = {
            'username': username,
            'checked': checked,
        }
        return render(request, "users/login.html", context)
        # 用户登录验证
        # 1.获取数据
    elif request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('pwd','')
        remember = request.POST.get('remember','')
        #校验数据是否为空
        if not all([username,password]):
            return render(request,'users/login.html',{'errmsg':'用户名或密码为空'})

        # 根据用户名密码，查找账户信息
        try:
            passport = Passport.objects.get(username=username,password=password)
        except Exception as e:
            return JsonResponse({'res': '0'})
        if passport:
            # 判断是否记住用户名
            print(passport)
            res = HttpResponseRedirect(request.session['login_from'])
            if remember=='true':
                res.set_cookie('username',username,max_age=7*24*3600)
            else:
                res.delete_cookie('username')

            # 记住登录状态
            request.session['islogin'] = True
            request.session['username'] = username
            request.session['passport_id'] = passport.id

            return res
        else:
            #用户不存在，账户或密码错误
            return JsonResponse({'res':'0'})

def logout(request):
    '''退出登录'''
    # 清除用户的session信息
    request.session.flush()
    return redirect(reverse('books:index'))

@login_required
def user(request):
    '''用户中心-信息页'''
    passport_id = request.session.get('passport_id')
    # 获取用户的基本信息
    addr = Address.objects.get_default_address(passport_id=passport_id)

    books_li = []

    context = {
        'addr':addr,
        'page':'users',
        'books_li':books_li,
    }

    return render(request,'users/user_center_info.html',context)


@login_required
def address(request):
    passport_id = request.session.get('passport_id')

    if request.method == 'GET':
        # 显示地址页面
        addr = Address.objects.get_default_address(passport_id=passport_id)
        return render(request,'users/user_center_site.html',{'addr':addr,'page':'address'})

    else:
        # 添加收获地址
        recipient_name = request.POST.get('username')
        recipient_addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone')

        # 校验数据是否为空
        if not all([recipient_name,recipient_addr,zip_code,recipient_phone]):
            return render(request,'users/user_center_site.html',{'errmsg':'参数不能为空'})

        Address.objects.add_one_address(passport_id=passport_id,
                                        recipient_name=recipient_name,
                                        recipient_addr=recipient_addr,
                                        recipient_phone=recipient_phone,
                                        zip_code=zip_code)

        return redirect(reverse('users:address'))


