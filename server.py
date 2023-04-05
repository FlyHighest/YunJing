import tornado.ioloop
import tornado.web
import os
from pywebio.platform.tornado import webio_handler
from search import SearchHandler
from pages import page_gallery,page_help,page_index,page_main,page_account
from secret import server_port
if __name__ == '__main__':
    reconnect_timeout = 600
    cdn = "/statics/html"
    application = tornado.web.Application([
        (r'/favicon.ico()', tornado.web.StaticFileHandler,{"path":os.path.join(os.path.dirname(__file__),"statics/favicon.ico")}),
        ('/', webio_handler(page_index, cdn=cdn,reconnect_timeout=reconnect_timeout)),
        ('/main', webio_handler(page_main, cdn=cdn,reconnect_timeout=reconnect_timeout)),
        ('/gallery', webio_handler(page_gallery, cdn=cdn,reconnect_timeout=reconnect_timeout)),
        ('/help', webio_handler(page_help, cdn=cdn,reconnect_timeout=reconnect_timeout)),
        ('/account', webio_handler(page_account, cdn=cdn,reconnect_timeout=reconnect_timeout)),
        (r'^/statics/(.*)$', tornado.web.StaticFileHandler,{"path":os.path.join(os.path.dirname(__file__),"statics")}),
        
    ])
    application.listen(port=server_port, address='localhost')
    tornado.ioloop.IOLoop.current().start()
