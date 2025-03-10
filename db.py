import sqlite3
import cv2
import face_recognition
import requests
from datetime import datetime
conn = sqlite3.connect('student_schedule.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS schedules (
    student_id INTEGER PRIMARY KEY,
    student_name TEXT NOT NULL,
    class_name TEXT NOT NULL,
    class_start_time TEXT NOT NULL,
    class_end_time TEXT NOT NULL
)
''')

def insert_schedule(student_id, student_name, class_name, class_start_time, class_end_time):
    c.execute('''
    INSERT INTO schedules (student_id, student_name, class_name, class_start_time, class_end_time)
    VALUES (?, ?, ?, ?, ?)
    ''', (student_id, student_name, class_name, class_start_time, class_end_time))
    conn.commit()

insert_schedule(1, 'Adarsh Kumar', 'Math 101', '09:00', '11:00')

conn.close()

cap = cv2.VideoCapture(0)
known_faces = []
known_names = []
image_of_student = face_recognition.load_image_file("download.png")
student_face_encoding = face_recognition.face_encodings(image_of_student)[0]
known_faces.append(student_face_encoding)
known_names.append("Adarsh Kumar")
while True:
    ret, frame = cap.read()
    
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        
        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
        else:
            name = "Unknown"
        
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow('Video', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

def check_class_schedule(student_id):
    conn = sqlite3.connect('student_schedule.db')
    c = conn.cursor()

    c.execute("SELECT class_start_time, class_end_time FROM schedules WHERE student_id = ?", (student_id,))
    result = c.fetchone()

    if result:
        class_start_time, class_end_time = result
        current_time = datetime.now().strftime('%H:%M')

        if class_start_time <= current_time <= class_end_time:
            return True
        else:
            return False
    else:
        return False

student_id = 1
is_in_class = check_class_schedule(student_id)

if is_in_class:
    print("Student is in class.")
else:
    print("Student is not in class.")


def send_email_alert(student_name):
    api_key = "82b6cf2ddf30b3bbd36e83965cf911e8-623424ea-e5afa4e7"
    domain = "sandbox9bbb39985f074106ba1247220c87de4d.mailgun.org"  
    sender = "codingkelie@gmail.com"  
    recipient = "akrk3321@gmail.com"  
    subject = f"Alert: {student_name} is not in class!"
    body = f"{student_name} has been detected outside of class during class hours."

    response = requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={"from": "Mailgun Sandbox <postmaster@sandbox9bbb39985f074106ba1247220c87de4d.mailgun.org>",
              "to": [recipient],
              "subject": subject,
              "text": body})

    if response.status_code == 200:
        print("Email sent successfully!")
    else:
        print(f"Error sending email: {response.text}")

if not is_in_class:
    send_email_alert("Adarsh Kumar")
