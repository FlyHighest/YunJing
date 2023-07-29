from utils.storage_tool import StorageTool

st = StorageTool()

import glob , os 
from tqdm import tqdm 
from PIL import Image 
imgs = glob.glob("/Users/zhangtianyu/Documents/gimages/*g")

d = dict()
output_file = open("output.txt","w")
print(len(imgs))
for img in tqdm(imgs):
    i = Image.open(img)
    i.save(img.replace(".jpeg",".webp"),"webp",quality=95)
    url = st.upload_tencent(img.replace(".jpeg",".webp"),"old-gallery")
    if url == "":
        continue 
    else:
        d[os.path.basename(img)] = url
        output_file.write(f"{os.path.basename(img)} {url}\n")
import json
json.dump(d,open("old-gallery.json","w"),indent=4)
