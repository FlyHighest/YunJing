
import pymysql,json
from secret import mysql_db_database,mysql_db_host,mysql_db_password,mysql_db_user

mysql_db = pymysql.connect(
        host=mysql_db_host,
        database=mysql_db_database,
        user=mysql_db_user,
        password=mysql_db_password,
        autocommit=True
    )
cursor = mysql_db.cursor()
import json 
cursor.execute("select genid,height,width,params from image")
res = cursor.fetchall()
for r in res:
    genid, h,w,params = r 
    data = json.loads(params)
    hei,wid = data['height'],data['width']
    cursor.execute(f"update image set height={hei},width={wid} where genid={genid}; ")
    mysql_db.commit()