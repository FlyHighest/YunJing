import pymysql ,redis,json 
from tqdm import tqdm 
import editdistance
from utils import MODEL_NAMES

def find_best_match(modelname):
    if modelname in MODEL_NAMES:
        return modelname
    res = None
    min_d = 100000
    for n in  MODEL_NAMES[::-1]:
        ed = editdistance.distance(n,modelname)
        if  ed < min_d:
            min_d = ed 
            res = n 
    return res 

mysql_db = pymysql.connect(
        host="127.0.0.1",
        database="yunjing",
        user="root",
        password="19941oO7",
    )
r=redis.Redis(decode_responses=True )

cursor = mysql_db.cursor()
cursor.execute("select genid,gentime from image;")

results = cursor.fetchall()
for res in tqdm(results):
    genid,gentime = res 
    gentime=str(gentime)
    
    r.hset(f"image:{genid}","gentime",gentime)
            
