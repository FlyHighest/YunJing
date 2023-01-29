import tornado.ioloop
import tornado.web
from pywebio.platform.tornado import webio_handler
from pages import page_shutdown

if __name__ == '__main__':
    reconnect_timeout = 600
    application = tornado.web.Application([
        ('/', webio_handler(page_shutdown, cdn=True,reconnect_timeout=reconnect_timeout)),
        ('/main', webio_handler(page_shutdown, cdn=True,reconnect_timeout=reconnect_timeout)),
        ('/gallery', webio_handler(page_shutdown, cdn=True,reconnect_timeout=reconnect_timeout)),

    ])
    application.listen(port=5001, address='localhost')
    tornado.ioloop.IOLoop.current().start()
