from django.urls import path, include, re_path
from .views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView, LogoutView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # path(r'register/', views.register, name='register'), # 注册
    # path(r'register_handle/', views.register_handle, name='register_handle'), #注册处理
    path(r'register/', RegisterView.as_view(), name='register'),
    re_path(r'active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    path(r"login/", LoginView.as_view(), name='login'),
    path(r'logout/', LogoutView.as_view(), name='logout'),
    # path('', login_required(UserInfoView.as_view()), name='user'),  # 用户中心信息页
    # path('order/', login_required(UserOrderView.as_view()), name='order'),  # 用户中心订单页
    # path('address/', login_required(AddressView.as_view()), name='address'),  # 用户中心地址页
     path('', UserInfoView.as_view(), name='user'),  # 用户中心信息页
     path('order/', UserOrderView.as_view(), name='order'),  # 用户中心订单页
     path('address/', AddressView.as_view(), name='address'),  # 用户中心地址页

]
