from secret import upload_key,upload_url
import json,httpx
import traceback

def upload_to_storage(img_path=None,img_bytes=None,expire=None):
    header = {
                "X-API-Key":upload_key
        }
    try:
        payload = {
            'format': 'json',
            'title': 'user generated image'
        }
        if expire is not None:
            payload['expiration']=expire

        if img_path is not None:
            files = [
                ('source', open(img_path,'rb'))
            ]
        else:
            files = [
                ('source', img_bytes)
            ]
        res = httpx.post(upload_url,
            timeout=20,
            files=files,headers=header,data=payload)
        assert res.status_code==200
        ret = json.loads(res.content.decode('utf-8'))
        return ret['image']["url"]
    except:
        traceback.print_exc()
        print("Error while uploading")
        return ""

class StorageTool:
    def __init__(self) -> None:
        self.header = {
                "X-API-Key":upload_key
        }
        
  
    def upload(self, img_path=None,img_bin=None,expire=None):
        try:
            payload = {
                'format': 'json',
                'title': 'user generated image'
            }
            if expire is not None:
                payload['expiration']=expire

            if img_path is not None:
                files = [
                    ('source', open(img_path,'rb'))
                ]
            else:
                files = [
                    ('source', img_bin)
                ]
            res = httpx.post(upload_url,
                timeout=20,
                files=files,headers=self.header,data=payload)
            assert res.status_code==200
            ret = json.loads(res.content.decode('utf-8'))
            return ret['image']["url"]
        except:
            traceback.print_exc()
            print("Error while uploading")
            return ""
