# -------------------------------------------------------------
# FULLY FUNCTIONAL SCHOLARSHIP SYSTEM (DB-Integrated, Scrollable, Dynamic Checklist + Centered Progress)
# -------------------------------------------------------------
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import subprocess
import os
import sys

# ----------------------- COLORS -----------------------
MAROON       = "#7B1113"
MAROON_DARK  = "#5B0E0F"
CARD_BORDER  = "#E6E6E6"
BG           = "#FAFAFA"
TEXT         = "#1E1E1E"
SUBDUED      = "#636363"

ctk.set_appearance_mode("light")

# ----------------------- DATABASE -----------------------
DB_FILE = "Scholarship.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def get_student(applicant_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT StudentID, Name, Username, Email, School, Course, Year_Level, Phone_Number, GWA, Status
        FROM Applicants
        WHERE Applicant_id = ?
    """, (applicant_id,))
    row = c.fetchone()
    conn.close()
    if row:
        parts = row[1].split()
        initials = "".join([p[0] for p in parts[:2]]).upper()
        return {
            "initials": initials,
            "name": row[1],
            "student_no": row[0],
            "program": f"{row[5]} ({row[4]})",
            "year": row[6],
            "status": row[9],
            "username": row[2],
            "email": row[3],
            "phone": row[7],
            "gwa": row[8]
        }
    return None

def get_applicant_requirements(applicant_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT COR, TOR, Good_Moral
        FROM Applicant_requirements
        WHERE applicants_id = ?
    """, (applicant_id,))
    row = c.fetchone()
    conn.close()

    requirements = {
        "COR (Certificate of Registration)": False,
        "Grades (Previous Semester)": False,
        "Good Moral Certificate": False
    }

    if row:
        requirements["COR (Certificate of Registration)"] = bool(row[0])
        requirements["Grades (Previous Semester)"] = bool(row[1])
        requirements["Good Moral Certificate"] = bool(row[2])

    return requirements

# ----------------------- COMPONENTS -----------------------
class Tag(ctk.CTkLabel):
    """Status pill"""
    def __init__(self, master, text="PENDING", fg="#FFF2CC", text_color=MAROON):
        super().__init__(master, text=text, fg_color=fg, text_color=text_color,
                         corner_radius=999, padx=12, pady=6)

class AvatarCanvas(tk.Canvas):
    """Big square avatar with initials."""
    def __init__(self, master, initials="JD", size=200,
                 bg_color="white", square_color="#F2E7E7",
                 text_color=MAROON):
        super().__init__(master, width=size, height=size,
                         highlightthickness=0, bg=bg_color)
        self.create_rectangle(2, 2, size-2, size-2, fill=square_color, outline=square_color)
        self.create_text(size/2, size/2, text=initials,
                         font=("Segoe UI", int(size/2.8), "bold"),
                         fill=text_color)

# ---------------------------------------------------------
# APPLICANT DASHBOARD
# ---------------------------------------------------------
class ApplicantsDashboard(ctk.CTkFrame):
    def __init__(self, master, student, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=16,
                         border_width=1, border_color=CARD_BORDER, **kwargs)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="APPLICANT'S DASHBOARD",
                     text_color=MAROON, font=("Segoe UI",18,"bold")).grid(
                        row=0, column=0, columnspan=2,
                        sticky="w", padx=18, pady=(16,6))

        AvatarCanvas(self, initials=student["initials"]).grid(
            row=1, column=0, rowspan=8, sticky="nw", padx=18, pady=4
        )

        ctk.CTkLabel(self, text=student["name"],
                     font=("Segoe UI",20,"bold"),
                     text_color=TEXT).grid(row=1, column=1, sticky="w", padx=6, pady=(6,2))

        def row(label, value, r):
            ctk.CTkLabel(self, text=label, text_color=SUBDUED,
                         font=("Segoe UI",13)).grid(row=r, column=1,
                         sticky="w", padx=6)
            ctk.CTkLabel(self, text=value, text_color=TEXT,
                         font=("Segoe UI",13,"bold")).grid(
                            row=r, column=1, sticky="w", padx=160
                         )

        row("Student No.:", student["student_no"], 2)
        row("Program:", student["program"], 3)
        row("Year Level:", str(student["year"]), 4)
        row("Username:", student["username"], 5)
        row("Email:", student["email"], 6)
        row("Phone:", student["phone"], 7)
        row("GWA:", str(student["gwa"]), 8)

        # Combined Status + Edit Button
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=9, column=1, sticky="e", padx=18, pady=(12,12))

        status = student["status"]
        color_map = {"APPROVED": "#DAF1DD", "PENDING": "#FFF2CC", "REJECTED": "#FCE5E5"}
        status_text_color = MAROON if status != "REJECTED" else "#B00020"

        Tag(container, text=f"STATUS: {status}",
            fg=color_map.get(status, "#FFF2CC"),
            text_color=status_text_color).pack(side="left", padx=(0,10))

        ctk.CTkButton(container, text="EDIT PROFILE",
                      fg_color="#EFEFEF", text_color=MAROON,
                      hover_color="#E5E5E5").pack(side="left")

# ---------------------------------------------------------
# SCROLLABLE FRAME WRAPPER
# ---------------------------------------------------------
class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)

