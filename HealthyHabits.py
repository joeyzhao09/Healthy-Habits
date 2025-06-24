import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import re
import csv
import os
import json

# ------------------- Data & Constants -------------------
MAX_LOGIN_ATTEMPTS = 3
USERS_FILE = "students.csv"
MEALS_FILE = "meals.json"

DEFAULT_MACRO_GOALS = {'carbs': 250, 'protein': 100, 'fat': 67}
DEFAULT_CAL_GOAL = 2000

FOOD_DB = {
    "apple":      (25, 0, 0, 95),
    "banana":     (27, 1, 0, 105),
    "egg":        (1, 6, 5, 70),
    "rice":       (45, 4, 0, 205),
    "chicken":    (0, 25, 3, 130),
    "milk":       (12, 8, 5, 120),
    "oats":       (27, 5, 3, 150),
    "tofu":       (2, 8, 4, 70),
    "almonds":    (6, 6, 14, 160),
    "broccoli":   (6, 3, 0, 30),
    "berries":    (15, 1, 0, 60),
    "salmon":     (0, 22, 12, 180),
    "avocado":    (12, 3, 21, 240),
    "bread":      (14, 2, 1, 70),
    "cheese":     (1, 7, 9, 115),
}

BUILTIN_RECIPES = [
    {
        "name": "Overnight Oats Bowl",
        "ingredients": [
            "1/2 cup rolled oats", "1/2 cup skim milk", "1/2 cup Greek yogurt",
            "1/2 banana, sliced", "1/2 cup mixed berries", "1 tsp chia seeds"
        ],
        "steps": [
            "Mix oats, milk, yogurt, and chia seeds in a bowl.",
            "Refrigerate overnight.",
            "Top with banana and berries in the morning."
        ],
        "imagePath": "images/oats_bowl.jpg",
        "macros": {"carbs": 45, "protein": 18, "fat": 4}
    },
    # ... (rest of recipes as before)
]

def save_student_to_csv(student_id, password):
    file_exists = os.path.isfile(USERS_FILE)
    with open(USERS_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["student_id", "password"])
        writer.writerow([student_id, password])

