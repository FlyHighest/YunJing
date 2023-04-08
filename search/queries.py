# 写一个函数，根据传入的内容，输出查询结果并构造json返回。
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
    #select image.imgurl, image.height,image.width,user.username,image.genid,image.prompt,image.face from image left outer join user on (image.userid_id=user.userid) where image.published=1 and user.username='TerryZhang' and image.modelname='GF2+3' and match(image.prompt) against('girl' in boolean mode) order by image.score desc;
    if keyword!="":
        keyword = f"and match(image.prompt) against('{keyword}' in boolean mode) "
    if model in MODEL_NAME_MAPPING:
        model = f"and image.modelname='{MODEL_NAME_MAPPING[model]}' "
    else:
        model = ""
    if username!="":
        username = f"and user.username='{username}'"
    
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

def query_recent_images(): # limit 1000
    face_detector = FaceDetector()
    mysql_db = pymysql.connect(
        host=mysql_db_host,
        database=mysql_db_database,
        user=mysql_db_user,
        password=mysql_db_password,
        autocommit=True
    )
    sql = "select image.imgurl, image.height,image.width,user.username,image.genid,image.prompt,image.face from image left outer join user on (image.userid_id=user.userid) where image.published=1 order by image.score desc limit 500;"
    cursor = mysql_db.cursor()
    cursor.execute(sql)
    query_result = cursor.fetchall()

    total = len(query_result)
    results = []
    for i in range(total):
        image, height,width,username,genid,prompt,face = query_result[i]
        if face is None:
            try:
                face = face_detector.detect(image)
                face_int = 1 if face else 0 
                sql = f"update image set face={face_int} where genid=\"{genid}\""
                cursor.execute(sql)
                print(image, face_int)
            except:
                traceback.print_exc()
                print(image,"error")
        if face==1:
            if random.randint(1,5)!=1:
                continue 
        results.append({
            "image": image,
            "height": height,
            "width": width,
            "username": username,
            "genid": genid
        })
    random.shuffle(results)
    cursor.close()
    mysql_db.close()
    return results