# ---------------------------------------------------------
# SCHOLARSHIPS SECTION
# ---------------------------------------------------------
class ScholarshipsAvailable(ctk.CTkFrame):
    def __init__(self, master, student_id=None, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=16,
                         border_width=1, border_color=CARD_BORDER, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="SCHOLARSHIP AVAILABLE",
                     text_color=MAROON,
                     font=("Segoe UI",18,"bold")).grid(
                        row=0, column=0, sticky="w",
                        padx=18, pady=(16,10))

        card = ctk.CTkFrame(self, fg_color="white",
                            corner_radius=14, border_width=1,
                            border_color=CARD_BORDER)
        card.grid(row=1, column=0, sticky="nsew", padx=12, pady=(2,16))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card,
                     text="GOVERNOR VILMA SANTOS-RECTO EDUCATIONAL ASSISTANCE",
                     wraplength=480, text_color=TEXT,
                     font=("Segoe UI",16,"bold")).grid(
                        row=0, column=0, sticky="n", padx=16, pady=(14,6)
                     )

        if student_id:
            self.status = get_applicant_requirements(student_id)
            student = get_student(student_id)
            scholarship_status = student["status"]
        else:
            self.status = {
                "COR (Certificate of Registration)": False,
                "Grades (Previous Semester)": False,
                "Good Moral Certificate": False
            }
            scholarship_status = "PENDING"

        # ---------------- Progress Section ----------------
        progress_section = ctk.CTkFrame(card, fg_color="transparent")
        progress_section.grid(row=1, column=0, sticky="ew", padx=16, pady=(6,12))
        progress_section.grid_columnconfigure(0, weight=1)

        completed = sum(1 for v in self.status.values() if v)
        total = len(self.status)
        progress_value = completed / total

        if scholarship_status == "APPROVED":
            progress_value = 1.0

        ctk.CTkLabel(progress_section, text="Document Requirements Progress",
                     text_color=TEXT, font=("Segoe UI",14,"bold")).grid(row=0,column=0,sticky="n", pady=(0,6))

        pb = ctk.CTkProgressBar(progress_section, height=12)
        pb.grid(row=1,column=0,sticky="ew", pady=(4,2))
        pb.set(progress_value)

        pct = int(progress_value*100)
        ctk.CTkLabel(progress_section, text=f"{pct}%", text_color=SUBDUED, font=("Segoe UI",12)).grid(row=2,column=0, sticky="n", pady=(2,0))

        legend_frame = ctk.CTkFrame(progress_section, fg_color="transparent")
        legend_frame.grid(row=3, column=0, sticky="w", pady=(8,2))
        for doc, done in self.status.items():
            row = ctk.CTkFrame(legend_frame, fg_color="transparent")
            row.pack(anchor="w", pady=2)

            icon = "🟩" if done else "🟥"
            text_color = "green" if done else "red"

            ctk.CTkLabel(row, text=icon, font=("Segoe UI",18)).pack(side="left", padx=(0,8))
            ctk.CTkLabel(row, text=doc, text_color=TEXT, font=("Segoe UI",13,"bold")).pack(side="left")
            status_text = "Completed" if done else "Not Submitted"
            ctk.CTkLabel(row, text=f"– {status_text}", text_color=text_color, font=("Segoe UI",12)).pack(side="left", padx=(6,0))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=2,column=0, sticky="ew", padx=12, pady=(10,16))
        btn_row.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_row, text="APPLY NOW", fg_color=MAROON, hover_color=MAROON_DARK).grid(row=0,column=0, sticky="ew", padx=(4,6))
        ctk.CTkButton(btn_row, text="VIEW DETAILS", fg_color="#EFEFEF", text_color=MAROON, hover_color="#E5E5E5").grid(row=0,column=1, sticky="ew", padx=(6,4))

# ------------------------- SIGN OUT FUNCTION -------------------------
def open_login(current_window):
    width = current_window.winfo_width()
    height = current_window.winfo_height()
    x = current_window.winfo_x()
    y = current_window.winfo_y()
    current_window.destroy()
    
    
    
    subprocess.Popen(["python", "login.py", str(width), str(height), str(x), str(y)])

# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------
class ScholarshipApp(ctk.CTk):
    def __init__(self, applicant_id=1):
        super().__init__()
        self.title("BatStateU • Scholarship Management System")
        self.geometry("1100x720")
        self.minsize(960,640)
        self.configure(fg_color=BG)

        header = ctk.CTkFrame(self, fg_color="#6F0000", height=110, corner_radius=0)
        header.pack(fill="x")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="BATANGAS STATE UNIVERSITY",
                     font=("Arial Black",34), text_color="white").grid(row=0,column=0, pady=(10,0))
        ctk.CTkLabel(header, text="SCHOLARSHIP MANAGEMENT SYSTEM",
                     font=("Arial",18), text_color="white").grid(row=1,column=0, pady=(0,10))

        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.grid(row=0,column=1,rowspan=2, padx=30, pady=20, sticky="e")
        ctk.CTkButton(button_frame, text="📢 Announcement",
                      fg_color="white", hover_color="#F5F5F5",
                      text_color=MAROON, corner_radius=12,
                      width=160, height=42,
                      font=("Segoe UI",14,"bold")).pack(side="left", padx=8)
        # ✅ SIGN OUT BUTTON FIXED
        ctk.CTkButton(button_frame, text="🚪 Sign Out",
                      fg_color=MAROON_DARK, hover_color="#4A0A0B",
                      text_color="white", corner_radius=12,
                      width=140, height=42,
                      font=("Segoe UI",14,"bold"),
                      border_width=0,
                      command=lambda: open_login()
                    ).pack(side="left", padx=8)

        scrollable = ScrollableFrame(self)
        scrollable.grid_columnconfigure(0, weight=1)
        content = scrollable

        student = get_student(applicant_id)
        if not student:
            messagebox.showerror("Error", "Applicant not found!")
            self.destroy()
            return

        dashboard = ApplicantsDashboard(content, student=student)
        dashboard.pack(fill="x", pady=(0,16))
        scholarships = ScholarshipsAvailable(content, student_id=applicant_id)
        scholarships.pack(fill="x")

# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------
if __name__ == "__main__":
    app = ScholarshipApp(applicant_id=1)
    app.mainloop()
