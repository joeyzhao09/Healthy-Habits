import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import re
import csv
import os
import json

# --- Color Constants ---
COLOR_BG = "#f7faff"
COLOR_ACCENT = "#b5d6ff"
COLOR_ACCENT2 = "#ffc6c6"
COLOR_ACCENT3 = "#c6ffd1"
COLOR_ACCENT4 = "#ffeec6"
COLOR_TEXT = "#23263b"
COLOR_PRIMARY = "#1976d2"
COLOR_SECONDARY = "#d81b60"
COLOR_TERTIARY = "#512da8"
COLOR_BTN = "#63b8ff"
COLOR_BTN_TXT = "#234b63"
COLOR_WHITE = "#ffffff"

# --- Data & Constants ---
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
    {
        "name": "Grilled Salmon & Greens",
        "ingredients": [
            "1 salmon fillet (120g)", "1 cup spinach", "1/2 cup cherry tomatoes",
            "1/4 avocado, sliced", "1 tsp olive oil", "1 lemon wedge"
        ],
        "steps": [
            "Grill the salmon fillet until cooked through.",
            "Toss spinach, tomatoes, avocado, and olive oil in a bowl.",
            "Serve salmon on top. Squeeze lemon before eating."
        ],
        "imagePath": "images/salmon_bowl.jpg",
        "macros": {"carbs": 7, "protein": 28, "fat": 18}
    }
]

