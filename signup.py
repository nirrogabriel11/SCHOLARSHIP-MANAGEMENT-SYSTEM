import customtkinter as ctk
from tkinter import messagebox
import subprocess
import sqlite3
import re

# ------------------------- CONFIG -------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ------------------------- HELPER FUNCTIONS -------------------------
def highlight(entry):
    entry.configure(border_color="red")

def reset_highlight(entry):
    entry.configure(border_color="#800000")

def is_valid_ph_number(number: str) -> bool:
    number = number.strip()
    pattern_local = r'^09\d{9}$'
    pattern_intl = r'^\+639\d{8}$'
    return bool(re.match(pattern_local, number) or re.match(pattern_intl, number))

def format_ph_number(number: str) -> str:
    number = number.strip()
    if number.startswith("09"):
        return "+63" + number[1:]
    return number

def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

# ------------------------- CORE FUNCTIONS -------------------------
def exit_fullscreen(event=None):
    win.state("normal")

def create_entry(parent, label_text):
    frame = ctk.CTkFrame(parent, fg_color=parent.cget("fg_color"), corner_radius=0)
    frame.pack(fill="x", pady=10)

    label = ctk.CTkLabel(frame, text=label_text, font=("Helvetica", 16, "bold"), text_color="#800000")
    label.pack(anchor="w", pady=(0, 5))

    entry = ctk.CTkEntry(
        frame, width=400, height=45,
        border_color="#800000", border_width=2,
        corner_radius=15, fg_color="white",
        text_color="black", font=("Helvetica", 14)
    )
    entry.pack(fill="x")
    return entry

