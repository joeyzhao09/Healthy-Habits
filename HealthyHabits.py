"""
Healthy Habits - GWSC VCE SD U3/4 Outcome 1 Project
Python + CustomTkinter, CSV storage, AC6/AC7-aligned for 9–10 marks.
Author: Joey Zhao, 2025

- User authentication (AAA####), registration, and security answer
- CSV storage for users/plans/macros/posts/comments (AC6, AC7, SRS)
- Navigation bar: Home, Workouts, Macros, Feed, Logout
- Modular OOP User class (protected attrs), camelCase everywhere, docstrings
- Placeholders for all SRS features; extensible for full AC7/AC6 marks

"""

# Required imports
import os
import csv
import re
import math
import shutil
import random
import json
import requests
import io
from datetime import date, datetime
from tkinter import messagebox, Canvas
import tkinter as tk
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("Warning: tkcalendar not available. Install with: pip install tkcalendar")
    
    # Fallback DateEntry class when tkcalendar is not available
    class DateEntry:
        """Fallback date entry widget using CTkEntry"""
        def __init__(self, parent, **kwargs):
            self.parent = parent
            self._date = datetime.now().date()
            # Create a simple entry with today's date
            self.entry = ctk.CTkEntry(parent, placeholder_text="YYYY-MM-DD")
            self.entry.insert(0, self._date.strftime("%Y-%m-%d"))
            
        def pack(self, **kwargs):
            self.entry.pack(**kwargs)
            
        def grid(self, **kwargs):
            self.entry.grid(**kwargs)
            
        def get_date(self):
            """Get the current date value"""
            try:
                date_str = self.entry.get().strip()
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return datetime.now().date()
                
        def set_date(self, new_date):
            """Set the date value"""
            self.entry.delete(0, 'end')
            if isinstance(new_date, str):
                self.entry.insert(0, new_date)
            else:
                self.entry.insert(0, new_date.strftime("%Y-%m-%d"))
import customtkinter as ctk
from PIL import Image, ImageTk

"""
This solution is developed using Python, an object-oriented programming (OOP)
language, and utilises a range of its features across the interface, logic, and
data source layers.

--- EXPLANATION OF DATA TYPES, STRUCTURES, AND SOURCES (9-10 Level) ---

A range of data types, data structures, and data sources are used to efficiently and
accurately model the problem space.

[1] DATA TYPES
Explanation: The following data types were selected to ensure data integrity,
prevent errors, and perform accurate calculations.

* **`float` (Numeric)**: Used for `weight`, `height`, and macronutrient values.
    **Justification**: These measurements require decimal precision for accuracy. Storing weight as an `integer` would result in a loss of important data (e.g., 70.5kg vs 70kg), leading to inaccurate health calculations.

* **`int` (Numeric)**: Used for countable items like `age`, `likes`, `calories`, and `workoutsCompleted`.
    **Justification**: These values are discrete whole numbers. Using integers is memory-efficient and simplifies incrementing operations (`+= 1`).

* **`str` (Text)**: Used for identifiers (`studentId`), passwords, and user-generated content.
    **Justification**: This is the only appropriate type for formatted or unstructured text data. All data from CSVs is read as strings, requiring deliberate type conversion (`int()`) for calculations, demonstrating robust data handling.

* **`bool` (Boolean)**: Used for state flags like `_isAdmin`, `_isLocked`, and `approved`.
    **Justification**: Booleans provide a clear, memory-efficient (True/False) way to handle binary states, simplifying conditional logic (`if`, `else`) compared to using text.

* **`datetime`**: Used for post timestamps and weight history dates.
    **Justification**: Storing dates as `datetime` objects (or convertible ISO strings) is essential for accurate sorting and time-based calculations (e.g., in `getWeightProgressStats`).

[2] DATA STRUCTURES
Explanation: Data structures were chosen to effectively organise related data,
making it easier to access, manipulate, and store.

* **List of Dictionaries (2D Array/List of Records)**: This is the primary structure for data loaded from CSV files (e.g., `self.posts`).
    **Justification**: It represents a collection of records where each dictionary has named fields. This is superior to a simple list of lists because data is accessed by a descriptive key (e.g., `post['authorId']`) rather than a non-intuitive index, making code more readable and robust.

* **List of Tuples (1D Array of Records)**: Used in `_weightHistory` as a list of `(date, weight)` tuples.
    **Justification**: Tuples are immutable and memory-efficient, making them perfect for storing historical data points that should not be altered.

[3] DATA SOURCES
Explanation: External files are used to persist data between application sessions.

* **CSV (Delimited)**: Chosen as the primary data source for users, posts, etc.
    **Justification**: CSV files are human-readable, easily editable, and universally compatible. Python's `csv` module reads data directly into record-like dictionaries, ideal for this application's data.

* **TXT (Plain Text)**: Chosen for the `error_log.txt` file.
    **Justification**: TXT files are the simplest format for appending sequential log entries, requiring no special parsing for unstructured, chronological error logging.

--- APPLICATION OF OOP PRINCIPLES (9-10 Level) ---

The solution applies all relevant OOP principles to create a modular, maintainable,
and extensible application.

* **Encapsulation**: The `User` class bundles data (attributes like `_studentId`, `_goalWeight`) and methods that operate on that data (`getGoalWeight()`, `checkPassword()`). Attributes are protected (prefixed with `_`) to prevent direct external modification, enforcing access through defined methods.

* **Abstraction**: The `User` object hides complex internal calculations. For example, a programmer using the `User` class can call `user.calculateCalorieGoal()` without needing to know the details of the Mifflin-St Jeor equation implemented inside the method. This simplifies the use of the object.

* **Inheritance**: The `AdminUser` and `PremiumUser` classes inherit from the parent `User` class. They automatically receive all common attributes and methods (like `_studentId`, `checkPassword`) while adding their own specialized features (e.g., `AdminUser.canModerate()`).

* **Generalisation**: The `User` class serves as a generalisation for different types of registered users. It contains the common properties shared by `AdminUser` and `PremiumUser`. This "bottom-up" design principle reduces code duplication and creates a logical hierarchy.

--- USE OF FUNCTIONS, METHODS, AND ACCESS MODIFIERS (9-10 Level) ---

* **Functions and Methods**: All logic is encapsulated in functions (e.g., `readCsv`) or class methods (e.g., `user.toDict()`) to promote code reuse and modularity.
* **Access Modifiers**: Protected attributes (e.g., `_studentId`) are used throughout the classes to demonstrate the application of access modifiers as part of encapsulation.
* **Classes and Objects**: The entire application is structured around classes (`HealthyHabitsApp`, `User`, `AdminUser`, etc.) and their instantiated objects, demonstrating a deep use of OOP.
"""

# --- MyFitnessPal Inspired Color Palette ---
# Primary brand color, actions, progress
COLOR_PRIMARY_GREEN = "#68B043"   # A vibrant, healthy green
COLOR_PRIMARY_DARK_GREEN = "#4F8D31" # Darker green for hover/active states

# Secondary accent, calming tones
COLOR_SECONDARY_BLUE = "#36A9AE"  # A fresh teal/blue
COLOR_SECONDARY_DARK_BLUE = "#2B878A" # Darker teal/blue

# Neutrals for backgrounds, text, and UI elements
COLOR_WHITE_CLEAN = "#FFFFFF"     # Pure white for main backgrounds
COLOR_WIDGET_BG = "#d5d0c3"       # Slightly darker than white for widget backgrounds
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
POSTS_CSV = "posts.csv"
WORKOUT_PLANS_CSV = "workout_plans.csv" # For user-created plans
ERROR_LOG = "error_log.txt"
BACKUP_DIR = "backups"
ASSETS_DIR = "assets" # For icons

# --- Utility: CSV ---
def readCsv(filename):
    """
    Read CSV file into a list of dictionaries.
    AC6: Demonstrates file I/O, data structures (list/dict), error handling, and function encapsulation.
    JUSTIFICATION (List of Dictionaries): This structure represents a collection of
    records from the CSV. It is superior to a list of lists as it allows accessing
    data by a descriptive key (e.g., row['studentId']) rather than a numerical
    index, making the code more robust and readable.
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
        # JUSTIFICATION (float): goalWeight, height, and weight use float for decimal precision,
        # which is crucial for accurate health tracking.
        self._goalWeight = goalWeight
        self._goalType = goalType
        self._planType = planType
        self._isAdmin = isAdmin # JUSTIFICATION (bool): Boolean flags provide clear, memory-efficient state management (True/False).
        self._badges = badges if badges else []
        self._securityAnswer = securityAnswer
        self._loginAttempts = 0  # FR02: 3-attempt lockout
        self._isLocked = False   # FR02: Lockout state 
        self._age = int(age) if age is not None else None # JUSTIFICATION (int): Age is stored as an integer as decimal precision is not required.
        self._height = float(height) if height is not None else None
        self._weight = float(weight) if weight is not None else None
        self._gender = gender
        self._activityLevel = activityLevel
        self._caloriesConsumed = 0
        self._caloriesBurned = 0
        self._calorieGoal = self.calculateCalorieGoal()
        # Macro tracking attributes
        self._proteinConsumed = 0.0
        self._carbsConsumed = 0.0
        self._fatConsumed = 0.0
        # Macro goals (calculated based on calorie goal and user type)
        self._proteinGoal = self.calculateProteinGoal()
        self._carbsGoal = self.calculateCarbsGoal()
        self._fatGoal = self.calculateFatGoal()
        # New attributes for home page features
        self._weeklyGoal = 3 # Default weekly workout goal
        self._workoutsCompleted = 0 # Workouts completed this week
        # Weight tracking attributes
        self._weightHistory = []  # List of (date, weight) tuples
        self._manualGoals = False
        # Workout completion tracking
        self._lastWorkoutCompletion = None  # Last completed workout info
        # JUSTIFICATION (List of Tuples): _weightHistory uses a list of (date, weight) tuples.
        # Tuples are immutable and efficient for storing paired data points that should not change.

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
    def addWorkoutCompleted(self, workout_name=None):
        """Add a completed workout to the user's progress tracking.
        
        Args:
            workout_name (str, optional): Name of the specific workout completed.
        """
        self._workoutsCompleted += 1
        
        # Track last completion with timestamp and workout name
        from datetime import datetime
        self._lastWorkoutCompletion = {
            "name": workout_name or "Workout",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M")
        }
    def resetWorkoutsCompleted(self):
        self._workoutsCompleted = 0

    def getLastWorkoutCompletion(self):
        """Get information about the last completed workout."""
        return self._lastWorkoutCompletion

    def getWeightHistory(self):
        return self._weightHistory
    
    def addWeightEntry(self, weight, date_str=None):
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        # Remove any existing entry for the same date
        self._weightHistory = [(d, w) for d, w in self._weightHistory if d != date_str]
        # Add new entry
        self._weightHistory.append((date_str, float(weight)))
        # Keep only last 12 weeks of data
        if len(self._weightHistory) > 84:  # 12 weeks * 7 days
            self._weightHistory = self._weightHistory[-84:]
    
    def getCurrentWeight(self):
        if self._weightHistory:
            return self._weightHistory[-1][1]
        return self._weight
    
    def getWeightProgressStats(self):
        """Calculate comprehensive weight progress statistics."""
        if not self._weightHistory or len(self._weightHistory) < 2:
            return {
                "total_change": 0,
                "weekly_change": 0,
                "monthly_change": 0,
                "progress_percentage": 0,
                "days_tracking": 0,
                "trend": "No data",
                "velocity": 0,
                "projected_goal_date": None
            }
        
        # Sort history by date
        sorted_history = sorted(self._weightHistory, key=lambda x: x[0])
        current_weight = sorted_history[-1][1]
        starting_weight = sorted_history[0][1]
        goal_weight = float(self._goalWeight) if self._goalWeight else current_weight
        
        # Calculate total change
        # JUSTIFICATION (Logic of Signs): The sign of 'total_change' is critical.
        # It's calculated as (current - start), so a negative value indicates weight
        # loss, and a positive value indicates gain. This sign directly determines
        # the 'trend' ("Losing" or "Gaining"), providing logical, accurate feedback.
        total_change = current_weight - starting_weight
        
        # Calculate time-based changes
        from datetime import datetime, timedelta
        current_date = datetime.strptime(sorted_history[-1][0], "%Y-%m-%d")
        
        # Weekly change (last 7 days)
        week_ago = current_date - timedelta(days=7)
        weekly_weights = [w for d, w in sorted_history if datetime.strptime(d, "%Y-%m-%d") >= week_ago]
        weekly_change = weekly_weights[-1] - weekly_weights[0] if len(weekly_weights) >= 2 else 0
        
        # Monthly change (last 30 days)
        month_ago = current_date - timedelta(days=30)
        monthly_weights = [w for d, w in sorted_history if datetime.strptime(d, "%Y-%m-%d") >= month_ago]
        monthly_change = monthly_weights[-1] - monthly_weights[0] if len(monthly_weights) >= 2 else 0
        
        # Progress toward goal
        # JUSTIFICATION (Algorithmic Logic): This percentage formula correctly handles
        # both weight loss and gain goals.
        # - For a loss goal (e.g., 80 -> 70), the denominator is positive.
        # - For a gain goal (e.g., 70 -> 80), the denominator is negative, and as
        #   current_weight increases, the numerator also becomes negative, resulting
        #   in a correct, positive progress percentage.
        if goal_weight != starting_weight:
            progress_percentage = ((starting_weight - current_weight) / (starting_weight - goal_weight)) * 100
        else:
            progress_percentage = 100 if current_weight == goal_weight else 0
        
        # Days tracking
        start_date = datetime.strptime(sorted_history[0][0], "%Y-%m-%d")
        days_tracking = (current_date - start_date).days + 1
        
        # Trend analysis
        if abs(total_change) < 0.5:
            trend = "Stable"
        elif total_change > 0:
            trend = "Gaining"
        else:
            trend = "Losing"
        
        # Velocity (kg per week)
        weeks_tracking = max(days_tracking / 7, 1)
        velocity = total_change / weeks_tracking
        
        # Projected goal date
        projected_goal_date = None
        if velocity != 0 and goal_weight != current_weight:
            weeks_to_goal = (goal_weight - current_weight) / velocity
            if weeks_to_goal > 0:
                projected_date = current_date + timedelta(weeks=weeks_to_goal)
                projected_goal_date = projected_date.strftime("%Y-%m-%d")
        
        return {
            "total_change": total_change,
            "weekly_change": weekly_change,
            "monthly_change": monthly_change,
            "progress_percentage": progress_percentage,
            "days_tracking": days_tracking,
            "trend": trend,
            "velocity": velocity,
            "projected_goal_date": projected_goal_date
        }


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
        
    def getPosts(self):
        """Retrieve all posts made by this user."""
        all_posts = readCsv(POSTS_CSV)
        return [p for p in all_posts if p.get("authorId") == self._studentId]

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

    def calculateProteinGoal(self):
        """Calculate daily protein goal based on body weight and goal type."""
        if self._weight is None:
            return 150.0  # Default fallback
        
        if self._goalType == "Gain Muscle":
            # Higher protein for muscle gain: 2.0g per kg body weight
            return round(self._weight * 2.0, 1)
        elif self._goalType == "Lose Weight":
            # Moderate protein for weight loss: 1.6g per kg body weight
            return round(self._weight * 1.6, 1)
        else:
            # Standard protein for maintenance: 1.2g per kg body weight
            return round(self._weight * 1.2, 1)
    
    def calculateCarbsGoal(self):
        """Calculate daily carbs goal based on calorie goal and activity level."""
        cal_goal = self._calorieGoal
        if self._goalType == "Lose Weight":
            # Lower carbs for weight loss: 30% of calories
            return round((cal_goal * 0.30) / 4, 1)  # 4 cal per gram
        elif self._goalType == "Gain Muscle":
            # Higher carbs for muscle gain: 45% of calories
            return round((cal_goal * 0.45) / 4, 1)
        else:
            # Balanced carbs for maintenance: 40% of calories
            return round((cal_goal * 0.40) / 4, 1)
    
    def calculateFatGoal(self):
        """Calculate daily fat goal based on calorie goal."""
        cal_goal = self._calorieGoal
        # Fat should be 25-35% of total calories, using 30% as standard
        return round((cal_goal * 0.30) / 9, 1)  # 9 cal per gram

    # Macro tracking methods
    def addMacros(self, calories, protein=0, carbs=0, fat=0):
        """Add macronutrients to daily totals."""
        self._caloriesConsumed += calories
        self._proteinConsumed += protein
        self._carbsConsumed += carbs
        self._fatConsumed += fat
    
    def getMacroGoals(self):
        """Return dictionary of all macro goals."""
        return {
            "calories": self._calorieGoal,
            "protein": self._proteinGoal,
            "carbs": self._carbsGoal,
            "fat": self._fatGoal
        }
    
    def getMacroConsumed(self):
        """Return dictionary of all consumed macros."""
        return {
            "calories": self._caloriesConsumed,
            "protein": self._proteinConsumed,
            "carbs": self._carbsConsumed,
            "fat": self._fatConsumed
        }
    
    def getMacroProgress(self):
        """Return macro progress as percentages."""
        goals = self.getMacroGoals()
        consumed = self.getMacroConsumed()
        progress = {}
        
        for macro in goals:
            if goals[macro] > 0:
                progress[macro] = min((consumed[macro] / goals[macro]) * 100, 100)
            else:
                progress[macro] = 0
        
        return progress
    
    def resetDailyMacros(self):
        """Reset daily macro tracking (call at midnight or new day)."""
        self._caloriesConsumed = 0
        self._proteinConsumed = 0.0
        self._carbsConsumed = 0.0
        self._fatConsumed = 0.0

    def set_manual_goals(self, calorie_goal, protein_goal, carbs_goal, fat_goal):
        """Set macro goals manually, overriding automatic calculation."""
        self._calorieGoal = calorie_goal
        self._proteinGoal = protein_goal
        self._carbsGoal = carbs_goal
        self._fatGoal = fat_goal
        self._manualGoals = True

    def reset_to_automatic_goals(self):
        """Reset goals to be calculated automatically based on profile."""
        self._manualGoals = False
        self._calorieGoal = self.calculateCalorieGoal()
        self._proteinGoal = self.calculateProteinGoal()
        self._carbsGoal = self.calculateCarbsGoal()
        self._fatGoal = self.calculateFatGoal()

    def toDict(self):
        """
        Convert user to dictionary for CSV storage (AC6: data structures, file I/O).
        JUSTIFICATION (Dictionary): A dictionary is used to represent a single user
        record. This structure allows for clear, key-based access to fields (e.g.,
        user['studentId']), making the code more readable and easier to maintain than
        using indexed lists.
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
            "proteinConsumed": str(self._proteinConsumed),
            "carbsConsumed": str(self._carbsConsumed),
            "fatConsumed": str(self._fatConsumed),
            "proteinGoal": str(self._proteinGoal),
            "carbsGoal": str(self._carbsGoal),
            "fatGoal": str(self._fatGoal),
            "weeklyGoal": str(self._weeklyGoal),
            "workoutsCompleted": str(self._workoutsCompleted),
            "weightHistory": "|".join([f"{date}:{weight}" for date, weight in self._weightHistory]),
            "manualGoals": str(self._manualGoals),
            "lastWorkoutCompletion": json.dumps(self._lastWorkoutCompletion) if self._lastWorkoutCompletion else ""
        }
        return d

    @staticmethod
    def fromDict(d):
        """
        Create a User, AdminUser, or PremiumUser from a dictionary.
        AC6: This factory method shows how a general data record can be
        instantiated into different specialized classes. The User class
        serves as the GENERALISATION for all these user types.
        """
        is_admin_flag = (d.get("isAdmin", "False") == "True")
        is_premium_flag = (d.get("isPremium", "False") == "True") # New check for premium users

        # Common arguments dictionary to pass to the constructor
        user_args = {
            "studentId": d.get("studentId", ""),
            "password": d.get("password", ""),
            "goalWeight": d.get("goalWeight"),
            "goalType": d.get("goalType"),
            "planType": d.get("planType"),
            "isAdmin": is_admin_flag,
            "badges": d.get("badges", "").split("|") if d.get("badges") else [],
            "securityAnswer": d.get("securityAnswer", ""),
            "age": d.get("age"),
            "height": d.get("height"),
            "weight": d.get("weight"),
            "gender": d.get("gender"),
            "activityLevel": d.get("activityLevel")
        }

        # Instantiate the correct class based on flags from the CSV
        if is_admin_flag:
            user = AdminUser(**user_args)
        elif is_premium_flag:
            user = PremiumUser(**user_args)
        else:
            user = User(**user_args)

        # The rest of the attribute setting is common to all user types
        user._caloriesConsumed = int(d.get("caloriesConsumed", 0))
        user._caloriesBurned = int(d.get("caloriesBurned", 0))
        
        user._manualGoals = (d.get("manualGoals", "False") == "True")
        if user._manualGoals:
            user._calorieGoal = int(d.get("calorieGoal", 2000))
            user._proteinGoal = float(d.get("proteinGoal", 150))
            user._carbsGoal = float(d.get("carbsGoal", 200))
            user._fatGoal = float(d.get("fatGoal", 60))
        else:
            user.reset_to_automatic_goals()

        user._proteinConsumed = float(d.get("proteinConsumed", 0))
        user._carbsConsumed = float(d.get("carbsConsumed", 0))
        user._fatConsumed = float(d.get("fatConsumed", 0))
        user._weeklyGoal = int(d.get("weeklyGoal", 3))
        user._workoutsCompleted = int(d.get("workoutsCompleted", 0))
        
        last_workout_str = d.get("lastWorkoutCompletion", "")
        if last_workout_str:
            try:
                user._lastWorkoutCompletion = json.loads(last_workout_str)
            except:
                user._lastWorkoutCompletion = None
        else:
            user._lastWorkoutCompletion = None
        
        weight_history_str = d.get("weightHistory", "")
        if weight_history_str:
            try:
                weight_entries = weight_history_str.split("|")
                user._weightHistory = []
                for entry in weight_entries:
                    if ":" in entry:
                        date_str, weight_str = entry.split(":", 1)
                        user._weightHistory.append((date_str, float(weight_str)))
            except:
                user._weightHistory = []
        else:
            user._weightHistory = []
            
        return user
    