EXERCISE_SUGGESTIONS = [
    [("Push-ups", "exercise1.png"), ("Squats", "exercise2.png"), ("Burpees", "exercise3.png")],
    [("Plank", "exercise4.png"), ("Wall Sit", "exercise5.png"), ("Jumping Jacks", "exercise6.png")],
    [("Lunges", "exercise7.png"), ("Pull-ups", "exercise8.png"), ("Mountain Climbers", "exercise9.png")],
    [("Crunches", "exercise10.png"), ("Glute Bridges", "exercise11.png"), ("High Knees", "exercise12.png")]
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
    def __init__(self, parent, label, value, goal, color, size=100, unit="g", **kwargs):
        super().__init__(parent, width=size, height=size, bg=COLOR_BG, highlightthickness=0, **kwargs)
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
        self.create_oval(10, 10, self.size-10, self.size-10, fill=COLOR_WHITE, outline=COLOR_ACCENT, width=2)
        self.create_arc(10, 10, self.size-10, self.size-10, start=90, extent=-angle_extent,
                        style="pieslice", outline="", fill=self.color)
        self.create_text(self.size//2, self.size//2-8,
                         text=f"{int(self.value)}{self.unit}", fill=COLOR_TEXT, font=("Arial", 14, "bold"))
        self.create_text(self.size//2, self.size//2+20,
                         text=self.label, fill="#888", font=("Arial", 11))

class CalorieWheel(ctk.CTkCanvas):
    def __init__(self, parent, cal_value, cal_goal, size=160, **kwargs):
        super().__init__(parent, width=size, height=size, bg=COLOR_BG, highlightthickness=0, **kwargs)
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
        self.create_oval(16, 16, self.size-16, self.size-16, fill=COLOR_WHITE, outline=COLOR_ACCENT2, width=3)
        self.create_arc(16, 16, self.size-16, self.size-16, start=90, extent=-angle_extent,
                        style="pieslice", outline="", fill=COLOR_ACCENT3)
        self.create_text(self.size//2, self.size//2-10,
                         text=f"{int(self.calValue)}", fill=COLOR_PRIMARY, font=("Arial", 22, "bold"))
        self.create_text(self.size//2, self.size//2+28,
                         text="Calories", fill="#888", font=("Arial", 13))

def clear_login_card():
    for widget in login_card.winfo_children():
        widget.destroy()

def show_login():
    clear_login_card()
    ctk.CTkLabel(login_card, text="Healthy Habits", text_color=COLOR_PRIMARY, font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(36, 0))
    ctk.CTkLabel(login_card, text="Sign In to GWSC", text_color=COLOR_TEXT, font=ctk.CTkFont(size=16)).pack(pady=(5, 24))
    ctk.CTkLabel(login_card, text="Student ID", text_color=COLOR_TEXT).pack(anchor="w", padx=40, pady=(0, 2))
    global username_entry
    username_entry = ctk.CTkEntry(login_card, width=320, height=42, corner_radius=8, font=ctk.CTkFont(size=15))
    username_entry.pack(padx=40, pady=(0, 16))
    ctk.CTkLabel(login_card, text="Password", text_color=COLOR_TEXT).pack(anchor="w", padx=40, pady=(0, 2))
    global password_entry
    password_entry = ctk.CTkEntry(login_card, show="*", width=320, height=42, corner_radius=8, font=ctk.CTkFont(size=15))
    password_entry.pack(padx=40, pady=(0, 16))
    ctk.CTkButton(login_card, text="Sign In", command=initiate_login, width=320, height=44, corner_radius=8, fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE).pack(padx=40, pady=(6, 10))
    ctk.CTkButton(login_card, text="Register ID instead", command=show_register, width=320, height=44, corner_radius=8, fg_color=COLOR_ACCENT, text_color=COLOR_BTN_TXT).pack(padx=40, pady=(0, 10))
    ctk.CTkButton(login_card, text="Skip (Dev Quick Login)", fg_color="#bbb", text_color=COLOR_WHITE,
                  command=lambda: show_home_page("Developer", workouts_logged=3, weekly_goal=4, left_frame=left_frame, right_frame=right_frame),
                  width=320, height=38, corner_radius=8).pack(padx=40, pady=(0, 10))

def show_register():
    clear_login_card()
    ctk.CTkLabel(login_card, text="Register New Student ID", text_color=COLOR_PRIMARY, font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(24, 0))

    # --- Registration slideshow state ---
    reg_state = {
        "step": 0,
        "studentId": "",
        "password": "",
        "goalWeight": "",
        "goalType": "",
        "planType": ""
    }

    # --- Step frames ---
    step_frames = []

    # Step 0: Student ID & Password
    frame0 = ctk.CTkFrame(login_card, fg_color=COLOR_WHITE, corner_radius=8)
    ctk.CTkLabel(frame0, text="Student ID (AAA####):", text_color=COLOR_TEXT, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=24, pady=(10,2))
    id_entry = ctk.CTkEntry(frame0, width=260, height=38, font=ctk.CTkFont(size=14))
    id_entry.pack(padx=24, pady=(0, 10))
    ctk.CTkLabel(frame0, text="Password:", text_color=COLOR_TEXT, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=24, pady=(2,2))
    pw_entry = ctk.CTkEntry(frame0, show="*", width=260, height=38, font=ctk.CTkFont(size=14))
    pw_entry.pack(padx=24, pady=(0, 10))
    step_frames.append(frame0)

    # Step 1: Goal Weight
    frame1 = ctk.CTkFrame(login_card, fg_color=COLOR_WHITE, corner_radius=8)
    ctk.CTkLabel(frame1, text="What is your goal weight (kg)?", text_color=COLOR_PRIMARY, font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w", padx=32, pady=(24,8))
    weight_entry = ctk.CTkEntry(frame1, width=120, height=38, font=ctk.CTkFont(size=14))
    weight_entry.pack(padx=32, pady=(0, 10))
    step_frames.append(frame1)

    # Step 2: Goal Type (Lose/Gain/Maintain)
    frame2 = ctk.CTkFrame(login_card, fg_color=COLOR_WHITE, corner_radius=8)
    ctk.CTkLabel(frame2, text="What is your main goal?", text_color=COLOR_PRIMARY, font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="center", pady=(24, 10))
    goal_type = ctk.StringVar(value="")
    for txt in ["Lose Weight", "Gain Muscle", "Maintain Health"]:
        btn = ctk.CTkRadioButton(frame2, text=txt, variable=goal_type, value=txt, font=ctk.CTkFont(size=15), fg_color=COLOR_ACCENT, border_color=COLOR_PRIMARY, hover_color=COLOR_ACCENT2)
        btn.pack(anchor="center", pady=6)
    step_frames.append(frame2)

    # Step 3: Preferred Plan Type
    frame3 = ctk.CTkFrame(login_card, fg_color=COLOR_WHITE, corner_radius=8)
    ctk.CTkLabel(frame3, text="Preferred Plan Type?", text_color=COLOR_PRIMARY, font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="center", pady=(24, 10))
    plan_type = ctk.StringVar(value="")
    for txt in ["Nutrition Focus", "Workout Focus", "Balanced"]:
        btn = ctk.CTkRadioButton(frame3, text=txt, variable=plan_type, value=txt, font=ctk.CTkFont(size=15), fg_color=COLOR_ACCENT3, border_color=COLOR_PRIMARY, hover_color=COLOR_ACCENT4)
        btn.pack(anchor="center", pady=6)
    step_frames.append(frame3)

    # Step 4: Review & Register
    frame4 = ctk.CTkFrame(login_card, fg_color=COLOR_WHITE, corner_radius=8)
    review_label = ctk.CTkLabel(frame4, text="", font=ctk.CTkFont(size=15), text_color=COLOR_PRIMARY)
    review_label.pack(padx=28, pady=(18,12))
    step_frames.append(frame4)

    # --- Navigation (Next/Back/Animate) ---
    def show_step(n, animate=True):
        for f in step_frames:
            f.pack_forget()
        if animate:
            step_frames[n].pack(padx=18, pady=18)
        else:
            step_frames[n].pack()
        reg_state["step"] = n
        # Special: update review
        if n == 4:
            review_label.configure(text=
                f"Please check your details:\n\n"
                f"Student ID: {reg_state['studentId']}\n"
                f"Goal Weight: {reg_state['goalWeight']}kg\n"
                f"Main Goal: {reg_state['goalType']}\n"
                f"Plan: {reg_state['planType']}\n"
            )

    def next_step():
        s = reg_state["step"]
        # Validate each step
        if s == 0:
            sid = id_entry.get().strip()
            pw = pw_entry.get().strip()
            if not re.fullmatch(r"[A-Za-z]{3}\d{4}", sid):
                messagebox.showwarning("Input Error", "Student ID must be in the format AAA#### (e.g., ZHA0301).")
                return
            if len(pw) < 4:
                messagebox.showwarning("Input Error", "Password too short.")
                return
            reg_state["studentId"] = sid
            reg_state["password"] = pw
        elif s == 1:
            try:
                w = float(weight_entry.get().strip())
                if w <= 20 or w >= 250:
                    raise ValueError()
                reg_state["goalWeight"] = str(int(w))
            except:
                messagebox.showwarning("Input Error", "Enter a realistic weight (21-249).")
                return
        elif s == 2:
            if not goal_type.get():
                messagebox.showwarning("Select a goal", "Please select your main goal.")
                return
            reg_state["goalType"] = goal_type.get()
        elif s == 3:
            if not plan_type.get():
                messagebox.showwarning("Select a plan", "Please select a plan type.")
                return
            reg_state["planType"] = plan_type.get()
        if s < len(step_frames) - 1:
            show_step(s + 1)
    def prev_step():
        s = reg_state["step"]
        if s > 0:
            show_step(s - 1)

    def do_register():
        # Actually save user
        sid = reg_state["studentId"]
        pw = reg_state["password"]
        # Save other info as JSON!
        user_data = {
            "goalWeight": reg_state["goalWeight"],
            "goalType": reg_state["goalType"],
            "planType": reg_state["planType"]
        }
        save_student_to_csv(sid, pw)
        # Save user extra info to a JSON file (for AC7 data structure)
        users_json = "users.json"
        users = {}
        if os.path.exists(users_json):
            with open(users_json, "r") as f:
                users = json.load(f)
        users[sid] = user_data
        with open(users_json, "w") as f:
            json.dump(users, f, indent=2)
        messagebox.showinfo("Success", f"Student ID '{sid}' registered successfully!")
        show_login()

    nav_frame = ctk.CTkFrame(login_card, fg_color=COLOR_WHITE)
    nav_frame.pack(pady=(0,10))
    prev_btn = ctk.CTkButton(nav_frame, text="Back", width=110, fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_TXT, command=prev_step)
    next_btn = ctk.CTkButton(nav_frame, text="Next", width=110, fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE, command=next_step)
    reg_btn = ctk.CTkButton(nav_frame, text="Finish & Register", width=180, fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE, command=do_register)
    def nav_update():
        s = reg_state["step"]
        prev_btn.pack_forget()
        next_btn.pack_forget()
        reg_btn.pack_forget()
        if s == 0:
            next_btn.pack(side="right", padx=10)
        elif s < 4:
            prev_btn.pack(side="left", padx=10)
            next_btn.pack(side="right", padx=10)
        else:
            prev_btn.pack(side="left", padx=10)
            reg_btn.pack(side="right", padx=10)
    def show_step_and_nav(n, animate=True):
        show_step(n, animate)
        nav_update()
    # Animation: fade in (simple slide in effect)
    def animated_next():
        s = reg_state["step"]
        if s < len(step_frames) - 1:
            frame = step_frames[s+1]
            frame.place(x=400, y=60)
            frame.update()
            for dx in range(400,18,-30):
                frame.place(x=dx, y=60)
                frame.update()
                frame.after(7)
            frame.place_forget()
        next_step()
        nav_update()
    def animated_prev():
        prev_step()
        nav_update()
    next_btn.configure(command=animated_next)
    prev_btn.configure(command=animated_prev)
    show_step_and_nav(0)

def getSuggestedExercises(goalType, planType):
    """
    Returns a list of 6 suggested exercises based on the user's goalType and planType.
    This is aligned to AC6: uses data structures and simple logic.
    """
    # Define possible exercises (can be expanded)
    all_exercises = {
        "Lose Weight": [
            "Jumping Jacks", "Burpees", "Mountain Climbers", "Running", "Cycling", "Skipping Rope"
        ],
        "Gain Muscle": [
            "Push-ups", "Pull-ups", "Squats", "Lunges", "Bench Press", "Deadlift"
        ],
        "Maintain Health": [
            "Brisk Walking", "Yoga", "Plank", "Bodyweight Squats", "Stretching", "Swimming"
        ]
    }
    plan_extras = {
        "Nutrition Focus": ["Track Calories", "Meal Prep", "Hydration"],
        "Workout Focus": ["HIIT", "Resistance Band", "Core Circuit"],
        "Balanced": ["Light Jog", "Dumbbell Rows", "Pilates"]
    }
    # Combine based on priorities (AC7: simple algorithm)
    base = all_exercises.get(goalType, all_exercises["Maintain Health"])
    extra = plan_extras.get(planType, [])
    # Return a 2x3 grid (6 elements)
    return (base[:3] + extra[:3]) if len(base) >= 3 else base + extra[:(6-len(base))]

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
        show_home_page(username, left_frame=left_frame, right_frame=right_frame)
    else:
        messagebox.showwarning("Login Failed", "Invalid Student ID or password, please try again.")

class BubblePopout(ctk.CTkFrame):
    """A floating log form, locked to root window, always visible even when scrolling."""
    def __init__(self, root, username, update_callback, anchor_widget, destroy_callback=None, preset=None):
        super().__init__(root, fg_color="#fff", corner_radius=18, border_width=2, border_color=COLOR_ACCENT)
        self.username = username
        self.update_callback = update_callback
        self.destroy_callback = destroy_callback
        self.anchor_widget = anchor_widget
        self.entries = []
        self.place_forget()
        # Form content
        ctk.CTkLabel(self, text="Log Meal", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(12, 6))
        for i, macro in enumerate(["Meal Name", "Carbs (g)", "Protein (g)", "Fat (g)"]):
            ctk.CTkLabel(self, text=macro, font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack()
            entry = ctk.CTkEntry(self, width=140, font=ctk.CTkFont(size=13))
            if preset and i > 0:
                macro_key = ["carbs", "protein", "fat"][i-1]
                entry.insert(0, str(preset.get(macro_key, "")))
            elif preset and i == 0:
                entry.insert(0, preset.get("mealName", ""))
            entry.pack(pady=(0, 5))
            self.entries.append(entry)
        ctk.CTkButton(self, text="Log", fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE, width=70, command=self.log_and_close).pack(pady=(8, 10))
        self.update_idletasks()
        self.update_position()
        self.lift()

    def update_position(self):
        """Update the popout's position to stay aligned with the anchor widget."""
        if not self.anchor_widget.winfo_exists():
            return
        ax = self.anchor_widget.winfo_rootx() - self.master.winfo_rootx()
        ay = self.anchor_widget.winfo_rooty() - self.master.winfo_rooty() + self.anchor_widget.winfo_height() + 8
        self.place(x=ax, y=ay)

    def log_and_close(self):
        try:
            meal = {
                "mealName": self.entries[0].get() or "Manual Log",
                "carbs": int(self.entries[1].get()),
                "protein": int(self.entries[2].get()),
                "fat": int(self.entries[3].get())
            }
            for macro in ["carbs", "protein", "fat"]:
                if not (0 <= meal[macro] <= 500):
                    raise ValueError(f"{macro.title()} out of range")
            save_meal(self.username, meal)
            if self.update_callback:
                self.update_callback()
            messagebox.showinfo("Success", "Meal logged!")
            self.destroy()
            if self.destroy_callback:
                self.destroy_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Please enter valid values. {e}")

def show_home_page(username="User", workouts_logged=3, weekly_goal=4, left_frame=None, right_frame=None):
    # Load user preferences if available
    user_data = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
            user_data = users.get(username, {})
    goalType = user_data.get("goalType", "Maintain Health")
    planType = user_data.get("planType", "Balanced")
    
    # Remove old frames if they exist
    if left_frame is not None:
        left_frame.grid_remove()
    if right_frame is not None:
        right_frame.grid_remove()

    home_frame = ctk.CTkFrame(root, fg_color=COLOR_BG)
    home_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    home_frame.grid_rowconfigure(1, weight=1)
    home_frame.grid_columnconfigure(0, weight=1)
    top_bar = ctk.CTkFrame(home_frame, fg_color=COLOR_BG, height=90)
    top_bar.grid(row=0, column=0, sticky="ew")
    top_bar.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(top_bar, text=f"Welcome, {username}!", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_PRIMARY).grid(row=0, column=0, sticky="w", padx=40, pady=24)
    ctk.CTkLabel(top_bar, text="🏠", font=ctk.CTkFont(size=22)).grid(row=0, column=1, sticky="e", padx=(0, 18))
    ctk.CTkLabel(top_bar, text="🌱", font=ctk.CTkFont(size=22)).grid(row=0, column=2, sticky="e", padx=(0, 18))
    ctk.CTkLabel(top_bar, text="GWSC healthy habits", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_SECONDARY).grid(row=0, column=3, sticky="e", padx=40)
    scroll_frame = ctk.CTkScrollableFrame(home_frame, fg_color=COLOR_BG)
    scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
    scroll_frame.grid_columnconfigure(0, weight=1)

    user_data = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
            user_data = users.get(username, {})
    goalType = user_data.get("goalType", "Maintain Health")
    planType = user_data.get("planType", "Balanced")
    suggested = getSuggestedExercises(goalType, planType)

    # Each row has 3 exercises, for 2 rows (6 total) - adjust as needed
    exercise_area = ctk.CTkFrame(scroll_frame, fg_color=COLOR_ACCENT4, corner_radius=18)
    exercise_area.grid(row=2, column=0, sticky="ew", padx=80, pady=(0, 24))
    ctk.CTkLabel(
        exercise_area,
        text=f"Suggested Exercises for You ({goalType}, {planType})",
        font=ctk.CTkFont(size=17, weight="bold"),
        text_color=COLOR_TEXT
    ).grid(row=0, column=0, columnspan=3, pady=(14, 14), sticky="ew")

    # Create a grid of large, equally sized, equally spaced buttons with image backgrounds
    # Button size and grid layout constants
    btn_width = 260
    btn_height = 110
    btn_padx = 16
    btn_pady = 12
    border_color = "#d0d3d8"
    
    pastel_colors = [COLOR_ACCENT, COLOR_ACCENT3, COLOR_ACCENT2, COLOR_ACCENT4]
    def create_placeholder_image(label, color):
        img = Image.new("RGB", (btn_width, btn_height), color)
        d = ImageDraw.Draw(img)
        # Draw a light border
        d.rectangle([0, 0, btn_width-1, btn_height-1], outline=border_color, width=4)
        # Optionally, semi-transparent text for debugging
        d.text((btn_width//2-30, btn_height//2-14), "IMG", fill="#b0b0b0")
        return ImageTk.PhotoImage(img)
    
    for i in range(2):  # rows
        for j in range(3):  # columns
            idx = i * 3 + j
            ex_name = suggested[idx] if idx < len(suggested) else ""
            # Use a different pastel for each, cycling if needed
            color = pastel_colors[(i*3 + j) % len(pastel_colors)]
            img = create_placeholder_image(ex_name, color)
            btn = ctk.CTkButton(
                exercise_area,
                text=ex_name,
                image=img,
                compound="center",  # Text is over the image, centered
                fg_color="transparent",
                width=btn_width,
                height=btn_height,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=COLOR_TEXT,
                corner_radius=22,
                hover_color="#f7f7f7"
            )
            btn.image = img  # keep a reference!
            btn.grid(row=i+1, column=j, padx=btn_padx, pady=btn_pady, sticky="nsew")
            exercise_area.grid_columnconfigure(j, weight=1)
        exercise_area.grid_rowconfigure(i+1, weight=1)

    def on_scroll(*args):
        if hasattr(home_frame, 'active_bubble') and home_frame.active_bubble and home_frame.active_bubble.winfo_exists():
            home_frame.active_bubble.update_position()

    scroll_frame._scrollbar.bind("<B1-Motion>", on_scroll)
    scroll_frame._scrollbar.bind("<Button-4>", on_scroll)
    scroll_frame._scrollbar.bind("<Button-5>", on_scroll)

    progress = min(workouts_logged / weekly_goal, 1.0) if weekly_goal > 0 else 0
    progress_text = f"You've done {workouts_logged} workout{'s' if workouts_logged != 1 else ''} this week!"
    progress_subtext = f"{int(progress * 100)}% of your weekly goal is reached!"
    progress_frame = ctk.CTkFrame(scroll_frame, fg_color=COLOR_ACCENT, corner_radius=14)
    progress_frame.grid(row=0, column=0, sticky="ew", padx=80, pady=(36, 30))
    progress_text_frame = ctk.CTkFrame(progress_frame, fg_color=COLOR_ACCENT)
    progress_text_frame.pack(fill="x", pady=(20, 0))
    ctk.CTkLabel(progress_text_frame, text=progress_text, font=ctk.CTkFont(size=19, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="center")
    ctk.CTkLabel(progress_text_frame, text=progress_subtext, font=ctk.CTkFont(size=14), text_color="#666").pack(anchor="center")
    progress_bar = ctk.CTkProgressBar(progress_frame, width=700, height=26, progress_color=COLOR_PRIMARY)
    progress_bar.set(progress)
    progress_bar.pack(padx=40, pady=(16, 20))

    macro_frame = ctk.CTkFrame(scroll_frame, fg_color=COLOR_WHITE, corner_radius=18)
    macro_frame.grid(row=1, column=0, sticky="ew", padx=80, pady=(0, 15))
    macro_frame.grid_columnconfigure(0, weight=1)
    macro_frame.grid_columnconfigure(1, weight=1)
    macro_frame.grid_columnconfigure(2, weight=1)
    macro_frame.grid_columnconfigure(3, weight=1)
    mini_colors = {"carbs": COLOR_PRIMARY, "protein": COLOR_SECONDARY, "fat": COLOR_TERTIARY}
    macro_labels = ["carbs", "protein", "fat"]
    mini_wheels = []
    for i, macro in enumerate(macro_labels):
        mw = MiniWheel(macro_frame, macro.title(), 0, DEFAULT_MACRO_GOALS[macro], mini_colors[macro])
        mw.grid(row=0, column=i, padx=18, pady=18)
        mini_wheels.append(mw)
    cal_wheel = CalorieWheel(macro_frame, 0, DEFAULT_CAL_GOAL)
    cal_wheel.grid(row=0, column=3, padx=24, pady=18)
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
    macro_side = ctk.CTkFrame(macro_frame, fg_color=COLOR_WHITE)
    macro_side.grid(row=1, column=0, columnspan=4, sticky="ew")
    btn_frame = ctk.CTkFrame(macro_side, fg_color=COLOR_WHITE)
    btn_frame.pack(pady=(6, 0))
    home_frame.active_bubble = None
    def toggle_bubble(anchor_btn, preset=None):
        # Close existing
        if home_frame.active_bubble and home_frame.active_bubble.winfo_exists():
            home_frame.active_bubble.destroy()
            home_frame.active_bubble = None
            return
        # Open new
        home_frame.active_bubble = BubblePopout(root, username, update_wheels, anchor_btn, destroy_callback=lambda: setattr(home_frame, 'active_bubble', None), preset=preset)
    btn_log_meal = ctk.CTkButton(btn_frame, text="Log Meal", width=130, fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE, command=lambda: toggle_bubble(btn_log_meal))
    btn_log_meal.pack(side="left", padx=12)
    btn_quick_log = ctk.CTkButton(btn_frame, text="Quick Log", width=130, fg_color=COLOR_ACCENT, text_color=COLOR_BTN_TXT, command=lambda: toggle_bubble(btn_quick_log))
    btn_quick_log.pack(side="left", padx=12)
    ctk.CTkButton(btn_frame, text="Browse Healthy Recipes", width=180, fg_color=COLOR_ACCENT3, text_color=COLOR_BTN_TXT, command=lambda: show_recipe_browser(username, update_wheels, home_frame)).pack(side="left", padx=12)

    exercise_area = ctk.CTkFrame(scroll_frame, fg_color=COLOR_ACCENT4, corner_radius=18)
    exercise_area.grid(row=2, column=0, sticky="ew", padx=80, pady=(0, 24))
    for row, ex_row in enumerate(EXERCISE_SUGGESTIONS):
        row_frame = ctk.CTkFrame(exercise_area, fg_color=COLOR_ACCENT4, corner_radius=0)
        row_frame.pack(fill="x", pady=2)
        for col, (ex_name, ex_img) in enumerate(ex_row):
            img = Image.new("RGB", (100, 68), COLOR_ACCENT if row % 2 == 0 else COLOR_ACCENT3)
            d = ImageDraw.Draw(img)
            d.rectangle([0,0,99,67], outline="#cfcfcf")
            d.text((28,26), "IMG", fill="#aaa")
            ph = ImageTk.PhotoImage(img)
            btn = ctk.CTkButton(
                row_frame, text=ex_name,
                image=ph, compound="left",
                width=210, height=68, corner_radius=14, font=ctk.CTkFont(size=16, weight="bold"),
                fg_color=COLOR_ACCENT if row % 2 == 0 else COLOR_ACCENT3, text_color=COLOR_BTN_TXT,
                hover_color=COLOR_ACCENT2 if row % 2 == 0 else COLOR_ACCENT4
            )
            btn.image = ph
            btn.pack(side="left", padx=(0 if col==0 else 1, 0), pady=0, expand=True, fill="both")

    meals_frame = ctk.CTkFrame(scroll_frame, fg_color=COLOR_ACCENT2, corner_radius=14)
    meals_frame.grid(row=3, column=0, sticky="ew", padx=80, pady=(0, 30))
    ctk.CTkLabel(meals_frame, text="Today's Meals", font=ctk.CTkFont(size=16, weight="bold"), text_color="#b94e22").pack(anchor="w", padx=24, pady=(12, 0))
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
    update_wheels()

def show_recipe_browser(username, update_callback, home_frame):
    for w in root.winfo_children():
        w.grid_remove()
    recipe_frame = ctk.CTkFrame(root, fg_color=COLOR_BG)
    recipe_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    recipe_frame.grid_columnconfigure(0, weight=1)
    recipe_frame.grid_rowconfigure(1, weight=1)
    top_bar = ctk.CTkFrame(recipe_frame, fg_color=COLOR_ACCENT, height=80, corner_radius=0)
    top_bar.grid(row=0, column=0, sticky="ew")
    ctk.CTkLabel(top_bar, text="Healthy Recipes", font=ctk.CTkFont(size=23, weight="bold"), text_color=COLOR_PRIMARY).grid(row=0, column=0, sticky="w", padx=44, pady=26)
    ctk.CTkButton(top_bar, text="Back to Home", command=lambda: show_home_page(username), width=120, fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE, corner_radius=18).grid(row=0, column=1, sticky="e", padx=44, pady=26)
    recipe_scroll = ctk.CTkScrollableFrame(recipe_frame, fg_color=COLOR_BG)
    recipe_scroll.grid(row=1, column=0, sticky="nsew", padx=62, pady=(0, 26))
    recipe_scroll.grid_columnconfigure((0, 1), weight=1)
    
    def on_scroll(*args):
        if hasattr(recipe_frame, 'active_bubble') and recipe_frame.active_bubble and recipe_frame.active_bubble.winfo_exists():
            recipe_frame.active_bubble.update_position()
    
    recipe_scroll._scrollbar.bind("<B1-Motion>", on_scroll)
    recipe_scroll._scrollbar.bind("<Button-4>", on_scroll)
    recipe_scroll._scrollbar.bind("<Button-5>", on_scroll)
    
    recipe_frame.active_bubble = None
    def toggle_recipe_bubble(anchor_btn, recipe):
        # Close existing
        if recipe_frame.active_bubble and recipe_frame.active_bubble.winfo_exists():
            recipe_frame.active_bubble.destroy()
            recipe_frame.active_bubble = None
            return
        recipe_frame.active_bubble = BubblePopout(root, username, update_callback, anchor_btn, destroy_callback=lambda: setattr(recipe_frame, 'active_bubble', None), preset=recipe["macros"] | {"mealName": recipe["name"]})
    for i, recipe in enumerate(BUILTIN_RECIPES):
        rf = ctk.CTkFrame(recipe_scroll, fg_color=COLOR_WHITE, corner_radius=24, border_color=COLOR_ACCENT, border_width=1)
        rf.grid(row=i//2, column=i%2, padx=16, pady=18, sticky="ew")
        rf.grid_columnconfigure(0, weight=0)
        rf.grid_columnconfigure(1, weight=1)
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
        ctk.CTkLabel(rf, text=recipe["name"], font=ctk.CTkFont(size=17, weight="bold"), text_color=COLOR_PRIMARY).grid(row=0, column=1, sticky="w", pady=(20,0))
        macroStr = f'C:{recipe["macros"]["carbs"]}g   P:{recipe["macros"]["protein"]}g   F:{recipe["macros"]["fat"]}g'
        ctk.CTkLabel(rf, text=macroStr, font=ctk.CTkFont(size=13), text_color="#666").grid(row=1, column=1, sticky="w")
        ctk.CTkLabel(rf, text=f'Ingredients: {len(recipe["ingredients"])} | Steps: {len(recipe["steps"])}', font=ctk.CTkFont(size=13), text_color="#888").grid(row=2, column=1, sticky="w")
        recipe_btn = ctk.CTkButton(rf, text="Log This Recipe", width=130, fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE, corner_radius=12)
        recipe_btn.grid(row=0, column=2, rowspan=3, padx=16, pady=16, sticky="e")
        recipe_btn.configure(command=lambda btn=recipe_btn, r=recipe: toggle_recipe_bubble(btn, r))

root = ctk.CTk()
root.title("Healthy Habits - Home")
root.geometry("1280x720")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

left_frame = ctk.CTkFrame(root, fg_color=COLOR_BG, corner_radius=0)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=0)
left_frame.grid_rowconfigure(2, weight=1)
left_frame.grid_columnconfigure(0, weight=1)

logo_placeholder = ctk.CTkLabel(left_frame, text="GWSC HABITS", text_color=COLOR_PRIMARY, font=ctk.CTkFont(size=22, weight="bold"))
logo_placeholder.place(x=40, y=40)

login_card = ctk.CTkFrame(left_frame, fg_color=COLOR_WHITE, border_color=COLOR_ACCENT, border_width=2, corner_radius=12)
login_card.grid(row=1, column=0, pady=0)
show_login()

right_frame = ctk.CTkFrame(root, fg_color=COLOR_BG, corner_radius=0)
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
    bg_label = ctk.CTkLabel(right_frame, text="Image Placeholder", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_PRIMARY)
    bg_label.place(relx=0.5, rely=0.5, anchor="center")

root.mainloop()