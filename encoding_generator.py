import cv2
import os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("C:/Users/Pramodh AVG/FaceRecognition/FaceRecognition/serviceAccountKey.json")

firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-50dca-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-50dca.firebasestorage.app"
    })

#importing the mode images into list
folderPath = 'Images'
PathList = os.listdir(folderPath)                 #Lists all the images from the modes
imgList = []
studentIds = []
print(PathList)

for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))   #Importing the cv2 image
    studentIds.append(os.path.splitext(path)[0])                #splitting the regno and jpeg
    #print(path)
    #print(os.path.splitext(path)[0])
    fileName = f'{folderPath}/{path}'                           #Stores the Images Folder in Firebase
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:                                                            #opencv uses bgr
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)                                     #face_recognition uses rgb
        encode = face_recognition.face_encodings(img)[0]                              #conversion from bgr to rgb
        encodeList.append(encode)

    return encodeList

print("Encoding started....")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIdts = [encodeListKnown,studentIds]
#print(encodeListKnown)                                             #array
print("Encoding Complete")

#Store it in a pickle file, so that we can import when we're using the webcam
#Save the encodings in a file and save the names or the IDS in another file


file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIdts,file)
file.close()
print("File Saved")