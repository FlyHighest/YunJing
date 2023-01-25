# 写一个函数，根据传入的内容，输出查询结果并构造json返回。
import pymysql,json
from secret import mysql_db_database,mysql_db_host,mysql_db_password,mysql_db_user



# 画廊中默认显示的图
def query_recent_images(): # limit 1000
    mysql_db = pymysql.connect(
        host=mysql_db_host,
        database=mysql_db_database,
        user=mysql_db_user,
        password=mysql_db_password
    )
    sql = "select image.imgurl, image.height,image.width,user.username from image left outer join user on (image.userid_id=user.userid) where published=1 order by gentime desc limit 1000;"
    cursor = mysql_db.cursor()
    cursor.execute(sql)
    query_result = cursor.fetchall()
    cursor.close()
    mysql_db.close()
    total = len(query_result)
    results = []
    for i in range(total):
        image, height,width,username = query_result[i]
       
        results.append({
            "image": image,
            "height": height,
            "width": width,
            "username": username
        })
    return results