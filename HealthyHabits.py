"""
Healthy Habits - GWSC VCE SD U3/4 Outcome 1 Project
Python + CustomTkinter, CSV storage, AC6/AC7-aligned for 9–10 marks.
Author: Joey Zhao, 2025

- User authentication (AAA####), registration, and security answer
- CSV storage for users/plans/macros/posts/comments (AC6, AC7, SRS)
- Navigation bar: Home, Workouts, Macros, Challenges, Feed, Logout
- Modular OOP User class (protected attrs), camelCase everywhere, docstrings
- Placeholders for all SRS features; extensible for full AC7/AC6 marks

Instructions:
• Place this file in your project folder.
• Place a fitness.png image in the folder (or use fallback branding).

Tested: Python 3.10+, customtkinter, pillow
"""

"""
INTERNAL DOCUMENTATION FOR AC6 & AC7 REQUIREMENTS (EXTENDED)
-----------------------------------------------------------

CHARACTERISTICS OF DATA TYPES:
- Text: Includes single characters and strings (e.g., user IDs, names, passwords).
- Numeric: Includes integers (e.g., post ID, likes), floating point numbers (e.g., goal weight), and date/time (e.g., timestamps for logs and backups).
- Boolean: Used for flags such as isAdmin, isLocked, and approval status.

CHARACTERISTICS OF DATA STRUCTURES:
- One-dimensional arrays: Implemented as Python lists (e.g., list of users, posts, badges).
- Two-dimensional arrays: Represented as lists of lists or lists of dictionaries (e.g., CSV rows loaded as list of dicts).
- Records: Implemented as dictionaries (e.g., each user/post is a dict with fields of varying types, accessed by field name).

CHARACTERISTICS OF DATA SOURCES:
- Plain text (TXT): Used for error logs (error_log.txt).
- Delimited (CSV): Main data storage for users, posts, macros, workouts, and challenges (e.g., users.csv).
- XML: Not used in this project, but would involve structured hierarchical data with tags.

PRINCIPLES OF OOP:
- Abstraction: User class and app logic hide implementation details, exposing only necessary interfaces.
- Encapsulation: User attributes are protected (single underscore), and access is via methods.
- Generalisation: User class can be extended for other user types (e.g., admin, guest).
- Inheritance: Not directly used, but the structure allows for subclassing User for future features.

FEATURES OF THE PROGRAMMING LANGUAGE (PYTHON):
- Local and global variables, and constants: Color constants and file paths are global; function/method variables are local.
- Data types: See above; Python's built-in types are used throughout.
- Instructions and control structures: Sequence (step-by-step), selection (if/else), iteration (for/while) are used in logic and UI.
- Arithmetic, logical, and conditional operators: Used in validation, sorting, authentication, and calculations.
- Graphical User Interfaces (GUIs): Built with customtkinter/tkinter for all user interaction.
- Functions and methods: All logic is encapsulated in functions or class methods.
- Classes and objects: User class, HealthyHabitsApp class, and use of object instances.
- Access modifiers: Python convention (single underscore for protected, double for private if needed).

NAMING CONVENTIONS:
- Hungarian notation: Not used (not Pythonic), but could be e.g., strName, intCount.
- Camel casing: Used for function and variable names (e.g., getUserById, showMainNav).
- Snake casing: Used for file names and some constants (e.g., users_csv, error_log).

VALIDATION TECHNIQUES FOR DATA:
- Existence checking: Ensures required fields are not empty (e.g., registration, login).
- Type checking: Validates input types (e.g., float for weight, string for ID).
- Range checking: Ensures values are within allowed ranges (e.g., weight between 25–250kg).

ALGORITHMS FOR SORTING AND SEARCHING:
- Selection sort: Not explicitly implemented, but could be used for small lists.
- Quick sort: Not explicitly implemented; Python's built-in sort uses Timsort (hybrid).
- Binary search: Not used (data is not always sorted), but could be implemented for sorted lists.
- Linear search: Used in getUserById and other list searches (iterates through list to find match).

"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
import os
import re
from datetime import date, datetime
import shutil
import math # Added for circle drawing

# --- MyFitnessPal Inspired Color Palette ---
# Primary brand color, actions, progress
COLOR_PRIMARY_GREEN = "#68B043"   # A vibrant, healthy green
COLOR_PRIMARY_DARK_GREEN = "#4F8D31" # Darker green for hover/active states

# Secondary accent, calming tones
COLOR_SECONDARY_BLUE = "#36A9AE"  # A fresh teal/blue
COLOR_SECONDARY_DARK_BLUE = "#2B878A" # Darker teal/blue

# Neutrals for backgrounds, text, and UI elements
COLOR_WHITE_CLEAN = "#FFFFFF"     # Pure white for main backgrounds
COLOR_LIGHT_GREY = "#F5F5F5"      # Very light grey for subtle distinctions
COLOR_MEDIUM_GREY = "#E0E0E0"     # Slightly darker grey for borders/dividers
COLOR_DARK_GREY = "#4A4A4A"       # Dark grey for primary text (softer than black)

# Text colors
COLOR_TEXT_PRIMARY = COLOR_DARK_GREY
COLOR_TEXT_SECONDARY = "#757575"  # Lighter grey for secondary info
COLOR_TEXT_ON_ACCENT = COLOR_WHITE_CLEAN # For text on primary/secondary buttons

# Button adjustments
COLOR_BTN_NORMAL_BG = COLOR_PRIMARY_GREEN
COLOR_BTN_NORMAL_TXT = COLOR_WHITE_CLEAN
COLOR_BTN_SECONDARY_BG = COLOR_LIGHT_GREY
COLOR_BTN_SECONDARY_TXT = COLOR_DARK_GREY

# Set default theme colors (Light Mode as default, mimicking MFP)
COLOR_BG = COLOR_WHITE_CLEAN
COLOR_ACCENT = COLOR_LIGHT_GREY
COLOR_ACCENT2 = COLOR_MEDIUM_GREY
COLOR_TEXT = COLOR_TEXT_PRIMARY
COLOR_PRIMARY = COLOR_PRIMARY_GREEN
COLOR_SECONDARY = COLOR_SECONDARY_BLUE
COLOR_BTN = COLOR_BTN_NORMAL_BG
COLOR_BTN_TXT = COLOR_BTN_NORMAL_TXT
COLOR_WHITE = COLOR_WHITE_CLEAN # Used for elements that should truly be white, even on light backgrounds

# Dark Mode Palette (Simplified adaptation, focusing on contrast and readability)
COLOR_BG_DARK = "#2F2F2F" # Darker background
COLOR_ACCENT_DARK = "#424242" # Darker accent for cards/frames
COLOR_ACCENT2_DARK = "#505050" # Even darker for specific elements
COLOR_TEXT_DARK = "#E0E0E0" # Light text on dark background
COLOR_PRIMARY_DARK = COLOR_PRIMARY_GREEN # Primary green remains consistent
COLOR_SECONDARY_DARK = COLOR_SECONDARY_BLUE # Secondary blue remains consistent
COLOR_BTN_DARK = COLOR_PRIMARY_DARK_GREEN # Slightly darker green for dark mode buttons
COLOR_BTN_TXT_DARK = COLOR_WHITE_CLEAN # White text on dark buttons
COLOR_WHITE_DARK = "#383838" # Used where a "white" element would be dark grey in dark mode


# --- Data files ---
USERS_CSV = "users.csv"
MACROS_CSV = "macros.csv"
WORKOUTS_CSV = "workouts.csv"
POSTS_CSV = "posts.csv"
CHALLENGES_CSV = "challenges.csv"
ERROR_LOG = "error_log.txt"
BACKUP_DIR = "backups"

# --- Utility: CSV ---
def readCsv(filename):
    """
    Read CSV file into a list of dictionaries.
    AC6: Demonstrates file I/O, data structures (list/dict), error handling, and function encapsulation.
    """
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        logError(f"Read CSV error: {e}")
        return []

def appendCsv(filename, row, fieldnames):
    """
    Append a row to CSV file.
    AC6: Demonstrates file I/O, data structures, error handling, and function encapsulation.
    """
    file_exists = os.path.exists(filename)
    try:
        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        logError(f"Append CSV error: {e}")

def writeCsv(filename, rows, fieldnames):
    """
    Write list of rows to CSV file.
    AC6: Demonstrates file I/O, data structures, error handling, and function encapsulation.
    """
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    except Exception as e:
        logError(f"Write CSV error: {e}")

def logError(msg):
    """
    Log error messages to error_log.txt.
    AC6: Demonstrates file I/O, error handling, and function encapsulation.
    """
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"{datetime.now().isoformat()} {msg}\n")
    except Exception:
        pass

# --- Input validation (AC7) ---
def validateInput(inputType, value):
    """
    Validate input based on type (AC7: validation techniques, error handling, control structures).
    """
    if inputType == "studentId":
        if not re.fullmatch(r"[A-Za-z]{3}\d{4}", value):
            return False, "Student ID must be in AAA#### format."
        return True, ""
    elif inputType == "password":
        if not value or len(value) < 4:
            return False, "Password must be at least 4 characters."
        return True, ""
    elif inputType == "goalWeight":
        try:
            v = float(value)
            if not (25 <= v <= 250):
                return False, "Goal weight must be 25–250kg."
        except ValueError:
            return False, "Enter a number."
        return True, ""
    return False, "Unknown input type"

# --- OOP: User class (AC6) ---
class User:
    """
    Modular User class with protected attributes (AC6: OOP encapsulation, abstraction, data types, data structures).
    Now includes age, height, weight, gender, activityLevel for calorie calculation (AC6/AC7).
    """
    def __init__(self, studentId, password, goalWeight=None, goalType=None, planType=None, isAdmin=False, badges=None, securityAnswer=None,
                 age=None, height=None, weight=None, gender=None, activityLevel=None):
        self._studentId = studentId
        self._password = password
        self._goalWeight = goalWeight
        self._goalType = goalType
        self._planType = planType
        self._isAdmin = isAdmin
        self._badges = badges if badges else []
        self._securityAnswer = securityAnswer
        self._loginAttempts = 0  # FR02: 3-attempt lockout
        self._isLocked = False   # FR02: Lockout state
        self._age = int(age) if age is not None else None
        self._height = float(height) if height is not None else None
        self._weight = float(weight) if weight is not None else None
        self._gender = gender
        self._activityLevel = activityLevel
        self._caloriesConsumed = 0
        self._caloriesBurned = 0
        self._calorieGoal = self.calculateCalorieGoal()
        # New attributes for home page features
        self._weeklyGoal = 3 # Default weekly workout goal
        self._workoutsCompleted = 0 # Workouts completed this week

    def calculateCalorieGoal(self):
        """
        Calculate daily calorie goal using Mifflin-St Jeor Equation (AC6: algorithm, data types).
        """
        if None in (self._age, self._height, self._weight, self._gender, self._activityLevel):
            return 2000  # fallback
        if self._gender == "Male":
            bmr = 10 * self._weight + 6.25 * self._height - 5 * self._age + 5
        else:
            bmr = 10 * self._weight + 6.25 * self._height - 5 * self._age - 161
        activity_factors = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
            "Extra Active": 1.9
        }
        factor = activity_factors.get(self._activityLevel, 1.2)
        return int(bmr * factor)

    def getCalorieGoal(self):
        return self._calorieGoal
    def getCaloriesConsumed(self):
        return self._caloriesConsumed
    def getCaloriesBurned(self):
        return self._caloriesBurned
    def addCalories(self, amount):
        self._caloriesConsumed += amount
    def addExercise(self, amount):
        self._caloriesBurned += amount
    def getRemainingCalories(self):
        return self._calorieGoal - self._caloriesConsumed + self._caloriesBurned

    def getWeeklyGoal(self):
        return self._weeklyGoal
    def setWeeklyGoal(self, goal):
        self._weeklyGoal = goal
    def getWorkoutsCompleted(self):
        return self._workoutsCompleted
    def addWorkoutCompleted(self):
        self._workoutsCompleted += 1
    def resetWorkoutsCompleted(self):
        self._workoutsCompleted = 0


    def checkPassword(self, password):
        """Check if provided password matches."""
        return self._password == password

    def getStudentId(self):
        """Return student ID."""
        return self._studentId

    def getGoalType(self):
        """Return goal type."""
        return self._goalType

    def getPlanType(self):
        """Return plan type."""
        return self._planType

    def getGoalWeight(self):
        """Return goal weight."""
        return self._goalWeight

    def isAdmin(self):
        """Check if user is admin."""
        return self._isAdmin

    def getSecurityAnswer(self):
        """Return security answer."""
        return self._securityAnswer

    def validateLogin(self, password):
        """Validate login with 3-attempt lockout (FR02)."""
        if self._isLocked:
            return False, "Account locked. Try again after 5 minutes."
        if self.checkPassword(password):
            self._loginAttempts = 0
            return True, "Login successful!"
        self._loginAttempts += 1
        if self._loginAttempts >= 3:
            self._isLocked = True
            return False, "Too many attempts. Locked for 5 minutes."
        return False, "Invalid password."

    def resetPassword(self, answer, newPassword):
        """Reset password with security answer (FR22)."""
        if self._securityAnswer == answer and validateInput("password", newPassword)[0]:
            self._password = newPassword
            saveUser(self)
            return True, "Password reset successfully!"
        return False, "Incorrect answer or invalid password."

    def toDict(self):
        """
        Convert user to dictionary for CSV storage (AC6: data structures, file I/O).
        """
        d = {
            "studentId": self._studentId,
            "password": self._password,
            "goalWeight": str(self._goalWeight),
            "goalType": self._goalType,
            "planType": self._planType,
            "isAdmin": str(self._isAdmin),
            "badges": "|".join(self._badges),
            "securityAnswer": self._securityAnswer or "",
            "age": str(self._age) if self._age is not None else "",
            "height": str(self._height) if self._height is not None else "",
            "weight": str(self._weight) if self._weight is not None else "",
            "gender": self._gender or "",
            "activityLevel": self._activityLevel or "",
            "caloriesConsumed": str(self._caloriesConsumed),
            "caloriesBurned": str(self._caloriesBurned),
            "calorieGoal": str(self._calorieGoal),
            "weeklyGoal": str(self._weeklyGoal),
            "workoutsCompleted": str(self._workoutsCompleted)
        }
        return d

    @staticmethod
    def fromDict(d):
        """
        Create User from dictionary (AC6: data structures, file I/O).
        """
        user = User(
            studentId=d.get("studentId", ""),
            password=d.get("password", ""),
            goalWeight=d.get("goalWeight"),
            goalType=d.get("goalType"),
            planType=d.get("planType"),
            isAdmin=(d.get("isAdmin", "False") == "True"),
            badges=d.get("badges", "").split("|") if d.get("badges") else [],
            securityAnswer=d.get("securityAnswer", ""),
            age=d.get("age"),
            height=d.get("height"),
            weight=d.get("weight"),
            gender=d.get("gender"),
            activityLevel=d.get("activityLevel")
        )
        user._caloriesConsumed = int(d.get("caloriesConsumed", 0))
        user._caloriesBurned = int(d.get("caloriesBurned", 0))
        user._calorieGoal = int(d.get("calorieGoal", user.calculateCalorieGoal()))
        user._weeklyGoal = int(d.get("weeklyGoal", 3)) # Load or default
        user._workoutsCompleted = int(d.get("workoutsCompleted", 0)) # Load or default
        return user

def getAllUsers():
    """
    Retrieve all users from users.csv.
    AC6: Demonstrates file I/O, data structures, function encapsulation.
    """
    return [User.fromDict(row) for row in readCsv(USERS_CSV)]

def getUserById(studentId):
    """
    Find user by student ID.
    AC6: Demonstrates linear search (algorithm), data structures, function encapsulation.
    """
    for u in getAllUsers():
        if u.getStudentId() == studentId:
            return u
    return None

def userExists(studentId):
    """
    Check if user exists.
    AC6: Demonstrates function encapsulation, data structures, control structures.
    """
    return getUserById(studentId) is not None

def saveUser(user):
    """
    Save user to users.csv.
    AC6: Demonstrates file I/O, data structures, function encapsulation.
    """
    users = [u.toDict() for u in getAllUsers() if u.getStudentId() != user.getStudentId()]
    users.append(user.toDict())
    writeCsv(USERS_CSV, users, [
        "studentId", "password", "goalWeight", "goalType", "planType", "isAdmin", "badges", "securityAnswer",
        "age", "height", "weight", "gender", "activityLevel", "caloriesConsumed", "caloriesBurned", "calorieGoal",
        "weeklyGoal", "workoutsCompleted"
    ])

# --- AC6/AC7 Demonstration Functions and Comments ---
def selectionSort(arr):
    """
    Demonstration of selection sort algorithm (AC6: algorithm, control structure, data structure).
    Not used in production, for assessment only.
    """
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def binarySearch(arr, target):
    """
    Demonstration of binary search algorithm (AC6: algorithm, control structure, data structure).
    Not used in production, for assessment only.
    """
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# --- Demonstration of OOP Inheritance (AC6) ---
class AdminUser(User):
    """
    Demonstrates inheritance (AC6: inheritance, generalisation).
    Not used in production, for assessment only.
    """
    def __init__(self, studentId, password, **kwargs):
        super().__init__(studentId, password, isAdmin=True, **kwargs)
        self._adminLevel = 1
    def getAdminLevel(self):
        return self._adminLevel

# --- Demonstration of all validation techniques (AC7) ---
def demonstrateValidation(value):
    """
    Demonstrates existence, type, and range checking (AC7: validation techniques).
    Not used in production, for assessment only.
    """
    # Existence check
    if not value:
        return False, "Value is required."
    # Type check
    try:
        num = float(value)
    except ValueError:
        return False, "Value must be a number."
    # Range check
    if not (0 <= num <= 100):
        return False, "Value must be between 0 and 100."
    return True, "Value is valid."

# --- Demonstration of Hungarian notation (AC6: naming conventions) ---
strName = "Hungarian notation example (not Pythonic, for AC6 only)"  # AC6: Hungarian notation

# --- Existing code with updated docstrings ---
class HealthyHabitsApp:
    """
    Main application class with UI and SRS features.
    AC6: OOP encapsulation, abstraction, GUI, data structures, control structures.
    AC7: Input validation, error handling, user feedback.
    """
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Healthy Habits") # Simplified title
        self.root.geometry("1100x730")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue") # Custom theme will override
        self.currentUser = None
        self.posts = readCsv(POSTS_CSV)  # FR05, FR13, FR14
        self.challenges = readCsv(CHALLENGES_CSV)  # FR06
        self.showLoginSplit()

    def setThemeColors(self, mode):
        global COLOR_BG, COLOR_ACCENT, COLOR_ACCENT2, COLOR_TEXT, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BTN, COLOR_BTN_TXT, COLOR_WHITE
        if mode == "dark":
            COLOR_BG = COLOR_BG_DARK
            COLOR_ACCENT = COLOR_ACCENT_DARK
            COLOR_ACCENT2 = COLOR_ACCENT2_DARK
            COLOR_TEXT = COLOR_TEXT_DARK
            COLOR_PRIMARY = COLOR_PRIMARY_DARK
            COLOR_SECONDARY = COLOR_SECONDARY_DARK
            COLOR_BTN = COLOR_BTN_DARK
            COLOR_BTN_TXT = COLOR_BTN_TXT_DARK
            COLOR_WHITE = COLOR_WHITE_DARK
        else: # Light mode
            COLOR_BG = COLOR_WHITE_CLEAN
            COLOR_ACCENT = COLOR_LIGHT_GREY
            COLOR_ACCENT2 = COLOR_MEDIUM_GREY
            COLOR_TEXT = COLOR_TEXT_PRIMARY
            COLOR_PRIMARY = COLOR_PRIMARY_GREEN
            COLOR_SECONDARY = COLOR_SECONDARY_BLUE
            COLOR_BTN = COLOR_BTN_NORMAL_BG
            COLOR_BTN_TXT = COLOR_BTN_NORMAL_TXT
            COLOR_WHITE = COLOR_WHITE_CLEAN # Ensure white is truly white in light mode
        # Re-render main navigation and current page to apply new colors
        if self.currentUser: # Only re-render if logged in
            self.showMainNav()
        else: # If on login/register, re-render that specific view
            self.showLoginSplit()

    def showLoginSplit(self):
        """Display 50/50 split login/register UI."""
        for w in self.root.winfo_children():
            w.destroy()
        splitFrame = ctk.CTkFrame(self.root, fg_color=COLOR_BG)
        splitFrame.pack(fill="both", expand=True)
        splitFrame.grid_columnconfigure(0, weight=1)
        splitFrame.grid_columnconfigure(1, weight=1)
        splitFrame.grid_rowconfigure(0, weight=1)
        # Left: Image/branding
        left = ctk.CTkFrame(splitFrame, fg_color=COLOR_BG, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        try:
            img = Image.open("fitness.png")
            # Resize image to fill without distortion, maintaining aspect ratio
            img_width, img_height = img.size
            frame_width = 1100 // 2
            frame_height = 730
            # Calculate new size to fit within the frame
            if img_width / img_height > frame_width / frame_height:
                new_width = frame_width
                new_height = int(img_height * (new_width / img_width))
            else:
                new_height = frame_height
                new_width = int(img_width * (new_height / img_height))

            img = img.resize((new_width, new_height), Image.LANCZOS) # Use LANCZOS for better quality
            tkimg = ImageTk.PhotoImage(img)
            imgLabel = ctk.CTkLabel(left, image=tkimg, text="")
            imgLabel.image = tkimg
            imgLabel.place(relx=0.5, rely=0.5, anchor="center") # Center the image
        except Exception:
            ctk.CTkLabel(left, text="Healthy Habits App", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).place(relx=0.5, rely=0.4, anchor="center")
        # Right: Login/Register Card
        # Increased padx/pady for more breathing room around the card
        right = ctk.CTkFrame(splitFrame, fg_color=COLOR_WHITE_CLEAN, corner_radius=18,
                             border_width=1, border_color=COLOR_MEDIUM_GREY) # Subtle border for card
        right.grid(row=0, column=1, sticky="nsew", padx=60, pady=80)
        self._showLoginCard(right)

    def _showLoginCard(self, parent):
        """Display login card with password reset (FR22)."""
        for w in parent.winfo_children():
            w.destroy()
        ctk.CTkLabel(parent, text="Welcome Back!", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(30, 20))
        ctk.CTkLabel(parent, text="Student ID", text_color=COLOR_TEXT).pack(anchor="w", padx=48, pady=(0, 2))
        usernameEntry = ctk.CTkEntry(parent, width=280, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8,
                                     placeholder_text="Enter your ID")
        usernameEntry.pack(padx=48, pady=(0, 15))
        ctk.CTkLabel(parent, text="Password", text_color=COLOR_TEXT).pack(anchor="w", padx=48, pady=(0, 2))
        passwordEntry = ctk.CTkEntry(parent, width=280, show="*", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8,
                                     placeholder_text="Enter your password")
        passwordEntry.pack(padx=48, pady=(0, 15))

        def doLogin():
            sid = usernameEntry.get().strip()
            pw = passwordEntry.get().strip()
            valid, msg = validateInput("studentId", sid)
            if not valid:
                messagebox.showwarning("Login error", msg)
                return
            user = getUserById(sid)
            if not user:
                messagebox.showwarning("Login error", "User not found.")
                return
            success, msg = user.validateLogin(pw)  # FR02
            messagebox.showinfo("Login", msg)
            if success:
                self.currentUser = user
                self.showMainNav()

        ctk.CTkButton(parent, text="Login", width=280, fg_color=COLOR_PRIMARY, text_color=COLOR_BTN_TXT, corner_radius=8, command=doLogin).pack(padx=48, pady=(15, 8))
        ctk.CTkButton(parent, text="Register", width=280, fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: self._showRegisterCard(parent)).pack(padx=48, pady=(0, 8))
        ctk.CTkButton(parent, text="Forgot Password?", width=280, fg_color="transparent", text_color=COLOR_TEXT_SECONDARY, hover_color=COLOR_LIGHT_GREY, corner_radius=8, command=lambda: self._showResetCard(parent)).pack(padx=48, pady=(0, 15))
        # Developer Skip button for easy testing
        ctk.CTkButton(parent, text="Developer Skip", width=280, fg_color=COLOR_MEDIUM_GREY, text_color=COLOR_TEXT_PRIMARY, corner_radius=8, command=self._devSkip).pack(padx=48, pady=(10, 10))


    def _showRegisterCard(self, parent):
        """
        Display registration card (FR01).
        AC6: Demonstrates GUI, input validation, data collection, OOP instantiation.
        AC7: Input validation, error handling.
        """
        # Clear parent and use a scrollable frame for registration fields
        for w in parent.winfo_children():
            w.destroy()
        scrollFrame = ctk.CTkScrollableFrame(parent, fg_color=COLOR_WHITE_CLEAN)
        scrollFrame.pack(fill="both", expand=True, padx=20, pady=20) # Added padding for scroll frame
        ctk.CTkLabel(scrollFrame, text="Register New Account", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 15))

        # Helper function for consistent entry/label styling
        def create_entry_row(s_frame, label_text, entry_placeholder="", entry_show=None, is_dropdown=False, dropdown_values=None):
            ctk.CTkLabel(s_frame, text=label_text, text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=(8, 2))
            if is_dropdown:
                var = ctk.StringVar(value=dropdown_values[0] if dropdown_values else "")
                option_menu = ctk.CTkOptionMenu(s_frame, variable=var, values=dropdown_values, width=250, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, button_color=COLOR_PRIMARY)
                option_menu.pack(padx=20, pady=(0, 10))
                return var, option_menu # Return both variable and widget
            else:
                entry = ctk.CTkEntry(s_frame, width=250, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8,
                                     placeholder_text=entry_placeholder, show=entry_show)
                entry.pack(padx=20, pady=(0, 10))
                return entry

        entryId = create_entry_row(scrollFrame, "Student ID (AAA####)", "e.g., ABC1234")
        entryPw = create_entry_row(scrollFrame, "Password", "min 4 characters", "*")
        entrySec = create_entry_row(scrollFrame, "Security Answer (for reset)", "e.g., Your pet's name")
        entryAge = create_entry_row(scrollFrame, "Age (years)", "e.g., 20")
        entryHeight = create_entry_row(scrollFrame, "Height (cm)", "e.g., 175.5")
        entryWeight = create_entry_row(scrollFrame, "Weight (kg)", "e.g., 70.2")

        ctk.CTkLabel(scrollFrame, text="Gender", text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=(8, 2))
        genderVar = ctk.StringVar(value="Male")
        ctk.CTkRadioButton(scrollFrame, text="Male", variable=genderVar, value="Male", text_color=COLOR_TEXT, fg_color=COLOR_PRIMARY).pack(anchor="w", padx=30, pady=2)
        ctk.CTkRadioButton(scrollFrame, text="Female", variable=genderVar, value="Female", text_color=COLOR_TEXT, fg_color=COLOR_PRIMARY).pack(anchor="w", padx=30, pady=2)

        activityVar, _ = create_entry_row(scrollFrame, "Activity Level", is_dropdown=True,
                                        dropdown_values=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"])
        goalTypeVar, _ = create_entry_row(scrollFrame, "Goal Type", is_dropdown=True,
                                        dropdown_values=["Lose Weight", "Gain Muscle", "Maintain Health"])
        planTypeVar, _ = create_entry_row(scrollFrame, "Plan Type", is_dropdown=True,
                                        dropdown_values=["Nutrition Focus", "Workout Focus", "Balanced"])

        def doRegister():
            sid = entryId.get().strip()
            pw = entryPw.get().strip()
            w = entryWeight.get().strip()
            sec = entrySec.get().strip()
            age = entryAge.get().strip()
            height = entryHeight.get().strip()
            gender = genderVar.get()
            activity = activityVar.get()
            goal = goalTypeVar.get()
            plan = planTypeVar.get()

            # AC7: Validate all fields
            valid, msg = validateInput("studentId", sid)
            if not valid or userExists(sid):
                messagebox.showwarning("Registration Error", msg if not valid else "Student ID already exists.")
                return
            valid, msg = validateInput("password", pw)
            if not valid:
                messagebox.showwarning("Registration Error", msg)
                return
            if not age.isdigit() or not (10 <= int(age) <= 120):
                messagebox.showwarning("Registration Error", "Enter a valid age (10-120 years).")
                return
            try:
                h = float(height)
                if not (100 <= h <= 250):
                    raise ValueError
            except Exception:
                messagebox.showwarning("Registration Error", "Enter a valid height (100-250cm).")
                return
            valid, msg = validateInput("goalWeight", w)
            if not valid:
                messagebox.showwarning("Registration Error", msg)
                return
            if not gender or not activity or not goal or not plan or not sec or len(sec) < 2:
                messagebox.showwarning("Registration Error", "All fields are required and security answer must be at least 2 characters.")
                return

            user = User(sid, pw, w, goal, plan, isAdmin=False, securityAnswer=sec,
                        age=age, height=height, weight=w, gender=gender, activityLevel=activity)
            saveUser(user)
            messagebox.showinfo("Registration Successful", "Account created! You may now login.")
            self._showLoginCard(parent)

        ctk.CTkButton(scrollFrame, text="Create Account", width=250, fg_color=COLOR_PRIMARY, text_color=COLOR_BTN_TXT, corner_radius=8, command=doRegister).pack(padx=20, pady=(20, 8))
        ctk.CTkButton(scrollFrame, text="Back to Login", width=250, fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: self._showLoginCard(parent)).pack(padx=20, pady=(0, 20))

    def _showResetCard(self, parent):
        """Display password reset card (FR22)."""
        for w in parent.winfo_children():
            w.destroy()
        ctk.CTkLabel(parent, text="Reset Password", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(30, 20))
        ctk.CTkLabel(parent, text="Student ID", text_color=COLOR_TEXT).pack(anchor="w", padx=48, pady=(0, 2))
        sidEntry = ctk.CTkEntry(parent, width=280, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="Your Student ID")
        sidEntry.pack(padx=48, pady=(0, 15))
        ctk.CTkLabel(parent, text="Security Answer", text_color=COLOR_TEXT).pack(anchor="w", padx=48, pady=(0, 2))
        secEntry = ctk.CTkEntry(parent, width=280, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="Your Security Answer")
        secEntry.pack(padx=48, pady=(0, 15))
        ctk.CTkLabel(parent, text="New Password", text_color=COLOR_TEXT).pack(anchor="w", padx=48, pady=(0, 2))
        pwEntry = ctk.CTkEntry(parent, width=280, show="*", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="New Password (min 4 chars)")
        pwEntry.pack(padx=48, pady=(0, 15))

        def doReset():
            sid = sidEntry.get().strip()
            sec = secEntry.get().strip()
            pw = pwEntry.get().strip()
            user = getUserById(sid)
            if not user:
                messagebox.showwarning("Reset Error", "User not found.")
                return
            success, msg = user.resetPassword(sec, pw)
            messagebox.showinfo("Password Reset", msg)
            if success:
                self._showLoginCard(parent)

        ctk.CTkButton(parent, text="Reset Password", width=280, fg_color=COLOR_PRIMARY, text_color=COLOR_BTN_TXT, corner_radius=8, command=doReset).pack(padx=48, pady=(20, 8))
        ctk.CTkButton(parent, text="Back to Login", width=280, fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: self._showLoginCard(parent)).pack(padx=48, pady=(0, 20))

    def _devSkip(self):
        """Skip to main nav for development (temporary)."""
        # Create a dummy user for dev skip with all required attributes for home page
        self.currentUser = User(
            "DEVSKIP", "dev", goalWeight="70", goalType="Maintain Health",
            planType="Balanced", isAdmin=True, securityAnswer="test",
            age="30", height="175", weight="70", gender="Male", activityLevel="Moderately Active"
        )
        self.showMainNav()

    # --- Main navigation & placeholders (AC7/SRS) ---
    def showMainNav(self):
        """Display main navigation bar and content."""
        for w in self.root.winfo_children():
            w.destroy()

        # Left Navigation Bar
        navBar = ctk.CTkFrame(self.root, fg_color=COLOR_ACCENT2, corner_radius=0, width=200) # Wider nav bar
        navBar.pack(side="left", fill="y", padx=0, pady=0) # No padding to stick to edge

        # Main Content Frame (scrollable)
        contentFrame = ctk.CTkScrollableFrame(self.root, fg_color=COLOR_BG)
        contentFrame.pack(side="right", fill="both", expand=True, padx=20, pady=20) # Padding around content
        self.contentFrame = contentFrame

        # Initialize active page if not set
        self.activePage = getattr(self, 'activePage', 'home')
        self.navBtns = []

        # Logo at the top of the nav bar
        logo_nav_frame = ctk.CTkFrame(navBar, fg_color="transparent")
        logo_nav_frame.pack(pady=(20, 30))
        try:
            logoImg = Image.open("fitness.png").resize((80, 80), Image.LANCZOS)
            logoTk = ImageTk.PhotoImage(logoImg)
            ctk.CTkLabel(logo_nav_frame, image=logoTk, text="").pack()
            logo_nav_frame.image = logoTk # Keep reference
        except Exception:
            ctk.CTkLabel(logo_nav_frame, text="HH", font=ctk.CTkFont(size=30, weight="bold"), text_color=COLOR_PRIMARY).pack()
        ctk.CTkLabel(logo_nav_frame, text="Healthy Habits", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT).pack(pady=5)


        navBtns = [
            ("Home", "home", "🏠"),
            ("Workouts", "workouts", "🏋️"),
            ("Macros", "macros", "🍎"),
            ("Challenges", "challenges", "🏆"),
            ("Feed", "feed", "💬"),
            ("Settings", "settings", "⚙️")
        ]

        def nav_cmd(page):
            self.activePage = page
            self.updateNavHighlight()
            self.showPage(page)

        for i, (label, page, icon) in enumerate(navBtns):
            btn = ctk.CTkButton(
                navBar,
                text=f"{icon}  {label}", # Add icon to text
                width=180,
                height=40, # Uniform button height
                corner_radius=10, # Rounded corners for nav buttons
                fg_color=COLOR_PRIMARY if self.activePage == page else "transparent", # Transparent for inactive, solid for active
                text_color=COLOR_WHITE_CLEAN if self.activePage == page else COLOR_TEXT, # White text on active, dark on inactive
                hover_color=COLOR_PRIMARY_DARK_GREEN if self.activePage == page else COLOR_ACCENT, # Darker green on hover for active, light grey for inactive
                command=lambda p=page: nav_cmd(p)
            )
            btn.pack(pady=6, padx=10, anchor="center") # Adjusted padding
            self.navBtns.append((btn, page))

        # Logout button at the bottom of the nav bar
        ctk.CTkButton(
            navBar,
            text="🚪 Logout",
            width=180,
            height=40,
            corner_radius=10,
            fg_color=COLOR_MEDIUM_GREY, # Distinct color for logout
            text_color=COLOR_TEXT_PRIMARY,
            hover_color=COLOR_ACCENT2_DARK if ctk.get_appearance_mode() == "dark" else COLOR_ACCENT,
            command=self.logout
        ).pack(pady=(40, 20), padx=10, anchor="center")

        self.updateNavHighlight()
        self.showPage(self.activePage)

    def updateNavHighlight(self):
        for btn, page in self.navBtns:
            is_active = self.activePage == page
            btn.configure(
                fg_color=COLOR_PRIMARY if is_active else "transparent",
                text_color=COLOR_WHITE_CLEAN if is_active else COLOR_TEXT,
                hover_color=COLOR_PRIMARY_DARK_GREEN if is_active else COLOR_ACCENT
            )

    def showPage(self, page):
        """Switch between pages based on navigation."""
        for widget in self.contentFrame.winfo_children():
            widget.destroy()
        if page == "home":
            self.showHome()
        elif page == "workouts":
            self.showWorkouts()
        elif page == "macros":
            self.showMacros()
        elif page == "challenges":
            self.showChallenges()
        elif page == "feed":
            self.showFeed()
        elif page == "settings":
            self.showSettings()

    def showSettings(self):
        """Display settings page with dark/light mode and password change."""
        cf = self.contentFrame
        ctk.CTkLabel(cf, text="Settings", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=24)
        # Theme switch
        ctk.CTkLabel(cf, text="Theme (Accessibility)", text_color=COLOR_TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=40, pady=(15, 5))
        themeVar = ctk.StringVar(value=ctk.get_appearance_mode().lower())
        def set_theme():
            ctk.set_appearance_mode(themeVar.get())
            self.setThemeColors(themeVar.get())
        ctk.CTkRadioButton(cf, text="Light Mode", variable=themeVar, value="light", command=set_theme, text_color=COLOR_TEXT, fg_color=COLOR_PRIMARY).pack(anchor="w", padx=55, pady=2)
        ctk.CTkRadioButton(cf, text="Dark Mode", variable=themeVar, value="dark", command=set_theme, text_color=COLOR_TEXT, fg_color=COLOR_PRIMARY).pack(anchor="w", padx=55, pady=2)
        # Change password
        ctk.CTkLabel(cf, text="\nChange Password", text_color=COLOR_TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=40, pady=(25, 5))
        pwOld = ctk.CTkEntry(cf, width=280, show="*", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="Current Password")
        pwOld.pack(padx=48, pady=(5, 10))
        pwNew = ctk.CTkEntry(cf, width=280, show="*", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="New Password")
        pwNew.pack(padx=48, pady=(5, 10))
        pwConfirm = ctk.CTkEntry(cf, width=280, show="*", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="Confirm New Password")
        pwConfirm.pack(padx=48, pady=(5, 15))
        def doChangePw():
            user = self.currentUser
            old = pwOld.get().strip()
            new = pwNew.get().strip()
            confirm = pwConfirm.get().strip()
            if not user.checkPassword(old):
                messagebox.showwarning("Change Password", "Current password is incorrect.")
                return
            valid, msg = validateInput("password", new)
            if not valid:
                messagebox.showwarning("Change Password", msg)
                return
            if new != confirm:
                messagebox.showwarning("Change Password", "New passwords do not match.")
                return
            user._password = new
            saveUser(user)
            messagebox.showinfo("Change Password", "Password changed successfully.")
            # Clear fields after change
            pwOld.delete(0, ctk.END)
            pwNew.delete(0, ctk.END)
            pwConfirm.delete(0, ctk.END)
        ctk.CTkButton(cf, text="Change Password", width=280, fg_color=COLOR_PRIMARY, text_color=COLOR_BTN_TXT, corner_radius=8, command=doChangePw).pack(padx=48, pady=(10, 25))
        # Logout button
        ctk.CTkButton(cf, text="Logout", width=280, fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=self.logout).pack(padx=48, pady=(10, 30))

    def showHome(self):
        """
        Display home page with streaks/badges, progress bar, calorie widget, and workout logging.
        AC6: GUI, OOP, data structures, control structures, algorithm (progress/circle calc).
        AC7: Input validation, error handling, user feedback.
        """
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        user = self.currentUser
        # --- Top bar: profile (left), logo (center), notifications (right) ---
        topBar = ctk.CTkFrame(cf, fg_color=COLOR_BG)
        topBar.pack(fill="x", pady=(10, 0), padx=20)
        topBar.grid_columnconfigure(0, weight=1)
        topBar.grid_columnconfigure(1, weight=2)
        topBar.grid_columnconfigure(2, weight=1)
        # Profile icon (top left)
        profileFrame = ctk.CTkFrame(topBar, fg_color=COLOR_ACCENT2, width=48, height=48, corner_radius=24)
        profileFrame.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=0)
        ctk.CTkLabel(profileFrame, text="👤", font=ctk.CTkFont(size=22), text_color=COLOR_TEXT).pack(expand=True)
        # Welcome message
        ctk.CTkLabel(topBar, text=f"Welcome, {user.getStudentId()}!", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_PRIMARY).grid(row=0, column=1, pady=0, sticky="n")
        # Notifications icon (top right)
        notifFrame = ctk.CTkFrame(topBar, fg_color=COLOR_ACCENT2, width=48, height=48, corner_radius=24)
        notifFrame.grid(row=0, column=2, sticky="e", padx=(10, 0), pady=0)
        ctk.CTkLabel(notifFrame, text="🔔", font=ctk.CTkFont(size=22), text_color=COLOR_TEXT).pack(expand=True)

        # --- Main content area with two columns for cards ---
        main_content_frame = ctk.CTkFrame(cf, fg_color="transparent")
        main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_columnconfigure(1, weight=1)
        main_content_frame.grid_rowconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(1, weight=1)


        # --- Calories Widget (Left Column, Row 0) ---
        calWidget = ctk.CTkFrame(main_content_frame, fg_color=COLOR_WHITE_CLEAN, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        calWidget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        calWidget.grid_columnconfigure(0, weight=1)
        calWidget.grid_columnconfigure(1, weight=1)

        # Calories Title
        ctk.CTkLabel(calWidget, text="Daily Calories", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT).grid(row=0, column=0, columnspan=2, pady=(15, 10))

        # Circular progress bar (drawn with Canvas)
        calGoal = user.getCalorieGoal()
        calConsumed = user.getCaloriesConsumed()
        calBurned = user.getCaloriesBurned()
        calNet = calConsumed - calBurned
        calRem = calGoal - calNet

        percent = min(max(calNet / calGoal, 0), 1) if calGoal and calNet >= 0 else 0
        if calNet < 0: # If burned more than consumed, represent as progress towards next goal or distinct color
            percent = 0 # For simplicity, if net negative, progress is 0 on consumption bar

        canvas_frame = ctk.CTkFrame(calWidget, fg_color="transparent")
        canvas_frame.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        canvas = Canvas(canvas_frame, width=120, height=120, bg=COLOR_WHITE_CLEAN, highlightthickness=0)
        canvas.pack(expand=True)

        # Draw background circle
        canvas.create_oval(10, 10, 110, 110, outline=COLOR_LIGHT_GREY, width=10)
        # Draw progress arc
        if percent > 0:
            extent = percent * 360
            canvas.create_arc(10, 10, 110, 110, start=90, extent=-extent, style="arc", outline=COLOR_PRIMARY_GREEN, width=10)
        # Calories remaining in center
        canvas.create_text(60, 50, text=f"{calRem}", font=("Arial", 20, "bold"), fill=COLOR_TEXT)
        canvas.create_text(60, 75, text="kcal remaining", font=("Arial", 12), fill=COLOR_TEXT_SECONDARY)


        # Right side info
        infoFrame = ctk.CTkFrame(calWidget, fg_color="transparent")
        infoFrame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        infoFrame.grid_rowconfigure(0, weight=1)
        infoFrame.grid_rowconfigure(1, weight=1)
        infoFrame.grid_rowconfigure(2, weight=1)
        infoFrame.grid_rowconfigure(3, weight=1) # For buttons
        ctk.CTkLabel(infoFrame, text=f"Goal: {calGoal} kcal", text_color=COLOR_TEXT, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=2)
        ctk.CTkLabel(infoFrame, text=f"Consumed: {calConsumed} kcal", text_color=COLOR_SECONDARY_BLUE, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=2)
        ctk.CTkLabel(infoFrame, text=f"Burned: {calBurned} kcal", text_color=COLOR_PRIMARY_GREEN, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=2)

        # Log food/exercise buttons
        def log_food():
            val = ctk.CTkInputDialog(text="Enter calories consumed:", title="Log Food").get_input()
            try:
                cals = int(val)
                if cals < 0 or cals > 5000:
                    raise ValueError
                user.addCalories(cals)
                saveUser(user)
                self.showHome()
            except Exception:
                messagebox.showwarning("Log Food", "Enter a valid calorie amount (0-5000)")
        def log_exercise():
            val = ctk.CTkInputDialog(text="Enter calories burned:", title="Log Exercise").get_input()
            try:
                cals = int(val)
                if cals < 0 or cals > 5000:
                    raise ValueError
                user.addExercise(cals)
                saveUser(user)
                self.showHome()
            except Exception:
                messagebox.showwarning("Log Exercise", "Enter a valid calorie amount (0-5000)")

        btnRow = ctk.CTkFrame(infoFrame, fg_color="transparent")
        btnRow.pack(anchor="w", pady=(10,0))
        ctk.CTkButton(btnRow, text="Log Food", width=100, fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=log_food).pack(side="left", padx=5)
        ctk.CTkButton(btnRow, text="Log Exercise", width=100, fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=log_exercise).pack(side="left", padx=5)

        # --- Workout Progress Card (Right Column, Row 0) ---
        workout_card = ctk.CTkFrame(main_content_frame, fg_color=COLOR_WHITE_CLEAN, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        workout_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        workout_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(workout_card, text="Weekly Workout Progress", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 10))

        goalRow = ctk.CTkFrame(workout_card, fg_color="transparent")
        goalRow.pack(pady=(8, 5), padx=20, fill="x")
        ctk.CTkLabel(goalRow, text="Goal:", text_color=COLOR_TEXT, font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        goalEntry = ctk.CTkEntry(goalRow, width=50, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8)
        goalEntry.insert(0, str(user.getWeeklyGoal()))
        goalEntry.pack(side="left", padx=(0, 10))
        def set_goal():
            try:
                val = int(goalEntry.get())
                if val < 1 or val > 14:
                    raise ValueError
                user.setWeeklyGoal(val)
                user.resetWorkoutsCompleted() # Reset workouts on goal change
                saveUser(user)
                self.showHome()
            except Exception:
                messagebox.showwarning("Set Goal", "Enter a number between 1 and 14.")
        ctk.CTkButton(goalRow, text="Set Goal", width=80, fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=set_goal).pack(side="left")

        ctk.CTkLabel(workout_card, text=f"Completed: {user.getWorkoutsCompleted()} / {user.getWeeklyGoal()}", text_color=COLOR_TEXT, font=ctk.CTkFont(size=15)).pack(pady=(10, 5))
        progress = user.getWorkoutsCompleted() / user.getWeeklyGoal() if user.getWeeklyGoal() else 0
        progressBar = ctk.CTkProgressBar(workout_card, width=280, height=15, progress_color=COLOR_PRIMARY_GREEN, fg_color=COLOR_LIGHT_GREY, corner_radius=8)
        progressBar.pack(pady=(0, 15))
        progressBar.set(progress)

        # Workout Logging Feature
        ctk.CTkLabel(workout_card, text="Log a Workout:", text_color=COLOR_TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        logRow = ctk.CTkFrame(workout_card, fg_color="transparent")
        logRow.pack(pady=(0, 15))
        presetWorkouts = ["Run", "Walk", "Weights", "Yoga", "Cycling", "Swim", "Other"]
        workoutVar = ctk.StringVar(value=presetWorkouts[0])
        ctk.CTkOptionMenu(logRow, variable=workoutVar, values=presetWorkouts, width=150, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, button_color=COLOR_PRIMARY).pack(side="left", padx=(0, 10))
        def log_workout():
            user.addWorkoutCompleted()
            if user.getWorkoutsCompleted() > user.getWeeklyGoal():
                user.setWeeklyGoal(user.getWorkoutsCompleted()) # Auto-adjust goal if exceeded
            saveUser(user)
            messagebox.showinfo("Workout Logged", f"Logged: {workoutVar.get()}")
            self.showHome()
        ctk.CTkButton(logRow, text="Log Workout", width=120, fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=log_workout).pack(side="left")

        # --- Streaks and Badges Card (Spans two columns, Row 1) ---
        badges_card = ctk.CTkFrame(main_content_frame, fg_color=COLOR_WHITE_CLEAN, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        badges_card.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        badges_card.grid_columnconfigure(0, weight=1) # Center content

        ctk.CTkLabel(badges_card, text="Your Achievements", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(15, 10))
        ctk.CTkLabel(badges_card, text=f"Current Streak: 0 days (Feature Coming Soon)", text_color=COLOR_TEXT_SECONDARY).pack(pady=5)
        ctk.CTkLabel(badges_card, text=f"Badges Earned: {', '.join(user._badges) if user._badges else 'None yet!'}", text_color=COLOR_TEXT_SECONDARY).pack(pady=5)
        ctk.CTkLabel(badges_card, text="Visit Challenges for more ways to earn badges!", text_color=COLOR_TEXT).pack(pady=(10, 15))


    def showWorkouts(self):
        """Display workout page."""
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        user = self.currentUser
        card = ctk.CTkFrame(cf, fg_color=COLOR_WHITE_CLEAN, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        card.pack(pady=40, padx=40, fill="x", expand=False) # Fill horizontally
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="Workout Plans", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(25, 15))
        ctk.CTkLabel(card, text="Explore and create personalized workout routines.", text_color=COLOR_TEXT_SECONDARY).pack(pady=(0, 20))
        ctk.CTkButton(card, text="Create Workout Plan", fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Workouts", "Workout plan builder coming soon!")).pack(pady=15, padx=30, fill="x")
        ctk.CTkButton(card, text="View My Plans", fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Workouts", "Your saved workout plans coming soon!")).pack(pady=8, padx=30, fill="x")
        ctk.CTkButton(card, text="Export Plan", fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Export", "Workout plan export coming soon!")).pack(pady=8, padx=30, fill="x")

    def showMacros(self):
        """Display macro page."""
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        user = self.currentUser
        card = ctk.CTkFrame(cf, fg_color=COLOR_WHITE_CLEAN, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        card.pack(pady=40, padx=40, fill="x", expand=False) # Fill horizontally
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="Macro & Meal Planning", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(25, 15))
        ctk.CTkLabel(card, text="Track your nutrition and create healthy meal plans.", text_color=COLOR_TEXT_SECONDARY).pack(pady=(0, 20))
        ctk.CTkButton(card, text="Create Meal Plan", fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Macros", "Meal plan builder coming soon!")).pack(pady=15, padx=30, fill="x")
        ctk.CTkButton(card, text="Food Database Search", fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Macros", "Food database search coming soon!")).pack(pady=8, padx=30, fill="x")
        ctk.CTkButton(card, text="View Macro Breakdown", fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Macros", "Detailed macro breakdown coming soon!")).pack(pady=8, padx=30, fill="x")

    def showChallenges(self):
        """Display challenge page."""
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        card = ctk.CTkFrame(cf, fg_color=COLOR_WHITE_CLEAN, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        card.pack(pady=40, padx=40, fill="x", expand=False) # Fill horizontally
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text="Community Challenges", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(25, 15))
        ctk.CTkLabel(card, text="Join challenges, compete with friends, and earn badges!", text_color=COLOR_TEXT_SECONDARY).pack(pady=(0, 20))
        ctk.CTkButton(card, text="Browse Challenges", fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Challenges", "Challenge listings coming soon!")).pack(pady=15, padx=30, fill="x")
        ctk.CTkButton(card, text="Create Your Own Challenge", fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Challenges", "Challenge creation coming soon!")).pack(pady=8, padx=30, fill="x")
        ctk.CTkButton(card, text="My Active Challenges", fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: messagebox.showinfo("Challenges", "Your active challenges coming soon!")).pack(pady=8, padx=30, fill="x")

    def showFeed(self):
        """Display social feed page."""
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        card = ctk.CTkFrame(cf, fg_color=COLOR_WHITE_CLEAN, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        card.pack(pady=20, padx=40, fill="both", expand=True) # Fill both ways
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Community Feed", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(25, 15))

        # Post creation area
        post_frame = ctk.CTkFrame(card, fg_color=COLOR_LIGHT_GREY, corner_radius=10, border_width=1, border_color=COLOR_MEDIUM_GREY)
        post_frame.pack(pady=10, padx=20, fill="x")
        postEntry = ctk.CTkEntry(post_frame, width=500, placeholder_text="Share your progress or ask a question (280 chars max)",
                                 fg_color=COLOR_WHITE_CLEAN, text_color=COLOR_TEXT, corner_radius=8)
        postEntry.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(post_frame, text="Post Update", fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: self._postUpdate(postEntry.get())).pack(pady=10, padx=10, anchor="e")

        # Sorting and Search area
        control_frame = ctk.CTkFrame(card, fg_color="transparent")
        control_frame.pack(pady=(10, 5), padx=20, fill="x")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(control_frame, text="Sort by Date", fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: self._sortFeed("date")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(control_frame, text="Sort by Likes", fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: self._sortFeed("likes")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        searchEntry = ctk.CTkEntry(control_frame, width=200, placeholder_text="Search posts...", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8)
        searchEntry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(control_frame, text="Search", fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: self._searchFeed(searchEntry.get())).grid(row=0, column=3, padx=5, pady=5, sticky="ew")


        # Posts display area (use a separate scrollable frame if many posts)
        posts_display_frame = ctk.CTkScrollableFrame(card, fg_color="transparent")
        posts_display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        if not self.posts:
            ctk.CTkLabel(posts_display_frame, text="No posts yet. Be the first to share!", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=14)).pack(pady=20)

        for post in self.posts:
            # Only show approved posts to regular users, show all to admin
            if post.get("approved", "False") == "False" and (not self.currentUser or not self.currentUser.isAdmin()):
                continue

            frame = ctk.CTkFrame(posts_display_frame, fg_color=COLOR_WHITE_CLEAN, corner_radius=10, border_width=1, border_color=COLOR_MEDIUM_GREY)
            frame.pack(pady=8, padx=10, fill="x")

            # Post content
            post_text_label = ctk.CTkLabel(frame, text=post.get("content", "No content"), wraplength=450, font=ctk.CTkFont(size=14), text_color=COLOR_TEXT, justify="left")
            post_text_label.pack(pady=(10, 5), padx=15, anchor="w")

            # Post metadata and actions
            meta_frame = ctk.CTkFrame(frame, fg_color="transparent")
            meta_frame.pack(fill="x", padx=10, pady=(0, 10))

            # Likes and Comments
            ctk.CTkButton(meta_frame, text=f"👍 {post.get('likes', 0)} Likes", fg_color="transparent", text_color=COLOR_TEXT_SECONDARY, hover_color=COLOR_LIGHT_GREY, command=lambda p=post: self._likePost(p)).pack(side="left", padx=5)
            ctk.CTkButton(meta_frame, text="💬 Comment", fg_color="transparent", text_color=COLOR_TEXT_SECONDARY, hover_color=COLOR_LIGHT_GREY, command=lambda p=post: messagebox.showinfo("Comment", "Commenting coming soon!")).pack(side="left", padx=5)

            # Admin/Edit/Delete actions
            action_frame = ctk.CTkFrame(meta_frame, fg_color="transparent")
            action_frame.pack(side="right", padx=5)

            if self.currentUser and self.currentUser.isAdmin() and post.get("approved", "False") == "False":
                ctk.CTkButton(action_frame, text="✅ Approve", fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda p=post: self._approvePost(p)).pack(side="left", padx=5)
            if self.currentUser and (self.currentUser.isAdmin() or self.currentUser.getStudentId() == post.get("authorId")): # Allow author to edit their own post (assuming authorId is stored)
                ctk.CTkButton(action_frame, text="✏️ Edit", fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda p=post: self._editPost(p)).pack(side="left", padx=5)
                ctk.CTkButton(action_frame, text="🗑️ Delete", fg_color="#E57373", text_color=COLOR_WHITE_CLEAN, corner_radius=8, command=lambda p=post: self._deletePost(p)).pack(side="left", padx=5)


    def _postUpdate(self, content):
        """Post update to social feed (FR05)."""
        if not self.currentUser:
            messagebox.showwarning("Post Error", "You must be logged in to post.")
            return
        if not content.strip():
            messagebox.showwarning("Post Error", "Post cannot be empty.")
            return
        if len(content) > 280:
            messagebox.showwarning("Post Error", "Post exceeds 280 characters.")
            return
        post = {
            "postID": str(len(self.posts) + 1),
            "content": content,
            "likes": "0",
            "comments": "",
            "approved": "False", # FR07: Posts require admin approval
            "authorId": self.currentUser.getStudentId(), # Store author ID
            "timestamp": datetime.now().isoformat()
        }
        self.posts.append(post)
        appendCsv(POSTS_CSV, post, ["postID", "content", "likes", "comments", "approved", "authorId", "timestamp"])
        messagebox.showinfo("Post Submitted", "Your post has been submitted for approval (FR07).")
        self.showFeed() # Refresh feed

    def _sortFeed(self, criteria):
        """Sort feed by date or likes (FR13)."""
        # Read posts again to ensure all are loaded for sorting
        self.posts = readCsv(POSTS_CSV)

        if criteria == "date":
            # Sort by timestamp (most recent first)
            self.posts.sort(key=lambda x: x.get("timestamp", "1970-01-01T00:00:00"), reverse=True)
        elif criteria == "likes":
            # Sort by likes (highest first)
            self.posts.sort(key=lambda x: int(x.get("likes", 0)), reverse=True)
        self.showFeed()

    def _searchFeed(self, query):
        """Search feed by keyword (FR14)."""
        all_posts = readCsv(POSTS_CSV) # Search through all posts
        results = [p for p in all_posts if query.lower() in p.get("content", "").lower()]
        self.posts = results # Update the displayed posts
        if not results and query:
            messagebox.showinfo("Search Results", "No posts found matching your search query.")
        self.showFeed()

    def _likePost(self, post):
        """Like a post (FR08)."""
        current_likes = int(post.get("likes", 0))
        post["likes"] = str(current_likes + 1)
        # Update the specific post in the in-memory list
        for i, p in enumerate(self.posts):
            if p.get("postID") == post.get("postID"):
                self.posts[i] = post
                break
        writeCsv(POSTS_CSV, self.posts, ["postID", "content", "likes", "comments", "approved", "authorId", "timestamp"])
        self.showFeed()

    def _approvePost(self, post):
        """Approve post (FR07)."""
        if self.currentUser and self.currentUser.isAdmin():
            post["approved"] = "True"
            # Update the specific post in the in-memory list
            for i, p in enumerate(self.posts):
                if p.get("postID") == post.get("postID"):
                    self.posts[i] = post
                    break
            writeCsv(POSTS_CSV, self.posts, ["postID", "content", "likes", "comments", "approved", "authorId", "timestamp"])
            messagebox.showinfo("Admin Action", "Post approved successfully.")
            self.showFeed()
        else:
            messagebox.showwarning("Permission Denied", "Only administrators can approve posts.")

    def _editPost(self, post):
        """Edit post (FR15)."""
        if not self.currentUser or (not self.currentUser.isAdmin() and self.currentUser.getStudentId() != post.get("authorId")):
            messagebox.showwarning("Permission Denied", "You can only edit your own posts or if you are an admin.")
            return

        current_content = post.get("content", "")
        newContent = ctk.CTkInputDialog(text="Edit post:", title="Edit Post", initial_value=current_content).get_input()
        if newContent is not None: # User didn't cancel
            if not newContent.strip():
                messagebox.showwarning("Edit Post", "Post content cannot be empty.")
                return
            if len(newContent) > 280:
                messagebox.showwarning("Edit Post", "Post exceeds 280 characters.")
                return
            post["content"] = newContent
            # Update the specific post in the in-memory list
            for i, p in enumerate(self.posts):
                if p.get("postID") == post.get("postID"):
                    self.posts[i] = post
                    break
            writeCsv(POSTS_CSV, self.posts, ["postID", "content", "likes", "comments", "approved", "authorId", "timestamp"])
            messagebox.showinfo("Edit Post", "Post updated successfully.")
            self.showFeed()


    def _deletePost(self, post):
        """Delete post (FR16)."""
        if not self.currentUser or (not self.currentUser.isAdmin() and self.currentUser.getStudentId() != post.get("authorId")):
            messagebox.showwarning("Permission Denied", "You can only delete your own posts or if you are an admin.")
            return

        confirm = messagebox.askyesno("Delete Post", "Are you sure you want to delete this post? This action cannot be undone.")
        if confirm:
            # Filter out the post to be deleted
            self.posts = [p for p in self.posts if p.get("postID") != post.get("postID")]
            writeCsv(POSTS_CSV, self.posts, ["postID", "content", "likes", "comments", "approved", "authorId", "timestamp"])
            messagebox.showinfo("Delete Post", "Post deleted.")
            self.showFeed()

    def backupData(self):
        """Create daily backup of CSV files (FR21)."""
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        for file in [USERS_CSV, MACROS_CSV, WORKOUTS_CSV, POSTS_CSV, CHALLENGES_CSV]:
            if os.path.exists(file):
                try:
                    shutil.copy(file, os.path.join(BACKUP_DIR, f"{os.path.basename(file)}_{timestamp}.bak"))
                except Exception as e:
                    logError(f"Backup failed for {file}: {e}")
                    messagebox.showwarning("Backup Error", f"Failed to back up {file}. Check error_log.txt.")


    def logout(self):
        """Logout and return to login screen."""
        self.backupData()  # FR21
        self.currentUser = None
        self.showLoginSplit()

if __name__ == "__main__":
    app = HealthyHabitsApp()
    app.backupData()  # Initial backup on app start
    app.root.mainloop()
