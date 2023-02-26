import time
from functools import partial

from pywebio import config, session
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import *
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

def show_useragreement():
    with popup("用户协议和隐私政策"):
        put_markdown("""
## 用户协议

欢迎使用我们的图像生成网站。在使用本网站之前，请仔细阅读以下协议。使用本网站即表示您同意以下条款和条件。

### 1. 使用限制
您不得将本网站用于任何非法目的。您不得以任何方式损害本网站的运作或影响其他用户的使用。您不得尝试未经授权地访问本网站的任何部分或功能。

### 2. 知识产权
您可以任意复制、分发、传播、修改、发布您使用本网站生成的图像。同时，我们拥有本网站中的您发布到画廊的材料和内容的知识产权。

### 3. 免责声明
本网站仅供娱乐和教育目的使用。我们不对任何结果的准确性、完整性、及时性、可靠性、适用性或合法性做出任何保证。我们不对您使用本网站的任何后果负责，包括任何直接或间接的损失或损害。

### 4. 隐私政策
我们尊重您的隐私，并且会根据我们的隐私政策保护您的个人信息。请在使用本网站之前仔细阅读我们的隐私政策。

### 5. 修改协议
我们保留随时修改本协议的权利。我们会在本网站上发布更新的协议。继续使用本网站即表示您同意新协议的条款。

### 6. 管辖法律
本协议受中华人民共和国法律管辖。

如果您有任何问题或疑问，请联系我们。

谢谢您使用我们的图像生成网站！

## 隐私政策

本隐私政策解释了我们如何收集、使用、处理和保护您的个人信息。在使用本网站之前，请仔细阅读以下政策。如果您有任何问题或疑虑，请联系我们。

### 1. 收集信息
当您使用本网站时，我们可能会收集您的个人信息。这些信息包括但不限于您的姓名、电子邮件地址、IP地址、浏览器类型、设备类型、操作系统、访问日期和时间、页面浏览量和其他与您相关的信息。

### 2. 使用信息
我们会使用您的个人信息来改进本网站的功能和性能，以及为您提供更好的用户体验。我们可能会使用您的信息来跟踪和分析流量、识别您的兴趣和偏好、与您联系、处理您的请求和订单，以及满足法律要求。

### 3. 信息保护
我们采取适当的措施来保护您的个人信息。我们会使用安全协议和加密技术来保护您的信息免遭未经授权的访问、使用或泄漏。我们只允许授权人员访问您的信息，并会尽一切努力保护您的信息的机密性和完整性。

### 4. 信息分享
我们不会将您的个人信息出售、出租或出借给第三方。但在某些情况下，我们可能会与第三方分享您的信息，例如：为了执行法律要求、防止欺诈或安全问题、改善本网站的性能或满足您的请求。我们会确保您的信息仅限于必要的范围内共享，并会采取适当的措施确保您的信息的安全和保密。

### 5. 未成年人保护
我们不会故意收集未满18岁的儿童的个人信息。如果您是未成年人，请不要使用本网站或向我们提供您的个人信息。

### 6. 修改政策
我们保留随时修改本政策的权利。我们会在本网站上发布更新的政策。继续使用本网站即表示您同意新政策的条款。

如果您有任何问题、疑虑或建议，请随时联系我们。我们将尽力解答您的问题并解决您的问题。

谢谢您使用我们的图像生成网站！
        
""")

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
            def check_checkbox(val):
                if not val:
                    return "请勾选后继续"
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
        if session.local.rclient.check_email_exists(inp):
            return "该电邮地址已被注册"

    def check_verif(code):
        if user_input["expected_code"]!=code:
            return "验证码错误"

    def send_mail(target_address, verif_code,times):
        if check_email(target_address) is not None:
            toast("地址错误或已被注册")
            return 
        if 'last_sendmail_time' not in session.local or time.time() - session.local.last_sendmail_time > 60:
            session.local.last_sendmail_time = time.time()

            success = send_verification_mail(target_address=target_address ,verif_code=verif_code, times=times)
            if success:
                toast("验证码已发送，请查看邮箱")
            else:
                toast("验证码发送失败，请联系管理员")
        else:
            toast("1分钟内只能发送一次",color="warn")

    token = get_localstorage(token_name)  # get token from user's web browser
    # try to decrypt the username from the token
    username = decode_signed_value(secret, token_name, token, max_age_days=expire_days)
    if username:
        username = username.decode('utf8')
    
    if not token or not username:  # no token or token validation failed
        wait_time = 1
        times=0
        while True:
            times+=1
            random_code = generate_random_code()
            user_input["expected_code"] = random_code
            user_input["email"] = ""
            info = input_group('注册新账户', [
                input("用户名", name='username', validate=check_username,help_text="用户名小于20个字，允许汉字、字母和数字"),
                input("密码", type=PASSWORD,onchange=get_firstpass, validate=check_pass,name='password1'),
                input("重复密码", type=PASSWORD,validate=check_secondpass, name='password2'),
                input("邮箱", name='email',validate=check_email,onchange=get_email,action=("发送验证码",lambda x: send_mail(target_address=user_input["email"] ,verif_code=random_code,times=times))),
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
        
    login_auth(session.local.rclient.verif_user, secret=verif_secret )
    session.run_js("location.reload();")

def show_register():
    register_auth(session.local.rclient.register_user,session.local.rclient.verif_user, secret=verif_secret )
    session.run_js("location.reload();")

def show_forgetpasswd():

    user_input = {}
    def get_email(email):
        user_input["email"] = email

    def check_username(username):
        sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])","",username)
        if username!=sub_str:
            return "仅允许汉字、字母和数字"
        if len(username)>20 or len(username)<1:
            return "用户名长度不符合要求（1-20）"
        if session.local.rclient.get_userid(username) is None:
            return "用户名尚未注册"
    def get_username(p):
        user_input["username"]=p

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
        if not session.local.rclient.check_user_email(user_input["username"],inp):
            return "此邮箱和注册时填写的邮箱不一致"
        

    def check_verif(code):
        if user_input["expected_code"]!=code:
            return "验证码错误"

    def send_mail(target_address, verif_code,times=1):
        if check_email(target_address) is not None:
            toast("地址错误或已被注册")
            return 
        if 'last_sendmail_time' not in session.local or time.time() - session.local.last_sendmail_time > 60:
            session.local.last_sendmail_time = time.time()

            success = send_verification_mail(target_address=target_address ,verif_code=verif_code,times=times)
            if success:
                toast("验证码已发送，请查看邮箱")
            else:
                toast("验证码发送失败，请联系管理员")
        else:
            toast("1分钟内只能发送一次",color="warn")
    
    wait_time = 1
    times=0
    while True:
        times+=1
        random_code = generate_random_code()
        user_input["expected_code"] = random_code
        user_input["email"] = ""
        info = input_group('重置密码', [
            input("用户名", name='username', onchange=get_username,validate=check_username,help_text="您注册的用户名"),
            input("密码", type=PASSWORD,onchange=get_firstpass, validate=check_pass,name='password1'),
            input("重复密码", type=PASSWORD,validate=check_secondpass, name='password2'),
            input("邮箱", name='email',validate=check_email,onchange=get_email,action=("发送验证码",lambda x: send_mail(target_address=user_input["email"] ,verif_code=random_code,times=times))),
            input("验证码", name='verif_answer',validate=check_verif),
            actions('', [
                {'label': '重置', 'color': 'warning', 'value':'signup'},
            ], name='action')
        ])

        if  info['verif_answer']!=random_code:
            toast("验证码错误")
            with put_loading():
                time.sleep(wait_time)
                wait_time *= 1.1
            continue

        ok = session.local.rclient.reset_pass_and_email(info['username'],info['password1'],info['email'])
        if not ok:
            toast(f'重置失败，请稍后再试或联系管理员解决', color='error')
            continue
        else:
            break 
    session.run_js("location.reload();")