class AdminUser(User):
    """
    An AdminUser subclass that inherits from the base User class.
    AC6: Demonstrates the OOP principle of Inheritance.
    This class has all the functionality of a standard User, plus
    additional administrative privileges.
    """
    def __init__(self, *args, **kwargs):
        # Use super() to call the __init__ method of the parent User class.
        # This ensures all the standard user attributes are set up correctly.
        super().__init__(*args, **kwargs)
        
        # Override the _isAdmin flag specifically for this subclass.
        self._isAdmin = True

    def getAdminGreeting(self):
        """A sample method specific to the AdminUser subclass."""
        return f"Welcome, Administrator {self.getStudentId()}!"

    def canModerate(self):
        """
        A specific method for checking privileges. This is clearer than
        checking a boolean flag elsewhere in the code.
        """
        return True
    
class PremiumUser(User):
    """
    A PremiumUser subclass that inherits from User.
    This demonstrates how the User class acts as a generalisation
    for different, more specialized types of users.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isPremium = True

    def accessPremiumFeatures(self):
        """A sample method for premium-only features."""
        messagebox.showinfo("Premium Feature", "Welcome to your premium analytics dashboard!")

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
        "proteinConsumed", "carbsConsumed", "fatConsumed",
        "proteinGoal", "carbsGoal", "fatGoal",
        "weeklyGoal", "workoutsCompleted", "weightHistory", "manualGoals", "lastWorkoutCompletion"
    ])



# --- Existing code with updated docstrings ---
class HealthyHabitsApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Healthy Habits")
        self.root.geometry("1100x730")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.weather_api_key = "68e9c19dc9ac617b698f3c4d315fca9b" 
        self.currentUser = None
        self.posts = readCsv(POSTS_CSV)
        self.exercise_library = self.loadExerciseLibrary()
        self.navBar = None
        self.contentFrame = None
        self.toggle_btn = None
        self.menu_visible = False  # Start with menu closed
        
        self.showLoginSplit()
    def getWeatherData(self):
        """Fetches live weather data from OpenWeatherMap API."""
        if self.weather_api_key == "YOUR_API_KEY_HERE" or not self.weather_api_key:
            return {"error": "API key not set."}

        # Coordinates for Mount Waverley, VIC, AU
        lat, lon = -37.8833, 145.1500
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            
            # Extract and format the information we need
            weather_info = {
                "temp": f"{data['main']['temp']:.1f}°C",
                "feels_like": f"Feels like {data['main']['feels_like']:.1f}°C",
                "description": data['weather'][0]['description'].title(),
                "location": f"{data['name']}",
                "icon_code": data['weather'][0]['icon'],
                "error": None
            }
            return weather_info
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                return {"error": "Invalid API Key provided."}
            return {"error": f"Weather data not found (HTTP Error)."}
        except requests.exceptions.RequestException as req_err:
            logError(f"Weather API request failed: {req_err}")
            return {"error": "Could not connect to weather service."}
        except Exception as e:
            logError(f"An error occurred fetching weather data: {e}")
            return {"error": "An unknown error occurred."}
    def setThemeColors(self, mode):
        global COLOR_BG, COLOR_ACCENT, COLOR_ACCENT2, COLOR_TEXT, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BTN, COLOR_BTN_TXT, COLOR_WHITE, COLOR_WIDGET_BG
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
            COLOR_WIDGET_BG = "#424242"  # Darker widget background for dark mode
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
            COLOR_WIDGET_BG = "#F8F9FA"  # Light widget background for light mode
        # Re-render main navigation and current page to apply new colors
        if self.currentUser: # Only re-render if logged in
            self.showMainNav()
        else: # If on login/register, re-render that specific view
            self.showLoginSplit()
    def loadExerciseLibrary(self):
        """Loads a predefined list of exercises. This is a data source for the planner."""
        return [
            {"name": "Push-ups", "group": "Chest", "desc": "A classic bodyweight exercise for the chest, shoulders, and triceps."},
            {"name": "Bench Press", "group": "Chest", "desc": "A fundamental compound lift for building upper body strength, primarily targeting the chest."},
            {"name": "Dumbbell Flyes", "group": "Chest", "desc": "An isolation exercise that stretches and targets the pectoral muscles."},
            {"name": "Pull-ups", "group": "Back", "desc": "A challenging bodyweight exercise that builds a wide, strong back."},
            {"name": "Bent-Over Rows", "group": "Back", "desc": "A compound exercise that targets the entire back, improving posture and strength."},
            {"name": "Deadlifts", "group": "Back", "desc": "A full-body lift that heavily engages the back, legs, and core."},
            {"name": "Squats", "group": "Legs", "desc": "The king of leg exercises, targeting quads, hamstrings, and glutes."},
            {"name": "Lunges", "group": "Legs", "desc": "A unilateral exercise excellent for balance, stability, and leg strength."},
            {"name": "Leg Press", "group": "Legs", "desc": "A machine-based exercise to build powerful quadriceps."},
            {"name": "Overhead Press", "group": "Shoulders", "desc": "A key lift for developing strong, broad shoulders."},
            {"name": "Lateral Raises", "group": "Shoulders", "desc": "An isolation exercise to target the medial deltoid for shoulder width."},
            {"name": "Bicep Curls", "group": "Arms", "desc": "The classic exercise for building bicep peaks."},
            {"name": "Tricep Dips", "group": "Arms", "desc": "A bodyweight or weighted exercise to build strong triceps."},
            {"name": "Plank", "group": "Core", "desc": "An isometric exercise to build core stability and endurance."},
            {"name": "Crunches", "group": "Core", "desc": "A basic but effective exercise for targeting the abdominal muscles."},
        ]
    def _openExerciseLibraryDialog(self, add_exercise_callback):
        """Opens a pop-up dialog to select exercises."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Exercise Library")
        dialog.geometry("500x700")
        dialog.transient(self.root) # Keep dialog on top
        
        ctk.CTkLabel(dialog, text="Exercise Library", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        library_scroll_frame = ctk.CTkScrollableFrame(dialog)
        library_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        for exercise in self.exercise_library:
            ex_frame = ctk.CTkFrame(library_scroll_frame)
            ex_frame.pack(fill="x", pady=4, padx=4)
            ctk.CTkLabel(ex_frame, text=f"{exercise['name']} ({exercise['group']})", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5,0))
            ctk.CTkLabel(ex_frame, text=exercise['desc'], wraplength=400, justify="left", text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(0,5))
            ctk.CTkButton(ex_frame, text="Add", width=50, command=lambda e=exercise: self._getSetsRepsAndAdd(e, add_exercise_callback, dialog)).pack(side="right", padx=10, pady=5)

    def _getSetsRepsAndAdd(self, exercise, add_exercise_callback, parent_dialog):
        """Opens a second small dialog to get sets/reps, then calls the callback."""
        sets_reps_dialog = ctk.CTkToplevel(self.root)
        sets_reps_dialog.title("Sets & Reps")
        sets_reps_dialog.geometry("300x200")
        sets_reps_dialog.transient(parent_dialog)

        ctk.CTkLabel(sets_reps_dialog, text=f"Adding: {exercise['name']}", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(sets_reps_dialog, text="Sets:").pack()
        sets_entry = ctk.CTkEntry(sets_reps_dialog, placeholder_text="e.g., 3")
        sets_entry.pack()

        ctk.CTkLabel(sets_reps_dialog, text="Reps:").pack()
        reps_entry = ctk.CTkEntry(sets_reps_dialog, placeholder_text="e.g., 8-12")
        reps_entry.pack()

        def confirm_add():
            sets = sets_entry.get().strip()
            reps = reps_entry.get().strip()
            if sets and reps:
                add_exercise_callback(exercise, sets, reps)
                sets_reps_dialog.destroy()
            else:
                messagebox.showwarning("Input Error", "Please enter both sets and reps.", parent=sets_reps_dialog)
        
        ctk.CTkButton(sets_reps_dialog, text="Confirm", command=confirm_add).pack(pady=10)

    def _drawPlannerHome(self, container):
        """Draws the main view of the planner widget."""
        for w in container.winfo_children(): w.destroy()

        # Current progress display
        user = self.currentUser
        progress_frame = ctk.CTkFrame(container, fg_color=COLOR_ACCENT2, corner_radius=8)
        progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        progress_frame.grid_columnconfigure(0, weight=1)
        progress_frame.grid_columnconfigure(1, weight=1)
        progress_frame.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(progress_frame, text="📊 Weekly Progress", font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=COLOR_PRIMARY).grid(row=0, column=0, columnspan=3, pady=(8, 2))
        
        # Progress stats
        completed = user.getWorkoutsCompleted()
        goal = user.getWeeklyGoal()
        progress_pct = (completed / goal * 100) if goal > 0 else 0
        
        ctk.CTkLabel(progress_frame, text=f"Completed: {completed}", font=ctk.CTkFont(size=12), 
                    text_color=COLOR_TEXT).grid(row=1, column=0, padx=5, pady=2)
        ctk.CTkLabel(progress_frame, text=f"Goal: {goal}", font=ctk.CTkFont(size=12), 
                    text_color=COLOR_TEXT).grid(row=1, column=1, padx=5, pady=2)
        ctk.CTkLabel(progress_frame, text=f"Progress: {progress_pct:.1f}%", font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color=COLOR_PRIMARY_GREEN if progress_pct >= 100 else COLOR_SECONDARY_BLUE).grid(row=1, column=2, padx=5, pady=2)
        
        # Mini progress bar
        mini_progress = ctk.CTkProgressBar(progress_frame, width=200, height=8, progress_color=COLOR_PRIMARY_GREEN)
        mini_progress.grid(row=2, column=0, columnspan=3, pady=(2, 8), padx=10, sticky="ew")
        mini_progress.set(min(progress_pct / 100, 1.0))

        # Last completed workout info
        last_workout = user.getLastWorkoutCompletion()
        if last_workout:
            last_workout_frame = ctk.CTkFrame(container, fg_color=COLOR_ACCENT2, corner_radius=8)
            last_workout_frame.pack(fill="x", padx=10, pady=(0, 10))
            ctk.CTkLabel(last_workout_frame, text=f"🏆 Last completed: {last_workout['name']} on {last_workout['date']} at {last_workout['time']}", 
                        text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(pady=6)

        ctk.CTkLabel(container, text="Select a plan to view or create a new one.", text_color=COLOR_TEXT_SECONDARY).pack(pady=(10, 10))
        
        user_plans = self.getUserWorkoutPlans()
        plan_names = [p['plan_name'] for p in user_plans]
        
        if not user_plans:
            no_plans_frame = ctk.CTkFrame(container, fg_color=COLOR_ACCENT, corner_radius=8)
            no_plans_frame.pack(fill="x", padx=10, pady=10)
            ctk.CTkLabel(no_plans_frame, text="🏃‍♀️ No workout plans created yet!", font=ctk.CTkFont(size=14, weight="bold"), 
                        text_color=COLOR_TEXT).pack(pady=(10, 5))
            ctk.CTkLabel(no_plans_frame, text="Create your first plan to start tracking workouts!", 
                        text_color=COLOR_TEXT_SECONDARY).pack(pady=(0, 10))
        else:
            plan_var = ctk.StringVar(value="Select a plan...")
            plan_menu = ctk.CTkOptionMenu(container, variable=plan_var, values=plan_names, 
                                          command=lambda name: self._drawPlanView(container, name, user_plans))
            plan_menu.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(container, text="➕ Create a New Plan", command=lambda: self._drawPlanCreator(container)).pack(pady=10, padx=20, fill="x")

    def _drawPlanView(self, container, plan_name, user_plans):
        """Draws the details of a selected plan in the widget."""
        for w in container.winfo_children(): w.destroy()
        
        selected_plan = next((p for p in user_plans if p['plan_name'] == plan_name), None)
        if not selected_plan:
            self._drawPlannerHome(container)
            return

        ctk.CTkLabel(container, text=selected_plan['plan_name'], font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Add completion status info
        completion_frame = ctk.CTkFrame(container, fg_color=COLOR_ACCENT, corner_radius=8)
        completion_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        completion_frame.grid_columnconfigure(0, weight=1)
        completion_frame.grid_columnconfigure(1, weight=0)
        
        ctk.CTkLabel(completion_frame, text="✅ Complete this workout to log progress on your home dashboard", 
                    text_color=COLOR_TEXT, font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=(10, 5), pady=8)
        
        # Quick navigation to home
        def go_to_home():
            self.activePage = "home"
            self.updateNavHighlight()
            self.showPage("home")
        
        ctk.CTkButton(completion_frame, text="🏠 View Progress", width=100, height=28, 
                     fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, 
                     command=go_to_home).grid(row=0, column=1, padx=(5, 10), pady=4)
        
        exercises_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        exercises_frame.pack(fill="both", expand=True, padx=10)

        for exercise in selected_plan['exercises']:
            ex_frame = ctk.CTkFrame(exercises_frame)
            ex_frame.pack(fill="x", pady=4)
            ctk.CTkLabel(ex_frame, text=f"{exercise['name']} | Sets: {exercise['sets']}, Reps: {exercise['reps']}").pack(anchor="w", padx=15, pady=8)

        def complete_workout():
            """Log the completed workout to the home progress tracker."""
            # Add workout completion to user's tracking
            user = self.currentUser
            user.addWorkoutCompleted(workout_name=plan_name)
            
            # Auto-adjust goal if user exceeds their weekly goal
            if user.getWorkoutsCompleted() > user.getWeeklyGoal():
                user.setWeeklyGoal(user.getWorkoutsCompleted())
            
            saveUser(user)
            
            # Show success message with plan name
            messagebox.showinfo("Workout Completed! 🎉", 
                              f"Great job! You completed '{plan_name}'.\n\n"
                              f"✅ Progress logged to home dashboard\n"
                              f"📊 Weekly progress: {user.getWorkoutsCompleted()}/{user.getWeeklyGoal()}\n\n"
                              f"Keep up the great work!")
            
            # Refresh the planner view to show updated completion status
            self._drawPlanView(container, plan_name, self.getUserWorkoutPlans())

        def delete_plan():
            if messagebox.askyesno("Delete Plan", f"Are you sure you want to delete '{plan_name}'?"):
                self.deleteWorkoutPlan(plan_name)
                self._drawPlannerHome(container)

        bottom_frame = ctk.CTkFrame(container, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_columnconfigure(2, weight=1)
        
        ctk.CTkButton(bottom_frame, text="← Back to Home", command=lambda: self._drawPlannerHome(container)).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(bottom_frame, text="🏁 Complete Workout", fg_color=COLOR_PRIMARY_GREEN, hover_color="#2E7D32", 
                     text_color=COLOR_BTN_TXT, command=complete_workout).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(bottom_frame, text="🗑️ Delete Plan", fg_color="#E57373", hover_color="#C06161", 
                     command=delete_plan).grid(row=0, column=2, padx=5, sticky="ew")


    def _drawPlanCreator(self, container):
        """Draws the UI for creating a new workout plan."""
        for w in container.winfo_children(): w.destroy()

        ctk.CTkLabel(container, text="Create a New Plan", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        name_entry = ctk.CTkEntry(container, placeholder_text="Enter Plan Name")
        name_entry.pack(fill="x", padx=20, pady=5)
        
        current_plan_exercises = []
        
        plan_display_frame = ctk.CTkScrollableFrame(container, label_text="Exercises in this Plan", height=200)
        plan_display_frame.pack(fill="x", expand=True, padx=20, pady=10)

        def redraw_plan_creator():
            for w in plan_display_frame.winfo_children(): w.destroy()
            if not current_plan_exercises:
                ctk.CTkLabel(plan_display_frame, text="No exercises added yet.", text_color=COLOR_TEXT_SECONDARY).pack()
            else:
                for ex in current_plan_exercises:
                    ctk.CTkLabel(plan_display_frame, text=f"• {ex['name']} ({ex['sets']} sets of {ex['reps']} reps)").pack(anchor="w", padx=5)

        def add_exercise_to_list(exercise, sets, reps):
            current_plan_exercises.append({"name": exercise['name'], "sets": sets, "reps": reps})
            redraw_plan_creator()

        def final_save_plan():
            plan_name = name_entry.get().strip()
            if not plan_name:
                messagebox.showwarning("Input Error", "Please enter a name for your plan.")
                return
            if not current_plan_exercises:
                messagebox.showwarning("Empty Plan", "Please add at least one exercise.")
                return
            
            new_plan = {"plan_name": plan_name, "exercises": current_plan_exercises}
            self.saveWorkoutPlan(new_plan)
            messagebox.showinfo("Success", f"Plan '{plan_name}' saved!")
            self._drawPlannerHome(container)

        redraw_plan_creator()
        
        bottom_frame = ctk.CTkFrame(container, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=10)
        ctk.CTkButton(bottom_frame, text="Add Exercise from Library", command=lambda: self._openExerciseLibraryDialog(add_exercise_to_list)).pack(side="left", padx=10)
        ctk.CTkButton(bottom_frame, text="Save Plan", command=final_save_plan, fg_color=COLOR_PRIMARY_GREEN).pack(side="right", padx=10)
        ctk.CTkButton(bottom_frame, text="Cancel", command=lambda: self._drawPlannerHome(container)).pack(side="right", padx=10)

    def showWorkoutPlannerHub(self, sub_page=None, plan_to_view=None):
        """Display workout planning hub."""
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()

        if sub_page == "create_plan":
            self._showCreatePlanPage(cf)
        elif sub_page == "view_plan" and plan_to_view:
            self._showViewPlanPage(cf, plan_to_view)
        elif sub_page == "exercise_library":
            self._showExerciseLibraryPage(cf)
        else:
            self._showWorkoutMainPage(cf)

    def _showWorkoutMainPage(self, cf):
        """Main menu for the workout section."""
        ctk.CTkLabel(cf, text="Workout Planner", font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(20, 10))
        ctk.CTkLabel(cf, text="Manage your plans, discover new exercises, and track your progress.", text_color=COLOR_TEXT_SECONDARY).pack(pady=(0, 20))

        # --- My Plans Section ---
        plans_card = ctk.CTkFrame(cf, fg_color=COLOR_WIDGET_BG, corner_radius=12)
        plans_card.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(plans_card, text="My Workout Plans", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=10)
        
        plans_scroll_frame = ctk.CTkScrollableFrame(plans_card, fg_color="transparent", height=200)
        plans_scroll_frame.pack(fill="x", padx=10, pady=(0, 10))

        user_plans = self.getUserWorkoutPlans()
        if not user_plans:
            ctk.CTkLabel(plans_scroll_frame, text="You haven't created any plans yet.", text_color=COLOR_TEXT_SECONDARY).pack(pady=20)
        else:
            for plan in user_plans:
                plan_frame = ctk.CTkFrame(plans_scroll_frame, fg_color=COLOR_ACCENT, corner_radius=8)
                plan_frame.pack(fill="x", pady=5)
                ctk.CTkLabel(plan_frame, text=plan['plan_name'], font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=15, pady=10)
                ctk.CTkButton(plan_frame, text="View", command=lambda p=plan: self.showWorkoutPlannerHub(sub_page="view_plan", plan_to_view=p)).pack(side="right", padx=15, pady=10)

        # --- Action Buttons ---
        action_frame = ctk.CTkFrame(cf, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)
        action_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(action_frame, text="➕ Create a New Plan", height=40, font=ctk.CTkFont(size=16), command=lambda: self.showWorkoutPlannerHub(sub_page="create_plan")).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(action_frame, text="📚 Exercise Library", height=40, font=ctk.CTkFont(size=16), command=lambda: self.showWorkoutPlannerHub(sub_page="exercise_library")).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(cf, text="Back to Main Workout Page", command=self.showWorkouts).pack(pady=15)

    def _showCreatePlanPage(self, cf, plan_type=None, plan_name=None):
        """Page for creating a new workout plan."""
        for w in cf.winfo_children(): w.destroy()
        
        if not plan_type:
            ctk.CTkLabel(cf, text="Create a New Workout Plan", font=ctk.CTkFont(size=24, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=20)
            ctk.CTkButton(cf, text="Get a Suggested Plan", command=lambda: self._showCreatePlanPage(cf, plan_type="suggested")).pack(pady=10)
            ctk.CTkButton(cf, text="Make My Own Plan", command=lambda: self._showCreatePlanPage(cf, plan_type="custom")).pack(pady=10)
            ctk.CTkButton(cf, text="Back", command=self.showWorkoutPlannerHub).pack(pady=20)
            return

        if plan_type == "suggested":
            plan = {
                "plan_name": "Full Body Beginner",
                "exercises": [
                    {"name": "Squats", "sets": "3", "reps": "8-12"},
                    {"name": "Push-ups", "sets": "3", "reps": "As many as possible"},
                    {"name": "Bent-Over Rows", "sets": "3", "reps": "8-12"},
                    {"name": "Plank", "sets": "3", "reps": "30-60 seconds"}
                ]
            }
            self.saveWorkoutPlan(plan)
            messagebox.showinfo("Plan Created", f"'{plan['plan_name']}' has been added to your plans.")
            self.showWorkoutPlannerHub()
            return
            
        if plan_type == "custom":
            if not plan_name:
                name_frame = ctk.CTkFrame(cf, fg_color="transparent")
                name_frame.pack(pady=20)
                ctk.CTkLabel(name_frame, text="Enter a name for your new plan:").pack()
                name_entry = ctk.CTkEntry(name_frame, width=300)
                name_entry.pack(pady=5)
                ctk.CTkButton(name_frame, text="Next", command=lambda: self._showCreatePlanPage(cf, plan_type="custom", plan_name=name_entry.get())).pack(pady=10)
                ctk.CTkButton(name_frame, text="Back", command=self.showWorkoutPlannerHub).pack()
                return

            ctk.CTkLabel(cf, text=f"Building Plan: {plan_name}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
            
            creator_frame = ctk.CTkFrame(cf, fg_color="transparent")
            creator_frame.pack(fill="both", expand=True, padx=20)
            creator_frame.grid_columnconfigure(0, weight=1)
            creator_frame.grid_columnconfigure(1, weight=2)
            creator_frame.grid_rowconfigure(0, weight=1)

            library_frame = ctk.CTkFrame(creator_frame, fg_color=COLOR_WIDGET_BG)
            library_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            ctk.CTkLabel(library_frame, text="Exercise Library").pack(pady=5)
            library_scroll = ctk.CTkScrollableFrame(library_frame, fg_color="transparent")
            library_scroll.pack(fill="both", expand=True, padx=5)

            plan_frame = ctk.CTkFrame(creator_frame, fg_color=COLOR_WIDGET_BG)
            plan_frame.grid(row=0, column=1, sticky="nsew")
            ctk.CTkLabel(plan_frame, text="Current Plan").pack(pady=5)
            plan_scroll = ctk.CTkScrollableFrame(plan_frame, fg_color="transparent")
            plan_scroll.pack(fill="both", expand=True, padx=5)

            current_plan_exercises = []

            def redraw_plan():
                for w in plan_scroll.winfo_children(): w.destroy()
                for i, ex in enumerate(current_plan_exercises):
                    ex_frame = ctk.CTkFrame(plan_scroll, fg_color=COLOR_ACCENT)
                    ex_frame.pack(fill="x", pady=2)
                    ctk.CTkLabel(ex_frame, text=f"{ex['name']} | Sets: {ex['sets']}, Reps: {ex['reps']}").pack(side="left", padx=10)
                    ctk.CTkButton(ex_frame, text="Remove", width=60, command=lambda i=i: remove_exercise(i)).pack(side="right", padx=10)

            def remove_exercise(index):
                current_plan_exercises.pop(index)
                redraw_plan()

            def add_exercise(exercise):
                dialog = ctk.CTkToplevel(self.root)
                dialog.title("Add Exercise")
                dialog.geometry("300x200")
                ctk.CTkLabel(dialog, text=f"Adding: {exercise['name']}").pack(pady=10)
                ctk.CTkLabel(dialog, text="Sets:").pack()
                sets_entry = ctk.CTkEntry(dialog)
                sets_entry.pack()
                ctk.CTkLabel(dialog, text="Reps:").pack()
                reps_entry = ctk.CTkEntry(dialog)
                reps_entry.pack()
                def confirm_add():
                    sets = sets_entry.get().strip()
                    reps = reps_entry.get().strip()
                    if sets and reps:
                        current_plan_exercises.append({"name": exercise['name'], "sets": sets, "reps": reps})
                        redraw_plan()
                        dialog.destroy()
                    else:
                        messagebox.showwarning("Input Error", "Please enter sets and reps.")
                ctk.CTkButton(dialog, text="Add", command=confirm_add).pack(pady=10)

            for ex in self.exercise_library:
                lib_ex_frame = ctk.CTkFrame(library_scroll, fg_color=COLOR_ACCENT)
                lib_ex_frame.pack(fill="x", pady=2)
                ctk.CTkLabel(lib_ex_frame, text=ex['name']).pack(side="left", padx=10)
                ctk.CTkButton(lib_ex_frame, text="Add", width=50, command=lambda e=ex: add_exercise(e)).pack(side="right", padx=10)

            def final_save_plan():
                if not current_plan_exercises:
                    messagebox.showwarning("Empty Plan", "Add at least one exercise to your plan.")
                    return
                
                new_plan = {"plan_name": plan_name, "exercises": current_plan_exercises}
                self.saveWorkoutPlan(new_plan)
                messagebox.showinfo("Success", f"Plan '{plan_name}' saved!")
                self.showWorkoutPlannerHub()
            
            save_button = ctk.CTkButton(cf, text="Save Plan", command=final_save_plan)
            save_button.pack(pady=10)

    def _showViewPlanPage(self, cf, plan):
        """Displays the details of a selected workout plan."""
        ctk.CTkLabel(cf, text=plan['plan_name'], font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        exercises_frame = ctk.CTkScrollableFrame(cf, fg_color="transparent")
        exercises_frame.pack(fill="both", expand=True, padx=20)

        for exercise in plan['exercises']:
            ex_frame = ctk.CTkFrame(exercises_frame, fg_color=COLOR_WIDGET_BG, corner_radius=8)
            ex_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(ex_frame, text=exercise['name'], font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(5,0))
            ctk.CTkLabel(ex_frame, text=f"Sets: {exercise['sets']} | Reps: {exercise['reps']}", text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", padx=15, pady=(0,5))
            
        ctk.CTkButton(cf, text="Back to Planner", command=self.showWorkoutPlannerHub).pack(pady=15)

    def _showExerciseLibraryPage(self, cf):
        """Displays the filterable exercise library."""
        ctk.CTkLabel(cf, text="Exercise Library", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        filter_frame = ctk.CTkFrame(cf, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(filter_frame, text="Filter by muscle group:").pack(side="left")
        
        muscle_groups = ["All"] + sorted(list(set(ex['group'] for ex in self.exercise_library)))
        filter_var = ctk.StringVar(value="All")
        
        library_scroll_frame = ctk.CTkScrollableFrame(cf)
        library_scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        def apply_filter(*args):
            for w in library_scroll_frame.winfo_children(): w.destroy()
            group = filter_var.get()
            filtered_list = self.exercise_library if group == "All" else [ex for ex in self.exercise_library if ex['group'] == group]
            
            for exercise in filtered_list:
                ex_frame = ctk.CTkFrame(library_scroll_frame, fg_color=COLOR_WIDGET_BG, corner_radius=8)
                ex_frame.pack(fill="x", pady=5)
                ctk.CTkLabel(ex_frame, text=f"{exercise['name']} ({exercise['group']})", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(5,0))
                ctk.CTkLabel(ex_frame, text=exercise['desc'], wraplength=800, text_color=COLOR_TEXT_SECONDARY, justify="left").pack(anchor="w", padx=15, pady=(0,5))
        
        filter_menu = ctk.CTkOptionMenu(filter_frame, variable=filter_var, values=muscle_groups, command=apply_filter)
        filter_menu.pack(side="left", padx=10)
        
        apply_filter()
        ctk.CTkButton(cf, text="Back to Planner", command=self.showWorkoutPlannerHub).pack(pady=15)

    def getUserWorkoutPlans(self):
        """Gets all workout plans for the current user."""
        all_plans = readCsv(WORKOUT_PLANS_CSV)
        user_plans = []
        for plan in all_plans:
            if plan.get('user_id') == self.currentUser.getStudentId():
                try:
                    plan['exercises'] = json.loads(plan['exercises'])
                    user_plans.append(plan)
                except json.JSONDecodeError:
                    logError(f"Could not parse exercises for plan: {plan.get('plan_name')}")
        return user_plans

    def saveWorkoutPlan(self, plan_data):
        """Saves a new or updated workout plan for the user."""
        all_plans = readCsv(WORKOUT_PLANS_CSV)
        
        plan_to_save = {
            "user_id": self.currentUser.getStudentId(),
            "plan_name": plan_data['plan_name'],
            "exercises": json.dumps(plan_data['exercises'])
        }

        plan_exists = False
        for i, existing_plan in enumerate(all_plans):
            if existing_plan.get('user_id') == plan_to_save['user_id'] and existing_plan.get('plan_name') == plan_to_save['plan_name']:
                all_plans[i] = plan_to_save
                plan_exists = True
                break
        
        if not plan_exists:
            all_plans.append(plan_to_save)

        writeCsv(WORKOUT_PLANS_CSV, all_plans, ["user_id", "plan_name", "exercises"])
    def showLoginSplit(self):
        """Display split login/register UI with content on left, image on right."""
        for w in self.root.winfo_children():
            w.destroy()
        splitFrame = ctk.CTkFrame(self.root, fg_color=COLOR_BG)
        splitFrame.pack(fill="both", expand=True)
        splitFrame.grid_columnconfigure(0, weight=1)  # Left side (content) - smaller
        splitFrame.grid_columnconfigure(1, weight=2)  # Right side (image) - much larger
        splitFrame.grid_rowconfigure(0, weight=1)
        
        # Left: Login/Register Card
        left = ctk.CTkFrame(splitFrame, fg_color=COLOR_WHITE_CLEAN, corner_radius=18,
                           border_width=1, border_color=COLOR_MEDIUM_GREY)
        left.grid(row=0, column=0, sticky="nsew", padx=40, pady=60)
        self._showLoginCard(left)
        
        # Right: Image/branding
        right = ctk.CTkFrame(splitFrame, fg_color=COLOR_BG, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        try:
            img = Image.open("fitness.png")
            # Calculate frame dimensions (right side is larger)
            total_width = 1100
            left_width = int(total_width * 1/3)  # 1 part out of 3
            right_width = int(total_width * 2/3)  # 2 parts out of 3
            frame_height = 730
            
            # Resize image to fill the entire right frame, stretching if necessary
            img = img.resize((1200, frame_height), Image.LANCZOS)
            tkimg = ImageTk.PhotoImage(img)
            imgLabel = ctk.CTkLabel(right, image=tkimg, text="")
            imgLabel.image = tkimg
            imgLabel.place(x=0, y=0, relwidth=1.8, relheight=1)  # Fill entire frame
        except Exception:
            ctk.CTkLabel(right, text="Healthy Habits App", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).place(relx=0.5, rely=0.5, anchor="center")

    def _showLoginCard(self, parent):
        """Display login card with password reset (FR22)."""
        for w in parent.winfo_children():
            w.destroy()
        
        # Create main container for centered content
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=30)
        
        ctk.CTkLabel(container, text="Welcome Back!", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(0, 30))
        
        # Student ID field with aligned label and entry
        id_frame = ctk.CTkFrame(container, fg_color="transparent")
        id_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(id_frame, text="Student ID", text_color=COLOR_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        usernameEntry = ctk.CTkEntry(id_frame, width=280, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8,
                                     placeholder_text="Enter your ID")
        usernameEntry.pack(fill="x")
        
        # Password field with aligned label and entry
        pw_frame = ctk.CTkFrame(container, fg_color="transparent")
        pw_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(pw_frame, text="Password", text_color=COLOR_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        passwordEntry = ctk.CTkEntry(pw_frame, width=280, show="*", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8,
                                     placeholder_text="Enter your password")
        passwordEntry.pack(fill="x")

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

        # Button container for consistent spacing
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(button_frame, text="Login", width=280, fg_color=COLOR_PRIMARY, text_color=COLOR_BTN_TXT, corner_radius=8, command=doLogin).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(button_frame, text="Register", width=280, fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: self._showRegisterCard(parent)).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(button_frame, text="Forgot Password?", width=280, fg_color="transparent", text_color=COLOR_TEXT_SECONDARY, hover_color=COLOR_LIGHT_GREY, corner_radius=8, command=lambda: self._showResetCard(parent)).pack(fill="x", pady=(0, 15))
        # Developer Skip button for easy testing
        ctk.CTkButton(button_frame, text="Developer Skip (Also is admin)", width=280, fg_color=COLOR_MEDIUM_GREY, text_color=COLOR_TEXT_PRIMARY, corner_radius=8, command=self._devSkip).pack(fill="x", pady=(10, 0))


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
            # Create container for each field
            field_container = ctk.CTkFrame(s_frame, fg_color="transparent")
            field_container.pack(fill="x", pady=(0, 15), padx=20)
            
            ctk.CTkLabel(field_container, text=label_text, text_color=COLOR_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
            if is_dropdown:
                var = ctk.StringVar(value=dropdown_values[0] if dropdown_values else "")
                option_menu = ctk.CTkOptionMenu(field_container, variable=var, values=dropdown_values, width=250, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, button_color=COLOR_PRIMARY)
                option_menu.pack(fill="x")
                return var, option_menu # Return both variable and widget
            else:
                entry = ctk.CTkEntry(field_container, width=250, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8,
                                     placeholder_text=entry_placeholder, show=entry_show)
                entry.pack(fill="x")
                return entry

        entryId = create_entry_row(scrollFrame, "Student ID (AAA####)", "e.g., ABC1234")
        entryPw = create_entry_row(scrollFrame, "Password", "min 4 characters", "*")
        entrySec = create_entry_row(scrollFrame, "Security Answer (for reset)", "e.g., Your pet's name")
        entryAge = create_entry_row(scrollFrame, "Age (years)", "e.g., 20")
        entryHeight = create_entry_row(scrollFrame, "Height (cm)", "e.g., 175.5")
        entryWeight = create_entry_row(scrollFrame, "Weight (kg)", "e.g., 70.2")

        ctk.CTkLabel(scrollFrame, text="Gender", text_color=COLOR_TEXT).pack(anchor="w", padx=20, pady=(8, 2))
        # Create container for gender radio buttons
        gender_container = ctk.CTkFrame(scrollFrame, fg_color="transparent")
        gender_container.pack(fill="x", pady=(0, 15), padx=20)
        
        genderVar = ctk.StringVar(value="Male")
        ctk.CTkRadioButton(gender_container, text="Male", variable=genderVar, value="Male", text_color=COLOR_TEXT, fg_color=COLOR_PRIMARY).pack(anchor="w", padx=10, pady=2)
        ctk.CTkRadioButton(gender_container, text="Female", variable=genderVar, value="Female", text_color=COLOR_TEXT, fg_color=COLOR_PRIMARY).pack(anchor="w", padx=10, pady=2)

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
            
        # Create main container for centered content
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=30)
        
        ctk.CTkLabel(container, text="Reset Password", font=ctk.CTkFont(size=22, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(0, 30))
        
        # Student ID field with aligned label and entry
        sid_frame = ctk.CTkFrame(container, fg_color="transparent")
        sid_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(sid_frame, text="Student ID", text_color=COLOR_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        sidEntry = ctk.CTkEntry(sid_frame, width=280, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="Your Student ID")
        sidEntry.pack(fill="x")
        
        # Security Answer field with aligned label and entry
        sec_frame = ctk.CTkFrame(container, fg_color="transparent")
        sec_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(sec_frame, text="Security Answer", text_color=COLOR_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        secEntry = ctk.CTkEntry(sec_frame, width=280, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="Your Security Answer")
        secEntry.pack(fill="x")
        
        # New Password field with aligned label and entry
        pw_frame = ctk.CTkFrame(container, fg_color="transparent")
        pw_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(pw_frame, text="New Password", text_color=COLOR_TEXT, anchor="w").pack(fill="x", pady=(0, 5))
        pwEntry = ctk.CTkEntry(pw_frame, width=280, show="*", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8, placeholder_text="New Password (min 4 chars)")
        pwEntry.pack(fill="x")

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

        # Button container for consistent spacing
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(button_frame, text="Reset Password", width=280, fg_color=COLOR_PRIMARY, text_color=COLOR_BTN_TXT, corner_radius=8, command=doReset).pack(fill="x", pady=(0, 10))
        ctk.CTkButton(button_frame, text="Back to Login", width=280, fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: self._showLoginCard(parent)).pack(fill="x")

    def _devSkip(self):
        """Skip to main nav for development (temporary)."""
        # Create a dummy ADMIN user for dev skip.
        # This now instantiates the AdminUser class directly so that
        # all admin checks (`isinstance(..., AdminUser)`) will pass.
        self.currentUser = AdminUser(
            "DEVSKIP", "dev", goalWeight="70", goalType="Maintain Health",
            planType="Balanced", isAdmin=True, securityAnswer="test",
            age="30", height="175", weight="70", gender="Male", activityLevel="Moderately Active"
        )
        self.showMainNav()
    def _openEditGoalDialog(self):
        """Opens a pop-up dialog to edit the user's goal weight."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Goal Weight")
        dialog.geometry("300x180")
        dialog.transient(self.root) # Keep dialog on top
        dialog.grab_set() # Modal - block interaction with the main window

        ctk.CTkLabel(dialog, text="Set New Goal Weight (kg)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        goal_entry = ctk.CTkEntry(dialog, placeholder_text="e.g., 72.5")
        goal_entry.insert(0, str(self.currentUser.getGoalWeight()))
        goal_entry.pack(pady=5, padx=20, fill="x")

        def save_new_goal():
            new_weight_str = goal_entry.get().strip()
            
            # Use the existing validation function
            is_valid, message = validateInput("goalWeight", new_weight_str)
            
            if not is_valid:
                messagebox.showwarning("Invalid Input", message, parent=dialog)
                return

            # If valid, update the user object
            self.currentUser._goalWeight = float(new_weight_str)
            saveUser(self.currentUser)
            
            messagebox.showinfo("Success", "Your goal weight has been updated!")
            dialog.destroy()
            self.showWorkouts() # Refresh the workouts page to show the new goal

        save_button = ctk.CTkButton(dialog, text="Save Goal", command=save_new_goal, fg_color=COLOR_PRIMARY_GREEN)
        save_button.pack(pady=(15, 10))
    # --- Main navigation & placeholders (AC7/SRS) ---
    def showMainNav(self):
        """Display main navigation bar and content with a slidable menu."""
        for w in self.root.winfo_children():
            w.destroy()

        # Main Content Frame (full width, menu will overlay when visible)
        self.contentFrame = ctk.CTkScrollableFrame(self.root, fg_color=COLOR_BG)
        self.contentFrame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Bind click event to content frame to close sidebar when clicked
        self.contentFrame.bind("<Button-1>", self.close_sidebar_on_click)
        
        # Left Navigation Bar (starts hidden, can slide in)
        self.navBar = ctk.CTkFrame(self.root, fg_color=COLOR_ACCENT2, corner_radius=0, width=220)
        self.navBar.place(x=-220, y=0, relheight=1)
        self.menu_visible = False

        # Initialize active page if not set
        self.activePage = getattr(self, 'activePage', 'home')
        self.navBtns = []

        # Logo at the top of the nav bar
        logo_nav_frame = ctk.CTkFrame(self.navBar, fg_color="transparent")
        logo_nav_frame.pack(pady=(20, 30))
        # Use text-based logo instead of fitness.png for sidebar
        ctk.CTkLabel(logo_nav_frame, text="HH", font=ctk.CTkFont(size=30, weight="bold"), text_color=COLOR_PRIMARY).pack()
        ctk.CTkLabel(logo_nav_frame, text="Healthy Habits", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT).pack(pady=5)

        navBtns_data = [
            ("Home", "home", os.path.join(ASSETS_DIR, "home.png")),
            ("Workouts", "workouts", os.path.join(ASSETS_DIR, "workout.png")),
            ("Macros", "macros", os.path.join(ASSETS_DIR, "macros.png")),
            ("Feed", "feed", os.path.join(ASSETS_DIR, "feed.png")),
            ("Settings", "settings", os.path.join(ASSETS_DIR, "logout.png"))
        ]

        def nav_cmd(page):
            self.activePage = page
            self.updateNavHighlight()
            self.showPage(page)

        for label, page, icon_path in navBtns_data:
            try:
                image = ctk.CTkImage(Image.open(icon_path), size=(24, 24))
            except FileNotFoundError:
                image = None # Fallback if icon is missing
            btn = ctk.CTkButton(
                self.navBar, text=f"  {label}", image=image, compound="left", anchor="w",
                width=180, height=40, corner_radius=10,
                fg_color="transparent", text_color=COLOR_TEXT,
                hover_color=COLOR_ACCENT,
                command=lambda p=page: nav_cmd(p)
            )
            btn.pack(pady=6, padx=20, anchor="w")
            self.navBtns.append((btn, page))


        # Toggle button for the menu
        self.toggle_btn = ctk.CTkButton(
            self.root, text="☰", width=40, height=40, corner_radius=20,
            font=ctk.CTkFont(size=20), fg_color=COLOR_PRIMARY, text_color=COLOR_WHITE_CLEAN,
            command=self.toggle_left_menu
        )
        self.toggle_btn.place(x=10, y=10)  # Always visible in top-left
        
        # Ensure toggle button stays on top
        self.root.after(100, lambda: self.toggle_btn.lift())

        self.updateNavHighlight()
        self.showPage(self.activePage)

    # --- NEW: Animation Functions ---
    def toggle_left_menu(self):
        """Toggle the left navigation menu with a sliding animation."""
        if self.menu_visible:
            # Hide menu - slide to the left
            self.animate_slide(self.navBar, start_x=0, end_x=-220)
            self.toggle_btn.configure(text="☰")
        else:
            # Show menu - slide from the left
            self.animate_slide(self.navBar, start_x=-220, end_x=0)
            self.toggle_btn.configure(text="✕")
        self.menu_visible = not self.menu_visible

    def animate_slide(self, widget, start_x, end_x):
        """Animate a widget sliding horizontally."""
        duration = 200  # Animation duration in milliseconds
        steps = 20      # Number of frames for the animation
        delay = duration // steps
        change_x = end_x - start_x

        def ease_out_cubic(t): 
            return 1 - pow(1 - t, 3)

        def step_animation(i):
            progress = i / steps
            eased_progress = ease_out_cubic(progress)
            current_x = start_x + change_x * eased_progress
            try:
                widget.place(x=int(current_x), y=0, relheight=1)
                # Ensure toggle button stays on top
                if hasattr(self, 'toggle_btn') and self.toggle_btn:
                    self.toggle_btn.lift()
            except:
                pass  # Handle case where widget might be destroyed
            if i < steps:
                self.root.after(delay, lambda: step_animation(i + 1))
        
        step_animation(0)


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
        page_methods = {
            "home": self.showHome, "workouts": self.showWorkouts,
            "macros": self.showMacros, "feed": self.showFeed, "settings": self.showSettings
        }
        method = page_methods.get(page)
        if method:
            method()
            # Bind close sidebar event to all widgets on the page
            self.root.after(100, lambda: self.bind_close_sidebar_to_children(self.contentFrame))

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

        # --- Horizontally Scrollable Widget Area ---
        scroll_container = ctk.CTkFrame(cf, fg_color="transparent")
        scroll_container.pack(fill="x", padx=20, pady=(0, 10))
        
        # Create horizontal scrollable frame
        horizontal_scroll = ctk.CTkScrollableFrame(scroll_container, orientation="horizontal", fg_color="transparent", height=280)
        horizontal_scroll.pack(fill="x", pady=10)
        
        # Container for widgets in horizontal scroll
        widgets_container = ctk.CTkFrame(horizontal_scroll, fg_color="transparent")
        widgets_container.pack(fill="both", expand=True)

        # --- Calories Widget (First in horizontal scroll) ---
        calWidget = ctk.CTkFrame(widgets_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY, width=350, height=260)
        calWidget.pack(side="left", padx=10, pady=10)
        calWidget.pack_propagate(False)  # Prevent widget from shrinking

        # Calories Title
        ctk.CTkLabel(calWidget, text="Daily Calories", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 10))

        # Main content container
        content_frame = ctk.CTkFrame(calWidget, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Circular progress bar (drawn with Canvas)
        calGoal = user.getCalorieGoal()
        calConsumed = user.getCaloriesConsumed()
        calBurned = user.getCaloriesBurned()
        calNet = calConsumed - calBurned
        calRem = calGoal - calNet

        percent = min(max(calNet / calGoal, 0), 1) if calGoal and calNet >= 0 else 0
        if calNet < 0: # If burned more than consumed, represent as progress towards next goal or distinct color
            percent = 0 # For simplicity, if net negative, progress is 0 on consumption bar

        canvas_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        canvas_frame.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="nsew")
        canvas = Canvas(canvas_frame, width=120, height=120, bg=COLOR_WIDGET_BG, highlightthickness=0)
        canvas.pack(expand=True)

        # Draw background circle
        canvas.create_oval(10, 10, 110, 110, outline=COLOR_LIGHT_GREY, width=10)
        # Draw progress arc
        if percent > 0:
            extent = percent * 360
            canvas.create_arc(10, 10, 110, 110, start=90, extent=-extent, style="arc", outline=COLOR_PRIMARY_GREEN, width=10)
        # Calories remaining in center
        canvas.create_text(60, 50, text=f"{calRem}", font=("Arial", 20, "bold"), fill=COLOR_TEXT)
        canvas.create_text(60, 75, text="Calories remaining", font=("Arial", 10), fill=COLOR_TEXT_SECONDARY)

        # Right side info
        infoFrame = ctk.CTkFrame(content_frame, fg_color="transparent")
        infoFrame.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="nsew")
        ctk.CTkLabel(infoFrame, text=f"Goal: {calGoal} kcal", text_color=COLOR_TEXT, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=2)
        ctk.CTkLabel(infoFrame, text=f"Consumed: {calConsumed} kcal", text_color=COLOR_SECONDARY_BLUE, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=2)
        ctk.CTkLabel(infoFrame, text=f"Burned: {calBurned} kcal", text_color=COLOR_PRIMARY_GREEN, font=ctk.CTkFont(size=13)).pack(anchor="w", pady=2)
        
        # Click hint
        ctk.CTkLabel(infoFrame, text="Click to log nutrition →", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(10, 0))

        # Make calorie widget clickable to navigate to macros page
        def on_calorie_click(event):
            self.activePage = "macros"
            self.updateNavHighlight()
            self.showPage("macros")
        
        calWidget.bind("<Button-1>", on_calorie_click)
        content_frame.bind("<Button-1>", on_calorie_click)
        canvas_frame.bind("<Button-1>", on_calorie_click)
        canvas.bind("<Button-1>", on_calorie_click)
        infoFrame.bind("<Button-1>", on_calorie_click)

        # --- Macro Widget (Second in horizontal scroll) ---
        macroWidget = ctk.CTkFrame(widgets_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY, width=350, height=260)
        macroWidget.pack(side="left", padx=10, pady=10)
        macroWidget.pack_propagate(False)  # Prevent widget from shrinking
        
        # Macro Title
        ctk.CTkLabel(macroWidget, text="Daily Macros", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 10))
        
        # Container for the three macro circles
        macro_circles_frame = ctk.CTkFrame(macroWidget, fg_color="transparent")
        macro_circles_frame.pack(pady=10, padx=10, fill="both", expand=True)
        macro_circles_frame.grid_columnconfigure(0, weight=1)
        macro_circles_frame.grid_columnconfigure(1, weight=1)
        macro_circles_frame.grid_columnconfigure(2, weight=1)
        
        # Get real user macro data
        macro_goals = user.getMacroGoals()
        macro_consumed = user.getMacroConsumed()
        
        protein_current, protein_goal = macro_consumed['protein'], macro_goals['protein']
        carbs_current, carbs_goal = macro_consumed['carbs'], macro_goals['carbs']
        fats_current, fats_goal = macro_consumed['fat'], macro_goals['fat']
        
        # Helper function to create macro circles
        def create_macro_circle(parent, title, current, goal, color, column):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
            
            # Title
            ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT).pack(pady=(0, 5))
            
            # Canvas for circle
            canvas = Canvas(frame, width=80, height=80, bg=COLOR_WIDGET_BG, highlightthickness=0)
            canvas.pack()
            
            # Calculate percentage
            percent = min(current / goal, 1) if goal > 0 else 0
            
            # Draw background circle
            canvas.create_oval(10, 10, 70, 70, outline=COLOR_LIGHT_GREY, width=6)
            
            # Draw progress arc
            if percent > 0:
                extent = percent * 360
                canvas.create_arc(10, 10, 70, 70, start=90, extent=-extent, style="arc", outline=color, width=6)
            
            # Center text
            canvas.create_text(40, 35, text=f"{current:.1f}g", font=("Arial", 12, "bold"), fill=COLOR_TEXT)
            canvas.create_text(40, 50, text=f"/{goal:.1f}g", font=("Arial", 8), fill=COLOR_TEXT_SECONDARY)
            
            return canvas, frame
        
        # Create the three macro circles
        protein_canvas, protein_frame = create_macro_circle(macro_circles_frame, "Protein", protein_current, protein_goal, "#FF6B6B", 0)
        carbs_canvas, carbs_frame = create_macro_circle(macro_circles_frame, "Carbs", carbs_current, carbs_goal, "#4ECDC4", 1)
        fats_canvas, fats_frame = create_macro_circle(macro_circles_frame, "Fats", fats_current, fats_goal, "#45B7D1", 2)
        
        # Click hint
        click_hint_frame = ctk.CTkFrame(macroWidget, fg_color="transparent")
        click_hint_frame.pack(pady=(5, 15))
        ctk.CTkLabel(click_hint_frame, text="Click to log detailed macros →", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack()

        # Make macro widget clickable to navigate to macros page
        def on_macro_click(event):
            self.activePage = "macros"
            self.updateNavHighlight()
            self.showPage("macros")
        
        macroWidget.bind("<Button-1>", on_macro_click)
        macro_circles_frame.bind("<Button-1>", on_macro_click)
        click_hint_frame.bind("<Button-1>", on_macro_click)
        protein_frame.bind("<Button-1>", on_macro_click)
        carbs_frame.bind("<Button-1>", on_macro_click)
        fats_frame.bind("<Button-1>", on_macro_click)
        protein_canvas.bind("<Button-1>", on_macro_click)
        carbs_canvas.bind("<Button-1>", on_macro_click)
        fats_canvas.bind("<Button-1>", on_macro_click)

        # --- Workout Progress Widget (Third in horizontal scroll) ---
        workout_widget = ctk.CTkFrame(widgets_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY, width=350, height=260)
        workout_widget.pack(side="left", padx=10, pady=10)
        workout_widget.pack_propagate(False)  # Prevent widget from shrinking

        ctk.CTkLabel(workout_widget, text="Weekly Workout Progress", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 10))

        goalRow = ctk.CTkFrame(workout_widget, fg_color="transparent")
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
                # Update progress display without full page refresh
                progress = user.getWorkoutsCompleted() / user.getWeeklyGoal() if user.getWeeklyGoal() else 0
                progressBar.set(progress)
            except Exception:
                messagebox.showwarning("Set Goal", "Enter a number between 1 and 14.")
        ctk.CTkButton(goalRow, text="Set Goal", width=80, fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=set_goal).pack(side="left")

        ctk.CTkLabel(workout_widget, text=f"Completed: {user.getWorkoutsCompleted()} / {user.getWeeklyGoal()}", text_color=COLOR_TEXT, font=ctk.CTkFont(size=15)).pack(pady=(10, 5))
        
        # Show last completed workout if available
        last_workout = user.getLastWorkoutCompletion()
        if last_workout:
            last_workout_frame = ctk.CTkFrame(workout_widget, fg_color=COLOR_ACCENT, corner_radius=6)
            last_workout_frame.pack(fill="x", padx=15, pady=(0, 8))
            ctk.CTkLabel(last_workout_frame, text=f"🏆 Last: {last_workout['name']} ({last_workout['date']})", 
                        text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(pady=4)
        
        progress = user.getWorkoutsCompleted() / user.getWeeklyGoal() if user.getWeeklyGoal() else 0
        progressBar = ctk.CTkProgressBar(workout_widget, width=280, height=15, progress_color=COLOR_PRIMARY_GREEN, fg_color=COLOR_LIGHT_GREY, corner_radius=8)
        progressBar.pack(pady=(0, 15))
        progressBar.set(progress)

        # Workout Logging Feature
        ctk.CTkLabel(workout_widget, text="Log a Workout:", text_color=COLOR_TEXT, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # Add tip about workout planner integration
        tip_frame = ctk.CTkFrame(workout_widget, fg_color=COLOR_ACCENT, corner_radius=6)
        tip_frame.pack(fill="x", padx=15, pady=(0, 8))
        ctk.CTkLabel(tip_frame, text="💡 Tip: Complete workouts from your plans in the Workouts page!", 
                    text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=11)).pack(pady=4)
        
        logRow = ctk.CTkFrame(workout_widget, fg_color="transparent")
        logRow.pack(pady=(0, 15))
        presetWorkouts = ["Run", "Walk", "Weights", "Yoga", "Cycling", "Swim", "Other"]
        workoutVar = ctk.StringVar(value=presetWorkouts[0])
        ctk.CTkOptionMenu(logRow, variable=workoutVar, values=presetWorkouts, width=150, fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, button_color=COLOR_PRIMARY).pack(side="left", padx=(0, 10))
        def log_workout():
            workout_name = workoutVar.get()
            user.addWorkoutCompleted(workout_name=workout_name)
            if user.getWorkoutsCompleted() > user.getWeeklyGoal():
                user.setWeeklyGoal(user.getWorkoutsCompleted()) # Auto-adjust goal if exceeded
            saveUser(user)
            messagebox.showinfo("Workout Logged", f"Logged: {workout_name}")
            self.showHome()
        ctk.CTkButton(logRow, text="Log Workout", width=120, fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=log_workout).pack(side="left")

        # --- Weight Tracking Widget (Fourth in horizontal scroll) ---
        weight_widget = ctk.CTkFrame(widgets_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY, width=350, height=260)
        weight_widget.pack(side="left", padx=10, pady=10)
        weight_widget.pack_propagate(False)  # Prevent widget from shrinking

        ctk.CTkLabel(weight_widget, text="Weight Progress Tracker", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_TEXT).pack(pady=(15, 5))

        # Get weight progress statistics
        progress_stats = user.getWeightProgressStats()
        current_weight = user.getCurrentWeight()
        goal_weight = float(user.getGoalWeight()) if user.getGoalWeight() else current_weight
        
        # Progress summary row
        progress_summary_frame = ctk.CTkFrame(weight_widget, fg_color="transparent")
        progress_summary_frame.pack(pady=5, padx=15, fill="x")
        progress_summary_frame.grid_columnconfigure(0, weight=1)
        progress_summary_frame.grid_columnconfigure(1, weight=1)
        progress_summary_frame.grid_columnconfigure(2, weight=1)
        
        # Current vs Goal
        ctk.CTkLabel(progress_summary_frame, text=f"Current: {current_weight:.1f}kg", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_TEXT).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(progress_summary_frame, text=f"Goal: {goal_weight:.1f}kg", font=ctk.CTkFont(size=13, weight="bold"), text_color=COLOR_PRIMARY).grid(row=0, column=1)
        
        # Progress percentage
        progress_pct = progress_stats["progress_percentage"]
        progress_color = COLOR_PRIMARY_GREEN if 0 <= progress_pct <= 100 else COLOR_SECONDARY_BLUE
        ctk.CTkLabel(progress_summary_frame, text=f"Progress: {progress_pct:.1f}%", font=ctk.CTkFont(size=13, weight="bold"), text_color=progress_color).grid(row=0, column=2, sticky="e")

        # Progress metrics frame
        metrics_frame = ctk.CTkFrame(weight_widget, fg_color=COLOR_ACCENT, corner_radius=8)
        metrics_frame.pack(pady=8, padx=15, fill="x")
        
        # Progress details in two columns
        metrics_left = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_left.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        metrics_right = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_right.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Left column metrics
        total_change = progress_stats["total_change"]
        change_color = COLOR_PRIMARY_GREEN if (goal_weight < current_weight and total_change < 0) or (goal_weight > current_weight and total_change > 0) else COLOR_SECONDARY_BLUE
        change_symbol = "+" if total_change > 0 else ""
        ctk.CTkLabel(metrics_left, text=f"Total: {change_symbol}{total_change:.1f}kg", font=ctk.CTkFont(size=11, weight="bold"), text_color=change_color).pack(anchor="w")
        
        weekly_change = progress_stats["weekly_change"]
        weekly_symbol = "+" if weekly_change > 0 else ""
        ctk.CTkLabel(metrics_left, text=f"This week: {weekly_symbol}{weekly_change:.1f}kg", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT).pack(anchor="w")
        
        ctk.CTkLabel(metrics_left, text=f"Trend: {progress_stats['trend']}", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w")
        
        # Right column metrics
        ctk.CTkLabel(metrics_right, text=f"Days tracking: {progress_stats['days_tracking']}", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT).pack(anchor="e")
        
        velocity = progress_stats["velocity"]
        velocity_symbol = "+" if velocity > 0 else ""
        ctk.CTkLabel(metrics_right, text=f"Rate: {velocity_symbol}{velocity:.2f}kg/week", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT).pack(anchor="e")
        
        # Projected goal date
        if progress_stats["projected_goal_date"]:
            try:
                proj_date = datetime.strptime(progress_stats["projected_goal_date"], "%Y-%m-%d")
                proj_text = proj_date.strftime("%b %d, %Y")
                ctk.CTkLabel(metrics_right, text=f"Est. goal: {proj_text}", font=ctk.CTkFont(size=10), text_color=COLOR_TEXT_SECONDARY).pack(anchor="e")
            except:
                pass

        # Weight progress over time (simplified graph)
        graph_frame = ctk.CTkFrame(weight_widget, fg_color="transparent")
        graph_frame.pack(pady=5, padx=15, fill="x")
        
        weight_history = user.getWeightHistory()
        if len(weight_history) >= 2:
            # Create a simple line graph using Canvas
            graph_canvas = Canvas(graph_frame, width=280, height=60, bg=COLOR_WIDGET_BG, highlightthickness=0)
            graph_canvas.pack()
            
            # Get last 8 weeks of data for display
            recent_weights = weight_history[-56:] if len(weight_history) > 56 else weight_history
            
            if len(recent_weights) >= 2:
                # Calculate graph boundaries
                weights = [w for d, w in recent_weights]
                min_weight = min(weights)
                max_weight = max(weights)
                weight_range = max_weight - min_weight if max_weight != min_weight else 1
                
                # Draw goal line if within range
                if min_weight <= goal_weight <= max_weight:
                    goal_y = 50 - ((goal_weight - min_weight) / weight_range * 40)
                    graph_canvas.create_line(20, goal_y, 260, goal_y, fill=COLOR_PRIMARY, width=1, dash=(3, 3))
                    graph_canvas.create_text(270, goal_y, text="Goal", font=("Arial", 8), fill=COLOR_PRIMARY, anchor="w")
                
                # Draw graph line
                points = []
                for i, (date, weight) in enumerate(recent_weights):
                    x = 20 + (i * (240 / (len(recent_weights) - 1)))
                    y = 50 - ((weight - min_weight) / weight_range * 40)
                    points.extend([x, y])
                
                if len(points) >= 4:
                    graph_canvas.create_line(points, fill=COLOR_PRIMARY_GREEN, width=2, smooth=True)
                    
                    # Add data points
                    for i in range(0, len(points), 2):
                        x, y = points[i], points[i+1]
                        graph_canvas.create_oval(x-2, y-2, x+2, y+2, fill=COLOR_PRIMARY_GREEN, outline=COLOR_PRIMARY_GREEN)
        else:
            ctk.CTkLabel(graph_frame, text="Log weights to see detailed progress", 
                        text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=12)).pack(expand=True)

        # Weight Logging Feature
        ctk.CTkLabel(weight_widget, text="Log Your Weight:", text_color=COLOR_TEXT, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(8, 3))
        weight_log_frame = ctk.CTkFrame(weight_widget, fg_color="transparent")
        weight_log_frame.pack(pady=(0, 10), padx=15, fill="x")
        weight_log_frame.grid_columnconfigure(0, weight=1)
        weight_log_frame.grid_columnconfigure(1, weight=1)
        
        # Weight entry
        weight_entry = ctk.CTkEntry(weight_log_frame, placeholder_text="Weight (kg)", width=120)
        weight_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Date picker for weight logging
        if CALENDAR_AVAILABLE:
            weight_date_picker = DateEntry(weight_log_frame, width=10, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        else:
            weight_date_picker = DateEntry(weight_log_frame)
        weight_date_picker.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        def log_weight():
            try:
                weight_str = weight_entry.get().strip()
                if not weight_str:
                    messagebox.showwarning("Input Error", "Please enter your weight")
                    return
                
                weight = float(weight_str)
                if weight < 20 or weight > 300:
                    messagebox.showwarning("Input Error", "Weight must be between 20 and 300 kg")
                    return
                
                # Get selected date
                selected_date = weight_date_picker.get_date()
                date_str = selected_date.strftime("%Y-%m-%d")
                
                # Check if this creates a significant change
                previous_weight = user.getCurrentWeight()
                weight_change = weight - previous_weight
                
                # Add weight entry to user's history
                user.addWeightEntry(weight, date_str)
                saveUser(user)
                
                # Clear the entry
                weight_entry.delete(0, ctk.END)
                weight_date_picker.set_date(datetime.now().date())
                
                # Enhanced feedback message
                change_text = ""
                if abs(weight_change) > 0.1:
                    change_symbol = "+" if weight_change > 0 else ""
                    change_text = f" ({change_symbol}{weight_change:.1f}kg change)"
                
                messagebox.showinfo("Weight Logged", f"Weight {weight:.1f}kg logged for {date_str}{change_text}\n\nProgress tracker updated!")
                self.showHome()  # Refresh the page to show updated graph
                
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid weight number")
        
        ctk.CTkButton(weight_widget, text="Log Weight", width=150, fg_color=COLOR_SECONDARY_BLUE, 
                     text_color=COLOR_BTN_TXT, corner_radius=8, command=log_weight).pack(pady=(5, 10))

        # --- Main content area for remaining cards ---
        main_content_frame = ctk.CTkFrame(cf, fg_color="transparent")
        main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_content_frame.grid_columnconfigure(0, weight=1)
        main_content_frame.grid_rowconfigure(0, weight=1)

        # --- REPLACEMENT: Weather Widget ---
        weather_card = ctk.CTkFrame(main_content_frame, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        weather_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Fetch weather data by calling our new method
        weather_data = self.getWeatherData()
        
        if weather_data and not weather_data.get("error"):
            # --- If data is available, display it ---
            weather_card.grid_columnconfigure(0, weight=1) 
            weather_card.grid_columnconfigure(1, weight=2)
            
            # Weather Icon
            try:
                icon_url = f"https://openweathermap.org/img/wn/{weather_data['icon_code']}@2x.png"
                icon_response = requests.get(icon_url, timeout=10)
                icon_image_data = icon_response.content
                icon_image = ctk.CTkImage(Image.open(io.BytesIO(icon_image_data)), size=(80, 80))
                icon_label = ctk.CTkLabel(weather_card, image=icon_image, text="")
                icon_label.grid(row=0, column=0, rowspan=3, padx=20, pady=15, sticky="e")
            except Exception as e:
                logError(f"Could not load weather icon: {e}")
                # Fallback text if icon fails to load
                ctk.CTkLabel(weather_card, text="Icon", font=ctk.CTkFont(size=18)).grid(row=0, column=0, rowspan=3, padx=20, pady=15, sticky="e")

            # Weather Information
            ctk.CTkLabel(weather_card, text=weather_data["location"], font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_PRIMARY).grid(row=0, column=1, pady=(15, 0), sticky="w")
            ctk.CTkLabel(weather_card, text=weather_data["temp"], font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_TEXT).grid(row=1, column=1, sticky="w")
            ctk.CTkLabel(weather_card, text=f"{weather_data['description']} | {weather_data['feels_like']}", font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_SECONDARY).grid(row=2, column=1, pady=(0, 15), sticky="w")
        
        else:
            # --- If there's an error, display the error message ---
            weather_card.grid_columnconfigure(0, weight=1) # Center the content
            error_message = weather_data.get("error", "Weather data unavailable.")
            if "API key" in error_message:
                error_message += "\nPlease set your API key in HealthyHabitsApp.__init__"
            
            ctk.CTkLabel(weather_card, text="🌤️ Live Weather", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(15, 5))
            ctk.CTkLabel(weather_card, text=error_message, font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_SECONDARY, wraplength=350).pack(pady=10, padx=20)
    def showWorkouts(self):
        """Displays the main workout page with weight tracking and the planner widget."""
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        
        user = self.currentUser
        
        # --- Main title ---
        title_frame = ctk.CTkFrame(cf, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(20, 2))
        ctk.CTkLabel(title_frame, text="Workouts & Weight Tracking", font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack()
        
        # --- Weight Tracking Card ---
        weight_card = ctk.CTkFrame(cf, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        weight_card.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(weight_card, text="Comprehensive Weight Progress Tracker", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 5))
        
        # Get comprehensive progress stats
        progress_stats = user.getWeightProgressStats()
        current_weight = user.getCurrentWeight()
        goal_weight = float(user.getGoalWeight()) if user.getGoalWeight() else current_weight
        
        # Main stats row
        main_stats_frame = ctk.CTkFrame(weight_card, fg_color="transparent")
        main_stats_frame.pack(fill="x", padx=15, pady=(5, 10))
        main_stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Current weight
        current_frame = ctk.CTkFrame(main_stats_frame, fg_color=COLOR_ACCENT, corner_radius=8)
        current_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(current_frame, text="Current Weight", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT).pack(pady=(5, 2))
        ctk.CTkLabel(current_frame, text=f"{current_weight:.1f} kg", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(0, 5))
        
        # Goal weight
        # Goal weight
        goal_frame = ctk.CTkFrame(main_stats_frame, fg_color=COLOR_ACCENT, corner_radius=8)
        goal_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(goal_frame, text="Goal Weight", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT).pack(pady=(5, 2))
        
        # Frame to hold the goal label and edit button side-by-side
        goal_display_frame = ctk.CTkFrame(goal_frame, fg_color="transparent")
        goal_display_frame.pack(pady=(0, 5))
        
        ctk.CTkLabel(goal_display_frame, text=f"{goal_weight:.1f} kg", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=(0,5))
        
        # Add the new Edit button
        ctk.CTkButton(goal_display_frame, text="✏️", font=ctk.CTkFont(size=14), width=28, height=28, 
                      fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_WHITE_CLEAN,
                      command=self._openEditGoalDialog).pack(side="left")
        
        # Progress percentage
        progress_frame = ctk.CTkFrame(main_stats_frame, fg_color=COLOR_ACCENT, corner_radius=8)
        progress_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(progress_frame, text="Progress", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT).pack(pady=(5, 2))
        progress_pct = progress_stats["progress_percentage"]
        progress_color = COLOR_PRIMARY_GREEN if 0 <= progress_pct <= 100 else COLOR_SECONDARY_BLUE
        ctk.CTkLabel(progress_frame, text=f"{progress_pct:.1f}%", font=ctk.CTkFont(size=16, weight="bold"), text_color=progress_color).pack(pady=(0, 5))
        
        # Remaining to goal
        remaining_frame = ctk.CTkFrame(main_stats_frame, fg_color=COLOR_ACCENT, corner_radius=8)
        remaining_frame.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(remaining_frame, text="Remaining", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT).pack(pady=(5, 2))
        remaining = abs(goal_weight - current_weight)
        ctk.CTkLabel(remaining_frame, text=f"{remaining:.1f} kg", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_SECONDARY_BLUE).pack(pady=(0, 5))

        # Detailed progress metrics
        details_frame = ctk.CTkFrame(weight_card, fg_color=COLOR_ACCENT2, corner_radius=8)
        details_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        # Create three columns for detailed metrics
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Column 1: Change metrics
        change_col = ctk.CTkFrame(details_frame, fg_color="transparent")
        change_col.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(change_col, text="📈 Weight Changes", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w")
        # JUSTIFICATION (Displaying Signed Values): The 'change_symbol' provides
        # clear user feedback. A weight gain of 1.5kg is shown as "+1.5kg", which is
        # more intuitive than just "1.5kg". This directly links the numerical sign to
        # a standard mathematical representation.
        total_change = progress_stats["total_change"]
        change_symbol = "+" if total_change > 0 else ""
        change_color = COLOR_PRIMARY_GREEN if (goal_weight < current_weight and total_change < 0) or (goal_weight > current_weight and total_change > 0) else COLOR_SECONDARY_BLUE
        ctk.CTkLabel(change_col, text=f"Total: {change_symbol}{total_change:.1f}kg", font=ctk.CTkFont(size=12), text_color=change_color).pack(anchor="w", pady=2)
        
        weekly_change = progress_stats["weekly_change"]
        weekly_symbol = "+" if weekly_change > 0 else ""
        ctk.CTkLabel(change_col, text=f"This week: {weekly_symbol}{weekly_change:.1f}kg", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(anchor="w", pady=2)
        
        monthly_change = progress_stats["monthly_change"]
        monthly_symbol = "+" if monthly_change > 0 else ""
        ctk.CTkLabel(change_col, text=f"This month: {monthly_symbol}{monthly_change:.1f}kg", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(anchor="w", pady=2)
        
        # Column 2: Tracking metrics
        tracking_col = ctk.CTkFrame(details_frame, fg_color="transparent")
        tracking_col.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(tracking_col, text="📊 Tracking Stats", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w")
        
        ctk.CTkLabel(tracking_col, text=f"Days tracking: {progress_stats['days_tracking']}", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(anchor="w", pady=2)
        ctk.CTkLabel(tracking_col, text=f"Trend: {progress_stats['trend']}", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(anchor="w", pady=2)
        
        velocity = progress_stats["velocity"]
        velocity_symbol = "+" if velocity > 0 else ""
        ctk.CTkLabel(tracking_col, text=f"Rate: {velocity_symbol}{velocity:.2f}kg/week", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(anchor="w", pady=2)
        
        # Column 3: Goal projection
        projection_col = ctk.CTkFrame(details_frame, fg_color="transparent")
        projection_col.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(projection_col, text="🎯 Goal Projection", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w")
        
        if progress_stats["projected_goal_date"]:
            try:
                proj_date = datetime.strptime(progress_stats["projected_goal_date"], "%Y-%m-%d")
                proj_text = proj_date.strftime("%b %d, %Y")
                ctk.CTkLabel(projection_col, text=f"Est. goal date:", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(anchor="w", pady=2)
                ctk.CTkLabel(projection_col, text=proj_text, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_PRIMARY_GREEN).pack(anchor="w", pady=2)
            except:
                ctk.CTkLabel(projection_col, text="Goal date: N/A", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=2)
        else:
            ctk.CTkLabel(projection_col, text="Goal date: N/A", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=2)
            ctk.CTkLabel(projection_col, text="(Need more data)", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=2)

        # Visual progress bar
        progress_bar_frame = ctk.CTkFrame(weight_card, fg_color="transparent")
        progress_bar_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(progress_bar_frame, text="Progress to Goal", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_TEXT).pack()
        
        # Create progress bar
        progress_bar = ctk.CTkProgressBar(progress_bar_frame, width=400, height=20, progress_color=progress_color, fg_color=COLOR_LIGHT_GREY, corner_radius=10)
        progress_bar.pack(pady=5)
        
        # Set progress (clamped between 0 and 1)
        progress_value = max(0, min(1, abs(progress_pct) / 100))
        progress_bar.set(progress_value)
        
        # Progress labels
        progress_labels_frame = ctk.CTkFrame(progress_bar_frame, fg_color="transparent")
        progress_labels_frame.pack(fill="x")
        progress_labels_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        starting_weight = user._weight if not user.getWeightHistory() else user.getWeightHistory()[0][1]
        ctk.CTkLabel(progress_labels_frame, text=f"Start: {starting_weight:.1f}kg", font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(progress_labels_frame, text=f"Current: {current_weight:.1f}kg", font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_TEXT).grid(row=0, column=1)
        ctk.CTkLabel(progress_labels_frame, text=f"Goal: {goal_weight:.1f}kg", font=ctk.CTkFont(size=11), text_color=COLOR_PRIMARY).grid(row=0, column=2, sticky="e")

        # Enhanced Weight History Graph
        graph_section = ctk.CTkFrame(weight_card, fg_color=COLOR_ACCENT, corner_radius=8)
        graph_section.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(graph_section, text="📈 Weight History (Last 12 Weeks)", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 5))
        
        weight_history = user.getWeightHistory()
        if len(weight_history) >= 2:
            # Create detailed graph
            graph_canvas = Canvas(graph_section, width=500, height=200, bg=COLOR_WIDGET_BG, highlightthickness=1, highlightcolor=COLOR_MEDIUM_GREY)
            graph_canvas.pack(pady=10)
            
            # Sort and get recent data (last 12 weeks = 84 days)
            sorted_history = sorted(weight_history, key=lambda x: x[0])
            recent_weights = sorted_history[-84:] if len(sorted_history) > 84 else sorted_history
            
            if len(recent_weights) >= 2:
                # Calculate graph boundaries with padding
                weights = [w for d, w in recent_weights]
                min_weight = min(weights)
                max_weight = max(weights)
                weight_range = max_weight - min_weight if max_weight != min_weight else 1
                
                # Add padding to the range
                padding = weight_range * 0.1
                graph_min = min_weight - padding
                graph_max = max_weight + padding
                graph_range = graph_max - graph_min
                
                # Graph dimensions
                graph_left, graph_right = 50, 450
                graph_top, graph_bottom = 30, 170
                graph_width = graph_right - graph_left
                graph_height = graph_bottom - graph_top
                
                # Draw axes
                graph_canvas.create_line(graph_left, graph_bottom, graph_right, graph_bottom, fill=COLOR_MEDIUM_GREY, width=2)  # X-axis
                graph_canvas.create_line(graph_left, graph_top, graph_left, graph_bottom, fill=COLOR_MEDIUM_GREY, width=2)  # Y-axis
                
                # Draw goal line if within visible range
                if graph_min <= goal_weight <= graph_max:
                    goal_y = graph_bottom - ((goal_weight - graph_min) / graph_range * graph_height)
                    graph_canvas.create_line(graph_left, goal_y, graph_right, goal_y, fill=COLOR_PRIMARY, width=2, dash=(5, 5))
                    graph_canvas.create_text(graph_right + 5, goal_y, text=f"Goal ({goal_weight:.1f}kg)", font=("Arial", 10, "bold"), fill=COLOR_PRIMARY, anchor="w")
                
                # Draw weight grid lines
                num_grid_lines = 5
                for i in range(num_grid_lines + 1):
                    y = graph_top + (i * graph_height / num_grid_lines)
                    weight_value = graph_max - (i * graph_range / num_grid_lines)
                    graph_canvas.create_line(graph_left, y, graph_right, y, fill=COLOR_LIGHT_GREY, width=1)
                    graph_canvas.create_text(graph_left - 5, y, text=f"{weight_value:.1f}", font=("Arial", 9), fill=COLOR_TEXT_SECONDARY, anchor="e")
                
                # Plot weight data points and line
                points = []
                for i, (date, weight) in enumerate(recent_weights):
                    x = graph_left + (i * graph_width / (len(recent_weights) - 1))
                    y = graph_bottom - ((weight - graph_min) / graph_range * graph_height)
                    points.extend([x, y])
                    
                    # Draw data point
                    graph_canvas.create_oval(x-3, y-3, x+3, y+3, fill=COLOR_PRIMARY_GREEN, outline=COLOR_PRIMARY_GREEN)
                    
                    # Add date labels for some points
                    if i % max(1, len(recent_weights) // 8) == 0 or i == len(recent_weights) - 1:
                        try:
                            date_obj = datetime.strptime(date, "%Y-%m-%d")
                            date_label = date_obj.strftime("%m/%d")
                            graph_canvas.create_text(x, graph_bottom + 15, text=date_label, font=("Arial", 8), fill=COLOR_TEXT_SECONDARY, angle=45)
                        except:
                            pass
                
                # Draw connecting line
                if len(points) >= 4:
                    graph_canvas.create_line(points, fill=COLOR_PRIMARY_GREEN, width=3, smooth=True)
                
                # Add trend arrow and statistics
                first_weight = recent_weights[0][1]
                last_weight = recent_weights[-1][1]
                trend_change = last_weight - first_weight

                # JUSTIFICATION (Symbolic Logic): The sign of 'trend_change' is used
                # to select a visual arrow symbol. This provides at-a-glance feedback
                # that is faster for a user to interpret than reading text or numbers.
                if abs(trend_change) > 0.1:  # Only show trend if meaningful change
                    trend_arrow = "↗️" if trend_change > 0 else "↘️"
                    trend_color = COLOR_SECONDARY_BLUE if trend_change > 0 else COLOR_PRIMARY_GREEN
                    graph_canvas.create_text(graph_right - 50, graph_top + 10, 
                                           text=f"{trend_arrow} {abs(trend_change):.1f}kg", 
                                           font=("Arial", 12, "bold"), fill=trend_color)
                
        else:
            ctk.CTkLabel(graph_section, text="📊 Log at least 2 weight entries to see your progress graph", 
                        text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=14)).pack(pady=20)
        
        # Weight Logging Section
        weight_log_section = ctk.CTkFrame(weight_card, fg_color=COLOR_ACCENT, corner_radius=8)
        weight_log_section.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(weight_log_section, text="Log New Weight Entry", font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_TEXT).pack(pady=(10, 5))
        
        # Weight logging form
        weight_form_frame = ctk.CTkFrame(weight_log_section, fg_color="transparent")
        weight_form_frame.pack(pady=(0, 10), padx=15, fill="x")
        weight_form_frame.grid_columnconfigure(0, weight=1)
        weight_form_frame.grid_columnconfigure(1, weight=1)
        weight_form_frame.grid_columnconfigure(2, weight=1)
        
        # Weight input
        weight_input_frame = ctk.CTkFrame(weight_form_frame, fg_color="transparent")
        weight_input_frame.grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkLabel(weight_input_frame, text="Weight (kg)", font=ctk.CTkFont(size=12, weight="bold")).pack()
        workout_weight_entry = ctk.CTkEntry(weight_input_frame, placeholder_text="e.g., 70.5")
        workout_weight_entry.pack(fill="x", pady=2)
        
        # Date input
        date_input_frame = ctk.CTkFrame(weight_form_frame, fg_color="transparent")
        date_input_frame.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(date_input_frame, text="Date", font=ctk.CTkFont(size=12, weight="bold")).pack()
        
        if CALENDAR_AVAILABLE:
            workout_date_picker = DateEntry(date_input_frame, width=10, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        else:
            workout_date_picker = DateEntry(date_input_frame)
        workout_date_picker.pack(fill="x", pady=2)
        
        # Log button
        button_frame = ctk.CTkFrame(weight_form_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkLabel(button_frame, text="", font=ctk.CTkFont(size=12)).pack()  # Spacer
        
        def log_weight_workout():
            try:
                weight_str = workout_weight_entry.get().strip()
                if not weight_str:
                    messagebox.showwarning("Input Error", "Please enter your weight")
                    return
                
                weight = float(weight_str)
                if weight < 20 or weight > 300:
                    messagebox.showwarning("Input Error", "Weight must be between 20 and 300 kg")
                    return
                
                # Get selected date
                selected_date = workout_date_picker.get_date()
                date_str = selected_date.strftime("%Y-%m-%d")
                
                # Check if this creates a significant change
                previous_weight = user.getCurrentWeight()
                weight_change = weight - previous_weight
                
                # Add weight entry to user's history
                user.addWeightEntry(weight, date_str)
                saveUser(user)
                
                # Clear the entry
                workout_weight_entry.delete(0, ctk.END)
                workout_date_picker.set_date(datetime.now().date())
                
                # Enhanced feedback message
                change_text = ""
                if abs(weight_change) > 0.1:
                    change_symbol = "+" if weight_change > 0 else ""
                    change_text = f" ({change_symbol}{weight_change:.1f}kg from last entry)"
                
                messagebox.showinfo("Weight Logged", f"Weight {weight:.1f}kg logged for {date_str}{change_text}\n\nProgress tracker updated!")
                self.showWorkouts()  # Refresh the page to show updated stats
                
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid weight number")
        
        ctk.CTkButton(button_frame, text="Log Weight", width=100, fg_color=COLOR_PRIMARY_GREEN, 
                     text_color=COLOR_BTN_TXT, corner_radius=8, command=log_weight_workout).pack(pady=2)
        
        # --- NEW: Workout Planner Widget ---
        planner_card = ctk.CTkFrame(cf, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        planner_card.pack(fill="both", expand=True, pady=10, padx=20)

        ctk.CTkLabel(planner_card, text="Workout Planner", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 5))
        
        # This frame will hold the dynamic content of the planner
        planner_display_frame = ctk.CTkFrame(planner_card, fg_color="transparent")
        planner_display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial draw of the planner widget
        self._drawPlannerHome(planner_display_frame)

    def getUserWorkoutPlans(self):
        """Gets all workout plans for the current user."""
        all_plans = readCsv(WORKOUT_PLANS_CSV)
        user_plans = []
        for plan in all_plans:
            if plan.get('user_id') == self.currentUser.getStudentId():
                try:
                    plan['exercises'] = json.loads(plan['exercises'])
                    user_plans.append(plan)
                except json.JSONDecodeError:
                    logError(f"Could not parse exercises for plan: {plan.get('plan_name')}")
        return user_plans

    def saveWorkoutPlan(self, plan_data):
        """Saves a new or updated workout plan for the user."""
        all_plans = readCsv(WORKOUT_PLANS_CSV)
        
        plan_to_save = {
            "user_id": self.currentUser.getStudentId(),
            "plan_name": plan_data['plan_name'],
            "exercises": json.dumps(plan_data['exercises'])
        }

        plan_exists = False
        for i, existing_plan in enumerate(all_plans):
            if existing_plan.get('user_id') == plan_to_save['user_id'] and existing_plan.get('plan_name') == plan_to_save['plan_name']:
                all_plans[i] = plan_to_save
                plan_exists = True
                break
        
        if not plan_exists:
            all_plans.append(plan_to_save)

        writeCsv(WORKOUT_PLANS_CSV, all_plans, ["user_id", "plan_name", "exercises"])
    def deleteWorkoutPlan(self, plan_name):
        """Deletes a workout plan for the current user."""
        all_plans = readCsv(WORKOUT_PLANS_CSV)
        
        # Create a new list excluding the plan to be deleted
        updated_plans = [
            p for p in all_plans 
            if not (p.get('user_id') == self.currentUser.getStudentId() and p.get('plan_name') == plan_name)
        ]
        
        # Save the updated list back to the CSV
        writeCsv(WORKOUT_PLANS_CSV, updated_plans, ["user_id", "plan_name", "exercises"])
    def showMacros(self):
        """
        Display comprehensive macro and meal planning page.
        AC6: GUI implementation, OOP, data structures, control structures
        AC7: Input validation, error handling, user feedback
        """
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        user = self.currentUser
        
        # Main title
        title_frame = ctk.CTkFrame(cf, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5, 2))
        ctk.CTkLabel(title_frame, text="Nutrition & Meal Planning Center", font=ctk.CTkFont(size=28, weight="bold"), text_color=COLOR_PRIMARY).pack()
        ctk.CTkLabel(title_frame, text="Create personalized meal plans and track your nutrition goals", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=14)).pack(pady=(1, 0))
        
        # Create main container with scrollable content - fill more screen
        main_container = ctk.CTkFrame(cf, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=2, pady=1)
        
        # --- Current Nutrition Summary Card ---
        nutrition_card = ctk.CTkFrame(main_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        nutrition_card.pack(fill="x", pady=(0, 8), padx=2)
        
        ctk.CTkLabel(nutrition_card, text="Today's Nutrition Summary", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 5))
        
        # Nutrition progress bars - using real user data
        progress_frame = ctk.CTkFrame(nutrition_card, fg_color="transparent")
        progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        progress_frame.grid_columnconfigure(0, weight=1)
        progress_frame.grid_columnconfigure(1, weight=1)
        progress_frame.grid_columnconfigure(2, weight=1)
        progress_frame.grid_columnconfigure(3, weight=1)
        
        # Get user's actual macro data
        macro_goals = user.getMacroGoals()
        macro_consumed = user.getMacroConsumed()
        macro_progress = user.getMacroProgress()
        
        # Calories progress
        cal_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        cal_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(cal_frame, text="Calories", font=ctk.CTkFont(size=14, weight="bold")).pack()
        cal_bar = ctk.CTkProgressBar(cal_frame, progress_color=COLOR_PRIMARY_GREEN)
        cal_bar.pack(pady=5, fill="x")
        cal_bar.set(macro_progress["calories"] / 100)
        ctk.CTkLabel(cal_frame, text=f"{int(macro_consumed['calories'])}/{int(macro_goals['calories'])}", font=ctk.CTkFont(size=12)).pack()
        
        # Protein progress
        protein_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        protein_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(protein_frame, text="Protein (g)", font=ctk.CTkFont(size=14, weight="bold")).pack()
        protein_bar = ctk.CTkProgressBar(protein_frame, progress_color="#FF6B6B")
        protein_bar.pack(pady=5, fill="x")
        protein_bar.set(macro_progress["protein"] / 100)
        ctk.CTkLabel(protein_frame, text=f"{macro_consumed['protein']:.1f}/{macro_goals['protein']:.1f}g", font=ctk.CTkFont(size=12)).pack()
        
        # Carbs progress
        carbs_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        carbs_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(carbs_frame, text="Carbs (g)", font=ctk.CTkFont(size=14, weight="bold")).pack()
        carbs_bar = ctk.CTkProgressBar(carbs_frame, progress_color="#4ECDC4")
        carbs_bar.pack(pady=5, fill="x")
        carbs_bar.set(macro_progress["carbs"] / 100)
        ctk.CTkLabel(carbs_frame, text=f"{macro_consumed['carbs']:.1f}/{macro_goals['carbs']:.1f}g", font=ctk.CTkFont(size=12)).pack()
        
        # Fat progress
        fat_frame = ctk.CTkFrame(progress_frame, fg_color="transparent")
        fat_frame.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(fat_frame, text="Fat (g)", font=ctk.CTkFont(size=14, weight="bold")).pack()
        fat_bar = ctk.CTkProgressBar(fat_frame, progress_color="#45B7D1")
        fat_bar.pack(pady=5, fill="x")
        fat_bar.set(macro_progress["fat"] / 100)
        ctk.CTkLabel(fat_frame, text=f"{macro_consumed['fat']:.1f}/{macro_goals['fat']:.1f}g", font=ctk.CTkFont(size=12)).pack()
        
        # --- Customize Macro Goals Card ---
        customize_card = ctk.CTkFrame(main_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        customize_card.pack(fill="x", pady=(0, 8), padx=2)
        
        ctk.CTkLabel(customize_card, text="Customize Your Macro Goals", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 5))
        
        goals_frame = ctk.CTkFrame(customize_card, fg_color="transparent")
        goals_frame.pack(fill="x", padx=10, pady=(0, 10))
        goals_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Get current goals to display in entry boxes
        current_goals = user.getMacroGoals()

        # Calories Goal Entry
        cal_goal_frame = ctk.CTkFrame(goals_frame, fg_color="transparent")
        cal_goal_frame.grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(cal_goal_frame, text="Calories", font=ctk.CTkFont(size=12, weight="bold")).pack()
        cal_goal_entry = ctk.CTkEntry(cal_goal_frame, placeholder_text="kcal")
        cal_goal_entry.insert(0, f"{current_goals['calories']:.0f}")
        cal_goal_entry.pack(fill="x")

        # Protein Goal Entry
        prot_goal_frame = ctk.CTkFrame(goals_frame, fg_color="transparent")
        prot_goal_frame.grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(prot_goal_frame, text="Protein (g)", font=ctk.CTkFont(size=12, weight="bold")).pack()
        prot_goal_entry = ctk.CTkEntry(prot_goal_frame, placeholder_text="grams")
        prot_goal_entry.insert(0, f"{current_goals['protein']:.1f}")
        prot_goal_entry.pack(fill="x")

        # Carbs Goal Entry
        carb_goal_frame = ctk.CTkFrame(goals_frame, fg_color="transparent")
        carb_goal_frame.grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(carb_goal_frame, text="Carbs (g)", font=ctk.CTkFont(size=12, weight="bold")).pack()
        carb_goal_entry = ctk.CTkEntry(carb_goal_frame, placeholder_text="grams")
        carb_goal_entry.insert(0, f"{current_goals['carbs']:.1f}")
        carb_goal_entry.pack(fill="x")

        # Fat Goal Entry
        fat_goal_frame = ctk.CTkFrame(goals_frame, fg_color="transparent")
        fat_goal_frame.grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(fat_goal_frame, text="Fat (g)", font=ctk.CTkFont(size=12, weight="bold")).pack()
        fat_goal_entry = ctk.CTkEntry(fat_goal_frame, placeholder_text="grams")
        fat_goal_entry.insert(0, f"{current_goals['fat']:.1f}")
        fat_goal_entry.pack(fill="x")

        def save_custom_goals():
            try:
                # Validate and get values
                cals = int(cal_goal_entry.get())
                prot = float(prot_goal_entry.get())
                carb = float(carb_goal_entry.get())
                fat = float(fat_goal_entry.get())
                # Basic range check
                if not (1000 < cals < 10000 and prot > 10 and carb > 10 and fat > 10):
                    raise ValueError("Values are out of reasonable range.")
                
                # Use the new setter method
                user.set_manual_goals(cals, prot, carb, fat)
                saveUser(user)
                messagebox.showinfo("Success", "Your custom goals have been saved.")
                self.showMacros() # Refresh page to show new goals
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter valid numbers for all goal fields.")

        def reset_goals():
            # Use the new reset method
            user.reset_to_automatic_goals()
            saveUser(user)
            messagebox.showinfo("Success", "Your goals have been reset to automatic calculation.")
            self.showMacros() # Refresh page

        # Buttons Frame
        buttons_frame = ctk.CTkFrame(customize_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(5, 15))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(buttons_frame, text="💾 Save Custom Goals", command=save_custom_goals, fg_color=COLOR_PRIMARY_GREEN).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(buttons_frame, text="🔄 Reset to Automatic", command=reset_goals, fg_color=COLOR_SECONDARY_BLUE).grid(row=0, column=1, padx=5, sticky="ew")
        
        # --- Quick Nutrition Log Card ---
        log_card = ctk.CTkFrame(main_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        log_card.pack(fill="x", pady=(0, 8), padx=2)
        
        ctk.CTkLabel(log_card, text="Detailed Nutrition Log", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 5))
        
        # Enhanced log form
        log_form_frame = ctk.CTkFrame(log_card, fg_color="transparent")
        log_form_frame.pack(fill="x", padx=10, pady=(0, 10))
        log_form_frame.grid_columnconfigure(0, weight=1)
        log_form_frame.grid_columnconfigure(1, weight=1)
        log_form_frame.grid_columnconfigure(2, weight=1)
        log_form_frame.grid_columnconfigure(3, weight=1)
        
        # Food entry
        food_frame = ctk.CTkFrame(log_form_frame, fg_color="transparent")
        food_frame.grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkLabel(food_frame, text="Food Item", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        food_entry = ctk.CTkEntry(food_frame, placeholder_text="e.g., Chicken Breast")
        food_entry.pack(fill="x", pady=2)
        
        # Calories entry
        cal_frame = ctk.CTkFrame(log_form_frame, fg_color="transparent")
        cal_frame.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(cal_frame, text="Calories", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        cal_entry = ctk.CTkEntry(cal_frame, placeholder_text="e.g., 165")
        cal_entry.pack(fill="x", pady=2)
        
        # Protein entry
        protein_frame = ctk.CTkFrame(log_form_frame, fg_color="transparent")
        protein_frame.grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkLabel(protein_frame, text="Protein (g)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        protein_entry = ctk.CTkEntry(protein_frame, placeholder_text="e.g., 31")
        protein_entry.pack(fill="x", pady=2)
        
        # Serving size entry
        serving_frame = ctk.CTkFrame(log_form_frame, fg_color="transparent")
        serving_frame.grid(row=0, column=3, padx=5, sticky="ew")
        ctk.CTkLabel(serving_frame, text="Serving (g)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        serving_entry = ctk.CTkEntry(serving_frame, placeholder_text="e.g., 100")
        serving_entry.pack(fill="x", pady=2)
        
        # Second row for additional macros
        carbs_frame = ctk.CTkFrame(log_form_frame, fg_color="transparent")
        carbs_frame.grid(row=1, column=0, padx=5, pady=(5, 0), sticky="ew")
        ctk.CTkLabel(carbs_frame, text="Carbs (g)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        carbs_entry = ctk.CTkEntry(carbs_frame, placeholder_text="e.g., 0")
        carbs_entry.pack(fill="x", pady=2)
        
        fat_frame = ctk.CTkFrame(log_form_frame, fg_color="transparent")
        fat_frame.grid(row=1, column=1, padx=5, pady=(5, 0), sticky="ew")
        ctk.CTkLabel(fat_frame, text="Fat (g)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        fat_entry = ctk.CTkEntry(fat_frame, placeholder_text="e.g., 3.6")
        fat_entry.pack(fill="x", pady=2)
        
        # Date picker for meal logging
        meal_date_frame = ctk.CTkFrame(log_form_frame, fg_color="transparent")
        meal_date_frame.grid(row=1, column=2, padx=5, pady=(5, 0), sticky="ew")
        ctk.CTkLabel(meal_date_frame, text="Date", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        if CALENDAR_AVAILABLE:
            meal_date_picker = DateEntry(meal_date_frame, width=10, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        else:
            meal_date_picker = DateEntry(meal_date_frame)
        meal_date_picker.pack(fill="x", pady=2)
        
        # Log button
        log_btn_frame = ctk.CTkFrame(log_card, fg_color="transparent")
        log_btn_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        def detailed_log_food():
            """Enhanced food logging with full macro tracking"""
            food_name = food_entry.get().strip()
            
            # Get all values
            entries = {
                'calories': cal_entry.get().strip(),
                'protein': protein_entry.get().strip(),
                'carbs': carbs_entry.get().strip(),
                'fat': fat_entry.get().strip(),
                'serving': serving_entry.get().strip()
            }
            
            # Validation
            if not food_name:
                messagebox.showwarning("Input Error", "Please enter a food item")
                return
            
            # Validate and convert numeric values
            try:
                calories = float(entries['calories']) if entries['calories'] else 0
                protein = float(entries['protein']) if entries['protein'] else 0
                carbs = float(entries['carbs']) if entries['carbs'] else 0
                fat = float(entries['fat']) if entries['fat'] else 0
                serving = float(entries['serving']) if entries['serving'] else 100
                
                # Range validation
                if calories < 0 or calories > 5000:
                    raise ValueError("Calories must be between 0 and 5000")
                if any(val < 0 or val > 1000 for val in [protein, carbs, fat]):
                    raise ValueError("Macro values must be between 0 and 1000g")
                if serving <= 0 or serving > 2000:
                    raise ValueError("Serving size must be between 1 and 2000g")
                    
            except ValueError as e:
                messagebox.showwarning("Input Error", f"Invalid input: {str(e)}")
                return
            
            # Scale values based on serving size if not 100g
            if serving != 100:
                scale_factor = serving / 100
                calories *= scale_factor
                protein *= scale_factor
                carbs *= scale_factor
                fat *= scale_factor
            
            # Log to user account
            selected_date = meal_date_picker.get_date()
            log_date = selected_date.strftime("%Y-%m-%d")
            
            # Add to user's daily totals
            user.addMacros(calories, protein, carbs, fat)
            saveUser(user)
            
            # Clear all entries
            for entry in [food_entry, cal_entry, protein_entry, carbs_entry, fat_entry, serving_entry]:
                entry.delete(0, ctk.END)
            meal_date_picker.set_date(datetime.now().date())
            
            messagebox.showinfo("Logged", f"Added {food_name} ({calories:.1f} cal, {protein:.1f}g protein) on {log_date}")
            
            # Refresh displays
            self.showMacros()
        
        ctk.CTkButton(log_btn_frame, text="📊 Log Detailed Nutrition", fg_color=COLOR_PRIMARY_GREEN, 
                     text_color=COLOR_BTN_TXT, corner_radius=8, height=35, 
                     font=ctk.CTkFont(size=14, weight="bold"), command=detailed_log_food).pack(fill="x")
        
        # Quick add suggestions
        suggestions_frame = ctk.CTkFrame(log_card, fg_color="transparent")
        suggestions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(suggestions_frame, text="Quick Add Common Foods:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        quick_foods_frame = ctk.CTkFrame(suggestions_frame, fg_color="transparent")
        quick_foods_frame.pack(fill="x")
        quick_foods_frame.grid_columnconfigure(0, weight=1)
        quick_foods_frame.grid_columnconfigure(1, weight=1)
        quick_foods_frame.grid_columnconfigure(2, weight=1)
        quick_foods_frame.grid_columnconfigure(3, weight=1)
        
        # Common foods with their macro profiles
        common_foods = [
            ("🍗 Chicken (100g)", 165, 31, 0, 3.6),
            ("🥚 Egg (1 large)", 155, 13, 1.1, 11),
            ("🍌 Banana (1 med)", 89, 1.1, 23, 0.3),
            ("🥑 Avocado (1/2)", 160, 2, 9, 15)
        ]
        
        def quick_add_food(name, calories, protein, carbs, fat):
            user.addMacros(calories, protein, carbs, fat)
            saveUser(user)
            messagebox.showinfo("Quick Added", f"Added {name} to your log!")
            self.showMacros()
        
        for i, (name, cal, prot, carb, fat_val) in enumerate(common_foods):
            btn = ctk.CTkButton(quick_foods_frame, text=name, width=120, height=30,
                               fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT,
                               corner_radius=6, font=ctk.CTkFont(size=11),
                               command=lambda n=name, c=cal, p=prot, cr=carb, f=fat_val: quick_add_food(n, c, p, cr, f))
            btn.grid(row=0, column=i, padx=2, sticky="ew")
        
        # --- AI-Generated Meal Plan Card ---
        meal_plan_card = ctk.CTkFrame(main_container, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        meal_plan_card.pack(fill="x", pady=(0, 8), padx=2)
        
        ctk.CTkLabel(meal_plan_card, text="🤖 AI-Generated Meal Plan", font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(10, 5))
        ctk.CTkLabel(meal_plan_card, text="Get personalized meal recommendations based on your goals and preferences", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=12)).pack(pady=(0, 10))
        
        # Meal plan preferences form
        preferences_frame = ctk.CTkFrame(meal_plan_card, fg_color="transparent")
        preferences_frame.pack(fill="x", padx=10, pady=(0, 10))
        preferences_frame.grid_columnconfigure(0, weight=1)
        preferences_frame.grid_columnconfigure(1, weight=1)
        preferences_frame.grid_columnconfigure(2, weight=1)
        
        # Diet preference dropdown
        diet_frame = ctk.CTkFrame(preferences_frame, fg_color="transparent")
        diet_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(diet_frame, text="Diet Type", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        diet_options = ["Balanced", "High Protein", "Low Carb", "Vegetarian", "Vegan", "Mediterranean", "Keto"]
        diet_dropdown = ctk.CTkComboBox(diet_frame, values=diet_options, state="readonly")
        diet_dropdown.set("Balanced")
        diet_dropdown.pack(fill="x", pady=2)
        
        # Meal count dropdown
        meals_frame = ctk.CTkFrame(preferences_frame, fg_color="transparent")
        meals_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(meals_frame, text="Meals per Day", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        meal_count_options = ["3 meals", "4 meals", "5 meals", "6 meals"]
        meals_dropdown = ctk.CTkComboBox(meals_frame, values=meal_count_options, state="readonly")
        meals_dropdown.set("3 meals")
        meals_dropdown.pack(fill="x", pady=2)
        
        # Allergies/restrictions entry
        restrictions_frame = ctk.CTkFrame(preferences_frame, fg_color="transparent")
        restrictions_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(restrictions_frame, text="Allergies/Restrictions", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        restrictions_entry = ctk.CTkEntry(restrictions_frame, placeholder_text="e.g., nuts, dairy, gluten")
        restrictions_entry.pack(fill="x", pady=2)
        
        # Generate meal plan button and display area
        generate_frame = ctk.CTkFrame(meal_plan_card, fg_color="transparent")
        generate_frame.pack(fill="x", padx=10, pady=(5, 15))
        
        def generate_meal_plan():
            """Generate an AI-style meal plan based on user preferences and goals"""
            diet_type = diet_dropdown.get()
            meal_count = int(meals_dropdown.get().split()[0])
            restrictions = restrictions_entry.get().strip().lower()
            goals = user.getMacroGoals()
            
            # Clear previous meal plan display
            for widget in meal_plan_display.winfo_children():
                widget.destroy()
            
            # Generate meal plan based on preferences
            meal_plan = self._generateSmartMealPlan(diet_type, meal_count, restrictions, goals)
            
            # Display the generated meal plan
            ctk.CTkLabel(meal_plan_display, text=f"🍽️ Your {diet_type} Meal Plan ({meal_count} meals/day)", 
                        font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(5, 10))
            
            daily_totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
            
            for i, meal in enumerate(meal_plan):
                meal_frame = ctk.CTkFrame(meal_plan_display, fg_color=COLOR_LIGHT_GREY, corner_radius=8)
                meal_frame.pack(fill="x", pady=2, padx=5)
                
                # Meal header
                meal_header = ctk.CTkFrame(meal_frame, fg_color="transparent")
                meal_header.pack(fill="x", padx=10, pady=(8, 2))
                ctk.CTkLabel(meal_header, text=f"{meal['name']}", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
                
                # Meal items
                for item in meal['items']:
                    item_frame = ctk.CTkFrame(meal_frame, fg_color="transparent")
                    item_frame.pack(fill="x", padx=15, pady=1)
                    item_frame.grid_columnconfigure(0, weight=1)
                    
                    ctk.CTkLabel(item_frame, text=f"• {item['food']}", anchor="w", font=ctk.CTkFont(size=11)).grid(row=0, column=0, sticky="w")
                    ctk.CTkLabel(item_frame, text=f"{item['calories']}cal | {item['protein']}g protein", 
                                font=ctk.CTkFont(size=10), text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=1, sticky="e")
                    
                    # Add to daily totals
                    daily_totals["calories"] += item["calories"]
                    daily_totals["protein"] += item["protein"]
                    daily_totals["carbs"] += item["carbs"]
                    daily_totals["fat"] += item["fat"]
                
                # Quick add button for the whole meal
                add_meal_btn = ctk.CTkButton(meal_frame, text=f"+ Add {meal['name']}", height=25, width=120,
                                           fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=6,
                                           font=ctk.CTkFont(size=10), 
                                           command=lambda m=meal: self._addMealToLog(m))
                add_meal_btn.pack(pady=(2, 8), anchor="e", padx=10)
            
            # Display daily totals
            totals_frame = ctk.CTkFrame(meal_plan_display, fg_color=COLOR_SECONDARY_BLUE, corner_radius=8)
            totals_frame.pack(fill="x", pady=(10, 5), padx=5)
            
            ctk.CTkLabel(totals_frame, text="📊 Daily Totals", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_BTN_TXT).pack(pady=(8, 2))
            
            totals_info = ctk.CTkFrame(totals_frame, fg_color="transparent")
            totals_info.pack(fill="x", padx=10, pady=(0, 8))
            totals_info.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            ctk.CTkLabel(totals_info, text=f"Calories\n{int(daily_totals['calories'])}", 
                        font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_BTN_TXT).grid(row=0, column=0)
            ctk.CTkLabel(totals_info, text=f"Protein\n{daily_totals['protein']:.1f}g", 
                        font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_BTN_TXT).grid(row=0, column=1)
            ctk.CTkLabel(totals_info, text=f"Carbs\n{daily_totals['carbs']:.1f}g", 
                        font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_BTN_TXT).grid(row=0, column=2)
            ctk.CTkLabel(totals_info, text=f"Fat\n{daily_totals['fat']:.1f}g", 
                        font=ctk.CTkFont(size=11, weight="bold"), text_color=COLOR_BTN_TXT).grid(row=0, column=3)
        
        ctk.CTkButton(generate_frame, text="🤖 Generate Personalized Meal Plan", fg_color=COLOR_PRIMARY, 
                     text_color=COLOR_BTN_TXT, corner_radius=8, height=35, 
                     font=ctk.CTkFont(size=14, weight="bold"), command=generate_meal_plan).pack(fill="x")
        
        # Scrollable meal plan display area
        meal_plan_display = ctk.CTkScrollableFrame(meal_plan_card, height=300, fg_color="transparent")
        meal_plan_display.pack(fill="both", expand=True, padx=10, pady=(10, 15))
        
        # Initial message
        ctk.CTkLabel(meal_plan_display, text="👆 Click 'Generate Personalized Meal Plan' to get started!", 
                    text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=12)).pack(pady=20)

    def _generateSmartMealPlan(self, diet_type, meal_count, restrictions, goals):
        """
        Generate an intelligent meal plan based on user preferences and macro goals.
        Uses a comprehensive food database with realistic nutritional profiles.
        """
        # Comprehensive food database organized by categories and diet types
        food_database = {
            "proteins": {
                "balanced": [
                    {"food": "Grilled Chicken Breast (150g)", "calories": 248, "protein": 46.5, "carbs": 0, "fat": 5.4},
                    {"food": "Salmon Fillet (120g)", "calories": 242, "protein": 33.6, "carbs": 0, "fat": 11.0},
                    {"food": "Lean Ground Turkey (100g)", "calories": 189, "protein": 29.1, "carbs": 0, "fat": 7.4},
                    {"food": "Eggs (2 large)", "calories": 310, "protein": 26, "carbs": 2.2, "fat": 22},
                    {"food": "Greek Yogurt (200g)", "calories": 130, "protein": 20, "carbs": 9, "fat": 0.4},
                    {"food": "Cottage Cheese (150g)", "calories": 124, "protein": 17.3, "carbs": 5.4, "fat": 2.3}
                ],
                "high_protein": [
                    {"food": "Protein Powder + Water (1 scoop)", "calories": 120, "protein": 25, "carbs": 3, "fat": 1},
                    {"food": "Chicken Breast (200g)", "calories": 330, "protein": 62, "carbs": 0, "fat": 7.2},
                    {"food": "Lean Beef (150g)", "calories": 312, "protein": 48.8, "carbs": 0, "fat": 11.7},
                    {"food": "Tuna (1 can, 150g)", "calories": 179, "protein": 39.3, "carbs": 0, "fat": 1.3},
                    {"food": "Egg Whites (6 whites)", "calories": 102, "protein": 21.2, "carbs": 1.4, "fat": 0.3}
                ],
                "vegetarian": [
                    {"food": "Tofu (150g)", "calories": 181, "protein": 19.9, "carbs": 4.3, "fat": 11},
                    {"food": "Lentils (1 cup cooked)", "calories": 230, "protein": 18, "carbs": 40, "fat": 0.8},
                    {"food": "Black Beans (1 cup)", "calories": 227, "protein": 15.2, "carbs": 40.8, "fat": 0.9},
                    {"food": "Greek Yogurt (200g)", "calories": 130, "protein": 20, "carbs": 9, "fat": 0.4},
                    {"food": "Quinoa (1 cup cooked)", "calories": 222, "protein": 8.1, "carbs": 39.4, "fat": 3.6}
                ],
                "vegan": [
                    {"food": "Tempeh (100g)", "calories": 192, "protein": 20.3, "carbs": 7.6, "fat": 10.8},
                    {"food": "Chickpeas (1 cup)", "calories": 269, "protein": 14.5, "carbs": 45, "fat": 4.2},
                    {"food": "Hemp Seeds (3 tbsp)", "calories": 170, "protein": 10, "carbs": 2.5, "fat": 12},
                    {"food": "Peanut Butter (2 tbsp)", "calories": 188, "protein": 8, "carbs": 8, "fat": 16},
                    {"food": "Almond Butter (2 tbsp)", "calories": 196, "protein": 7.2, "carbs": 7.5, "fat": 18.3}
                ]
            },
            "carbs": {
                "balanced": [
                    {"food": "Brown Rice (1 cup cooked)", "calories": 216, "protein": 5, "carbs": 45, "fat": 1.8},
                    {"food": "Sweet Potato (medium, 200g)", "calories": 180, "protein": 4, "carbs": 41.4, "fat": 0.3},
                    {"food": "Oatmeal (1 cup cooked)", "calories": 154, "protein": 5.4, "carbs": 28, "fat": 3.2},
                    {"food": "Whole Wheat Bread (2 slices)", "calories": 138, "protein": 7.4, "carbs": 23, "fat": 2.5},
                    {"food": "Banana (medium)", "calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4}
                ],
                "low_carb": [
                    {"food": "Cauliflower Rice (1 cup)", "calories": 25, "protein": 2, "carbs": 5, "fat": 0.3},
                    {"food": "Zucchini Noodles (1 cup)", "calories": 20, "protein": 1.5, "carbs": 4, "fat": 0.4},
                    {"food": "Shirataki Noodles (1 package)", "calories": 20, "protein": 1, "carbs": 6, "fat": 0},
                    {"food": "Berries Mix (1/2 cup)", "calories": 42, "protein": 0.6, "carbs": 10.2, "fat": 0.2}
                ],
                "keto": [
                    {"food": "Avocado (1/2 medium)", "calories": 160, "protein": 2, "carbs": 9, "fat": 15},
                    {"food": "Macadamia Nuts (30g)", "calories": 204, "protein": 2.2, "carbs": 3.9, "fat": 21.5}
                ]
            },
            "vegetables": [
                {"food": "Broccoli (1 cup)", "calories": 31, "protein": 3, "carbs": 6, "fat": 0.4},
                {"food": "Spinach (2 cups)", "calories": 14, "protein": 1.8, "carbs": 2.2, "fat": 0.2},
                {"food": "Bell Peppers (1 cup)", "calories": 30, "protein": 1, "carbs": 7, "fat": 0.3},
                {"food": "Asparagus (1 cup)", "calories": 27, "protein": 3, "carbs": 5.2, "fat": 0.2},
                {"food": "Green Beans (1 cup)", "calories": 35, "protein": 2, "carbs": 8, "fat": 0.1},
                {"food": "Brussels Sprouts (1 cup)", "calories": 38, "protein": 3, "carbs": 8, "fat": 0.3},
                {"food": "Kale (2 cups)", "calories": 33, "protein": 2.9, "carbs": 6.7, "fat": 0.6}
            ],
            "healthy_fats": [
                {"food": "Olive Oil (1 tbsp)", "calories": 119, "protein": 0, "carbs": 0, "fat": 13.5},
                {"food": "Avocado (1/2 medium)", "calories": 160, "protein": 2, "carbs": 9, "fat": 15},
                {"food": "Almonds (30g)", "calories": 173, "protein": 6.4, "carbs": 6.1, "fat": 14.8},
                {"food": "Walnuts (30g)", "calories": 196, "protein": 4.6, "carbs": 4.1, "fat": 19.6},
                {"food": "Chia Seeds (2 tbsp)", "calories": 138, "protein": 4.7, "carbs": 12, "fat": 8.7}
            ]
        }
        
        # Meal templates based on meal count
        meal_templates = {
            3: [
                {"name": "🌅 Breakfast", "protein_ratio": 0.25, "carb_ratio": 0.35, "fat_ratio": 0.30},
                {"name": "🍽️ Lunch", "protein_ratio": 0.40, "carb_ratio": 0.35, "fat_ratio": 0.35},
                {"name": "🌙 Dinner", "protein_ratio": 0.35, "carb_ratio": 0.30, "fat_ratio": 0.35}
            ],
            4: [
                {"name": "🌅 Breakfast", "protein_ratio": 0.25, "carb_ratio": 0.35, "fat_ratio": 0.25},
                {"name": "🍽️ Lunch", "protein_ratio": 0.35, "carb_ratio": 0.35, "fat_ratio": 0.30},
                {"name": "🥪 Snack", "protein_ratio": 0.15, "carb_ratio": 0.15, "fat_ratio": 0.20},
                {"name": "🌙 Dinner", "protein_ratio": 0.25, "carb_ratio": 0.15, "fat_ratio": 0.25}
            ],
            5: [
                {"name": "🌅 Breakfast", "protein_ratio": 0.20, "carb_ratio": 0.30, "fat_ratio": 0.25},
                {"name": "🥪 Mid-Morning", "protein_ratio": 0.15, "carb_ratio": 0.20, "fat_ratio": 0.15},
                {"name": "🍽️ Lunch", "protein_ratio": 0.30, "carb_ratio": 0.25, "fat_ratio": 0.25},
                {"name": "🍎 Afternoon", "protein_ratio": 0.15, "carb_ratio": 0.15, "fat_ratio": 0.15},
                {"name": "🌙 Dinner", "protein_ratio": 0.20, "carb_ratio": 0.10, "fat_ratio": 0.20}
            ],
            6: [
                {"name": "🌅 Breakfast", "protein_ratio": 0.18, "carb_ratio": 0.25, "fat_ratio": 0.20},
                {"name": "🥪 Mid-Morning", "protein_ratio": 0.12, "carb_ratio": 0.15, "fat_ratio": 0.15},
                {"name": "🍽️ Lunch", "protein_ratio": 0.25, "carb_ratio": 0.25, "fat_ratio": 0.25},
                {"name": "🍎 Afternoon", "protein_ratio": 0.15, "carb_ratio": 0.15, "fat_ratio": 0.15},
                {"name": "🌙 Dinner", "protein_ratio": 0.20, "carb_ratio": 0.15, "fat_ratio": 0.15},
                {"name": "🌜 Evening", "protein_ratio": 0.10, "carb_ratio": 0.05, "fat_ratio": 0.10}
            ]
        }
        
        # Filter foods based on diet type and restrictions
        def filter_foods(food_list, diet_type, restrictions):
            filtered = []
            for food in food_list:
                food_name = food["food"].lower()
                
                # Apply restrictions filter
                if restrictions:
                    restriction_terms = [term.strip() for term in restrictions.split(',')]
                    if any(term in food_name for term in restriction_terms):
                        continue
                
                # Diet-specific filtering
                if diet_type.lower() == "vegan":
                    if any(term in food_name for term in ["chicken", "beef", "turkey", "salmon", "tuna", "egg", "yogurt", "cheese"]):
                        continue
                elif diet_type.lower() == "vegetarian":
                    if any(term in food_name for term in ["chicken", "beef", "turkey", "salmon", "tuna"]):
                        continue
                elif diet_type.lower() == "keto":
                    if food["carbs"] > 10:  # Strict carb limit for keto
                        continue
                
                filtered.append(food)
            return filtered
        
        # Get appropriate protein sources
        protein_key = diet_type.lower().replace(" ", "_")
        if protein_key not in food_database["proteins"]:
            protein_key = "balanced"
        
        proteins = filter_foods(food_database["proteins"][protein_key], diet_type, restrictions)
        
        # Get appropriate carb sources
        carb_key = "low_carb" if diet_type.lower() in ["low carb", "keto"] else "balanced"
        if diet_type.lower() == "keto":
            carb_key = "keto"
        
        carbs = filter_foods(food_database["carbs"].get(carb_key, food_database["carbs"]["balanced"]), diet_type, restrictions)
        vegetables = filter_foods(food_database["vegetables"], diet_type, restrictions)
        fats = filter_foods(food_database["healthy_fats"], diet_type, restrictions)
        
        # Generate meal plan
        meal_plan = []
        templates = meal_templates[meal_count]
        
        for template in templates:
            meal = {
                "name": template["name"],
                "items": []
            }
            
            # Calculate target macros for this meal
            target_calories = goals["calories"] * (template["protein_ratio"] + template["carb_ratio"] + template["fat_ratio"])
            target_protein = goals["protein"] * template["protein_ratio"]
            
            # Select foods for the meal
            meal_items = []
            
            # Add a protein source
            if proteins:
                protein_choice = random.choice(proteins)
                meal_items.append(protein_choice)
            
            # Add carbs (unless keto)
            if carbs and diet_type.lower() != "keto":
                carb_choice = random.choice(carbs)
                meal_items.append(carb_choice)
            
            # Add vegetables
            if vegetables:
                veg_choice = random.choice(vegetables)
                meal_items.append(veg_choice)
            
            # Add healthy fats if needed
            current_fat = sum(item["fat"] for item in meal_items)
            target_fat = goals["fat"] * template["fat_ratio"]
            
            if current_fat < target_fat * 0.7 and fats:
                fat_choice = random.choice(fats)
                meal_items.append(fat_choice)
            
            meal["items"] = meal_items
            meal_plan.append(meal)
        
        return meal_plan

    def _addMealToLog(self, meal):
        """Add all items from a meal to the user's nutrition log"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for item in meal["items"]:
            total_calories += item["calories"]
            total_protein += item["protein"]
            total_carbs += item["carbs"]
            total_fat += item["fat"]
        
        # Add to user's daily totals
        self.currentUser.addMacros(total_calories, total_protein, total_carbs, total_fat)
        saveUser(self.currentUser)
        
        # Show confirmation
        messagebox.showinfo("Meal Added", 
                           f"Added {meal['name']} to your log!\n"
                           f"Calories: {int(total_calories)} | Protein: {total_protein:.1f}g\n"
                           f"Carbs: {total_carbs:.1f}g | Fat: {total_fat:.1f}g")
        
        # Refresh the macros page to show updated progress
        self.showMacros()

    def showFeed(self):
        """Display social feed page with admin approval and unique likes."""
        cf = self.contentFrame
        for widget in cf.winfo_children():
            widget.destroy()
        card = ctk.CTkFrame(cf, fg_color=COLOR_WIDGET_BG, corner_radius=12, border_width=1, border_color=COLOR_MEDIUM_GREY)
        card.pack(pady=10, padx=10, fill="both", expand=True)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Community Feed", font=ctk.CTkFont(size=26, weight="bold"), text_color=COLOR_PRIMARY).pack(pady=(20, 12))

        # Post creation area
        post_frame = ctk.CTkFrame(card, fg_color=COLOR_LIGHT_GREY, corner_radius=10, border_width=1, border_color=COLOR_MEDIUM_GREY)
        post_frame.pack(pady=8, padx=15, fill="x")
        postEntry = ctk.CTkEntry(post_frame, width=500, placeholder_text="Share your progress or ask a question (280 chars max)",
                                 fg_color=COLOR_WHITE_CLEAN, text_color=COLOR_TEXT, corner_radius=8)
        postEntry.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(post_frame, text="Post Update", fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: self._postUpdate(postEntry.get())).pack(pady=10, padx=10, anchor="e")

        # Sorting and Search area
        control_frame = ctk.CTkFrame(card, fg_color="transparent")
        control_frame.pack(pady=(8, 5), padx=15, fill="x")
        control_frame.grid_columnconfigure((0,1,2,3), weight=1)

        ctk.CTkButton(control_frame, text="Sort by Date", fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: self._sortFeed("date")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(control_frame, text="Sort by Likes", fg_color=COLOR_ACCENT2, text_color=COLOR_BTN_SECONDARY_TXT, corner_radius=8, command=lambda: self._sortFeed("likes")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        searchEntry = ctk.CTkEntry(control_frame, width=200, placeholder_text="Search posts...", fg_color=COLOR_ACCENT, text_color=COLOR_TEXT, corner_radius=8)
        searchEntry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(control_frame, text="Search", fg_color=COLOR_SECONDARY_BLUE, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda: self._searchFeed(searchEntry.get())).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Posts display area
        posts_display_frame = ctk.CTkScrollableFrame(card, fg_color="transparent")
        posts_display_frame.pack(fill="both", expand=True, padx=15, pady=8)

        # Determine which posts to show based on user type
        is_admin = isinstance(self.currentUser, AdminUser)
        if is_admin:
            posts_to_show = self.posts
        else:
            posts_to_show = [p for p in self.posts if p.get("approved") == "True"]

        if not posts_to_show:
            ctk.CTkLabel(posts_display_frame, text="No posts to display.", text_color=COLOR_TEXT_SECONDARY, font=ctk.CTkFont(size=14)).pack(pady=20)

        current_user_id = self.currentUser.getStudentId()

        for post in posts_to_show:
            is_approved = post.get("approved", "False") == "True"
            
            # Admin sees unapproved posts with a different background color
            post_bg_color = COLOR_WIDGET_BG
            if is_admin and not is_approved:
                post_bg_color = "#FFF5E1" # A light yellow for pending posts

            frame = ctk.CTkFrame(posts_display_frame, fg_color=post_bg_color, corner_radius=10, border_width=1, border_color=COLOR_MEDIUM_GREY)
            frame.pack(pady=8, padx=10, fill="x")

            # --- NEW: Header for Author and Timestamp ---
            header_frame = ctk.CTkFrame(frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(8, 2))
            header_frame.grid_columnconfigure(0, weight=1) # Author on left
            header_frame.grid_columnconfigure(1, weight=1) # Timestamp on right

            # Author Label
            author_id = post.get("authorId", "Unknown User")
            ctk.CTkLabel(header_frame, text=f"👤 Posted by: {author_id}", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT).grid(row=0, column=0, sticky="w")
            
            # Formatted Timestamp Label
            try:
                # Parse the ISO format timestamp stored in the CSV
                dt_object = datetime.fromisoformat(post.get("timestamp"))
                # Format it into a user-friendly string
                formatted_time = dt_object.strftime("%b %d, %Y at %I:%M %p")
            except (ValueError, TypeError):
                formatted_time = "" # Fallback for old or malformed timestamps
            
            ctk.CTkLabel(header_frame, text=formatted_time, font=ctk.CTkFont(size=11), text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=1, sticky="e")
            
            # Add "PENDING APPROVAL" label for admins
            if is_admin and not is_approved:
                ctk.CTkLabel(frame, text="PENDING APPROVAL", font=ctk.CTkFont(size=10, weight="bold"), text_color="#D97706").pack(pady=(0,2), padx=15, anchor="w")

            # Post content
            post_text_label = ctk.CTkLabel(frame, text=post.get("content", "No content"), wraplength=450, font=ctk.CTkFont(size=14), text_color=COLOR_TEXT, justify="left")
            post_text_label.pack(pady=(5, 5), padx=15, anchor="w")

            # Post metadata and actions
            meta_frame = ctk.CTkFrame(frame, fg_color="transparent")
            meta_frame.pack(fill="x", padx=10, pady=(0, 10))

            # --- Likes and Comments ---
            likers = post.get('likedBy', '').split('|')
            user_has_liked = current_user_id in likers

            like_btn_text = f"👍 {post.get('likes', 0)} Liked" if user_has_liked else f"👍 {post.get('likes', 0)} Like"
            like_btn_state = "disabled" if user_has_liked else "normal"
            like_btn_color = COLOR_SECONDARY_BLUE if user_has_liked else "transparent"
            
            ctk.CTkButton(meta_frame, text=like_btn_text, fg_color=like_btn_color, text_color=COLOR_TEXT_SECONDARY, hover_color=COLOR_LIGHT_GREY, state=like_btn_state, command=lambda p=post: self._likePost(p)).pack(side="left", padx=5)
            ctk.CTkButton(meta_frame, text="💬 Comment", fg_color="transparent", text_color=COLOR_TEXT_SECONDARY, hover_color=COLOR_LIGHT_GREY, command=lambda p=post: messagebox.showinfo("Comment", "Commenting coming soon!")).pack(side="left", padx=5)

            # --- Admin/Edit/Delete actions ---
            action_frame = ctk.CTkFrame(meta_frame, fg_color="transparent")
            action_frame.pack(side="right", padx=5)

            if is_admin and not is_approved:
                ctk.CTkButton(action_frame, text="✅ Approve", fg_color=COLOR_PRIMARY_GREEN, text_color=COLOR_BTN_TXT, corner_radius=8, command=lambda p=post: self._approvePost(p)).pack(side="left", padx=5)
            
            is_author = current_user_id == post.get("authorId")
            if is_admin or is_author:
                ctk.CTkButton(action_frame, text="🗑️ Delete", fg_color="#E57373", text_color=COLOR_WHITE_CLEAN, corner_radius=8, command=lambda p=post: self._deletePost(p)).pack(side="left", padx=5)
                
    def _editPost(self, post):
        """Edit post functionality (placeholder)."""
        messagebox.showinfo("Edit Post", "Post editing coming soon!")
    
    def _sortFeed(self, sort_by):
        """Sort feed by date or likes using selection sort."""
        # JUSTIFICATION (Algorithmic Logic): The 'reverse=True' parameter is
        # deliberately used to sort posts by date (newest first) and likes (most
        # popular first). This provides the standard, expected user experience for a
        # social media feed, enhancing usability.
        if sort_by == "date":
            # Timestamps are strings and can be compared directly. Sort descending (newest first).
            self.posts = selection_sort(self.posts, "timestamp", reverse=True)
        elif sort_by == "likes":
            # 'likes' are stored as strings, so we use the type_converter 
            # to treat them as integers for sorting.
            self.posts = selection_sort(self.posts, "likes", reverse=True, type_converter=int)
        
        # Refresh the feed page to show the newly sorted posts
        self.showFeed()
    
    def _searchFeed(self, search_term):
        """Search posts by content."""
        if not search_term.strip():
            messagebox.showwarning("Search", "Enter a search term.")
            return
        filtered_posts = [p for p in self.posts if search_term.lower() in p.get("content", "").lower()]
        if not filtered_posts:
            messagebox.showinfo("Search Results", "No posts found matching your search.")
        else:
            messagebox.showinfo("Search Results", f"Found {len(filtered_posts)} posts. (Full search filtering coming soon!)")

    # --- Feed interaction methods (_postUpdate, _likePost, etc.) ---
    def _postUpdate(self, content):
        if not self.currentUser: messagebox.showwarning("Post Error", "You must be logged in."); return
        if not content.strip() or len(content) > 280: messagebox.showwarning("Post Error", "Post cannot be empty and must be under 280 characters."); return
        post = {
            "postID": str(len(self.posts) + 1), 
            "content": content, 
            "likes": "0", 
            "comments": "", 
            "approved": "False",  # Posts now start as unapproved
            "authorId": self.currentUser.getStudentId(), 
            "timestamp": datetime.now().isoformat(),
            "likedBy": ""  # New field to track who has liked the post
        }
        # Add the new fieldname to the appendCsv call
        appendCsv(POSTS_CSV, post, ["postID", "content", "likes", "comments", "approved", "authorId", "timestamp", "likedBy"])
        self.posts.append(post)
        messagebox.showinfo("Post Submitted", "Your post has been submitted for approval by an administrator.")
        self.showFeed()
    def _likePost(self, post):
        user_id = self.currentUser.getStudentId()
        
        # Ensure 'likedBy' key exists and is a string, then split into a list
        likers = post.get('likedBy', '').split('|')
        
        if user_id in likers:
            messagebox.showinfo("Already Liked", "You have already liked this post.")
            return

        # Add user to likers list and update count
        likers.append(user_id)
        post['likedBy'] = "|".join(filter(None, likers)) # filter(None, ...) removes empty strings
        post["likes"] = str(int(post.get("likes", 0)) + 1)
        
        self._update_and_save_posts()
        self.showFeed()
    def _approvePost(self, post):
        if self.currentUser and isinstance(self.currentUser, AdminUser): 
            post["approved"] = "True"; self._update_and_save_posts(); self.showFeed()
    def _deletePost(self, post):
        # An admin can delete any post, a regular user can only delete their own.
        is_author = self.currentUser.getStudentId() == post.get("authorId")
        if self.currentUser and (isinstance(self.currentUser, AdminUser) or is_author):
            if messagebox.askyesno("Delete Post", "Are you sure?"): 
                self.posts = [p for p in self.posts if p.get("postID") != post.get("postID")]
                self._update_and_save_posts(from_memory=True)
                self.showFeed()
    def _update_and_save_posts(self, from_memory=False):
        all_posts = self.posts if from_memory else readCsv(POSTS_CSV)
        if not from_memory:
            for i, p_disk in enumerate(all_posts):
                for p_mem in self.posts:
                    if p_disk.get("postID") == p_mem.get("postID"): all_posts[i] = p_mem; break
        # Add the new fieldname to the writeCsv call
        writeCsv(POSTS_CSV, all_posts, ["postID", "content", "likes", "comments", "approved", "authorId", "timestamp", "likedBy"])

    def backupData(self):
        """Create daily backup of CSV files (FR21)."""
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        for file in [USERS_CSV, MACROS_CSV, POSTS_CSV, WORKOUT_PLANS_CSV]:
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

    def close_sidebar_on_click(self, event):
        """Close sidebar when clicking on content area."""
        if self.menu_visible:
            self.toggle_left_menu()
    
    def bind_close_sidebar_to_children(self, widget):
        """Recursively bind the close sidebar event to all child widgets."""
        try:
            widget.bind("<Button-1>", self.close_sidebar_on_click, add=True)
            for child in widget.winfo_children():
                self.bind_close_sidebar_to_children(child)
        except:
            pass  # Some widgets might not support binding

# --- COMPREHENSIVE MEAL PLANNING SYSTEM (AC6/AC7 REQUIREMENTS) ---

class FoodItem:
    """
    AC6: OOP class demonstrating encapsulation, abstraction, data types
    Represents a single food item with nutritional information
    """
    def __init__(self, name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, category="Other"):
        self._name = name  # AC6: Encapsulation with protected attributes
        self._calories_per_100g = float(calories_per_100g)  # AC6: Data types (numeric - float)
        self._protein_per_100g = float(protein_per_100g)
        self._carbs_per_100g = float(carbs_per_100g)
        self._fat_per_100g = float(fat_per_100g)
        self._category = category  # AC6: Data types (text - string)
        self._is_vegetarian = self._determine_vegetarian()  # AC6: Data types (boolean)
    
    def _determine_vegetarian(self):
        """AC6: Private method, control structures (selection)"""
        meat_keywords = ["chicken", "beef", "pork", "fish", "salmon", "tuna", "turkey", "lamb"]
        return not any(keyword in self._name.lower() for keyword in meat_keywords)
    
    def get_nutrition_per_serving(self, serving_size_g):
        """
        AC6: Method demonstrating arithmetic operations, data types
        AC7: Range checking for serving size
        """
        # AC7: Validation - range checking
        if serving_size_g <= 0 or serving_size_g > 1000:
            raise ValueError("Serving size must be between 1-1000g")
        
        # AC6: Arithmetic operations
        multiplier = serving_size_g / 100.0
        return {
            "calories": round(self._calories_per_100g * multiplier, 1),
            "protein": round(self._protein_per_100g * multiplier, 1),
            "carbs": round(self._carbs_per_100g * multiplier, 1),
            "fat": round(self._fat_per_100g * multiplier, 1)
        }
    
    # AC6: Getter methods (encapsulation)
    def get_name(self): return self._name
    def get_category(self): return self._category
    def is_vegetarian(self): return self._is_vegetarian

class MealPlan:
    """
    AC6: OOP class demonstrating data structures, algorithms, control structures
    AC7: Input validation, error handling
    """
    def __init__(self, user, duration_days=7):
        self._user = user  # AC6: Object composition
        self._duration_days = int(duration_days)  # AC6: Type conversion
        self._meals = {}  # AC6: Data structure (dictionary)
        self._daily_targets = self._calculate_daily_targets()  # AC6: Algorithm
        self._food_database = self._initialize_food_database()  # AC6: Data structure (list)
        
    def _calculate_daily_targets(self):
        """
        AC6: Algorithm for calculating nutritional targets
        AC6: Arithmetic operations, conditional operations
        """
        calorie_goal = self._user.getCalorieGoal()
        
        # AC6: Conditional operators based on user goals
        if self._user.getGoalType() == "Lose Weight":
            protein_ratio, carb_ratio, fat_ratio = 0.35, 0.30, 0.35
        elif self._user.getGoalType() == "Gain Muscle":
            protein_ratio, carb_ratio, fat_ratio = 0.30, 0.40, 0.30
        else:  # Maintain Health
            protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30
        
        return {
            "calories": calorie_goal,
            "protein": round((calorie_goal * protein_ratio) / 4, 1),  # 4 cal/g protein
            "carbs": round((calorie_goal * carb_ratio) / 4, 1),  # 4 cal/g carbs
            "fat": round((calorie_goal * fat_ratio) / 9, 1)  # 9 cal/g fat
        }
    
    def _initialize_food_database(self):
        """
        AC6: Data structures (list of objects), iteration control structure
        AC7: Data source simulation (would be CSV/database in production)
        """
        # AC6: One-dimensional array (list) of food items
        foods = [
            # Proteins
            FoodItem("Chicken Breast", 165, 31, 0, 3.6, "Protein"),
            FoodItem("Salmon Fillet", 208, 20, 0, 13, "Protein"),
            FoodItem("Eggs", 155, 13, 1.1, 11, "Protein"),
            FoodItem("Greek Yogurt", 100, 10, 3.6, 5, "Protein"),
            FoodItem("Tofu", 76, 8, 1.9, 4.8, "Protein"),
            FoodItem("Lentils", 116, 9, 20, 0.4, "Protein"),
            
            # Carbohydrates
            FoodItem("Brown Rice", 123, 2.6, 25, 1, "Carbs"),
            FoodItem("Oats", 389, 16.9, 66, 6.9, "Carbs"),
            FoodItem("Sweet Potato", 86, 1.6, 20, 0.1, "Carbs"),
            FoodItem("Quinoa", 368, 14, 64, 6, "Carbs"),
            FoodItem("Whole Wheat Bread", 247, 13, 41, 4.2, "Carbs"),
            
            # Vegetables
            FoodItem("Broccoli", 34, 2.8, 7, 0.4, "Vegetables"),
            FoodItem("Spinach", 23, 2.9, 3.6, 0.4, "Vegetables"),

            FoodItem("Bell Peppers", 31, 1, 7, 0.3, "Vegetables"),
            FoodItem("Carrots", 41, 0.9, 10, 0.2, "Vegetables"),
            FoodItem("Avocado", 160, 2, 9, 15, "Vegetables"),
            
            # Fruits
            FoodItem("Banana", 89, 1.1, 23, 0.3, "Fruits"),
            FoodItem("Apple", 52, 0.3, 14, 0.2, "Fruits"),
            FoodItem("Berries", 57, 0.7, 14, 0.3, "Fruits"),
            FoodItem("Orange", 47, 0.9, 12, 0.1, "Fruits"),
            
            # Fats
            FoodItem("Olive Oil", 884, 0, 0, 100, "Fats"),
            FoodItem("Almonds", 579, 21, 22, 50, "Fats"),
            FoodItem("Walnuts", 654, 15, 14, 65, "Fats"),
        ]
        return foods
    
    def generate_meal_plan(self, dietary_preferences=None):
        """
        AC6: Complex algorithm using control structures (iteration, selection)
        AC6: Data structures (nested dictionaries, lists)
        AC7: Error handling with try-catch
        """
        try:
            dietary_preferences = dietary_preferences or []
            self._meals = {}
            
            # AC6: Iteration control structure (for loop)
            for day in range(1, self._duration_days + 1):
                daily_meals = {
                    "breakfast": self._generate_meal("breakfast", dietary_preferences),
                    "lunch": self._generate_meal("lunch", dietary_preferences),
                    "dinner": self._generate_meal("dinner", dietary_preferences),
                    "snacks": self._generate_meal("snacks", dietary_preferences)
                }
                
                # AC6: Nested data structure (dictionary of dictionaries)
                self._meals[f"Day {day}"] = daily_meals
                
            return True, "Meal plan generated successfully!"
            
        except Exception as e:
            # AC7: Error handling
            return False, f"Error generating meal plan: {str(e)}"
    
    def _generate_meal(self, meal_type, dietary_preferences):
        """
        AC6: Algorithm with selection and iteration control structures
        AC6: List comprehension, filtering operations
        """
        # AC6: Selection control structure
        if meal_type == "breakfast":
            target_calories = self._daily_targets["calories"] * 0.25
            preferred_categories = ["Carbs", "Protein", "Fruits"]
        elif meal_type == "lunch":
            target_calories = self._daily_targets["calories"] * 0.35
            preferred_categories = ["Protein", "Carbs", "Vegetables"]
        elif meal_type == "dinner":
            target_calories = self._daily_targets["calories"] * 0.30
            preferred_categories = ["Protein", "Vegetables", "Carbs"]
        else:  # snacks
            target_calories = self._daily_targets["calories"] * 0.10
            preferred_categories = ["Fruits", "Fats"]
        
        # AC6: List comprehension with filtering
        available_foods = [
            food for food in self._food_database
            if food.get_category() in preferred_categories
            and (not ("vegetarian" in dietary_preferences) or food.is_vegetarian())
        ]
        
        # AC6: Random selection algorithm
        if len(available_foods) < 2:
            available_foods = self._food_database  # Fallback
        
        selected_foods = []
        current_calories = 0
        attempts = 0
        max_attempts = 20
        
        # AC6: Iteration with condition checking
        while current_calories < target_calories * 0.8 and attempts < max_attempts:
            attempts += 1
            food = random.choice(available_foods)
            
            # AC6: Arithmetic operations for serving size calculation
            needed_calories = target_calories - current_calories
            base_serving = min(150, max(50, needed_calories / 2))
            
            nutrition = food.get_nutrition_per_serving(base_serving)
            
            selected_foods.append({
                "food": food.get_name(),
                "serving_g": base_serving,
                "nutrition": nutrition
            })
            
            current_calories += nutrition["calories"]
        
        return selected_foods
    
    def get_daily_nutrition_summary(self, day):
        """
        AC6: Algorithm for aggregating nutritional data
        AC6: Arithmetic operations, data structures
        """
        if f"Day {day}" not in self._meals:
            return None
        
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        
        # AC6: Nested iteration
        for meal_type, foods in self._meals[f"Day {day}"].items():
            for food_item in foods:
                nutrition = food_item["nutrition"]
                # AC6: Arithmetic operations
                totals["calories"] += nutrition["calories"]
                totals["protein"] += nutrition["protein"]
                totals["carbs"] += nutrition["carbs"]
                totals["fat"] += nutrition["fat"]
        
        return totals
    
    def export_meal_plan_to_csv(self, filename):
        """
        AC6: File I/O operations, data structures
        AC7: Error handling for file operations
        """
        try:
            # AC6: Two-dimensional array structure (list of lists)
            csv_data = []
            headers = ["Day", "Meal", "Food", "Serving (g)", "Calories", "Protein (g)", "Carbs (g)", "Fat (g)"]
            csv_data.append(headers)
            
            # AC6: Nested iteration through data structures
            for day, meals in self._meals.items():
                for meal_type, foods in meals.items():
                    for food_item in foods:
                        row = [
                            day,
                            meal_type.capitalize(),
                            food_item["food"],
                            food_item["serving_g"],
                            food_item["nutrition"]["calories"],
                            food_item["nutrition"]["protein"],
                            food_item["nutrition"]["carbs"],
                            food_item["nutrition"]["fat"]
                        ]
                        csv_data.append(row)
            
            # AC6: File I/O with CSV format
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(csv_data)
            
            return True, f"Meal plan exported to {filename}"
            
        except Exception as e:
            # AC7: Error handling
            return False, f"Export failed: {str(e)}"
    
    def analyze_nutritional_balance(self):
        """
        AC6: Algorithm for data analysis using arithmetic and logical operations
        AC6: Control structures for analysis
        """
        analysis_results = []
        
        # AC6: Iteration through all days
        for day in range(1, self._duration_days + 1):
            daily_nutrition = self.get_daily_nutrition_summary(day)
            if not daily_nutrition:
                continue
            
            targets = self._daily_targets
            
            # AC6: Arithmetic operations for percentage calculations
            calorie_diff = ((daily_nutrition["calories"] - targets["calories"]) / targets["calories"]) * 100
            protein_diff = ((daily_nutrition["protein"] - targets["protein"]) / targets["protein"]) * 100
            carb_diff = ((daily_nutrition["carbs"] - targets["carbs"]) / targets["carbs"]) * 100
            fat_diff = ((daily_nutrition["fat"] - targets["fat"]) / targets["fat"]) * 100
            
            # AC6: Conditional operations for analysis
            balance_score = 100
            if abs(calorie_diff) > 10: balance_score -= 20
            if abs(protein_diff) > 15: balance_score -= 15
            if abs(carb_diff) > 15: balance_score -= 10
            if abs(fat_diff) > 15: balance_score -= 10
            
            # AC6: Data structure (record/dictionary)
            day_analysis = {
                "day": day,
                "balance_score": max(0, balance_score),
                "calorie_variance": round(calorie_diff, 1),
                "protein_variance": round(protein_diff, 1),
                "carb_variance": round(carb_diff, 1),
                "fat_variance": round(fat_diff, 1),
                "recommendations": self._generate_recommendations(calorie_diff, protein_diff, carb_diff, fat_diff)
            }
            
            analysis_results.append(day_analysis)
        
        return analysis_results
    
    def _generate_recommendations(self, cal_diff, prot_diff, carb_diff, fat_diff):
        """
        AC6: Algorithm using conditional logic for recommendation generation
        AC6: String operations, control structures
        """
        recommendations = []
        
        # AC6: Selection control structures with logical operations
        if cal_diff > 10:
            recommendations.append("Reduce portion sizes or choose lower-calorie alternatives")
        elif cal_diff < -10:
            recommendations.append("Add healthy snacks or increase portion sizes")
        
        if prot_diff < -15:
            recommendations.append("Add more protein sources like lean meats, eggs, or legumes")
        elif prot_diff > 15:
            recommendations.append("Reduce protein portions and balance with other macros")
        
        if carb_diff < -15:
            recommendations.append("Include more complex carbohydrates like whole grains")
        elif carb_diff > 15:
            recommendations.append("Reduce refined carbs and focus on vegetables")
        
        if fat_diff < -15:
            recommendations.append("Add healthy fats like nuts, avocado, or olive oil")
        elif fat_diff > 15:
            recommendations.append("Reduce high-fat foods and cooking oils")
        
        return recommendations if recommendations else ["Your nutrition is well balanced!"]

# AC6: Global constants (naming convention demonstration)
MEAL_PLAN_CSV = "meal_plans.csv"
NUTRITION_LOG_CSV = "nutrition_log.csv"

def quick_sort_food_by_calories(food_list):
    """
    Quick sort algorithm for sorting food items by calories (AC6: sorting algorithm).
    Used in food database functionality.
    """
    if len(food_list) <= 1:
        return food_list
    
    pivot = food_list[len(food_list) // 2]
    left = [food for food in food_list if food._calories_per_100g < pivot._calories_per_100g]
    middle = [food for food in food_list if food._calories_per_100g == pivot._calories_per_100g]
    right = [food for food in food_list if food._calories_per_100g > pivot._calories_per_100g]
    
    return quick_sort_food_by_calories(left) + middle + quick_sort_food_by_calories(right)

def binary_search_food_by_name(sorted_food_list, target_name):
    """
    Binary search algorithm for finding food by name (AC6: searching algorithm).
    Used in food database search functionality.
    """
    left, right = 0, len(sorted_food_list) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if sorted_food_list[mid].get_name().lower() == target_name.lower():
            return mid
        elif sorted_food_list[mid].get_name().lower() < target_name.lower():
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
def selection_sort(data_list, key, reverse=False, type_converter=None):
    """
    Sorts a list of dictionaries using the Selection Sort algorithm.
    AC6: Demonstrates a classic sorting algorithm.

    Args:
        data_list (list): The list of dictionaries to sort.
        key (str): The dictionary key to sort by.
        reverse (bool): If True, sorts in descending order.
        type_converter (function): A function to convert the key's value before comparison (e.g., int).
    """
    n = len(data_list)
    # Outer loop to move the boundary of the unsorted subarray
    for i in range(n):
        # Assume the first element of the unsorted part is the minimum/maximum
        min_max_idx = i
        
        # Inner loop to find the actual minimum/maximum element in the rest of the list
        for j in range(i + 1, n):
            # Get the values to compare
            val_j = data_list[j].get(key)
            val_min_max = data_list[min_max_idx].get(key)

            # Use the type_converter if provided
            if type_converter:
                val_j = type_converter(val_j)
                val_min_max = type_converter(val_min_max)
            
            # Compare the values
            # If sorting in reverse (descending), find the maximum element
            if reverse:
                if val_j > val_min_max:
                    min_max_idx = j
            # Otherwise, find the minimum element
            else:
                if val_j < val_min_max:
                    min_max_idx = j

        # Swap the found minimum/maximum element with the first element of the unsorted part
        data_list[i], data_list[min_max_idx] = data_list[min_max_idx], data_list[i]
        
    return data_list
def validate_meal_plan_input(plan_duration, dietary_prefs):
    """
    AC7: Comprehensive validation function demonstrating all validation techniques
    """
    errors = []
    
    # AC7: Existence checking
    if not plan_duration:
        errors.append("Plan duration is required")
    
    # AC7: Type checking
    try:
        duration = int(plan_duration)
    except (ValueError, TypeError):
        errors.append("Plan duration must be a number")
        return False, errors
    
    # AC7: Range checking
    if not (1 <= duration <= 30):
        errors.append("Plan duration must be between 1 and 30 days")
    
    # AC7: Format checking for dietary preferences
    if dietary_prefs and not isinstance(dietary_prefs, list):
        errors.append("Dietary preferences must be a list")
    
    return len(errors) == 0, errors

# --- End of Meal Planning System ---
if __name__ == "__main__":
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        print(f"Created '{ASSETS_DIR}' folder. Please add your icon files there.")
    app = HealthyHabitsApp()
    app.backupData()
    app.root.mainloop()
