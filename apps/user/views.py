from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.conf import settings
from .models import User, Address
from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from utils.mixin import LoginRequiredMixin
import re


# Create your views here.
def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    else:
        # 进行注册的处理
        # 接受数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        # 进行数据的校验
        if not all([username, password, email]):
            return render(request, "register.html", {"errmsg": "数据不完整"})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {"errmsg": "邮箱格式不正确"})

        if allow != "on":
            return render(request, "register.html", {"errmsg": "请同意协议"})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理 ： 进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 返回应答, 跳转到首页
        return redirect(reverse('goods:index'))


def register_handle(request):
    # 进行注册的处理
    # 接受数据
    username = request.POST.get("user_name")
    password = request.POST.get("pwd")
    email = request.POST.get("email")
    allow = request.POST.get("allow")

    # 进行数据的校验
    if not all([username, password, email]):
        return render(request, "register.html", {"errmsg": "数据不完整"})

    # 校验邮箱
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, "register.html", {"errmsg": "邮箱格式不正确"})

    if allow != "on":
        return render(request, "register.html", {"errmsg": "请同意协议"})

    # 校验用户名是否重复
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # 用户名不存在
        user = None

    if user:
        # 用户名已存在
        return render(request, 'register.html', {'errmsg': '用户名已存在'})
    # 进行业务处理 ： 进行用户注册
    user = User.objects.create_user(username, email, password)
    user.is_active = 0
    user.save()

    # 返回应答, 跳转到首页
    return redirect(reverse('goods:index'))


# /user/register/
class RegisterView(View):
    # 注册
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 进行注册处理
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        # 进行数据的校验
        if not all([username, password, email]):
            return render(request, "register.html", {"errmsg": "数据不完整"})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {"errmsg": "邮箱格式不正确"})

        if allow != "on":
            return render(request, "register.html", {"errmsg": "请同意协议"})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理 ： 进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件，包含激活链接： http://127.0.0.1:8000/user/active/3
        # 激活链接中需要包含用户的身份信息， 并且要把身份信息进行加密

        # 加密用户的身份信息，生成激活的token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode("utf8")

        # 发邮件
        send_register_active_email.delay(email, username, token)

        # 返回应答, 跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    # 用户激活
    def get(self, request, token):
        # 进行用户激活
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户id
            user_id = info["confirm"]

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse("user:login"))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse("激活链接已失效")


# /user/login/
class LoginView(View):
    def get(self, request):
        # 判断是否记住了用户名
        if "username " in request.COOKIES:
            username = request.COOKIES.get("username")
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {"username": username, "checked": checked})

    # 用户登录校验
    def post(self, request):
        # 接受数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")
        remember = request.POST.get("remember")

        # 数据校验
        if not all([username, password]):
            return render(request, 'login.html', {"errormsg": "账号或者密码缺失"})

        # 校验数据库是否存在该用户名和密码
        user = authenticate(username=username, password=password)
        # 判断用户是否激活,激活了回到首页，没激活提示账号未激活
        if user is not None:
            if user.is_active:
                # 保存登录状态到session中
                login(request, user)

                # 获取登录后所要跳转的地址
                # 默认跳转到首页
                next_url = request.GET.get("next", reverse('goods:index'))
                # 跳转到next_url
                print("next_url", next_url)
                response = redirect(next_url)
                # 通过判断checkbox的状态来查看是否需要记住用户名
                if remember == 'on':
                    response.set_cookie("username", username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie("username")
                return response

            else:
                return render(request, 'login.html', {"errormsg": "该账号未激活"})
        else:
            return render(request, 'login.html', {"errormsg": "用户名或密码错误"})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse("goods:index"))


# /user
class UserInfoView(LoginRequiredMixin, View):
    # 用户中心-信息页
    def get(self, request):
        # 显示
        # page:user
        # 获取用户的个人信息

        # 获取用户的历史浏览记录

        # 除了你给模板文件传递的模板变了之外，django框架会把request.user也传给模板文件
        return render(request, "user_center_info.html", {"page": "user", "address": address})


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    # 用户中心-订单页
    def get(self, request):
        # 获取用户的订单信息
        return render(request, "user_center_order.html", {"page": "order"})


# /user/address
class AddressView(LoginRequiredMixin, View):
    # 用户中心-信息页
    def get(self, request):
        # 显示
        # 获取用户的默认收货地址
        user = request.user
        #
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)

        return render(request, "user_center_site.html", {"page": "address", "address": address})

    def post(self, request):
        # 接受数据
        receiver = request.POST.get("receiver")
        addr = request.POST.get("addr")
        zip_code = request.POST.get("zip_code")
        phone = request.POST.get("phone")

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, "user_center_site.html", {"errormsg": "数据填写不完整"})

        if not re.match("1[0-9]{10}", phone):
            return render(request, "user_center_site.html", {"errormsg": "电话号码格式错误"})

        # 业务处理：添加收货地址

        # 需求： 如果地址不为默认地址添加的地址就为默认地址，不然为非默认地址
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user, receiver=receiver, addr=addr, zip_code=zip_code, phone=phone,
                               is_default=is_default)
        # 返回模板
        return redirect(reverse("user:address"))
