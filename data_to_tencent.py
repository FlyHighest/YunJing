import pymysql,json
from secret import mysql_db_database,mysql_db_host,mysql_db_password,mysql_db_user
import random ,httpx
from utils import FaceDetector
import traceback
from utils.constants import MODEL_NAME_MAPPING
from utils.storage_tool import StorageTool
# 画廊中默认显示的图
from PIL import Image 
from io import BytesIO

st = StorageTool()

mysql_db = pymysql.connect(
    host=mysql_db_host,
    database=mysql_db_database,
    user=mysql_db_user,
    password=mysql_db_password,
    autocommit=True
)
sql = f"select image.imgurl,image.genid,image.userid_id from image where image.published=1;"

cursor = mysql_db.cursor()
cursor.execute(sql)
query_result = cursor.fetchall()

total = len(query_result)
results = []
for i in range(total):
    image_url, genid, userid = query_result[i]
    if "dong-liu" in image_url:
        continue 
    
    # get image from storage.yunjing
    img_bytes = httpx.get(image_url).content 
    img =Image.open(BytesIO(img_bytes))
    img.save("temp.webp",quality=90)

    st.upload_tencent("temp.webp",userid)


        

cursor.close()
mysql_db.close()
