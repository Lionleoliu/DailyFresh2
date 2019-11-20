# 使用celery
from celery import Celery

# 创建一个celery的实例对象
from django.core.mail import send_mail

from dailyfresh2 import settings

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "dailyfresh2.settings")
django.setup()

BROKER_URL = 'redis://:sunck@127.0.0.1:6379/2'

app = Celery("celery_task.tasks", broker=BROKER_URL)


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    # 发送激活邮件
    # 组织邮件信息
    # 发邮件
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
        username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
