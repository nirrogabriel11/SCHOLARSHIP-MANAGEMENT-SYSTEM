import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import subprocess
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ------------------------- CONFIG -------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

DB_PATH = "Scholarship.db"

# ------------------------- EMAIL FUNCTION -------------------------
def send_confirmation_email(receiver_email, receiver_name):
    sender_email = "bsu.smsoffice@gmail.com"
    app_password = "eltk hyar kjve dbhu"  # Use app password for Gmail SMTP

    subject = "Your Scholarship Account Has Been Created"
    body = f"""
    <html>
    <body>
        <p>Hello <b>{receiver_name}</b>,</p>

        <p>Your <i>Scholarship Management System</i> account has been successfully created.</p>

        <p>Once your scholarship application is <b>approved</b>, you will be able to log in as a <b>Scholar</b> (Maintainer Account). An email notification will be sent to you regarding the approval.</p>

        <p>Please wait for further announcements from the Scholarship Office.</p>

        <p>Thank you,<br>
        <b>Batangas State University Scholarship Office</b></p>
    </body>
    </html>

    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent to:", receiver_email)

    except Exception as e:
        print("EMAIL ERROR:", e)

# ------------------------- FUNCTIONS -------------------------
def exit_fullscreen(event=None):
    win.state("normal")

def reset_form():
    username_entry.delete(0, "end")
    password_entry.delete(0, "end")
    confirm_password_entry.delete(0, "end")

def submit_application():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    confirm = confirm_password_entry.get().strip()

    if not (username and password and confirm):
        messagebox.showerror("Error", "Please fill in all required fields.")
        return False

    if password != confirm:
        messagebox.showerror("Error", "Passwords do not match.")
        return False
    
    if len(password) <= 7:
        messagebox.showerror("Error", "Your password should contain a minimum of 8 characters.")
        return False
        

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get the last applicant
        c.execute("""
            SELECT Applicant_id, Name, Email
            FROM Applicants
            WHERE Applicant_id = (SELECT MAX(Applicant_id) FROM Applicants)
        """)
        result = c.fetchone()

        if not result:
            messagebox.showerror("Error", "No applicant found.")
            conn.close()
            return False

        applicant_id, fullname, email = result

        # Update account info
        c.execute("""
            UPDATE Applicants
            SET Username = ?, Password = ?
            WHERE Applicant_id = ?
        """, (username, password, applicant_id))

        conn.commit()
        conn.close()

        # Send confirmation email
        send_confirmation_email(email, fullname)

        messagebox.showinfo(
            "Success", "Account created! A confirmation email has been sent."
        )
        reset_form()
        return True

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))
        return False

def submit_and_go_to_login():
    if submit_application():
        win.destroy()
        subprocess.Popen(["python", "login.py"])

def back_to_login():
    win.destroy()
    subprocess.Popen(["python", "signup.py"])

# ------------------------- UI -------------------------
win = ctk.CTk()
win.title("Create Scholarship Account")
win.after(50, lambda: win.state("zoomed"))
win.configure(fg_color="white")
win.bind("<Escape>", exit_fullscreen)

# ---------------- HEADER ----------------
header = ctk.CTkFrame(win, fg_color="#6F0000", height=110, corner_radius=0)
header.pack(fill="x")

ctk.CTkLabel(
    header,
    text="BATANGAS STATE UNIVERSITY",
    font=("Arial Black", 34),
    text_color="white"
).pack(pady=(10, 0))

ctk.CTkLabel(
    header,
    text="SCHOLARSHIP MANAGEMENT SYSTEM",
    font=("Arial", 18),
    text_color="white"
).pack(pady=(0, 10))

# ---------------- CENTER CONTENT ----------------
content = ctk.CTkFrame(win, fg_color="white")
content.pack(expand=True)

ctk.CTkLabel(
    content,
    text="III. SUBMIT APPLICATION",
    font=("Arial", 26, "bold"),
    text_color="#800000"
).pack(pady=20)

# ---------------- USERNAME ----------------
username_entry = ctk.CTkEntry(
    content,
    placeholder_text="Username",
    width=400,
    height=45,
    border_color="#800000",
    border_width=2,
    corner_radius=15,
    fg_color="white",
)
username_entry.pack(pady=10)

# ---------------- PASSWORD ----------------
password_container = ctk.CTkFrame(content, fg_color="transparent")
password_container.pack()

password_entry = ctk.CTkEntry(
    password_container,
    placeholder_text="Password",
    show="●",
    width=400,
    height=45,
    border_color="#800000",
    border_width=2,
    corner_radius=15,
    fg_color="white",
)
password_entry.pack()

eye_open_img = ctk.CTkImage(Image.open("eye_open.png"), size=(23, 23))
eye_closed_img = ctk.CTkImage(Image.open("eye_closed.png"), size=(23, 23))

def toggle_password():
    if password_entry.cget("show") == "●":
        password_entry.configure(show="")
        eye_button.configure(image=eye_open_img)
    else:
        password_entry.configure(show="●")
        eye_button.configure(image=eye_closed_img)

eye_button = ctk.CTkButton(
    password_container,
    text="",
    width=30,
    height=30,
    fg_color="white",
    hover_color="white",
    corner_radius=10,
    image=eye_closed_img,
    command=toggle_password
)
eye_button.place(relx=1, x=-20, rely=0.5, anchor="e")

# ---------------- CONFIRM PASSWORD ----------------
confirm_container = ctk.CTkFrame(content, fg_color="transparent")
confirm_container.pack(pady=10)

confirm_password_entry = ctk.CTkEntry(
    confirm_container,
    placeholder_text="Confirm Password",
    show="●",
    width=400,
    height=45,
    border_color="#800000",
    border_width=2,
    corner_radius=15,
    fg_color="white",
)
confirm_password_entry.pack()

def toggle_confirm():
    if confirm_password_entry.cget("show") == "●":
        confirm_password_entry.configure(show="")
        confirm_eye_button.configure(image=eye_open_img)
    else:
        confirm_password_entry.configure(show="●")
        confirm_eye_button.configure(image=eye_closed_img)

confirm_eye_button = ctk.CTkButton(
    confirm_container,
    text="",
    width=30,
    height=30,
    fg_color="white",
    hover_color="white",
    corner_radius=10,
    image=eye_closed_img,
    command=toggle_confirm
)
confirm_eye_button.place(relx=1, x=-20, rely=0.5, anchor="e")

# ---------------- BUTTONS ----------------
button_frame = ctk.CTkFrame(content, fg_color="white")
button_frame.pack(pady=25)

back_btn = ctk.CTkButton(
    button_frame,
    text="Back",
    fg_color="#800000",
    hover_color="#A52A2A",
    width=150,
    height=45,
    corner_radius=25,
    font=("Arial", 14, "bold"),
    command=back_to_login
)
back_btn.pack(side="left", padx=10)

submit_btn = ctk.CTkButton(
    button_frame,
    text="Submit Application",
    fg_color="#800000",
    hover_color="#A52A2A",
    width=200,
    height=45,
    corner_radius=25,
    font=("Arial", 14, "bold"),
    command=submit_and_go_to_login
)
submit_btn.pack(side="left", padx=10)

win.mainloop()
