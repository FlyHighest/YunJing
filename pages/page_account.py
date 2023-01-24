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
from utils import send_verification_mail, get_username
from utils.constants import *
import re
import random 
from secret import verif_secret


def generate_random_code():
    num = [1,2,3,4,5,6,7,8,9]
    return f"{random.choice(num)}{random.choice(num)}{random.choice(num)}{random.choice(num)}{random.choice(num)}{random.choice(num)}"

def generate_random_cal():
    num = [1,2,3,4,5,6,7]
    op = ["*","+","-"]
    return f"{random.choice(num)}{random.choice(op)}{random.choice(num)}{random.choice(op)}{random.choice(num)}"

@use_scope("login")
def login_auth(verify_func: Callable[[str, str], bool], secret: Union[str, bytes],
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
            def check_answer(inp):
                if not str(inp)==str(answer):
                    return "回答错误"

            info = input_group('登录', [
                input("用户名", name='username', help_text=""),
                input("密码", type=PASSWORD, name='password'),
                input("验证问题", validate=check_answer, name='verif_answer',help_text="请输入"+random_cal+"的答案"),
                actions('', [
                    {'label': '登录', 'value': 'signin'}], name='action')
            ])

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

def register_auth(register_func,verify_func: Callable[[str, str], bool], secret: Union[str, bytes],
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
    user_input = {}
    def get_email(email):
        user_input["email"] = email

    def check_username(username):
        sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])","",username)
        if username!=sub_str:
            return "仅允许汉字、字母和数字"
        if len(username)>20 or len(username)<1:
            return "用户名长度不符合要求（1-20）"
        if session.local.rclient.get_userid(username) is not None:
            return "用户名已被注册"
    
    def get_firstpass(p):
        user_input["first_p"] = p 

    def check_pass(p):
        if len(p)<6:
            return "密码过短，长度至少大于6"

    def check_secondpass(p):
        if p!=user_input["first_p"]:
            return "两次输入不一致"
        
    def check_email(inp):
        if "@" not in inp:
            return "请输入有效的电子邮箱地址"

    def check_verif(code):
        if user_input["expected_code"]!=code:
            return "验证码错误"

    def send_mail(target_address, verif_code):
        if 'last_sendmail_time' not in session.local or time.time() - session.local.last_sendmail_time > 60:
            send_verification_mail(target_address=user_input["email"] ,verif_code=random_code)
            session.local.last_sendmail_time = time.time()
        else:
            toast("1分钟内只能发送一次",color="warn")

    token = get_localstorage(token_name)  # get token from user's web browser
    # try to decrypt the username from the token
    username = decode_signed_value(secret, token_name, token, max_age_days=expire_days)
    if username:
        username = username.decode('utf8')
    
    if not token or not username:  # no token or token validation failed
        wait_time = 1
        while True:
            random_code = generate_random_code()
            user_input["expected_code"] = random_code
            info = input_group('注册新账户', [
                input("用户名", name='username', validate=check_username,help_text="用户名小于20个字，允许汉字、字母和数字"),
                input("密码", type=PASSWORD,onchange=get_firstpass, validate=check_pass,name='password1'),
                input("重复密码", type=PASSWORD,validate=check_secondpass, name='password2'),
                input("邮箱", name='email',validate=check_email,onchange=get_email,action=("发送验证码",lambda x: send_verification_mail(target_address=user_input["email"] ,verif_code=random_code))),
                input("验证码", name='verif_answer',validate=check_verif),
                actions('', [
                    {'label': '注册', 'color': 'warning', 'value':'signup'},
                ], name='action')
            ])

            if  info['verif_answer']!=random_code:
                toast("验证码错误")
                with put_loading():
                    time.sleep(wait_time)
                    wait_time *= 1.1
                continue

            signup_ok = register_func(info['username'],info['password1'],info['email'])
            if not signup_ok:
                toast(f'注册失败，请稍后再试或联系管理员解决', color='error')
                continue


            username = info['username']
            ok = verify_func(username, info['password1']) and username!="匿名用户"
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

def show_login():
    username = login_auth(session.local.rclient.verif_user, secret=verif_secret )
    session.run_js("location.reload();")

def show_register():
    username = register_auth(session.local.rclient.register_user,session.local.rclient.verif_user, secret=verif_secret )
    session.run_js("location.reload();")


@config(theme="minty", css_style=css)
def page_account():
    session.set_env(title='云景 · 个人中心', output_max_width='80%')
    session.local.rclient: RClient = RClient()

    username = get_username()
    if username:
        session.local.client_id = session.local.rclient.get_userid(username)
        print(session.local.client_id)
    else:
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
        if get_cookie("client_id") is None or not get_cookie("client_id").startswith("@"):
            new_client_id = session.local.rclient.get_new_client_id()
            set_cookie("client_id", new_client_id)
        session.local.client_id = get_cookie("client_id")

    put_html(header_html_account)
    
    put_scope("login").style("text-align:center")
    put_scope("options").style("text-align:center")

    if not username:
        with use_scope("options"):
            put_row([
                put_button("已有账号，点击登录",outline=True,onclick=show_login),
                None,
                put_button("没有账号，点击注册",outline=True,onclick=show_register),
            ])
    else:
        with use_scope("login"):
            put_text("您已成功登录，欢迎您，"+username)
            put_text("注册用户的历史记录保留7天，数量提升至100张；发布作品时会关联到您的用户名")
            put_button("退出登录",onclick=revoke_auth)
        with use_scope("options"):
            clear()



