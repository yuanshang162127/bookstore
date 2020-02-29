from botocore.paginate import Paginator
from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from util.decorators import login_required
from django.http import HttpResponse,JsonResponse
from users.models import Address
from books.models import Books
from order.models import OrderInfo, OrderBooks
from django_redis import get_redis_connection
from datetime import datetime
from django.conf import settings
from cart.models import Cart_item
from django.db import transaction
import os
import time
# Create your views here.


def order_place(request):
    # 访问提交订单页面
    if not request.session.has_key('islogin'):
        return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

    books_ids = request.POST.getlist('books_ids')
    passport_id = request.session.get('passport_id')


    # 校验数据
    if not all(books_ids):
        return redirect(reverse('cart:show'))

    # 用户收获地址
    try:
        addr = Address.objects.get(passport_id = passport_id,is_default=True)
    except Exception as e:
        addr = Address.objects.filter(passport_id=passport_id)[0]

    # 购物车信息
    books_li = []
    total_count = 0
    total_price = 0

    cart_items = Cart_item.objects.filter(passport_id=passport_id)
    for item in cart_items:
        if int(item.quantity) <=0:
            continue
        books = item.books
        books_count = item.quantity
        # 计算每一个商品条目的总数与总价
        books.count = books_count
        books.amount = int(books_count) * int(books.price)
        books_li.append(books)
        # 计算订单所有商品总数，总价
        total_count += int(books_count)
        total_price += books.amount

    # 商品运费，暂定为10，后续开发模块后修改
    transit_price = 10
    total_pay = total_price + transit_price

    books_ids = ','.join(books_ids)
    print(books_ids)
    context = {
        'addr': addr,
        'books_li': books_li,
        'total_count': total_count,
        'total_price': total_price,
        'transit_price': transit_price,
        'total_pay': total_pay,
        'books_ids': books_ids,
    }
    print('books_ids',books_ids)
    return render(request,'order/place_order.html',context)

@login_required
@transaction.atomic
def order_commit(request):
    '''提交订单'''
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    books_ids = request.POST.get('books_ids')
    print('add',addr_id,'pay',pay_method,'books',books_ids)
    # 校验数据
    if not all([addr_id,pay_method,books_ids]):
        return JsonResponse({'res':'1','errmsg':'数据不完整'})

    try:
        addr = Address.objects.get(id = addr_id)
    except Exception as e:
        return JsonResponse({'res':'2','errmsg':'地址信息错误'})

    if int(pay_method) not in OrderInfo.PAY_METHODS_ENUM.values():
        return JsonResponse({'res':'3','errmsg':'不支持的支付方式'})

    # 创建订单
    passport_id = request.session.get('passport_id')
    # 订单号
    order_id = datetime.now().strftime('%Y%m%d%H%M%S')+str(passport_id)
    # 运费，暂定为10，后序
    transit_price = 10

    total_count = 0
    total_price = 0

    # 创建一个保存点
    sid = transaction.savepoint()
    try:
        # 向订单信息表中添加一条记录
        order = OrderInfo.objects.create(
            order_id=order_id,
            passport_id=passport_id,
            addr_id=addr_id,
            total_count=total_count,
            total_price=total_price,
            transit_price=transit_price,
            pay_method=pay_method)

        # 向订单商品表添加订单商品的记录
        books_ids = books_ids.split(',')

        for id in books_ids:
            books = Books.objects.get_books_by_id(books_id=id)
            if books is None:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':'4','errmsg':'商品信息错误'})

            # 判断商品的库存
            cart_item = Cart_item.objects.get(passport_id=passport_id,books_id=id)
            count = cart_item.quantity
            if count >books.stock:
                transaction.savepoint_rollback(sid)
                return JsonResponse({'res':'5','errmsg':'商品库存不足'})

            # 创建一条订单商品记录
            OrderBooks.objects.create(
                order_id=order_id,
                books_id=id,
                count=count,
                price=books.price
            )

            # 增加商品的销量，减少商品库存
            books.sales += int(count)
            books.stock -= int(count)
            books.save()

            #计算商品的总数和总价
            total_count += int(count)
            total_price += int(count) * int(books.price)

            #购物车商品归零
            cart_item.quantity = 0
            cart_item.save()

        # 更新订单的商品总数和总金额
        order.total_count = total_count
        order.total_price = total_price
        order.save()

    except Exception as e:
        # 数据库错误，回滚
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res':'7','errmsg':'服务器错误'})

    # 提交事务
    transaction.savepoint_commit(sid)

    return JsonResponse({'res':'6'})


@login_required
def order_pay(request):
    '''订单支付'''

    # 接收订单id
    order_id = request.POST.get('order_id')
    print(order_id)
    # 数据校验
    if not order_id:
        return JsonResponse({'res': 1, 'errmsg': '订单不存在'})

    try:
        order = OrderInfo.objects.get(order_id=order_id,
                                      status=1,)
    except OrderInfo.DoesNotExist:
        return JsonResponse({'res': 2, 'errmsg': '订单信息出错'})


    # 模拟支付成功
    order.status = 2
    order.trade_id = datetime.now().strftime('%Y%m%d%H%M%S')
    order.save()

    return JsonResponse({'res':'3'})
