def check_student_in_csv(student_id, password):
    if not os.path.isfile(USERS_FILE):
        return False
    with open(USERS_FILE, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["student_id"] == student_id and row["password"] == password:
                return True
    return False

def load_meals(username):
    if not os.path.isfile(MEALS_FILE):
        return []
    with open(MEALS_FILE, "r") as f:
        data = json.load(f)
    return data.get(username, [])

def save_meal(username, meal_data):
    if os.path.isfile(MEALS_FILE):
        with open(MEALS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}
    if username not in data:
        data[username] = []
    data[username].append(meal_data)
    with open(MEALS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def calc_calories(carbs, protein, fat):
    return carbs * 4 + protein * 4 + fat * 9

class MiniWheel(ctk.CTkCanvas):
    def __init__(self, parent, label, value, goal, color, size=90, unit="g", **kwargs):
        super().__init__(parent, width=size, height=size, bg="white", highlightthickness=0, **kwargs)
        self.value = value
        self.goal = goal
        self.label = label
        self.color = color
        self.size = size
        self.unit = unit
        self.draw_wheel()

    def update_value(self, value):
        self.value = value
        self.delete("all")
        self.draw_wheel()

    def draw_wheel(self):
        portion = min(self.value / self.goal, 1.0) if self.goal > 0 else 0
        angle_extent = 360 * portion
        self.create_oval(10, 10, self.size-10, self.size-10, fill="#f0f0f0", outline="")
        self.create_arc(10, 10, self.size-10, self.size-10, start=90, extent=-angle_extent,
                        style="pieslice", outline="", fill=self.color)
        self.create_text(self.size//2, self.size//2-6,
                         text=f"{int(self.value)}{self.unit}", fill="#222", font=("Arial", 12, "bold"))
        self.create_text(self.size//2, self.size//2+15,
                         text=self.label, fill="#888", font=("Arial", 10))

class CalorieWheel(ctk.CTkCanvas):
    def __init__(self, parent, cal_value, cal_goal, size=180, **kwargs):
        super().__init__(parent, width=size, height=size, bg="white", highlightthickness=0, **kwargs)
        self.calValue = cal_value
        self.calGoal = cal_goal
        self.size = size
        self.draw_wheel()

    def update_value(self, cal_value):
        self.calValue = cal_value
        self.delete("all")
        self.draw_wheel()

    def draw_wheel(self):
        portion = min(self.calValue / self.calGoal, 1.0) if self.calGoal > 0 else 0
        angle_extent = 360 * portion
        self.create_oval(12, 12, self.size-12, self.size-12, fill="#f8f8f8", outline="")
        self.create_arc(12, 12, self.size-12, self.size-12, start=90, extent=-angle_extent,
                        style="pieslice", outline="", fill="#ffa726")
        self.create_text(self.size//2, self.size//2-8,
                         text=f"{int(self.calValue)}", fill="#d84315", font=("Arial", 24, "bold"))
        self.create_text(self.size//2, self.size//2+22,
                         text="Calories", fill="#888", font=("Arial", 13))

def clear_login_card():
    for widget in login_card.winfo_children():
        widget.destroy()

def show_login():
    clear_login_card()
    ctk.CTkLabel(login_card, text="Welcome to Healthy Habits!", text_color="#222").pack(pady=(30, 0))
    ctk.CTkLabel(login_card, text="Sign In to GWSC", text_color="#222").pack(pady=(5, 20))
    ctk.CTkLabel(login_card, text="Student ID", text_color="#222").pack(anchor="w", padx=40, pady=(0, 2))
    global username_entry
    username_entry = ctk.CTkEntry(login_card, width=320, height=38, corner_radius=4)
    username_entry.pack(padx=40, pady=(0, 18))

    ctk.CTkLabel(login_card, text="Password", text_color="#222").pack(anchor="w", padx=40, pady=(0, 2))
    global password_entry
    password_entry = ctk.CTkEntry(login_card, show="*", width=320, height=38, corner_radius=4)
    password_entry.pack(padx=40, pady=(0, 18))

    ctk.CTkButton(login_card, text="Sign In", command=initiate_login, width=320, height=38, corner_radius=4).pack(padx=40, pady=(10, 10))
    ctk.CTkButton(login_card, text="Register ID instead", command=show_register, width=320, height=38, corner_radius=4).pack(padx=40, pady=(0, 10))
    ctk.CTkButton(login_card, text="Skip (Dev Quick Login)", fg_color="#888", text_color="white",
                  command=lambda: show_home_page("Developer", workouts_logged=3, weekly_goal=4),
                  width=320, height=38, corner_radius=4).pack(padx=40, pady=(0, 10))

def show_register():
    clear_login_card()
    ctk.CTkLabel(login_card, text="Register New Student ID", text_color="#222", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 0))
    ctk.CTkLabel(login_card, text="Student ID (AAA####)", text_color="#222", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=40, pady=(20, 2))
    reg_id_entry = ctk.CTkEntry(login_card, width=320, height=38, corner_radius=4, font=ctk.CTkFont(size=14))
    reg_id_entry.pack(padx=40, pady=(0, 18))
    ctk.CTkLabel(login_card, text="Password", text_color="#222", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=40, pady=(0, 2))
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
    ctk.CTkButton(login_card, text="Register", command=submit_registration, width=320, height=38, corner_radius=4).pack(padx=40, pady=(10, 10))
    ctk.CTkButton(login_card, text="Back to Login", command=show_login, width=320, height=38, corner_radius=4).pack(padx=40, pady=(0, 10))

def initiate_login():
    username = username_entry.get()
    password = password_entry.get()
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

# ------------- Main Window Setup -------------
root = ctk.CTk()
root.title("Healthy Habits - Home")
root.geometry("1280x720")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

left_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=0)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=0)
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

logo_placeholder = ctk.CTkLabel(left_frame, text="GWSC HABITS", text_color="#1a237e", font=ctk.CTkFont(size=22, weight="bold"))
logo_placeholder.place(x=40, y=40)

login_card = ctk.CTkFrame(left_frame, fg_color="white", border_color="#e0e0e0", border_width=2, corner_radius=8)
login_card.grid(row=1, column=0, pady=0)
show_login()

right_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=0)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

