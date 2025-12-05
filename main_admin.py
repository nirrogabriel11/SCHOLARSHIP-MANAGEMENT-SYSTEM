import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Import your custom modules
from New_Applicants import NewApplicantsDashboard
from Maintainers import MaintainersDashboard

class ScholarshipManagementSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Batangas State University - Scholarship Management System")
        
        # Get screen dimensions and maximize
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Configure database connection
        self.conn = sqlite3.connect("Scholarship.db", timeout=10)
        self.cursor = self.conn.cursor()
        
        # Create header
        self.create_header()
        
        # Create main container
        self.create_main_container()
        
        # Show dashboard by default
        self.show_dashboard()
        
        # Try to maximize after everything loads
        self.after(100, lambda: self.state('zoomed'))
    
    def create_header(self):
        header_height = 110
        header = ctk.CTkFrame(self, fg_color="#6F0000", height=header_height, corner_radius=0)
        header.pack(side="top", fill="x")
        header.grid_propagate(False)
        
        ctk.CTkLabel(header, text="BATANGAS STATE UNIVERSITY", 
                     font=("Arial Black", 34), text_color="white").pack(pady=(20, 0))
        ctk.CTkLabel(header, text="SCHOLARSHIP MANAGEMENT SYSTEM", 
                     font=("Arial", 18), text_color="white").pack()
    
    def create_main_container(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Sidebar
        sidebar = ctk.CTkFrame(self.main_frame, fg_color="#6F0000", width=250, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Sidebar title
        ctk.CTkLabel(sidebar, text="Admin Dashboard", 
                     font=("Arial Black", 20), text_color="white").pack(pady=30)
        
        # Menu buttons
        self.create_menu_button(sidebar, "Dashboard", self.show_dashboard)
        self.create_menu_button(sidebar, "New Applicants List", self.open_new_applicants)
        self.create_menu_button(sidebar, "Maintainers List", self.open_maintainers)
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(sidebar, text="Logout", font=("Arial", 14), 
                                   fg_color="white", text_color="black",
                                   hover_color="#f0f0f0", corner_radius=25,
                                   height=50, command=self.logout)
        logout_btn.pack(side="bottom", fill="x", padx=15, pady=20)
        
        # Content area (changes based on selection)
        self.content_area = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.content_area.pack(side="right", fill="both", expand=True)
    
    def create_menu_button(self, parent, text, command):
        btn = ctk.CTkButton(parent, text=text, font=("Arial", 14), 
                           fg_color="white", text_color="black",
                           hover_color="#f0f0f0", corner_radius=25,
                           height=50, command=command)
        btn.pack(fill="x", padx=15, pady=8)
    
    # ----- BUTTON FUNCTIONS -----
    def open_new_applicants(self):
        self.withdraw()
        win = NewApplicantsDashboard(parent=self)
        win.grab_set()
        

    def open_maintainers(self):
        self.withdraw()
        win = MaintainersDashboard(parent=self)
        win.grab_set()
    
    def logout(self):
        """Handle logout functionality"""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.destroy()
    
    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        # Main content frame with padding
        content = ctk.CTkFrame(self.content_area, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Title
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(title_frame, text="Dashboard Overview", 
                     font=("Arial Black", 28), text_color="black").pack()
        
        # Stats container
        stats_container = ctk.CTkFrame(content, fg_color="transparent")
        stats_container.pack(fill="both", expand=True, pady=20)
        
        # Configure grid to center the cards
        stats_container.grid_columnconfigure(0, weight=1)
        stats_container.grid_columnconfigure(1, weight=1)
        stats_container.grid_columnconfigure(2, weight=1)
        stats_container.grid_rowconfigure(0, weight=1)
        
        # Get counts from database
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Applicants")
            applicants_count = self.cursor.fetchone()[0]
        except:
            applicants_count = 0
            
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer")
            maintainers_count = self.cursor.fetchone()[0]
        except:
            maintainers_count = 0
        
        # Statistics cards
        self.create_stat_card(stats_container, "Total Applicants", 
                             applicants_count, "#1f6aa5", 0)
        self.create_stat_card(stats_container, "Total Maintainers", 
                             maintainers_count, "#2b8a3e", 1)
        self.create_stat_card(stats_container, "Active Scholarships", 
                             applicants_count + maintainers_count, "#f39c12", 2)
    
    def create_stat_card(self, parent, title, value, color, col):
        # Card frame
        card = ctk.CTkFrame(parent, fg_color=color, width=280, height=180, corner_radius=15)
        card.grid(row=0, column=col, padx=25, pady=20, sticky="nsew")
        card.grid_propagate(False)
        
        # Value
        ctk.CTkLabel(card, text=str(value), font=("Arial Black", 56), 
                     text_color="white").pack(expand=True, pady=(40, 0))
        
        # Title
        ctk.CTkLabel(card, text=title, font=("Arial", 18), 
                     text_color="white").pack(expand=True, pady=(0, 30))

if __name__ == "__main__":
    app = ScholarshipManagementSystem()
    app.mainloop()