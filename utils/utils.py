import os 
from pywebio_battery import get_localstorage
from tornado.web import  decode_signed_value
from secret import verif_secret
from pywebio.io_ctrl import safely_destruct_output_when_exp
from pywebio.output import put_html,put_widget
import html 

@safely_destruct_output_when_exp('content')
def put_column_autosize(content=[], scope=None, position=-1):
    """Use column layout to output content. The content is arranged vertically

    :param list content: Content list, the item is ``put_xxx()`` call or ``None``. ``None`` represents the space between the output
    :param str size: Used to indicate the width of the items, is a list of width values separated by space.
        The format is the same as the ``size`` parameter of the `put_row()` function.
    :param int scope, position: Those arguments have the same meaning as for `put_text()`
    """

    return _row_column_layout_autosize(content, flow='row', scope=scope, position=position).enable_context_manager()


def _row_column_layout_autosize(content, flow, scope=None, position=-1):
    content = [c if c is not None else put_html('<div></div>') for c in content]
    
    style = 'grid-auto-flow: {flow};'.format(flow=flow)
    tpl = """
    <div style="display: grid; %s">
        {{#contents}}
            {{& pywebio_output_parse}}
        {{/contents}}
    </div>""".strip() % html.escape(style, quote=True)
    return put_widget(template=tpl, data=dict(contents=content), scope=scope,
                      position=position)

def get_username(token_name="pywebio_auth_token",secret=verif_secret):
    token = get_localstorage(token_name)  # get token from user's web browser
    # try to decrypt the username from the token
    username = decode_signed_value(secret, token_name, token, max_age_days=7)
    if username:
        return username.decode('utf8')
    else:
        return None