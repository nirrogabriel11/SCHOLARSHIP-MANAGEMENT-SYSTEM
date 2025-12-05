import customtkinter as ctk
import subprocess
import sys
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

def splash_screen():
    splash = ctk.CTk()
    splash.overrideredirect(True)

    # Splash size
    w, h = 640, 360

    # Center window
    splash.update_idletasks()
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    splash.geometry(f"{w}x{h}+{x}+{y}")

    # Full maroon background
    splash.configure(fg_color="maroon")

    # --------- Elements (properly spaced) ---------
    # Logo
    logo_label = ctk.CTkLabel(splash, text="🎓", font=("Helvetica", 36, "bold"), text_color="white", fg_color="maroon")
    logo_label.place(relx=0.5, rely=0.25, anchor="center")

    # University name
    uni_label = ctk.CTkLabel(splash, text="Batangas State University",
                             font=("Helvetica", 24, "bold"),
                             text_color="white", fg_color="maroon")
    uni_label.place(relx=0.5, rely=0.50, anchor="center")

    # Scholarship system text
    sys_label = ctk.CTkLabel(splash, text="Scholarship Management System",
                             font=("Helvetica", 16),
                             text_color="white", fg_color="maroon")
    sys_label.place(relx=0.5, rely=0.65, anchor="center")

    # Loading dots
    dots_label = ctk.CTkLabel(splash, text="", font=("Helvetica", 18, "bold"),
                              text_color="white", fg_color="maroon")
    dots_label.place(relx=0.5, rely=0.80, anchor="center")

    # --------- Animations ---------
    def animate_dots(counter=0):
        dots_label.configure(text="." * ((counter % 3) + 1))
        splash.after(500, animate_dots, counter + 1)

    animate_dots()

    # Close splash after 4 seconds and open login (pass the splash window)
    splash.after(4000, lambda: open_login(splash))

    splash.mainloop()

def open_login(splash):
    try:
        splash.destroy()
    except Exception:
        pass
    login_path = os.path.join(os.path.dirname(__file__), "login.py")
    try:
        subprocess.Popen([sys.executable, login_path], cwd=os.path.dirname(__file__))
    except Exception as e:
        print("Failed to launch login.py:", e)

if __name__ == "__main__":
    splash_screen()