try:
    bg_img = Image.open("fitness.png")
    bg_img = bg_img.resize((1400, 820), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = ctk.CTkLabel(right_frame, image=bg_photo, text="")
    bg_label.image = bg_photo
    bg_label.place(relx=0.8, rely=0.5, anchor="center")
except Exception:
    bg_label = ctk.CTkLabel(right_frame, text="Image Placeholder", font=ctk.CTkFont(size=24, weight="bold"))
    bg_label.place(relx=0.5, rely=0.5, anchor="center")

# --------- Real-Time Macro/Calorie Wheel Update System ---------
def show_home_page(username="User", workouts_logged=3, weekly_goal=4):
    left_frame.grid_remove()
    right_frame.grid_remove()

    home_frame = ctk.CTkFrame(root, fg_color="white")
    home_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    home_frame.grid_rowconfigure(1, weight=1)
    home_frame.grid_columnconfigure(0, weight=1)

    top_bar = ctk.CTkFrame(home_frame, fg_color="white", height=90)
    top_bar.grid(row=0, column=0, sticky="ew")
    top_bar.grid_columnconfigure(0, weight=1)
    top_bar.grid_columnconfigure(1, weight=0)
    top_bar.grid_columnconfigure(2, weight=0)
    top_bar.grid_columnconfigure(3, weight=0)
    ctk.CTkLabel(top_bar, text=f"Welcome, {username}!", font=ctk.CTkFont(size=24, weight="bold"), text_color="#222").grid(row=0, column=0, sticky="w", padx=40, pady=30)
    ctk.CTkLabel(top_bar, text="🔔", font=ctk.CTkFont(size=22)).grid(row=0, column=1, sticky="e", padx=(0, 18))
    ctk.CTkLabel(top_bar, text="💬", font=ctk.CTkFont(size=22)).grid(row=0, column=2, sticky="e", padx=(0, 18))
    ctk.CTkLabel(top_bar, text="GWSC healthy habits", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1a237e").grid(row=0, column=3, sticky="e", padx=40)

    scroll_frame = ctk.CTkScrollableFrame(home_frame, fg_color="white")
    scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
    scroll_frame.grid_columnconfigure(0, weight=1)

    progress = min(workouts_logged / weekly_goal, 1.0) if weekly_goal > 0 else 0
    progress_text = f"You've done {workouts_logged} workout{'s' if workouts_logged != 1 else ''} this week!"
    progress_subtext = f"{int(progress * 100)}% of your weekly goal is reached!"

    progress_frame = ctk.CTkFrame(scroll_frame, fg_color="#f5f5f5", corner_radius=14)
    progress_frame.grid(row=0, column=0, sticky="ew", padx=80, pady=(40, 30))
    progress_text_frame = ctk.CTkFrame(progress_frame, fg_color="#f5f5f5")
    progress_text_frame.pack(fill="x", pady=(22, 0))
    ctk.CTkLabel(progress_text_frame, text=progress_text, font=ctk.CTkFont(size=20, weight="bold"), text_color="#222").pack(anchor="center")
    ctk.CTkLabel(progress_text_frame, text=progress_subtext, font=ctk.CTkFont(size=15), text_color="#666").pack(anchor="center")
    progress_bar = ctk.CTkProgressBar(progress_frame, width=700, height=26, progress_color="#1976d2")
    progress_bar.set(progress)
    progress_bar.pack(padx=40, pady=(18, 22))

    macro_frame = ctk.CTkFrame(scroll_frame, fg_color="#f5f5f5", corner_radius=14)
    macro_frame.grid(row=2, column=0, sticky="ew", padx=80, pady=(0, 30))
    macro_frame.grid_columnconfigure(0, weight=1)
    macro_frame.grid_columnconfigure(1, weight=1)
    macro_frame.grid_columnconfigure(2, weight=1)
    macro_frame.grid_columnconfigure(3, weight=1)

    # --- Real-time wheels ---
    mini_colors = {"carbs": "#1976d2", "protein": "#d81b60", "fat": "#512da8"}
    macro_labels = ["carbs", "protein", "fat"]
    mini_wheels = []
    for i, macro in enumerate(macro_labels):
        mw = MiniWheel(macro_frame, macro.title(), 0, DEFAULT_MACRO_GOALS[macro], mini_colors[macro])
        mw.grid(row=0, column=i, padx=14, pady=18)
        mini_wheels.append(mw)
    cal_wheel = CalorieWheel(macro_frame, 0, DEFAULT_CAL_GOAL)
    cal_wheel.grid(row=0, column=3, padx=18, pady=18)

    macro_side = ctk.CTkFrame(macro_frame, fg_color="#f5f5f5")
    macro_side.grid(row=1, column=0, columnspan=4, sticky="ew")
    btn_frame = ctk.CTkFrame(macro_side, fg_color="#f5f5f5")
    btn_frame.pack(pady=(6, 0))
    ctk.CTkButton(btn_frame, text="Log Meal", width=85, command=lambda: show_meal_log(username)).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Quick Log", width=85, fg_color="#90caf9", text_color="#1565c0", command=lambda: show_quick_log(username)).pack(side="left", padx=8)
    ctk.CTkButton(macro_side, text="Browse Healthy Recipes", width=180, command=lambda: show_recipe_browser(username)).pack(pady=(14, 10))

    # --- Meals Section ---
    meals_frame = ctk.CTkFrame(scroll_frame, fg_color="#fff8e1", corner_radius=14)
    meals_frame.grid(row=3, column=0, sticky="ew", padx=80, pady=(0, 30))
    ctk.CTkLabel(meals_frame, text="Today's Meals", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e65100").pack(anchor="w", padx=24, pady=(12, 0))

    meal_labels = []
    def update_meals():
        meals = load_meals(username)
        for label in meal_labels:
            label.destroy()
        meal_labels.clear()
        if meals:
            for meal in meals[-4:][::-1]:
                txt = f"{meal['mealName']}  -  C:{meal['carbs']}g  P:{meal['protein']}g  F:{meal['fat']}g"
                lbl = ctk.CTkLabel(meals_frame, text=txt, font=ctk.CTkFont(size=14))
                lbl.pack(anchor="w", padx=32, pady=3)
                meal_labels.append(lbl)
        else:
            lbl = ctk.CTkLabel(meals_frame, text="No meals logged today.", font=ctk.CTkFont(size=14), text_color="#888")
            lbl.pack(anchor="w", padx=32, pady=3)
            meal_labels.append(lbl)

    # --- Real-time update function ---
    def update_wheels():
        meals = load_meals(username)
        macros_today = {"carbs": 0, "protein": 0, "fat": 0}
        total_cals = 0
        for meal in meals:
            for m in macros_today:
                macros_today[m] += meal.get(m, 0)
            total_cals += calc_calories(meal.get("carbs", 0), meal.get("protein", 0), meal.get("fat", 0))
        for i, macro in enumerate(macro_labels):
            mini_wheels[i].update_value(macros_today[macro])
        cal_wheel.update_value(total_cals)
        update_meals()
        macro_frame.after(1000, update_wheels)  # update every second

    update_wheels()

# ------------------- Login/Register -------------------
def clear_login_card():
    for widget in login_card.winfo_children():
        widget.destroy()

def show_login():
    clear_login_card()
    ctk.CTkLabel(login_card, text="Welcome to Healthy Habits!", text_color="#222").pack(pady=(30, 0))
    ctk.CTkLabel(login_card, text="Sign In to GWSC", text_color="#222").pack(pady=(5, 20))
    ctk.CTkLabel(login_card, text="Student ID", text_color="#222").pack(anchor="w", padx=40, pady=(0, 2))
    global username_entry
    username_entry = ctk.CTkEntry(login_card, width=320, height=38, corner_radius=4)
    username_entry.pack(padx=40, pady=(0, 18))

    ctk.CTkLabel(login_card, text="Password", text_color="#222").pack(anchor="w", padx=40, pady=(0, 2))
    global password_entry
    password_entry = ctk.CTkEntry(login_card, show="*", width=320, height=38, corner_radius=4)
    password_entry.pack(padx=40, pady=(0, 18))

    ctk.CTkButton(login_card, text="Sign In", command=initiate_login, width=320, height=38, corner_radius=4).pack(padx=40, pady=(10, 10))
    ctk.CTkButton(login_card, text="Register ID instead", command=show_register, width=320, height=38, corner_radius=4).pack(padx=40, pady=(0, 10))
    ctk.CTkButton(login_card, text="Skip (Dev Quick Login)", fg_color="#888", text_color="white",
                  command=lambda: show_home_page("Developer", workouts_logged=3, weekly_goal=4),
                  width=320, height=38, corner_radius=4).pack(padx=40, pady=(0, 10))

def show_register():
    clear_login_card()
    ctk.CTkLabel(login_card, text="Register New Student ID", text_color="#222", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 0))
    ctk.CTkLabel(login_card, text="Student ID (AAA####)", text_color="#222", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=40, pady=(20, 2))
    reg_id_entry = ctk.CTkEntry(login_card, width=320, height=38, corner_radius=4, font=ctk.CTkFont(size=14))
    reg_id_entry.pack(padx=40, pady=(0, 18))
    ctk.CTkLabel(login_card, text="Password", text_color="#222", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=40, pady=(0, 2))
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
    ctk.CTkButton(login_card, text="Register", command=submit_registration, width=320, height=38, corner_radius=4).pack(padx=40, pady=(10, 10))
    ctk.CTkButton(login_card, text="Back to Login", command=show_login, width=320, height=38, corner_radius=4).pack(padx=40, pady=(0, 10))

def initiate_login():
    username = username_entry.get()
    password = password_entry.get()
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

# ------------------- Main Window Setup -------------------
root = ctk.CTk()
root.title("Healthy Habits - Home")
root.geometry("1280x720")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

left_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=0)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=0)
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

