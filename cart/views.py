from django.http import JsonResponse
from django.shortcuts import render
from cart.models import *
from util.decorators import *
from books.models import *
import json

# Create your views here.

@login_required
def cart_add(request):
    # 商品加入购物车
    # 接收数据
    passport_id = request.session['passport_id']
    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')

    # 校验数据
    if not all([books_id,books_count]):
        return JsonResponse({'res':'0','errmsg':'数据不完整'})

    books = Books.objects.get_books_by_id(books_id=books_id)
    if books is None:
        #商品不存在
        return JsonResponse({'res':'2','errmsg':'商品不存在'})

    try:
        count = int(books_count)
    except Exception as e:
        # 商品数目不合法
        return JsonResponse({'res':'3','errmsg':'商品数目不合法'})
    # 添加商品到购物车
    # 购物车数据以dict形式存放在session中
    cart_items = Cart_item.objects.filter(passport_id=passport_id)
    # 校验是商品是否已在购物车
    is_cart = False
    for item in cart_items:
        book = item.books
        quantity = item.quantity
        if int(books_id) == int(book.id):
            is_cart = True
            cart_id = item.id
            books_count = int(books_count) + int(quantity)
    if int(books_count) > int(books.stock):
        return JsonResponse({'res':'4','errmsg':'库存不足'})

    # 购物车增改
    if is_cart:
        cart_item = Cart_item.objects.get(id=cart_id)
        cart_item.quantity = books_count
        cart_item.save()
    else:
        cart_item = Cart_item.objects.create(passport_id=passport_id,quantity=books_count,books_id=books_id)
    return JsonResponse({'res':'1'})

@login_required
def cart_count(request):
    '''获取购物车中的商品数量'''

    # 计算用户购物车商品的数量
    res = 0
    passport_id = request.session['passport_id']
    cart_items = Cart_item.objects.filter(passport_id = passport_id)
    if cart_items:
        for item in cart_items:
            res += int(item.quantity)
    return JsonResponse({'res':res})


@login_required
def cart_show(request):
    '''用户购物车页面'''
    passport_id = request.session.get('passport_id')
    # 获取用户购物车记录

    books_items = Cart_item.objects.filter(passport_id=passport_id)

    books_li = []
    total_count = 0
    total_price = 0

    for item in books_items:
        books = item.books
        # 单个商品的数量
        books.count = item.quantity
        # 单个商品的总价
        books_amount = int(books.count) * int(books.price)
        if books.count > 0:
            books_li.append(books)
            # 求购物车商品数量总和及总价格
            total_count += books.count
            total_price += books_amount

    context = {
        'books_li':books_li,
        'total_count':total_count,
        'total_price':total_price,
    }
    return render(request,'cart/cart.html',context)


@login_required
def cart_del(request):
    '''删除用户购物车中的信息'''
    # 接收数据
    passport_id = request.session.get('passport_id')
    books_id = request.POST.get('books_id')
    # 商品是否在购物车内
    if not all([books_id]):
        return JsonResponse({'res':'0','errmsg':'数据不完整'})

    books = Books.objects.get_books_by_id(books_id=books_id)
    if books is None:
        return JsonResponse({'res':'2','errmsg':'商品不存在'})

    # 删除商品信息,购物车数据库内数量改为0
    cart_item = Cart_item.objects.get(passport_id=passport_id,books_id=books_id)
    cart_item.quantity = 0
    cart_item.save()

    return JsonResponse({'res':'1'})


@login_required
def cart_update(request):
    '''更新购物车商品数目'''

    passport_id = request.session.get('passport_id')
    books_id = request.POST.get('books_id')
    books_count = request.POST.get('books_count')

    # 校验数据
    if not all([books_id,books_count]):
        return JsonResponse({'res':'1','errmsg':'数据不完整'})

    books = Books.objects.get_books_by_id(books_id=books_id)
    if books is None:
        return JsonResponse({'res':'2','errmsg':'商品不存在'})

    try:
        books_count = int(books_count)
    except Exception as e:
        return JsonResponse({'res':'3','errmsg':'商品数目必须为数字'})

    # 判断库存
    if books_count > books.stock:
        return JsonResponse({'res':'4','errmsg':'库存不足'})

    # 更新购物车数据库
    cart_item = Cart_item.objects.get(passport_id=passport_id,books_id=books_id)
    cart_item.quantity = books_count
    cart_item.save()

    return JsonResponse({'res':'5'})


