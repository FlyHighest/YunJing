import os 
from whoosh.index import create_in,open_dir
from whoosh.fields import TEXT, ID, SchemaClass
from jieba.analyse import ChineseAnalyzer
import time
analyzer = ChineseAnalyzer()

class Text2ImageSchema(SchemaClass):
    author = ID(stored=True)
    prompt = TEXT(stored=True,analyzer=analyzer)
    model = TEXT(stored=True,analyzer=analyzer)
    genid = ID(stored=True,unique=True)

def init_schema(dir_path):
    os.makedirs(dir_path)
    schema = Text2ImageSchema()
    ix = create_in(dir_path,schema,indexname="gallery_index")

class GalleryDataManager:
    def __init__(self,dir_path="../GIndex") -> None:
        self.ix = open_dir(dir_path,indexname="gallery_index")
    
    def add_item(self,author,prompt,model,genid):
        writer = self.ix.writer(timeout=10) 
        writer.add_document(author=author,prompt=prompt,model=model,genid=genid)
        writer.commit()

    def search_prompt(self,keyword):
        ret = []
        with self.ix.searcher() as searcher:
            results = searcher.find("prompt",keyword)
            for r in results:
                ret.append(r)
        return ret

if __name__=="__main__":
    # init_schema("../GIndex")
    g = GalleryDataManager()
    #g.add_item("张天宇","一个大皮球2","Anything-v5","123")
    results= g.search_prompt("皮球")
    for r in results:
        print (r)
