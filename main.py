import os
import cv2
import pickle
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

cred = credentials.Certificate("C:/Users/nitis/OneDrive/Desktop/FaceRecognition/serviceAccountKey.json")

firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-50dca-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-50dca.firebasestorage.app"
    }) 

bucket = storage.bucket()
cap = cv2.VideoCapture(1)           #1 = No of cameras we use
cap.set(3,490)                     #1423 = width
cap.set(4,380)                      #800 = height

imgBackground = cv2.imread('Resources/Modes/Background/Background.png')

#importing the mode images into list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)                 #Lists all the images from the modes
imgModeList = []
#print(modePathList)

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))   #Importing the cv2 image

#print(len(imgModeList))

#Load the encoding file
print("Loading Encoding File....")
file = open('EncodeFile.p','rb')                            #rb - reading
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown,studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encoding File Loaded")

modeType = 0                                                                        #0 means it will show active
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    #Squeeze in the images since it takes a lot of computation if the images are large
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)                                    #imgS -> Small Images
    imgS = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)                                     #face_recognition uses rgb

    #feed-in the images
    faceCurFrame = face_recognition.face_locations(imgS)                           #Location of the face in the images
    encodeCurFrame = face_recognition.face_encodings(imgS)                         #Encoding the current frames of the new images

    imgBackground[200:200+380,55:55+490] = img
    imgBackground[200:200+350,630:630+300] = imgModeList[modeType]                  #imgBackground[200:200+350,630:630+300] = imgModeList[modType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):                   #encodeFace -> encoding the current images     
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)       #Comparing the images in our list with the current encodeFace     
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            #print("matches",matches)
            #print("faceDis",faceDis)

            matchIndex = np.argmin(faceDis)
            #print("Match Index",matchIndex)

            if matches[matchIndex]:
                #print("Known Face Detected")
                #print(studentIds[matchIndex])

                y1,x2,y2,x1 = faceLoc
                #y1,x2,y2,x1 = y1 * 4 ,x2 * 4 ,y2 * 4 ,x1 * 4                 #*4 , since we reduced the image pixels by 0.25
                bbox = 55 + x1, 200 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=2)           #we can also give cv2.rect. And bbox = bounding box, rt = rectangle thickness

                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading", (275,400))
                    cv2.imshow("Face Attendance",imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
        
        if counter!= 0:
            #Get the data
            if counter ==1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                #Get the Image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                            "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed>30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    modeType = 3
                    counter = 0
                    imgBackground[200:200+350,630:630+300] = imgModeList[modeType]
        
            if modeType!= 3:
            
                if 10<counter<20:
                    modeType = 2

                    imgBackground[200:200+350,630:630+300] = imgModeList[modeType]

                    if counter<=10:    
                        cv2.putText(imgBackground,str(studentInfo['total_attendance']),(845,252),
                                    cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                        cv2.putText(imgBackground,str(studentInfo['major']),(738,530),
                                    cv2.FONT_HERSHEY_COMPLEX,0.4,(255,255,255),1)
                        cv2.putText(imgBackground,str(studentInfo['standing']),(700,435),
                                    cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                        cv2.putText(imgBackground,str(studentInfo['year']),(700,380),
                                    cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                        cv2.putText(imgBackground,str(studentInfo['starting_year']),(690,320),
                                    cv2.FONT_HERSHEY_COMPLEX,0.6,(255,255,255),1)
                        cv2.putText(imgBackground,str(studentInfo['id']),(750,500),
                                    cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        
                        (w,h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,0.7,1)
                        offset = (300 - w) // 2
                        cv2.putText(imgBackground,str(studentInfo['name']),(680 + offset, 470),
                                    cv2.FONT_HERSHEY_COMPLEX,0.7,(50,50,50),1)
                        
                        imgBackground[275:275+171,760:760+161] = imgStudent

            

                counter+=1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[200:200+350,630:630+300] = imgModeList[modeType]


    else:
        modeType = 0
        counter = 0    
    #cv2.imshow("Webcam",img)
    cv2.imshow("Face Attendance",imgBackground)           #Display
    cv2.waitKey(1)