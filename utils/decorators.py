from typing import Any
from pywebio import session
from .constants import *
from pywebio.output import toast 
import time 

class base_checker:
    def __init__(self) -> None:
        pass

    def __call__(self, func) -> Any:
        def wrapper(*args,**kwargs):
            return func(*args,**kwargs)

        return wrapper

def queue_checker(func):
    def wrapper(*args, **kwargs):
        if session.local.rclient.get_queue_size() > MAX_QUEUE:
            toast(queue_too_long_text, duration=2,color="warn")
            return None 
        else:
            res = func(*args, **kwargs)
            return res 
    return wrapper

def frequency_checker(func):
    def wrapper(*args, **kwargs):
        if 'last_task_time' not in session.local:
            session.local.last_task_time = time.time() - 5
        if time.time() - session.local.last_task_time <  5:
            toast(too_frequent_error_text, duration=2,color="warn")
            return None 
        else:
            session.local.last_task_time = time.time()
            res = func(*args, **kwargs)
            return res 
        
    return wrapper

def login_checker(func):
    def wrapper(*args, **kwargs):
        if session.local.client_id.startswith("@"):
            toast(not_login_error_text, duration=2,color="warn")
            return None 
        else:
            res = func(*args, **kwargs)
            return res 
        
    return wrapper

# 调用api之前检查
def api_checker(func):
    def wrapper(*args, **kwargs):

        if session.local.client_id.startswith("@"):
            toast(not_login_error_text, duration=2,color="warn")
            return None 
        
        if 'last_task_time' not in session.local:
            session.local.last_task_time = time.time() - 5
        if time.time() - session.local.last_task_time <  5:
            toast(too_frequent_error_text, duration=2,color="warn")
            return None 
        
        if session.local.rclient.get_queue_size() > MAX_QUEUE:
            toast(queue_too_long_text, duration=2,color="warn")
            return None 
        
        res = func(*args, **kwargs)
        return res 
        
    return wrapper


def cd_checker(func):
    def wrapper(*args, **kwargs):
        userid = session.local.client_id
        if session.local.rclient.exists_generation_lock(userid):
            toast(too_frequent_error_text, duration=2,color="warn")
            return None 
        else:
            # 分享率大于10的用户，固定为10；分享率小于10的，为60*（10-分享率）+10
            sharerate,_,_ = session.local.rclient.get_sharerate(userid)
            cool_down_time =  max(0, (10 - sharerate)*60) + 10
            session.local.rclient.set_generation_lock(userid, cd=cool_down_time)
        
        res = func(*args, **kwargs)
        return res 

    return wrapper
