import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import re
import csv
import os

MAX_LOGIN_ATTEMPTS = 3
login_attempts = 0
is_locked = False

def save_student_to_csv(student_id, password):
    file_exists = os.path.isfile("students.csv")
    with open("students.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["student_id", "password"])
        writer.writerow([student_id, password])

def check_student_in_csv(student_id, password):
    if not os.path.isfile("students.csv"):
        return False
    with open("students.csv", "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["student_id"] == student_id and row["password"] == password:
                return True
    return False

def clear_login_card():
    for widget in login_card.winfo_children():
        widget.destroy()

def show_login():
    clear_login_card()
    title = ctk.CTkLabel(login_card, text="Welcome to Healthy Habits!", text_color="#222")
    title.pack(pady=(30, 0))

    subtitle = ctk.CTkLabel(login_card, text="Sign In to GWSC", text_color="#222")
    subtitle.pack(pady=(5, 20))

    username_label = ctk.CTkLabel(login_card, text="Student ID", text_color="#222")
    username_label.pack(anchor="w", padx=40, pady=(0, 2))
    global username_entry
    username_entry = ctk.CTkEntry(login_card, width=320, height=38, corner_radius=4)
    username_entry.pack(padx=40, pady=(0, 18))

    password_label = ctk.CTkLabel(login_card, text="Password", text_color="#222")
    password_label.pack(anchor="w", padx=40, pady=(0, 2))
    global password_entry
    password_entry = ctk.CTkEntry(login_card, show="*", width=320, height=38, corner_radius=4)
    password_entry.pack(padx=40, pady=(0, 18))

    login_button = ctk.CTkButton(login_card, text="Sign In", command=initiate_login, width=320, height=38, corner_radius=4)
    login_button.pack(padx=40, pady=(10, 10))

    switch_to_register = ctk.CTkButton(login_card, text="Register ID instead", command=show_register, width=320, height=38, corner_radius=4)
    switch_to_register.pack(padx=40, pady=(0, 10))

    # Developer skip button
    skip_button = ctk.CTkButton(login_card, text="Skip (Dev Quick Login)", fg_color="#888", text_color="white",
                                command=lambda: show_home_page("Developer", workouts_logged=3, weekly_goal=4),
                                width=320, height=38, corner_radius=4)
    skip_button.pack(padx=40, pady=(0, 10))


def show_register():
    clear_login_card()
    title = ctk.CTkLabel(login_card, text="Register New Student ID", text_color="#222", font=ctk.CTkFont(size=18, weight="bold"))
    title.pack(pady=(30, 0))

    id_label = ctk.CTkLabel(login_card, text="Student ID (AAA####)", text_color="#222", font=ctk.CTkFont(size=14))
    id_label.pack(anchor="w", padx=40, pady=(20, 2))
    reg_id_entry = ctk.CTkEntry(login_card, width=320, height=38, corner_radius=4, font=ctk.CTkFont(size=14))
    reg_id_entry.pack(padx=40, pady=(0, 18))

    pw_label = ctk.CTkLabel(login_card, text="Password", text_color="#222", font=ctk.CTkFont(size=14))
    pw_label.pack(anchor="w", padx=40, pady=(0, 2))
    reg_pw_entry = ctk.CTkEntry(login_card, show="*", width=320, height=38, corner_radius=4, font=ctk.CTkFont(size=14))
    reg_pw_entry.pack(padx=40, pady=(0, 18))

    def submit_registration():
        new_id = reg_id_entry.get()
        new_pw = reg_pw_entry.get()
        if not re.fullmatch(r"[A-Za-z]{3}\d{4}", new_id):
            messagebox.showwarning("Input Error", "Student ID must be in the format AAA#### (e.g., ZHA0301).")
        elif not new_pw:
            messagebox.showwarning("Input Error", "Password cannot be empty.")
        else:
            save_student_to_csv(new_id, new_pw)
            messagebox.showinfo("Success", f"Student ID '{new_id}' registered successfully!")
            show_login()

    reg_submit = ctk.CTkButton(login_card, text="Register", command=submit_registration, width=320, height=38, corner_radius=4, font=ctk.CTkFont(size=16, weight="bold"))
    reg_submit.pack(padx=40, pady=(10, 10))

    back_to_login = ctk.CTkButton(login_card, text="Back to Login", command=show_login, width=320, height=38, corner_radius=4, font=ctk.CTkFont(size=16, weight="bold"))
    back_to_login.pack(padx=40, pady=(0, 10))

def initiate_login():
    global login_attempts, is_locked
    if is_locked:
        messagebox.showerror("Locked", "Account locked. Try again after 5 minutes.")
        return

    username = username_entry.get()
    password = password_entry.get()

    # Student ID format validation: AAA####
    if not re.fullmatch(r"[A-Za-z]{3}\d{4}", username):
        messagebox.showwarning("Input Error", "Student ID must be in the format AAA#### (e.g., ZHA0301).")
        return

    if not username or not password:
        messagebox.showwarning("Input Error", "Student ID and password cannot be empty.")
        return

    if check_student_in_csv(username, password):
        show_home_page(username)
    else:
        messagebox.showwarning("Login Failed", "Invalid Student ID or password, please try again.")

# Main window setup
root = ctk.CTk()
root.title("Healthy Habits - Home")
root.geometry("1280x720")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Configure grid for root to split exactly in half
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# --- Left Frame ---
left_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=0)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=0)
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