def show_resetemail():

    user_input = {}
    def get_email(email):
        user_input["email"] = email

    def check_username(username):
        sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])","",username)
        if username!=sub_str:
            return "仅允许汉字、字母和数字"
        if len(username)>20 or len(username)<1:
            return "用户名长度不符合要求（1-20）"
        if session.local.rclient.get_userid(username) is None:
            return "用户名尚未注册"

    def get_username(p):
        user_input["username"]=p

    def get_firstpass(p):
        user_input["first_p"] = p 

    def check_pass(p):
        if len(p)<6:
            return "密码过短，长度至少大于6"

        
    def check_email(inp):
        if "@" not in inp:
            return "请输入有效的电子邮箱地址"
     
        

    def check_verif(code):
        if user_input["expected_code"]!=code:
            return "验证码错误"

    def send_mail(target_address, verif_code,times=1):
        if check_email(target_address) is not None:
            toast("地址错误或已被注册")
            return 
        if 'last_sendmail_time' not in session.local or time.time() - session.local.last_sendmail_time > 60:
            session.local.last_sendmail_time = time.time()

            success = send_verification_mail(target_address=target_address ,verif_code=verif_code,times=times)
            if success:
                toast("验证码已发送，请查看邮箱")
            else:
                toast("验证码发送失败，请联系管理员")
        else:
            toast("1分钟内只能发送一次",color="warn")
    
    wait_time = 1
    times = 0
    while True:
        times += 1
        random_code = generate_random_code()
        user_input["expected_code"] = random_code
        user_input["email"] = ""
        info = input_group('修改邮箱', [
            input("用户名", name='username', onchange=get_username,validate=check_username,help_text="您注册的用户名"),
            input("密码", type=PASSWORD,onchange=get_firstpass, validate=check_pass,name='password1'),
            input("邮箱", name='email',validate=check_email,onchange=get_email,action=("发送验证码",lambda x: send_mail(target_address=user_input["email"] ,verif_code=random_code,times=times))),
            input("验证码", name='verif_answer',validate=check_verif),
            actions('', [
                {'label': '重置', 'color': 'warning', 'value':'signup'},
            ], name='action')
        ])

        if  info['verif_answer']!=random_code:
            toast("验证码错误")
            with put_loading():
                time.sleep(wait_time)
                wait_time *= 1.1
            continue

        username = info['username']
        ok = session.local.rclient.verif_user(username, info['password1']) and username!="匿名用户"
        if not ok:
            toast('请输入正确的用户名和密码', color='error')
            with put_loading():
                time.sleep(wait_time)
                wait_time *= 1.1
            continue

        ok = session.local.rclient.reset_pass_and_email(info['username'],info['password1'],info['email'])
        if not ok:
            toast('重置失败，请稍后再试或联系管理员解决', color='error')
            continue
        else:
            break 
    session.run_js("location.reload();")


    
