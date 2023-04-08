import pymysql,json
from secret import mysql_db_database,mysql_db_host,mysql_db_password,mysql_db_user
import random 
from utils import FaceDetector
import traceback
from utils.constants import MODEL_NAME_MAPPING
# 画廊中默认显示的图

def query_by_input(keyword,model,username):
    mysql_db = pymysql.connect(
        host=mysql_db_host,
        database=mysql_db_database,
        user=mysql_db_user,
        password=mysql_db_password,
    )
    sql = f"select image.imgurl, image.height,image.width,user.username,image.genid,image.prompt,image.face from image left outer join user on (image.userid_id=user.userid) where image.published=1 {username} {model} {keyword} order by image.gentime desc;"

    cursor = mysql_db.cursor()
    cursor.execute(sql)
    query_result = cursor.fetchall()

    total = len(query_result)
    results = []
    for i in range(total):
        image, height,width,username,genid,prompt,face = query_result[i]
       
        results.append({
            "image": image,
            "height": height,
            "width": width,
            "username": username,
            "genid": genid
        })

    cursor.close()
    mysql_db.close()
    return results