# Logo at top left
logo_placeholder = ctk.CTkLabel(left_frame, text="GWSC HABITS", text_color="#1a237e", font=ctk.CTkFont(size=22, weight="bold"))
logo_placeholder.place(x=40, y=40)

# Card-like login box centered
login_card = ctk.CTkFrame(left_frame, fg_color="white", border_color="#e0e0e0", border_width=2, corner_radius=8)
login_card.grid(row=1, column=0, pady=0)

show_login()

# --- Right Frame ---
right_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=0)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

try:
    bg_img = Image.open("fitness.png")  # Use your own image here
    bg_img = bg_img.resize((1400, 820), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = ctk.CTkLabel(right_frame, image=bg_photo, text="")
    bg_label.image = bg_photo
    bg_label.place(relx=0.8, rely=0.5, anchor="center")
except Exception:
    bg_label = ctk.CTkLabel(right_frame, text="Image Placeholder", font=ctk.CTkFont(size=24, weight="bold"))
    bg_label.place(relx=0.5, rely=0.5, anchor="center")

#HOME PAGE (NOT LOGIN PAGE)

def show_home_page(username="User", workouts_logged=3, weekly_goal=4):
    # Remove login/register frames
    left_frame.grid_remove()
    right_frame.grid_remove()

    # Main Home Frame
    home_frame = ctk.CTkFrame(root, fg_color="white")
    home_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    home_frame.grid_rowconfigure(1, weight=1)
    home_frame.grid_columnconfigure(0, weight=1)

    # --- Top Bar ---
    top_bar = ctk.CTkFrame(home_frame, fg_color="white", height=90)
    top_bar.grid(row=0, column=0, sticky="ew")
    top_bar.grid_columnconfigure(0, weight=1)
    top_bar.grid_columnconfigure(1, weight=0)
    top_bar.grid_columnconfigure(2, weight=0)
    top_bar.grid_columnconfigure(3, weight=0)

    welcome_label = ctk.CTkLabel(top_bar, text=f"Welcome, {username}!", font=ctk.CTkFont(size=24, weight="bold"), text_color="#222")
    welcome_label.grid(row=0, column=0, sticky="w", padx=40, pady=30)

    notif_icon = ctk.CTkLabel(top_bar, text="🔔", font=ctk.CTkFont(size=22))
    notif_icon.grid(row=0, column=1, sticky="e", padx=(0, 18))
    msg_icon = ctk.CTkLabel(top_bar, text="💬", font=ctk.CTkFont(size=22))
    msg_icon.grid(row=0, column=2, sticky="e", padx=(0, 18))

    logo = ctk.CTkLabel(top_bar, text="GWSC healthy habits", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1a237e")
    logo.grid(row=0, column=3, sticky="e", padx=40)

    # --- Scrollable Main Content ---
    scroll_frame = ctk.CTkScrollableFrame(home_frame, fg_color="white")
    scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
    scroll_frame.grid_columnconfigure(0, weight=1)

    # Calculate progress
    progress = min(workouts_logged / weekly_goal, 1.0) if weekly_goal > 0 else 0
    progress_text = f"You've done {workouts_logged} workout{'s' if workouts_logged != 1 else ''} this week!"
    progress_subtext = f"{int(progress * 100)}% of your weekly goal is reached!"

    # Progress Bar Section
    progress_frame = ctk.CTkFrame(scroll_frame, fg_color="#f5f5f5", corner_radius=14)
    progress_frame.grid(row=0, column=0, sticky="ew", padx=80, pady=(40, 30))

    # Centered text above the bar
    progress_text_frame = ctk.CTkFrame(progress_frame, fg_color="#f5f5f5")
    progress_text_frame.pack(fill="x", pady=(22, 0))
    progress_label = ctk.CTkLabel(progress_text_frame, text=progress_text, font=ctk.CTkFont(size=20, weight="bold"), text_color="#222")
    progress_label.pack(anchor="center")
    progress_sub = ctk.CTkLabel(progress_text_frame, text=progress_subtext, font=ctk.CTkFont(size=15), text_color="#666")
    progress_sub.pack(anchor="center")

    progress_bar = ctk.CTkProgressBar(progress_frame, width=700, height=26, progress_color="#1976d2")
    progress_bar.set(progress)
    progress_bar.pack(padx=40, pady=(18, 22))

    # ...rest of your home page code...

    # Tabs for Today's Plan, Workouts, Group
    tabs_frame = ctk.CTkFrame(scroll_frame, fg_color="white")
    tabs_frame.grid(row=1, column=0, sticky="ew", padx=80, pady=(0, 30))
    for i, tab in enumerate(["Today's Plan", "Workouts", "Group"]):
        tab_label = ctk.CTkLabel(
            tabs_frame,
            text=tab,
            font=ctk.CTkFont(size=18, weight="bold" if i == 0 else "normal"),
            text_color="#1976d2" if i == 0 else "#888"
        )
        tab_label.grid(row=0, column=i, padx=40, pady=18)

    # Macro Tracker Section
    macro_frame = ctk.CTkFrame(scroll_frame, fg_color="#f5f5f5", corner_radius=14)
    macro_frame.grid(row=2, column=0, sticky="ew", padx=80, pady=(0, 30))
    macro_frame.grid_columnconfigure((0,1,2), weight=1)

    # Carbs
    carbs_frame = ctk.CTkFrame(macro_frame, fg_color="#e3f2fd", corner_radius=14)
    carbs_frame.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
    ctk.CTkLabel(carbs_frame, text="Carbs", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1976d2").pack(pady=(16,0))
    ctk.CTkLabel(carbs_frame, text="66g / 250g", font=ctk.CTkFont(size=15)).pack()
    ctk.CTkLabel(carbs_frame, text="184g left", font=ctk.CTkFont(size=13), text_color="#666").pack(pady=(0,16))

    # Protein
    protein_frame = ctk.CTkFrame(macro_frame, fg_color="#fce4ec", corner_radius=14)
    protein_frame.grid(row=0, column=1, padx=24, pady=24, sticky="nsew")
    ctk.CTkLabel(protein_frame, text="Protein", font=ctk.CTkFont(size=16, weight="bold"), text_color="#d81b60").pack(pady=(16,0))
    ctk.CTkLabel(protein_frame, text="46g / 100g", font=ctk.CTkFont(size=15)).pack()
    ctk.CTkLabel(protein_frame, text="54g left", font=ctk.CTkFont(size=13), text_color="#666").pack(pady=(0,16))

    # Fat
    fat_frame = ctk.CTkFrame(macro_frame, fg_color="#ede7f6", corner_radius=14)
    fat_frame.grid(row=0, column=2, padx=24, pady=24, sticky="nsew")
    ctk.CTkLabel(fat_frame, text="Fat", font=ctk.CTkFont(size=16, weight="bold"), text_color="#512da8").pack(pady=(16,0))
    ctk.CTkLabel(fat_frame, text="51g / 67g", font=ctk.CTkFont(size=15)).pack()
    ctk.CTkLabel(fat_frame, text="16g left", font=ctk.CTkFont(size=13), text_color="#666").pack(pady=(0,16))

    # --- Bottom Section: Today's Workout & Group Challenge ---
    bottom_frame = ctk.CTkFrame(scroll_frame, fg_color="white")
    bottom_frame.grid(row=3, column=0, sticky="nsew", padx=80, pady=(0, 40))
    bottom_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(1, weight=1)

    # Today's Workout
    workout_frame = ctk.CTkFrame(bottom_frame, fg_color="#fff8e1", corner_radius=14)
    workout_frame.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
    ctk.CTkLabel(workout_frame, text="Today's Workout", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e65100").pack(pady=(18,0))
    ctk.CTkLabel(workout_frame, text="Upper Body", font=ctk.CTkFont(size=15, weight="bold"), text_color="#b71c1c").pack()
    for text in ["3x12 Pushups", "3x8 Rows", "3x8 Dips", "3x8 Pull ups", "3x8 Pushups"]:
        ctk.CTkCheckBox(workout_frame, text=text, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=28, pady=4)
    ctk.CTkButton(workout_frame, text="Change Split", width=140, height=34, font=ctk.CTkFont(size=14)).pack(pady=16)

    # Group Challenge
    challenge_frame = ctk.CTkFrame(bottom_frame, fg_color="#e3f2fd", corner_radius=14)
    challenge_frame.grid(row=0, column=1, padx=24, pady=24, sticky="nsew")
    ctk.CTkLabel(challenge_frame, text="Group Challenge", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1976d2").pack(pady=(18,0))
    ctk.CTkLabel(challenge_frame, text="Marathon!", font=ctk.CTkFont(size=15, weight="bold"), text_color="#b71c1c").pack()
    ctk.CTkLabel(challenge_frame, text="19/43km   4 days", font=ctk.CTkFont(size=14)).pack()
    leaderboard = ctk.CTkLabel(challenge_frame, text="1. You: 6km\n2. Fred: 5.3km\n3. Rob: 3.1km", font=ctk.CTkFont(size=14), justify="left")
    leaderboard.pack(pady=(16,0))

root.mainloop()