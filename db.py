import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("C:/Users/Pramodh AVG/FaceRecognition/FaceRecognition/serviceAccountKey.json")

firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendancerealtime-50dca-default-rtdb.firebaseio.com/"
    })
 
ref = db.reference('Students')
data ={
    "22BCE5179":
        {
            "name":"Nitish Manica",
            "major":"Computer Science",
            "starting year":2022,
            "total_attendance":7,
             "standing": "G",
            "year": 4,
            "last_attendance_time": "2025-12-11 00:54:34",
            "id": "22BCE5179"
        }
    "21BPS1135":
        {
            "name": "S Ashwin",
            "major": "Cyber Physical Systems",
            "starting_year": 2021,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2025-12-11 00:54:34",
            "id": "21BPS1135"
        },
    
    "21BPS1503":
        {
            "name": "Pramodh AVG",
            "major": "Cyber Physical Systems",
            "starting_year": 2021,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2025-12-11 00:54:34",
            "id":"21BPS1503"
        }
}

for key,value in data.items():
    ref.child(key).set(value)