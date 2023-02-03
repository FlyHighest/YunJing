import requests,os,httpx,json
from secret import chevereto_key
from PIL import Image
url = "https://storage.yunjing.gallery/api/1/upload"
header = {
    "X-API-Key":chevereto_key
}
import glob
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
       
file_list = glob.glob("/root/images/*")
file_list.sort()

for image in file_list:
    payload = {
        'format': 'json',
        'title': os.path.basename(image)
    }
    img = Image.open(image)
    img.save(image+".jpeg",format="jpeg",quality=90)
    genid = os.path.basename(image).split(".")[0]
    files = [
        ('source', open(image+".jpeg",'rb'))
    ]
    res = httpx.post(url,files=files, headers=header,json=payload)
    #response = requests.request("POST", url, data = payload, content = files)
    print(res.status_code)
    ret = json.loads(res.content.decode('utf-8'))
    img_url = ret["image"]["url"]
    # update image and history
    sql1 = f'update image set imgurl="{img_url}" where genid="{genid}"'
    cursor.execute(sql1)
    # sql2 = f'update histories set genid="{genid}" where imgurl="{img_url}"'
    # cursor.execute(sql2)
    break 