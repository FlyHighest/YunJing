import requests,os,httpx,json
from secret import chevereto_key
from PIL import Image

# 写一个函数，根据传入的内容，输出查询结果并构造json返回。
import pymysql,json
from secret import mysql_db_database,mysql_db_host,mysql_db_password,mysql_db_user



# 画廊中默认显示的图
mysql_db = pymysql.connect(
        host=mysql_db_host,
        database=mysql_db_database,
        user=mysql_db_user,
        password=mysql_db_password,
        autocommit=True
    )
#    sql = "select image.imgurl, image.height,image.width,user.username,image.genid from image left outer join user on (image.userid_id=user.userid) where published=1 order by gentime desc limit 1000;"
cursor = mysql_db.cursor()

sql = "select imgurl from histories"

cursor.execute(sql)
res = cursor.fetchall()
for r in res:
    u = r[0]
    genid = os.path.basename(u).split(".")[0]
    cursor.execute(f'update histories set genid="{genid}" where imgurl="{u}"')