def save_to_database():
    # Reset highlights
    for entry in [studentID_entry, fullname_entry, phone_entry, email_entry, gwa_entry]:
        reset_highlight(entry)

    studentID = studentID_entry.get().strip()
    fullname = fullname_entry.get().strip()
    phone = phone_entry.get().strip()
    email = email_entry.get().strip()
    yearlevel = yearlevel_var.get().strip()
    gwa = gwa_entry.get().strip()
    school = school_var.get().strip()
    course = course_var.get().strip()

    # Validate required fields
    if not all([studentID, fullname, phone, email, yearlevel, gwa, school, course]):
        messagebox.showerror("Error", "Please fill in all required fields!")
        return False

    # Validate email
    if not is_valid_email(email):
        highlight(email_entry)
        messagebox.showerror("Error", "Please enter a valid email address.")
        return False

    # Validate phone
    if not is_valid_ph_number(phone):
        highlight(phone_entry)
        messagebox.showerror("Error", "Please enter a valid PH mobile number.")
        return False
    phone = format_ph_number(phone)

    # Validate GWA
    try:
        gwa_value = float(gwa)
        if not (1.00 <= gwa_value <= 5.00):
            raise ValueError
    except ValueError:
        highlight(gwa_entry)
        messagebox.showerror("Error", "GWA must be a number between 1.00 and 5.00.")
        return False

    # Database operations
    try:
        conn = sqlite3.connect("Scholarship.db")
        cur = conn.cursor()

        # Check duplicates in Applicants
        cur.execute("SELECT 1 FROM Applicants WHERE StudentID=? OR Email=? OR Phone_Number=?", (studentID, email, phone))
        if cur.fetchone():
            highlight(studentID_entry)
            messagebox.showerror("Error", "Student ID, Email, or Phone number already exists in Applicants.")
            conn.close()
            return False

        # Check duplicates in Maintainer
        cur.execute("SELECT 1 FROM Maintainer WHERE student_id=?", (studentID,))
        if cur.fetchone():
            highlight(studentID_entry)
            messagebox.showerror("Error", f"The Student ID '{studentID}' already exists in Maintainer.")
            conn.close()
            return False

        # Insert applicant
        cur.execute("""
            INSERT INTO Applicants (studentID, Name, Email, School, Course, Year_Level, Phone_Number, GWA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (studentID, fullname, email, school, course, yearlevel, phone, gwa_value))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Applicant information saved successfully!")
        return True

    except Exception as e:
        messagebox.showerror("DATABASE ERROR", str(e))
        return False

def open_window_same_size(file_name):
    width = win.winfo_width()
    height = win.winfo_height()
    x = win.winfo_x()
    y = win.winfo_y()
    win.destroy()
    subprocess.Popen(["python", file_name, str(width), str(height), str(x), str(y)])

def continue_action():
    if save_to_database():
        open_window_same_size("upload.py")

def back_to_login():
    open_window_same_size("login.py")

# ------------------------- MAIN WINDOW -------------------------
win = ctk.CTk()
win.title("Scholarship Sign Up")
win.after(50, lambda: win.state("zoomed"))
win.configure(fg_color="#F5F5F5")
win.bind("<Escape>", exit_fullscreen)

# ------------------------- HEADER -------------------------
header = ctk.CTkFrame(win, fg_color="#6F0000", height=120, corner_radius=0)
header.pack(fill="x")

ctk.CTkLabel(header, text="BATANGAS STATE UNIVERSITY", font=("Helvetica", 28, "bold"), text_color="white").pack(pady=(10, 0))
ctk.CTkLabel(header, text="SCHOLARSHIP MANAGEMENT SYSTEM", font=("Helvetica", 18), text_color="white").pack(pady=(0, 15))

# ------------------------- MAIN FORM -------------------------
main_content = ctk.CTkFrame(win, fg_color="#F5F5F5")
main_content.pack(fill="both", expand=True, padx=50, pady=20)

form_title = ctk.CTkLabel(main_content, text="I. PERSONAL INFORMATION", font=("Helvetica", 24, "bold"), text_color="#800000")
form_title.pack(anchor="w", pady=(0, 20))

form_area = ctk.CTkFrame(main_content, fg_color="#F5F5F5")
form_area.pack(fill="both", expand=True)

# LEFT COLUMN
left_col = ctk.CTkFrame(form_area, fg_color="#F5F5F5")
left_col.pack(side="left", fill="both", expand=True, padx=20)

studentID_entry = create_entry(left_col, "Student ID :")
fullname_entry = create_entry(left_col, "Full Name :")
phone_entry = create_entry(left_col, "Phone :")
email_entry = create_entry(left_col, "Email :")

# RIGHT COLUMN
right_col = ctk.CTkFrame(form_area, fg_color="#F5F5F5")
right_col.pack(side="left", fill="both", expand=True, padx=20)

# Year Level Dropdown
ctk.CTkLabel(right_col, text="Year Level :", font=("Helvetica", 16, "bold"), text_color="#800000").pack(anchor="w", pady=(10, 5))
yearlevel_options = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
yearlevel_var = ctk.StringVar(value=yearlevel_options[0])
yearlevel_dropdown = ctk.CTkOptionMenu(
    right_col, values=yearlevel_options, variable=yearlevel_var,
    fg_color="white", button_color="white", button_hover_color="#F0F0F0",
    dropdown_fg_color="white", dropdown_hover_color="#DCDCDC",
    text_color="#800000", corner_radius=15, font=("Helvetica", 16, "bold"),
    width=400, height=45
)
yearlevel_dropdown.pack(fill="x", pady=(0, 10))

gwa_entry = create_entry(right_col, "General Weighted Average :")

# School Dropdown
ctk.CTkLabel(right_col, text="Campus :", font=("Helvetica", 16, "bold"), text_color="#800000").pack(anchor="w", pady=(10, 5))
school_options = ["Lipa-Campus", "Arasof-Campus", "Alangilan-Campus", "Pablo Borbon-Campus", 
                  "Malvar-Campus", "Rosario-Campus", "San Juan-Campus", "Balayan-Campus", 
                  "Lobo-Campus", "Lemery-Campus", "Lima Estate-Campus"]
school_var = ctk.StringVar(value=school_options[0])
school_dropdown = ctk.CTkOptionMenu(
    right_col, values=school_options, variable=school_var,
    fg_color="white", button_color="white", button_hover_color="#F0F0F0",
    dropdown_fg_color="white", dropdown_hover_color="#DCDCDC",
    text_color="#800000", corner_radius=15, font=("Helvetica", 16, "bold"),
    width=400, height=45
)
school_dropdown.pack(fill="x", pady=(0, 10))

# Course Dropdown
ctk.CTkLabel(right_col, text="Course :", font=("Helvetica", 16, "bold"), text_color="#800000").pack(anchor="w", pady=(10, 5))
course_options = [
    "BS Computer Science", "BS Information Technology",
    "BS Accountancy", "BS Business Administration",
    "BS Hospitality Management", "BS Education"
]
course_var = ctk.StringVar(value=course_options[0])
course_dropdown = ctk.CTkOptionMenu(
    right_col, values=course_options, variable=course_var,
    fg_color="white", button_color="white", button_hover_color="#F0F0F0",
    dropdown_fg_color="white", dropdown_hover_color="#DCDCDC",
    text_color="#800000", corner_radius=15, font=("Helvetica", 16, "bold"),
    width=400, height=45
)
course_dropdown.pack(fill="x", pady=(0, 10))

# ------------------------- BUTTONS -------------------------
button_frame = ctk.CTkFrame(main_content, fg_color="#F5F5F5")
button_frame.pack(fill="x", pady=30)

back_button = ctk.CTkButton(
    button_frame, text="Back to Login", fg_color="#800000", hover_color="#A52A2A",
    text_color="white", corner_radius=25, width=180, height=55, font=("Helvetica", 14, "bold"),
    command=back_to_login
)
back_button.pack(side="left", padx=20)

continue_button = ctk.CTkButton(
    button_frame, text="Continue", fg_color="#800000", hover_color="#A52A2A",
    text_color="white", corner_radius=25, width=180, height=55, font=("Helvetica", 14, "bold"),
    command=continue_action
)
continue_button.pack(side="right", padx=20)

win.mainloop()