logo_placeholder = ctk.CTkLabel(left_frame, text="GWSC HABITS", text_color="#1a237e", font=ctk.CTkFont(size=22, weight="bold"))
logo_placeholder.place(x=40, y=40)

login_card = ctk.CTkFrame(left_frame, fg_color="white", border_color="#e0e0e0", border_width=2, corner_radius=8)
login_card.grid(row=1, column=0, pady=0)
show_login()

right_frame = ctk.CTkFrame(root, fg_color="white", corner_radius=0)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

try:
    bg_img = Image.open("fitness.png")
    bg_img = bg_img.resize((1400, 820), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = ctk.CTkLabel(right_frame, image=bg_photo, text="")
    bg_label.image = bg_photo
    bg_label.place(relx=0.8, rely=0.5, anchor="center")
except Exception:
    bg_label = ctk.CTkLabel(right_frame, text="Image Placeholder", font=ctk.CTkFont(size=24, weight="bold"))
    bg_label.place(relx=0.5, rely=0.5, anchor="center")

# ------------------- Quick Log (with Food Search) -------------------
def show_quick_log(username):
    win = ctk.CTkToplevel(root)
    win.title("Quick Macro Log")
    win.geometry("380x340")
    ctk.CTkLabel(win, text="Quick Macro Log", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=10)
    carbs_entry = ctk.CTkEntry(win, width=80, placeholder_text="Carbs (g)")
    carbs_entry.pack(pady=6)
    protein_entry = ctk.CTkEntry(win, width=80, placeholder_text="Protein (g)")
    protein_entry.pack(pady=6)
    fat_entry = ctk.CTkEntry(win, width=80, placeholder_text="Fat (g)")
    fat_entry.pack(pady=6)
    # Food search UI
    ctk.CTkLabel(win, text="Search Common Foods (auto-fill):", font=ctk.CTkFont(size=13)).pack(pady=(12,0))
    search_entry = ctk.CTkEntry(win, width=200, placeholder_text="e.g. apple, egg")
    search_entry.pack(pady=(2, 2))
    result_var = ctk.StringVar()
    result_label = ctk.CTkLabel(win, textvariable=result_var, font=ctk.CTkFont(size=12), text_color="#1976d2")
    result_label.pack()
    def do_search():
        food = search_entry.get().strip().lower()
        if food in FOOD_DB:
            c, p, f, cal = FOOD_DB[food]
            carbs_entry.delete(0, "end")
            carbs_entry.insert(0, str(c))
            protein_entry.delete(0, "end")
            protein_entry.insert(0, str(p))
            fat_entry.delete(0, "end")
            fat_entry.insert(0, str(f))
            result_var.set(f"{food.title()}: {c}g C, {p}g P, {f}g F, {cal} kcal")
        else:
            result_var.set("Food not found.")
    ctk.CTkButton(win, text="Search", command=do_search, width=80).pack(pady=2)
    def submit():
        try:
            meal = {
                "mealName": "Quick Log",
                "carbs": int(carbs_entry.get()),
                "protein": int(protein_entry.get()),
                "fat": int(fat_entry.get())
            }
            for macro in ["carbs", "protein", "fat"]:
                if not (0 <= meal[macro] <= 500):
                    raise ValueError(f"{macro.title()} out of range")
            save_meal(username, meal)
            messagebox.showinfo("Success", "Quick log added!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Please enter valid values. {e}")
    ctk.CTkButton(win, text="Add Quick Log", command=submit, width=120).pack(pady=16)

# ------------------- Meal Log -------------------
def show_meal_log(username, parent_frame=None):
    win = ctk.CTkToplevel(root) if parent_frame is None else ctk.CTkFrame(parent_frame)
    win.title("Log Meal" if parent_frame is None else "")
    win.geometry("420x460") if parent_frame is None else None
    labels = ["Meal Name", "Carbs (g)", "Protein (g)", "Fat (g)"]
    entries = []
    for i, label in enumerate(labels):
        lbl = ctk.CTkLabel(win, text=label)
        lbl.pack(pady=(16, 2))
        entry = ctk.CTkEntry(win, width=340)
        entry.pack(pady=(0, 8))
        entries.append(entry)
    def submit():
        try:
            meal = {
                "mealName": entries[0].get(),
                "carbs": int(entries[1].get()),
                "protein": int(entries[2].get()),
                "fat": int(entries[3].get())
            }
            for macro in ["carbs", "protein", "fat"]:
                if not (0 <= meal[macro] <= 500):
                    raise ValueError(f"{macro.title()} out of range")
            save_meal(username, meal)
            messagebox.showinfo("Success", "Meal logged!")
            if parent_frame is None: win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Please enter valid values. {e}")
    ctk.CTkButton(win, text="Log Meal", command=submit).pack(pady=(14, 8))
    if parent_frame is None:
        return win
    else:
        return win

# ------------------- Recipe Browser -------------------
def show_recipe_browser(username):
    for widget in root.winfo_children():
        widget.grid_remove()
    recipe_frame = ctk.CTkFrame(root, fg_color="#f3f6fd")
    recipe_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    recipe_frame.grid_columnconfigure(0, weight=1)
    recipe_frame.grid_rowconfigure(1, weight=1)
    # Top bar
    top_bar = ctk.CTkFrame(recipe_frame, fg_color="#e3f2fd", height=82, corner_radius=0)
    top_bar.grid(row=0, column=0, sticky="ew")
    ctk.CTkLabel(top_bar, text="Healthy Recipes", font=ctk.CTkFont(size=23, weight="bold"), text_color="#1976d2").grid(row=0, column=0, sticky="w", padx=44, pady=26)
    ctk.CTkButton(top_bar, text="Back to Home", command=lambda: show_home_page(username), width=120, fg_color="#1565c0", text_color="white", corner_radius=22).grid(row=0, column=1, sticky="e", padx=44, pady=26)
    # Recipe grid
    recipe_scroll = ctk.CTkScrollableFrame(recipe_frame, fg_color="#f3f6fd")
    recipe_scroll.grid(row=1, column=0, sticky="nsew", padx=62, pady=(0, 26))
    recipe_scroll.grid_columnconfigure((0, 1), weight=1)
    for i, recipe in enumerate(BUILTIN_RECIPES):
        rf = ctk.CTkFrame(recipe_scroll, fg_color="white", corner_radius=24, border_color="#dae1ed", border_width=1)
        rf.grid(row=i//2, column=i%2, padx=16, pady=18, sticky="ew")
        rf.grid_columnconfigure(0, weight=0)
        rf.grid_columnconfigure(1, weight=1)
        # Image
        if recipe.get("imagePath") and os.path.exists(recipe["imagePath"]):
            try:
                img = Image.open(recipe["imagePath"]).resize((110, 110))
                tkImg = ImageTk.PhotoImage(img)
                imgLabel = ctk.CTkLabel(rf, image=tkImg, text="")
                imgLabel.image = tkImg
                imgLabel.grid(row=0, column=0, rowspan=3, padx=24, pady=18)
            except Exception:
                imgLabel = ctk.CTkLabel(rf, text="[No Image]", width=100)
                imgLabel.grid(row=0, column=0, rowspan=3, padx=24, pady=18)
        else:
            imgLabel = ctk.CTkLabel(rf, text="[No Image]", width=100)
            imgLabel.grid(row=0, column=0, rowspan=3, padx=24, pady=18)
        ctk.CTkLabel(rf, text=recipe["name"], font=ctk.CTkFont(size=17, weight="bold"), text_color="#1976d2").grid(row=0, column=1, sticky="w", pady=(20,0))
        macroStr = f'C:{recipe["macros"]["carbs"]}g   P:{recipe["macros"]["protein"]}g   F:{recipe["macros"]["fat"]}g'
        ctk.CTkLabel(rf, text=macroStr, font=ctk.CTkFont(size=13), text_color="#666").grid(row=1, column=1, sticky="w")
        ctk.CTkLabel(rf, text=f'Ingredients: {len(recipe["ingredients"])} | Steps: {len(recipe["steps"])}', font=ctk.CTkFont(size=13), text_color="#888").grid(row=2, column=1, sticky="w")
        def make_view_recipe(recipe=recipe):
            def view_recipe_window():
                win = ctk.CTkToplevel(root)
                win.title(recipe["name"])
                win.geometry("540x600")
                win.configure(bg="#f3f6fd")
                inner = ctk.CTkFrame(win, fg_color="white", corner_radius=16)
                inner.pack(padx=18, pady=18, fill="both", expand=True)
                if recipe.get("imagePath") and os.path.exists(recipe["imagePath"]):
                    try:
                        img = Image.open(recipe["imagePath"]).resize((220, 220))
                        tkImg = ImageTk.PhotoImage(img)
                        ctk.CTkLabel(inner, image=tkImg, text="").pack(pady=12)
                        win.image = tkImg
                    except Exception:
                        pass
                ctk.CTkLabel(inner, text=recipe["name"], font=ctk.CTkFont(size=16, weight="bold"), text_color="#1976d2").pack()
                macroStr = f'Carbs: {recipe["macros"]["carbs"]}g   Protein: {recipe["macros"]["protein"]}g   Fat: {recipe["macros"]["fat"]}g'
                ctk.CTkLabel(inner, text=macroStr, font=ctk.CTkFont(size=13), text_color="#666").pack()
                ingrText = "\n".join("- " + i for i in recipe["ingredients"])
                ingrBox = ctk.CTkTextbox(inner, width=480, height=90, wrap="word")
                ingrBox.pack(pady=(8, 2))
                ingrBox.insert("end", "Ingredients:\n" + ingrText)
                ingrBox.configure(state="disabled")
                ctk.CTkLabel(inner, text="Steps:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=8)
                stepsText = "\n".join(f"{idx+1}. {s}" for idx, s in enumerate(recipe["steps"]))
                stepsBox = ctk.CTkTextbox(inner, width=480, height=140, wrap="word")
                stepsBox.pack()
                stepsBox.insert("end", stepsText)
                stepsBox.configure(state="disabled")
            return view_recipe_window
        ctk.CTkButton(rf, text="View", width=60, fg_color="#1976d2", text_color="white", command=make_view_recipe()).grid(row=0, column=2, rowspan=3, padx=16, pady=16, sticky="e")

# ------------------- Home Page (with Macro + Calorie Wheels) -------------------
def show_home_page(username="User", workouts_logged=3, weekly_goal=4):
    left_frame.grid_remove()
    right_frame.grid_remove()

    home_frame = ctk.CTkFrame(root, fg_color="white")
    home_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    home_frame.grid_rowconfigure(1, weight=1)
    home_frame.grid_columnconfigure(0, weight=1)

    top_bar = ctk.CTkFrame(home_frame, fg_color="white", height=90)
    top_bar.grid(row=0, column=0, sticky="ew")
    top_bar.grid_columnconfigure(0, weight=1)
    top_bar.grid_columnconfigure(1, weight=0)
    top_bar.grid_columnconfigure(2, weight=0)
    top_bar.grid_columnconfigure(3, weight=0)
    ctk.CTkLabel(top_bar, text=f"Welcome, {username}!", font=ctk.CTkFont(size=24, weight="bold"), text_color="#222").grid(row=0, column=0, sticky="w", padx=40, pady=30)
    ctk.CTkLabel(top_bar, text="🔔", font=ctk.CTkFont(size=22)).grid(row=0, column=1, sticky="e", padx=(0, 18))
    ctk.CTkLabel(top_bar, text="💬", font=ctk.CTkFont(size=22)).grid(row=0, column=2, sticky="e", padx=(0, 18))
    ctk.CTkLabel(top_bar, text="GWSC healthy habits", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1a237e").grid(row=0, column=3, sticky="e", padx=40)

    scroll_frame = ctk.CTkScrollableFrame(home_frame, fg_color="white")
    scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
    scroll_frame.grid_columnconfigure(0, weight=1)

    progress = min(workouts_logged / weekly_goal, 1.0) if weekly_goal > 0 else 0
    progress_text = f"You've done {workouts_logged} workout{'s' if workouts_logged != 1 else ''} this week!"
    progress_subtext = f"{int(progress * 100)}% of your weekly goal is reached!"

    progress_frame = ctk.CTkFrame(scroll_frame, fg_color="#f5f5f5", corner_radius=14)
    progress_frame.grid(row=0, column=0, sticky="ew", padx=80, pady=(40, 30))
    progress_text_frame = ctk.CTkFrame(progress_frame, fg_color="#f5f5f5")
    progress_text_frame.pack(fill="x", pady=(22, 0))
    ctk.CTkLabel(progress_text_frame, text=progress_text, font=ctk.CTkFont(size=20, weight="bold"), text_color="#222").pack(anchor="center")
    ctk.CTkLabel(progress_text_frame, text=progress_subtext, font=ctk.CTkFont(size=15), text_color="#666").pack(anchor="center")
    progress_bar = ctk.CTkProgressBar(progress_frame, width=700, height=26, progress_color="#1976d2")
    progress_bar.set(progress)
    progress_bar.pack(padx=40, pady=(18, 22))

    macro_frame = ctk.CTkFrame(scroll_frame, fg_color="#f5f5f5", corner_radius=14)
    macro_frame.grid(row=2, column=0, sticky="ew", padx=80, pady=(0, 30))
    macro_frame.grid_columnconfigure(0, weight=1)
    macro_frame.grid_columnconfigure(1, weight=1)
    macro_frame.grid_columnconfigure(2, weight=1)
    macro_frame.grid_columnconfigure(3, weight=1)

    meals = load_meals(username)
    macros_today = {"carbs": 0, "protein": 0, "fat": 0}
    total_cals = 0
    for meal in meals:
        for m in macros_today:
            macros_today[m] += meal.get(m, 0)
        total_cals += calc_calories(meal.get("carbs", 0), meal.get("protein", 0), meal.get("fat", 0))

    mini_colors = {"carbs": "#1976d2", "protein": "#d81b60", "fat": "#512da8"}
    for i, macro in enumerate(["carbs", "protein", "fat"]):
        mw = MiniWheel(macro_frame, macro.title(), macros_today[macro], DEFAULT_MACRO_GOALS[macro], mini_colors[macro])
        mw.grid(row=0, column=i, padx=14, pady=18)
    cal_wheel = CalorieWheel(macro_frame, total_cals, DEFAULT_CAL_GOAL)
    cal_wheel.grid(row=0, column=3, padx=18, pady=18)

    macro_side = ctk.CTkFrame(macro_frame, fg_color="#f5f5f5")
    macro_side.grid(row=1, column=0, columnspan=4, sticky="ew")
    btn_frame = ctk.CTkFrame(macro_side, fg_color="#f5f5f5")
    btn_frame.pack(pady=(6, 0))
    ctk.CTkButton(btn_frame, text="Log Meal", width=85, command=lambda: show_meal_log(username)).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Quick Log", width=85, fg_color="#90caf9", text_color="#1565c0", command=lambda: show_quick_log(username)).pack(side="left", padx=8)
    ctk.CTkButton(macro_side, text="Browse Healthy Recipes", width=180, command=lambda: show_recipe_browser(username)).pack(pady=(14, 10))

    meals_frame = ctk.CTkFrame(scroll_frame, fg_color="#fff8e1", corner_radius=14)
    meals_frame.grid(row=3, column=0, sticky="ew", padx=80, pady=(0, 30))
    ctk.CTkLabel(meals_frame, text="Today's Meals", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e65100").pack(anchor="w", padx=24, pady=(12, 0))
    if meals:
        for meal in meals[-4:][::-1]:
            txt = f"{meal['mealName']}  -  C:{meal['carbs']}g  P:{meal['protein']}g  F:{meal['fat']}g"
            ctk.CTkLabel(meals_frame, text=txt, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=32, pady=3)
    else:
        ctk.CTkLabel(meals_frame, text="No meals logged today.", font=ctk.CTkFont(size=14), text_color="#888").pack(anchor="w", padx=32, pady=3)

    # ... (rest of your home page: tabs, workouts, group challenge, etc.)

root.mainloop()
