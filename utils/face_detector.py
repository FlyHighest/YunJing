import cv2
import sys
import os.path
from io import BytesIO
import httpx
def detect_pil(gray, cascade):

    faces = cascade.detectMultiScale(gray,
                                     # detector options
                                     scaleFactor = 1.1,
                                     minNeighbors = 5,
                                     minSize = (16, 16))
    return len(faces) > 0

class FaceDetector:
    def __init__(self,device=None):
        self.anime_face_detector = cv2.CascadeClassifier("utils/lbpcascade_animeface.xml")
        self.front_face_detector = cv2.CascadeClassifier("utils/lbpcascade_frontalface.xml")
        self.profile_face_detector = cv2.CascadeClassifier("utils/lbpcascade_profileface.xml")

    
    def detect(self,img:str):
        img_bytes = httpx.get(img).content
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        gray = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2GRAY)
        gray = cv2.equalizeHist(gray)
        return detect_pil(gray,self.anime_face_detector) or detect_pil(gray ,self.front_face_detector) \
                or detect_pil(gray ,self.profile_face_detector)
    
if __name__=="__main__":
    from PIL import Image
    import glob
    import numpy as np
    fd=FaceDetector()
    for i in glob.glob("testimage/*g"):
        print(i)
        print(fd.detect(Image.open(i)))