def update_user_config():
    config = {} 
    config["autopub"] = True if pin['config_autopub']=="开启" else False 
    config["colnum"] = int(pin['config_colnum'])
    config["hisnum"] = int(pin['config_hisnum'])
    if session.local.rclient.update_user_config(session.local.client_id, config):
        toast("保存配置成功",duration=1)
    else:
        toast("保存配置失败",color="warn",duration=1)

@config(theme="minty", css_style=css, title='云景AI绘图平台',description="AI画图工具，输入文本生成图像，二次元、写实、人物、风景、设计素材，支持中文，图像库分享")
def page_account():
    session.set_env(title='云景 · 个人中心', output_max_width='80%')
    session.local.rclient: RClient = RClient()

    username = get_username()
    if username:
        session.local.client_id = session.local.rclient.get_userid(username)
    else:
    # 检查本地有没有cookie client id，如果没有，让服务器赋予一个。
        if get_cookie("client_id") is None or not get_cookie("client_id").startswith("@"):
            new_client_id = session.local.rclient.get_new_client_id()
            set_cookie("client_id", new_client_id)
        session.local.client_id = get_cookie("client_id")

    put_html(header_html_account)
    
    put_scope("login").style("text-align:center")
    put_scope("options").style("text-align:center")
    put_scope("userconfig")
    put_scope("check").style("text-align:center")
    if not username:
        with use_scope("options"):
            put_button("已有账号，点击登录",outline=True,onclick=show_login)
            put_button("没有账号，点击注册",outline=True,onclick=show_register)
            
            put_row([
                None,
                put_button("重置密码",link_style=True,onclick=show_forgetpasswd),
                put_button("修改邮箱",link_style=True,onclick=show_resetemail),
                None
            ],size="1fr 100px 100px 1fr")
            
            put_markdown("""
**注册**或**登录**代表您**同意**我们的用户协议和隐私政策：
            """)
            put_button("用户协议和隐私政策",color="primary",onclick=show_useragreement)
           
    else:
        with use_scope("login"):
            put_text("您已成功登录，欢迎您，"+username)
            # put_text("注册用户的历史记录保留7天，数量提升至200张；发布作品时会关联到您的用户名")
            sharerate,num_gen,num_pub = session.local.rclient.get_sharerate(session.local.client_id)
            put_text("您当前分享值为: {:.2f}% (生成数{} | 分享数{})".format(sharerate,num_gen,num_pub))
            put_text("（分享值小于10%，生成速度将受限; 生成数量低于100时不计算分享值）")
            put_button("退出登录",onclick=revoke_auth)

        with use_scope("userconfig"):
            config = session.local.rclient.get_user_config(session.local.client_id)
            if "autopub" in config and config["autopub"]==True:
                autopub_val = "开启"
            else:
                autopub_val = "关闭"
            if "colnum" in config:
                colnum_val = str(config["colnum"])
            else:
                colnum_val = "6"
            if "hisnum" in config:
                hisnum_val = str(config['hisnum'])
            else:
                hisnum_val = "200"
            put_markdown("-----")
            put_row([
                None,
                put_column([
                    put_radio("config_autopub", label="- 自动发布图像到画廊",options=["开启","关闭"],value=autopub_val),
                    put_select("config_colnum", label="- 画廊显示列数", options=["2","3","4","5","6","7","8"], value=colnum_val),   
                    put_select("config_hisnum", label="- 历史记录图像数", options=["10","20","50","80","110","140","170","200"],value=hisnum_val)                 
                ]),
                None
            ],size="20% 60% 20%")
            put_row([
                put_button("保存用户配置",onclick=update_user_config),
            ]).style("text-align:center")
           
            

        with use_scope("options"):
            clear()

        with use_scope("check"):
            user_level = session.local.rclient.get_user_level(session.local.client_id)
            if user_level==6:
                
                while True:
                    genid = session.local.rclient.get_check_image()
                    if genid is None:
                        break 
                    check_img = session.local.rclient.get_imgurl_by_id(genid)
                    put_image(check_img)
                    res_sfw = radio("Safe for work?",options=["SFW","NSFW"])
                    if res_sfw=="SFW":
                        session.local.rclient.record_publish(genid)
                        toast("已发布")
                    clear()
                put_text("审核队列为空")