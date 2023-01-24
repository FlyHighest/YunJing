import time
from functools import partial

from pywebio import config, session
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio_battery.web import *
from tornado.web import create_signed_value, decode_signed_value
from typing import *
from utils.custom_exception import *
from data import RClient

from utils.constants import *
import re
import random 

def generate_random_cal():
    num = [1,2,3,4,5,6,7]
    op = ["*","+","-"]
    return f"{random.choice(num)}{random.choice(op)}{random.choice(num)}{random.choice(op)}{random.choice(num)}"

def login_auth(register_func,verify_func: Callable[[str, str], bool], secret: Union[str, bytes],
               expire_days=7, token_name='pywebio_auth_token') -> str:
    """Persistence authentication with username and password.

    You need to provide a function to verify the current user based on username and password. The ``basic_auth()``
    function will save the authentication state in the user's web browser, so that the authed user does not need
    to log in again.

    :param callable verify_func: User authentication function. It should receive two arguments: username and password.
        If the authentication is successful, it should return ``True``, otherwise return ``False``.
    :param str secret: HMAC secret for the signature. It should be a long, random str.
    :param int expire_days: how many days the auth state can keep valid.
       After this time, authed users need to log in again.
    :param str token_name: the name of the token to store the auth state in user browser.
    :return str: username of the current authed user

    Example:

    .. exportable-codeblock::
        :name: basic_auth
        :summary: Persistence authentication with username and password

        user_name = basic_auth(lambda username, password: username == 'admin' and password == '123',
                               secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__")
        put_text("Hello, %s. You can refresh this page and see what happen" % user_name)


    .. versionadded:: 0.4
    """

    token = get_localstorage(token_name)  # get token from user's web browser
    # try to decrypt the username from the token
    username = decode_signed_value(secret, token_name, token, max_age_days=expire_days)
    if username:
        username = username.decode('utf8')
    
    if not token or not username:  # no token or token validation failed
        wait_time = 1
        while True:
            random_cal = generate_random_cal()
            answer = eval(random_cal)
            info = input_group('登录', [
                input("用户名", name='username', help_text="用户名小于20个字，允许汉字、字母和数字"),
                input("密码", type=PASSWORD, name='password'),
                input("人机验证", name='verif_answer',help_text="请输入"+random_cal+"的答案"),
                actions('', [
                    {'label': '登录', 'value': 'signin'},
                    {'label': '注册', 'color': 'warning', 'value':'signup'},
                ], name='action')
            ])
            if (info['verif_answer'].isdigit() or info['verif_answer'][1:].isdigit()) and int(info['verif_answer'])!=answer:
                toast("验证问题错误",info['password'])
                with put_loading():
                    time.sleep(wait_time)
                    wait_time *= 2 
                continue

            if info['action'] == 'signup':
                signup_ok = register_func(info['username'],info['password'])
                if not signup_ok:
                    toast(f'用户名格式不正确或已被占用', color='error')
                    continue


            username = info['username']
            ok = verify_func(username, info['password']) and username!="匿名用户"
            if ok:
                # encrypt username to token
                signed = create_signed_value(secret, token_name, username).decode("utf-8")
                set_localstorage(token_name, signed)  # set token to user's web browser
                break
            else:
                toast(f'用户名或密码错误', color='error')
                with put_loading():
                    time.sleep(wait_time)
                    wait_time *= 2 

    return username

def revoke_auth(token_name='pywebio_auth_token'):
    """Revoke the auth state of current user

    :param str token_name: the name of the token to store the auth state in user browser.

    .. versionadded:: 0.4
    """
    set_localstorage(token_name, '')
    session.run_js("location.reload();")

from secret import verif_secret
@config(theme="minty", css_style=css)
def page_account():
    session.set_env(title='云景 · 个人中心', output_max_width='80%')
    session.local.rclient: RClient = RClient()
    put_html(header_html_account)
    put_scope("login").style("text-align:center")
    with use_scope("login"):
        username = login_auth(session.local.rclient.register_user,session.local.rclient.verif_user, secret=verif_secret )
        put_text("您已成功登录，欢迎您，"+username)
        put_text("注册用户的历史记录保留7天，数量提升至100张；发布作品时会关联到您的用户名")
        put_button("退出登录",onclick=revoke_auth)

