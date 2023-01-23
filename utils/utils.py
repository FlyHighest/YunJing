import os 

def get_generation_id(img_url):
    return os.path.basename(img_url).split(".")[0]
