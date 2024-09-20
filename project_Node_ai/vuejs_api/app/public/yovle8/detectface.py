import cv2
import face_recognition
import mysql.connector
import numpy as np
import os

# Check face
conn = mysql.connector.connect(
    host="localhost",
    port=8889,
    user="root",
    password="root",
    database="face_db"
)

# 1. Load all faces
cursor = conn.cursor(dictionary=True)
cursor.execute('''
SELECT f.staffId, s.displayName name, f.id faceId, f.faceData 
FROM staffs s
  JOIN faces f ON f.staffId=s.id''')

faces = cursor.fetchall()

if len(faces) == 0:
    print("No faces found in the database.")
    conn.close()
    exit()

all_faces = [np.frombuffer(face["faceData"], dtype=np.float64) for face in faces]
print("Loaded all faces.")

video_capture = cv2.VideoCapture(0)
print("Camera ready.")

while True:
    ok, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=1 / 4, fy=1 / 4)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)

    if len(face_locations) == 0:
        cv2.putText(frame, "No face detected.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Press 'r' to register.", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('Video', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('r'):
            # Call the register script
            video_capture.release()
            cv2.destroyAllWindows()
            conn.close()
            os.system('python3 register.py')
            break
        continue

    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        face_distances = face_recognition.face_distance(all_faces, face_encoding)
        
        if len(face_distances) > 0:
            min_index = np.argmin(face_distances)
            min_distance = face_distances[min_index]

            # Minimum distance threshold for matching faces
            threshold = 0.6

            if min_distance < threshold:
                name = faces[min_index]["name"]
            else:
                name = "Face not recognized. Press 'r' to register."

            top, right, bottom, left = face_location
            cv2.putText(frame, name, (left * 4, top * 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            
            if name == "Face not recognized. Press 'r' to register." and cv2.waitKey(1) & 0xFF == ord('r'):
                # Call the register script
                video_capture.release()
                cv2.destroyAllWindows()
                conn.close()
                os.system('python3 /path/to/your/register.py')
                break
        else:
            print("No face distances found.")

    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
conn.close()
