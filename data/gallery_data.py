from __future__ import unicode_literals
from whoosh.analysis import LowercaseFilter, StopFilter, StemFilter
from whoosh.analysis import Tokenizer, Token
from whoosh.lang.porter import stem
from whoosh.qparser import QueryParser

import jieba
import re
import os 
from whoosh.index import create_in,open_dir
from whoosh.fields import TEXT, ID, SchemaClass,STORED
import time

STOP_WORDS = frozenset(('a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'can',
                        'for', 'from', 'have', 'if', 'in', 'is', 'it', 'may',
                        'not', 'of', 'on', 'or', 'tbd', 'that', 'the', 'this',
                        'to', 'us', 'we', 'when', 'will', 'with', 'yet',
                        'you', 'your', '的', '了', '和'))

accepted_chars = re.compile(r"[\u4E00-\u9FD5]+")


class ChineseTokenizerPlusSingleChar(Tokenizer):

    def __call__(self, text, **kargs):
        words = jieba.tokenize(text, mode="search")
        token = Token()
        word_set = set()
        for (w, start_pos, stop_pos) in words:
            is_chinese = accepted_chars.match(w) 
            if not is_chinese and len(w)<=1:
                continue
            word_set.add((w,start_pos,stop_pos))
            if is_chinese and len(w)>1:
                for idx, single_char in enumerate(w):
                    word_set.add((single_char, start_pos+idx, start_pos+idx+1))
                    
        for w, start_pos, stop_pos in word_set:
            token.original = token.text = w
            token.pos = start_pos
            token.startchar = start_pos
            token.endchar = stop_pos
            yield token


def ChineseAnalyzerPlusSingleChar(stoplist=STOP_WORDS, minsize=1, stemfn=stem, cachesize=50000):
    return (ChineseTokenizerPlusSingleChar() | LowercaseFilter() |
            StopFilter(stoplist=stoplist, minsize=minsize) |
            StemFilter(stemfn=stemfn, ignore=None, cachesize=cachesize))


analyzer = ChineseAnalyzerPlusSingleChar()

class Text2ImageSchema(SchemaClass):
    
    author = ID(stored=True)
    prompt = TEXT(stored=True,analyzer=analyzer)
    model = TEXT(stored=True,analyzer=analyzer)
    genid = ID(stored=True, unique=True)

def init_schema(dir_path):
    os.makedirs(dir_path)
    schema = Text2ImageSchema()
    ix = create_in(dir_path,schema,indexname="gallery_index")

class GalleryDataManager:
    def __init__(self,dir_path="GIndex") -> None:
        self.ix = open_dir(dir_path,indexname="gallery_index",schema=Text2ImageSchema())
    
    def add_item(self,author,prompt,model,genid):
        writer = self.ix.writer(timeout=10) 
        writer.add_document(author=author,prompt=prompt,model=model,genid=genid)
        writer.commit()

    def del_item(self,genid):
        writer = self.ix.writer(timeout=10)
        writer.delete_by_term("genid",genid)
        writer.commit()

    def search_prompt(self,keyword):
        ret = []
        with self.ix.searcher() as searcher:
            results = searcher.find("prompt",keyword)
            for r in results:
                ret.append(r["genid"])
        return ret

    def search(self,author,modelname,text):
        ret = []
        query_str = ''
        if author is not None:
            query_str += f'author:"{author}" '
        if modelname is not None:
            query_str += f'model:"{modelname}" '
        if text is not None:
            query_str += f'prompt:"{text}" '
        with self.ix.searcher() as searcher:
            parser=QueryParser("prompt",self.ix.schema)
            query = parser.parse(query_str)
            results = searcher.search(query,limit=200)
            for r in results:
                ret.append(r["genid"])
        return ret


if __name__=="__main__":
    init_schema("../GIndex")
    #g = GalleryDataManager()
    # g.add_item("张天宇","一个大皮球2","Anything-v5","123")
    #results= g.search_prompt("皮")
    #for r in results:
    #    print (r)
