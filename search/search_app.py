from .queries import *
from tornado.web import RequestHandler,Application

class SearchHandler(RequestHandler):

    def get(self):
        # 搜索参数
        query_type = self.get_argument("type")
        match query_type:
            case "recent":
                ret = query_recent_images()
        
        self.write(ret)
        