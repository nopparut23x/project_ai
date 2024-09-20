import cv2
import face_recognition
import mysql.connector
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import numpy as np
import datetime

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    port=8889,
    user="root",
    password="root",
    database="face_db"
)

# Directory to save face images
FACE_IMAGE_DIR = "vuejs_api/app/public/yovle8/face_images"
if not os.path.exists(FACE_IMAGE_DIR):
    os.makedirs(FACE_IMAGE_DIR)

# Global variables
face_encodings = []
face_images = []

# Function to save face data
def save_face_data():
    global face_encodings, face_images
    name = entry_name.get().strip()
    dept = entry_dept.get().strip()

    if not name:
        messagebox.showwarning("Warning", "Please enter a name.")
        return

    if not dept:
        messagebox.showwarning("Warning", "Please enter a department.")
        return

    cursor = conn.cursor()
    
    # Check if the name already exists
    cursor.execute("SELECT id FROM staffs WHERE displayName = %s", (name,))
    staff = cursor.fetchone()

    if staff:
        messagebox.showwarning("Warning", "Name already exists. Please choose a different name.")
        return

    # Insert a new record
    if face_images:
        image_path = save_face_image(face_images[0], name)  # Save the face image and get the path
        cursor.execute("INSERT INTO staffs (displayName, dept, face_img) VALUES (%s, %s, %s)", (name, dept, image_path))
        staffId = cursor.lastrowid

        if face_encodings:
            face_data = face_encodings[0].tobytes()
            cursor.execute("INSERT INTO faces (staffId, faceData) VALUES (%s, %s)", (staffId, face_data))
            insert_id = cursor.lastrowid
            conn.commit()

            messagebox.showinfo("Info", f"Saved name: {name}, department: {dept}, and face data with ID: {insert_id}")
        else:
            messagebox.showwarning("Warning", "No face data detected. Please try again.")
    else:
        messagebox.showwarning("Warning", "No face image captured. Please try again.")

# Function to save face image
def save_face_image(face_image, name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    base_filename = f"{name.replace(' ', '_')}_{timestamp}.jpg"
    filepath = os.path.join(FACE_IMAGE_DIR, base_filename)

    # Ensure face_image is in the correct RGB format
    if face_image.ndim == 3 and face_image.shape[2] == 3:  # Check for RGB format
        img = Image.fromarray(face_image)
        img.save(filepath)
    else:
        raise ValueError("The face image does not have the correct shape (expected RGB).")
    
    return f"face_images/{base_filename}"

# Function to update frame from camera
def update_frame():
    global face_encodings, face_images
    ok, frame = video_capture.read()

    if ok:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        except Exception as e:
            print(f"Error during face detection: {e}")
            return

        face_images = []
        for (top, right, bottom, left) in face_locations:
            padding = 20  # Adjust padding for better face image
            top = max(0, top - padding)
            right = min(frame.shape[1], right + padding)
            bottom = min(frame.shape[0], bottom + padding)
            left = max(0, left - padding)

            face_image = frame[top:bottom, left:right]
            if face_image.shape[2] == 3:  # Ensure face_image is in RGB format
                face_images.append(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
            else:
                print("Error: Face image does not have 3 channels.")
            
            # Draw a rectangle around the face in the original frame
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Convert the frame to ImageTk format for display
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)
    
    root.after(10, update_frame)

# Function to exit the program
def exit_program():
    video_capture.release()
    conn.close()
    root.destroy()

# Set up GUI
root = tk.Tk()
root.title("Face Registration")
root.attributes("-fullscreen", True)

lbl_video = tk.Label(root)
lbl_video.pack(fill=tk.BOTH, expand=True)

entry_name = tk.Entry(root, width=50, font=('Arial', 14))
entry_name.pack(pady=5)
entry_name.insert(0, "Name")

entry_dept = tk.Entry(root, width=50, font=('Arial', 14))
entry_dept.pack(pady=5)
entry_dept.insert(0, "Department")

btn_save = tk.Button(root, text="Save", command=save_face_data, font=('Arial', 14))
btn_save.pack(pady=5)

btn_exit = tk.Button(root, text="Exit", command=exit_program, font=('Arial', 14))
btn_exit.pack(pady=5)

video_capture = cv2.VideoCapture(0)

update_frame()
root.mainloop()
