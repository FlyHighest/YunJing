import tornado.ioloop
import tornado.web
from pywebio.platform.tornado import webio_handler

from pages import page_gallery,page_help,page_index,page_main

if __name__ == '__main__':
    application = tornado.web.Application([
        ('/', webio_handler(page_index, cdn=True)),
        ('/main', webio_handler(page_main, cdn=True)),
        ('/gallery', webio_handler(page_gallery, cdn=True)),
        ('/help', webio_handler(page_help, cdn=True))
    ])
    application.listen(port=5002, address='localhost')
    tornado.ioloop.IOLoop.current().start()
