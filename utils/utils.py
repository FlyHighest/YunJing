import os 
from pywebio_battery import get_localstorage
from tornado.web import  decode_signed_value
from secret import verif_secret


def get_username(token_name="pywebio_auth_token",secret=verif_secret):
    token = get_localstorage(token_name)  # get token from user's web browser
    # try to decrypt the username from the token
    username = decode_signed_value(secret, token_name, token, max_age_days=7)
    if username:
        return username.decode('utf8')
    else:
        return None