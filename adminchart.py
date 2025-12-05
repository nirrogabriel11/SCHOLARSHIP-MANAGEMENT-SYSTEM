import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import subprocess
import sys

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
        subprocess.Popen([sys.executable, 'New_Applicants.py'])
        

    def open_maintainers(self):
        if hasattr(self, 'maintainers_window') and self.maintainers_window.winfo_exists():
        # Window already open, just bring it to front
            self.maintainers_window.lift()
        else:
        # Create new window and pass self as parent
            self.maintainers_window = MaintainersDashboard(self)
            self.withdraw() 


    
    def logout(self):
        """Handle logout functionality"""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.destroy()
            subprocess.Popen(["python", "login.py"])
    
    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        # Main content frame with padding
        content = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Title
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(title_frame, text="Dashboard Overview", 
                     font=("Arial Black", 28), text_color="black").pack()
        
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
        
        # Get status counts for New Applicants
        # Accepted count = Total Maintainers (since accepted applicants become maintainers)
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer")
            accepted_count = self.cursor.fetchone()[0]
        except:
            accepted_count = 0
            
        # Pending count = Applicants who haven't been accepted yet
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Applicants WHERE LOWER(TRIM(Status)) IN ('pending', 'waiting', 'in progress')")
            pending_count = self.cursor.fetchone()[0]
        except:
            pending_count = 0
        
        # Get document status counts for Maintainers
        # Get all distinct values in the status column for debugging
        try:
            self.cursor.execute("SELECT DISTINCT status FROM Maintainer")
            all_doc_statuses = self.cursor.fetchall()
            print("Available values in status column:", all_doc_statuses)  # Debug print
        except Exception as e:
            print(f"Error fetching document statuses: {e}")
            all_doc_statuses = []
        
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer WHERE LOWER(TRIM(status)) IN ('claimed', 'claim')")
            claimed_count = self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting claimed: {e}")
            claimed_count = 0
            
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer WHERE LOWER(TRIM(status)) IN ('unclaim', 'unclaimed', 'not claimed')")
            unclaim_count = self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting unclaim: {e}")
            unclaim_count = 0
            
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer WHERE LOWER(TRIM(status)) IN ('on process', 'processing', 'in process')")
            on_process_count = self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting on process: {e}")
            on_process_count = 0
            
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer WHERE LOWER(TRIM(status)) IN ('ready to claim', 'ready', 'ready for claim')")
            ready_claim_count = self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting ready to claim: {e}")
            ready_claim_count = 0
            
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer WHERE LOWER(TRIM(status)) IN ('no uploaded documents', 'no documents', 'no upload', 'not uploaded')")
            no_upload_count = self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error counting no upload: {e}")
            no_upload_count = 0
        
        print(f"Claimed: {claimed_count}, Unclaim: {unclaim_count}, On Process: {on_process_count}, Ready: {ready_claim_count}, No Upload: {no_upload_count}")  # Debug print
        
        # Stats container - 4 cards in a row
        stats_container = ctk.CTkFrame(content, fg_color="transparent")
        stats_container.pack(fill="x", pady=20)
        
        # Configure grid for 4 columns
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # Statistics cards
        self.create_stat_card(stats_container, "Total New Applicants", 
                             applicants_count, "#1f6aa5", 0)
        self.create_stat_card(stats_container, "Total Maintainers", 
                             maintainers_count, "#2b8a3e", 1)
        self.create_stat_card(stats_container, "Accepted", 
                             accepted_count, "#28a745", 2)
        self.create_stat_card(stats_container, "Pending", 
                             pending_count, "#ffc107", 3)
        
        # Graphs container - 3x2 grid
        graphs_container = ctk.CTkFrame(content, fg_color="transparent")
        graphs_container.pack(fill="both", expand=True, pady=20)
        
        # Configure grid for 3x2 layout
        graphs_container.grid_columnconfigure(0, weight=1)
        graphs_container.grid_columnconfigure(1, weight=1)
        graphs_container.grid_rowconfigure(0, weight=1)
        graphs_container.grid_rowconfigure(1, weight=1)
        graphs_container.grid_rowconfigure(2, weight=1)
        
        # Row 0: Course Bar Graphs
        # Top-left: Applicants by Course Bar Graph
        self.create_applicants_bar_graph(graphs_container, 0, 0)
        
        # Top-right: Maintainers by Course Bar Graph
        self.create_maintainers_bar_graph(graphs_container, 0, 1)
        
        # Row 1: Year Level and Document Status
        # Middle-left: Combined Year Level Bar Graph (Applicants & Maintainers)
        self.create_combined_year_level_bar_graph(graphs_container, 1, 0)
        
        # Middle-right: Maintainers Document Status Pie Graph
        self.create_maintainers_status_pie_graph(graphs_container, claimed_count, unclaim_count, 
                                                  on_process_count, ready_claim_count, no_upload_count, 1, 1)
        
        # Row 2: School/Campus Bar Graphs
        # Bottom-left: Applicants by School/Campus Bar Graph
        self.create_applicants_campus_bar_graph(graphs_container, 2, 0)
        
        # Bottom-right: Maintainers by School/Campus Bar Graph
        self.create_maintainers_campus_bar_graph(graphs_container, 2, 1)
    
    def create_applicants_bar_graph(self, parent, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="Applicants by Course", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get data by course
        try:
            self.cursor.execute("SELECT Course, COUNT(*) FROM Applicants GROUP BY Course")
            course_data = self.cursor.fetchall()
            courses = [row[0] if row[0] else "Unknown" for row in course_data]
            counts = [row[1] for row in course_data]
        except:
            courses = ["No Data"]
            counts = [0]
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create horizontal bar chart
        y_pos = range(len(courses))
        ax.barh(y_pos, counts, color='#1f6aa5')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(courses)
        ax.set_xlabel('Count')
        ax.set_ylabel('Courses')
        
        # Set x-axis to show 0, 2, 4, 6, 8, 10
        max_count = max(counts) if counts else 10
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_xlim(0, max(10, max_count + 1))
        
        ax.invert_yaxis()
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_maintainers_bar_graph(self, parent, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="Maintainers by Course", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get data by course
        try:
            self.cursor.execute("SELECT course, COUNT(*) FROM Maintainer GROUP BY course")
            course_data = self.cursor.fetchall()
            courses = [row[0] if row[0] else "Unknown" for row in course_data]
            counts = [row[1] for row in course_data]
        except:
            courses = ["No Data"]
            counts = [0]
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create horizontal bar chart
        y_pos = range(len(courses))
        ax.barh(y_pos, counts, color='#2b8a3e')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(courses)
        ax.set_xlabel('Count')
        ax.set_ylabel('Courses')
        
        # Set x-axis to show 0, 2, 4, 6, 8, 10
        max_count = max(counts) if counts else 10
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_xlim(0, max(10, max_count + 1))
        
        ax.invert_yaxis()
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_applicants_status_pie_graph(self, parent, accepted, pending, rejected, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="New Applicants Status", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Data
        labels = ['Accepted', 'Pending', 'Declined']
        sizes = [accepted, pending, rejected]
        colors = ['#28a745', '#ffc107', '#dc3545']
        
        # Create figure
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Only show pie if there's data
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(sizes, labels=None, colors=colors, 
                                               autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
            # Add legend
            ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        else:
            ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                   verticalalignment='center', transform=ax.transAxes, fontsize=14)
            ax.axis('off')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_maintainers_status_pie_graph(self, parent, claimed, unclaim, on_process, ready_claim, no_upload, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="Maintainers Document Status", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Data
        labels = ['Claimed', 'Unclaim', 'On Process', 'Ready to Claim', 'No Uploaded Docs']
        sizes = [claimed, unclaim, on_process, ready_claim, no_upload]
        colors = ['#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6c757d']
        
        # Create figure
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Only show pie if there's data
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(sizes, labels=None, colors=colors, 
                                               autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
            # Add legend
            ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        else:
            ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                   verticalalignment='center', transform=ax.transAxes, fontsize=14)
            ax.axis('off')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_combined_year_level_bar_graph(self, parent, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="Year Level Distribution", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get applicants data by year level
        try:
            self.cursor.execute("SELECT Year_Level, COUNT(*) FROM Applicants GROUP BY Year_Level")
            applicants_data = self.cursor.fetchall()
            print(f"Applicants year level data: {applicants_data}")  # Debug print
        except Exception as e:
            print(f"Error fetching applicants year level data: {e}")
            applicants_data = []
        
        # Get maintainers data by year level
        try:
            self.cursor.execute("SELECT yearlevel, COUNT(*) FROM Maintainer GROUP BY yearlevel")
            maintainers_data = self.cursor.fetchall()
            print(f"Maintainers year level data: {maintainers_data}")  # Debug print
        except Exception as e:
            print(f"Error fetching maintainers year level data: {e}")
            maintainers_data = []
        
        # Combine and organize data
        year_levels_set = set()
        applicants_dict = {}
        maintainers_dict = {}
        
        for year, count in applicants_data:
            year_key = year if year else "Unknown"
            year_levels_set.add(year_key)
            applicants_dict[year_key] = count
        
        for year, count in maintainers_data:
            year_key = year if year else "Unknown"
            year_levels_set.add(year_key)
            maintainers_dict[year_key] = count
        
        # Sort year levels (1st Year, 2nd Year, 3rd Year, 4th Year)
        year_levels = sorted(list(year_levels_set))
        
        # Get counts for each year level
        applicants_counts = [applicants_dict.get(year, 0) for year in year_levels]
        maintainers_counts = [maintainers_dict.get(year, 0) for year in year_levels]
        
        # Create figure
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        
        if year_levels:
            # Create grouped bar chart
            x = range(len(year_levels))
            width = 0.35
            
            bars1 = ax.bar([i - width/2 for i in x], applicants_counts, width, 
                          label='New Applicants', color='#1f6aa5')
            bars2 = ax.bar([i + width/2 for i in x], maintainers_counts, width, 
                          label='Maintainers', color='#2b8a3e')
            
            ax.set_xlabel('Year Level')
            ax.set_ylabel('Count')
            ax.set_xticks(x)
            ax.set_xticklabels(year_levels, rotation=45, ha='right')
            ax.legend()
            
            # Set y-axis to show even numbers
            max_count = max(max(applicants_counts) if applicants_counts else 0, 
                          max(maintainers_counts) if maintainers_counts else 0)
            ax.set_yticks([0, 2, 4, 6, 8, 10])
            ax.set_ylim(0, max(10, max_count + 1))
        else:
            ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                   verticalalignment='center', transform=ax.transAxes, fontsize=14)
            ax.axis('off')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_applicants_year_level_pie_graph(self, parent, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="Applicants by Year Level", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get data by year level
        try:
            self.cursor.execute("SELECT year_level, COUNT(*) FROM Applicants GROUP BY year_level")
            year_data = self.cursor.fetchall()
            year_levels = [row[0] if row[0] else "Unknown" for row in year_data]
            counts = [row[1] for row in year_data]
            print(f"Year level data: {year_data}")  # Debug print
        except Exception as e:
            print(f"Error fetching year level data: {e}")
            year_levels = []
            counts = []
        
        # Define colors for different year levels
        colors = ['#1f6aa5', '#2b8a3e', '#ffc107', '#dc3545', '#17a2b8', '#6c757d']
        
        # Create figure
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Only show pie if there's data
        if sum(counts) > 0:
            wedges, texts, autotexts = ax.pie(counts, labels=None, colors=colors[:len(year_levels)], 
                                               autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            
            # Add legend
            ax.legend(wedges, year_levels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        else:
            ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                   verticalalignment='center', transform=ax.transAxes, fontsize=14)
            ax.axis('off')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_applicants_campus_bar_graph(self, parent, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="Applicants by Campus", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get data by school (campus)
        try:
            self.cursor.execute("SELECT school, COUNT(*) FROM Applicants GROUP BY school")
            campus_data = self.cursor.fetchall()
            campuses = [row[0] if row[0] else "Unknown" for row in campus_data]
            counts = [row[1] for row in campus_data]
        except Exception as e:
            print(f"Error fetching applicants campus data: {e}")
            campuses = ["No Data"]
            counts = [0]
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create horizontal bar chart
        y_pos = range(len(campuses))
        ax.barh(y_pos, counts, color='#1f6aa5')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(campuses)
        ax.set_xlabel('Count')
        ax.set_ylabel('Campus')
        
        # Set x-axis to show 0, 2, 4, 6, 8, 10
        max_count = max(counts) if counts else 10
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_xlim(0, max(10, max_count + 1))
        
        ax.invert_yaxis()
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_maintainers_campus_bar_graph(self, parent, row, col):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(graph_frame, text="Maintainers by Campus", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get data by school (campus)
        try:
            self.cursor.execute("SELECT school, COUNT(*) FROM Maintainer GROUP BY school")
            campus_data = self.cursor.fetchall()
            campuses = [row[0] if row[0] else "Unknown" for row in campus_data]
            counts = [row[1] for row in campus_data]
        except Exception as e:
            print(f"Error fetching maintainers campus data: {e}")
            campuses = ["No Data"]
            counts = [0]
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create horizontal bar chart
        y_pos = range(len(campuses))
        ax.barh(y_pos, counts, color='#2b8a3e')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(campuses)
        ax.set_xlabel('Count')
        ax.set_ylabel('Campus')
        
        # Set x-axis to show 0, 2, 4, 6, 8, 10
        max_count = max(counts) if counts else 10
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_xlim(0, max(10, max_count + 1))
        
        ax.invert_yaxis()
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_stat_card(self, parent, title, value, color, col):
        # Card frame - smaller height for 5 cards
        card = ctk.CTkFrame(parent, fg_color=color, width=180, height=120, corner_radius=10)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        
        # Value
        ctk.CTkLabel(card, text=str(value), font=("Arial Black", 36), 
                     text_color="white").pack(expand=True, pady=(20, 0))
        
        # Title
        ctk.CTkLabel(card, text=title, font=("Arial", 12), 
                     text_color="white").pack(expand=True, pady=(0, 15))

if __name__ == "__main__":
    app = ScholarshipManagementSystem()
    app.mainloop()