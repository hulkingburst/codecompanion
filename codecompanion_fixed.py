#!/usr/bin/env python3
"""
CodeCompanion - Enhanced Gamified Python Learning Platform
===========================================================
Complete single-file application with enhanced UI/UX and advanced features.
Learn Python while growing your companion!

Version 2.1 - Enhanced Edition with MCQ, Drills, and Bug Fixes
"""

import io
import json
import os
import sys
import random
import urllib.request
import webbrowser
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
from typing import Dict, List, Tuple, Optional, Any, Set
import customtkinter as ctk
from customtkinter import (CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry,
                           CTkScrollableFrame, CTkTextbox, CTkProgressBar,
                           CTkOptionMenu, CTkSwitch, CTkTabview, CTkCheckBox, 
                           CTkRadioButton, CTkToplevel)

# ============================================================================
# VERSION & UPDATE SYSTEM
# ============================================================================

CURRENT_VERSION = "2.2.0"  # Updated with bug fix drills!
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/yourusername/codecompanion/main/version.json"
DOWNLOAD_URL = "https://github.com/yourusername/codecompanion/releases/latest"


def check_for_updates():
    """Check if a newer version is available"""
    try:
        with urllib.request.urlopen(UPDATE_CHECK_URL, timeout=3) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get("version", CURRENT_VERSION)
            download_url = data.get("download_url", DOWNLOAD_URL)

            if latest_version > CURRENT_VERSION:
                return True, latest_version, download_url
    except:
        pass  # Silently fail if update check doesn't work
    return False, CURRENT_VERSION, None


def auto_update_check_and_install():
    """Automatically check for updates on startup and offer to install"""
    try:
        has_update, latest_version, download_url = check_for_updates()
        if has_update:
            return True, latest_version, download_url
    except:
        pass
    return False, CURRENT_VERSION, None


# ============================================================================
# THEME SYSTEM
# ============================================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Dark mode only - clean and simple
COLORS = {
    'primary': '#3B82F6',
    'primary_hover': '#2563EB',
    'success': '#10B981',
    'success_hover': '#059669',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'bg_dark': '#1E1E1E',
    'bg_medium': '#2A2A2A',
    'bg_light': '#363636',
    'text_primary': '#FFFFFF',
    'text_secondary': '#A3A3A3',
    'accent': '#8B5CF6',
    'info': '#06B6D4',
}


def get_colors():
    """Return color scheme (dark mode only)"""
    return COLORS


# Default font settings
DEFAULT_FONT = "Segoe UI"  # Clean, modern font
CODE_FONT = "Consolas"  # Monospace for code

# Available fonts for user selection
UI_FONTS = [
    "Segoe UI",
    "Arial",
    "Helvetica",
    "Verdana",
    "Calibri",
    "Trebuchet MS",
    "Georgia",
    "Times New Roman"
]

CODE_FONTS = [
    "Consolas",
    "Courier New",
    "Monaco",
    "Menlo",
    "Source Code Pro",
    "Fira Code",
    "JetBrains Mono",
    "Roboto Mono"
]


# ============================================================================
# SECTION 1: CORE DATA MODELS & STORAGE
# ============================================================================

@dataclass
class ActivityLog:
    """Track recent user activities"""
    timestamp: str
    activity_type: str  # 'lesson_complete', 'exercise_complete', 'streak', 'level_up'
    description: str
    xp_gained: int = 0


@dataclass
class User:
    """Represents a learner's profile and progress"""
    username: str
    xp: int = 0
    level: int = 1
    streak_days: int = 0
    last_active: str = field(default_factory=lambda: datetime.now().date().isoformat())
    daily_goal_xp: int = 50
    today_xp: int = 0
    completed_lessons: Set[str] = field(default_factory=set)
    completed_exercises: Dict[str, int] = field(default_factory=dict)
    companion_type: str = "plant"
    companion_stage: int = 0
    companion_vitality: int = 100
    achievements: List[str] = field(default_factory=list)
    review_queue: List[Tuple[str, str]] = field(default_factory=list)
    mistake_tracker: Dict[str, int] = field(default_factory=dict)
    theme: str = "dark"
    font_size: int = 12
    activity_log: List[Dict] = field(default_factory=list)
    total_exercises_completed: int = 0
    total_hints_used: int = 0
    fastest_completion_time: int = 999999
    coding_time_minutes: int = 0
    favorite_topics: List[str] = field(default_factory=list)
    daily_challenge_completed: str = ""
    completed_drills: Dict[str, int] = field(default_factory=dict)
    total_drills_completed: int = 0
    last_update_check: str = ""
    auto_check_updates: bool = True
    weekly_xp: int = 0
    weekly_goal_xp: int = 200
    total_study_sessions: int = 0
    average_session_time: int = 0  # minutes
    perfect_scores: int = 0  # exercises completed without hints
    current_session_start: str = ""
    ui_font: str = "Segoe UI"
    code_font: str = "Consolas"
    reduce_animations: bool = False
    high_contrast: bool = False

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['completed_lessons'] = list(self.completed_lessons)
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        if 'completed_lessons' in data:
            data['completed_lessons'] = set(data['completed_lessons'])
        # Set defaults for new fields
        defaults = {
            'theme': 'dark',
            'font_size': 12,
            'activity_log': [],
            'total_exercises_completed': 0,
            'total_hints_used': 0,
            'fastest_completion_time': 999999,
            'coding_time_minutes': 0,
            'favorite_topics': [],
            'daily_challenge_completed': '',
            'completed_drills': {},
            'total_drills_completed': 0,
            'last_update_check': '',
            'auto_check_updates': True,
            'weekly_xp': 0,
            'weekly_goal_xp': 200,
            'total_study_sessions': 0,
            'average_session_time': 0,
            'perfect_scores': 0,
            'current_session_start': '',
            'ui_font': 'Segoe UI',
            'code_font': 'Consolas',
            'reduce_animations': False,
            'high_contrast': False
        }
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        return cls(**data)

    def add_activity(self, activity_type: str, description: str, xp_gained: int = 0):
        """Add an activity to the log"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'activity_type': activity_type,
            'description': description,
            'xp_gained': xp_gained
        }
        self.activity_log.append(activity)
        # Keep only last 50 activities
        if len(self.activity_log) > 50:
            self.activity_log = self.activity_log[-50:]


class CompanionType(Enum):
    PLANT = "plant"
    PET = "pet"
    DRAGON = "dragon"
    ROBOT = "robot"


@dataclass
class Companion:
    """Defines a streak companion's properties and visual representation"""
    type: CompanionType
    stage: int = 0
    vitality: int = 100

    EVOLUTION_DATA = {
        CompanionType.PLANT: {
            'names': ['Seed', 'Sprout', 'Seedling', 'Young Plant', 'Bush',
                      'Small Tree', 'Tree', 'Great Tree', 'Ancient Oak', 'Mystical Ent', 'World Tree'],
            'ascii': {
                0: '  •  ',
                1: ' \\|/ \n  |  ',
                2: ' \\|/ \n  |  \n -+-',
                3: '  Y  \n  |  \n -+-',
                4: ' \\|/ \n\\|||/\n -+-',
                5: '  🌿 \n \\|/ \n  |  \n _|_ ',
                6: '  🌳 \n /|\\ \n  |  \n_/|\\_ ',
                7: '  🌲 \n /|\\ \n//|\\\\\n _|_ ',
                8: ' 🌟🌳🌟\n//|||\\\\\n  |||  \n_/|||\\_ ',
                9: '✨ 🌳 ✨\n /||\\ \n//|||\\\\n  |||  \n_/|||\\_ ',
                10: '  ★  \n 🌳🌟🌳\n//|||\\\\n  |||  \n_/|||\\_ \nLEGENDARY'
            },
            'description': 'Grows from a tiny seed into a legendary World Tree'
        },
        CompanionType.PET: {
            'names': ['Egg', 'Hatchling', 'Chick', 'Young Bird', 'Adult Bird',
                      'Swift Falcon', 'Guardian Eagle', 'Majestic Phoenix', 'Star Phoenix', 'Cosmic Phoenix',
                      'Eternal Phoenix'],
            'ascii': {
                0: ' (O) ',
                1: ' ^v^ ',
                2: ' >v< \n  V  ',
                3: ' >O< \n  V  \n  W  ',
                4: ' \\o/ \n  V  \n /W\\ ',
                5: '  🐦 \n <|> \n /W\\ ',
                6: '  🦅 \n <||>\n /WW\\',
                7: '  🔥🐦🔥\n  <||> \n  /WW\\ ',
                8: ' ✨🔥🐦🔥✨\n   <||>  \n   /WW\\  ',
                9: '  ★ 🔥 ★\n  🐦🔥🐦 \n   <||>  \n   /WW\\  ',
                10: '  ★ 🔥 ★\n 🐦🔥🐦🔥🐦\n   <||>   \n   /WW\\   \n  ETERNAL '
            },
            'description': 'Hatches from an egg and becomes an Eternal Phoenix'
        },
        CompanionType.DRAGON: {
            'names': ['Dragon Egg', 'Wyrmling', 'Drake', 'Young Dragon', 'Dragon',
                      'Great Dragon', 'Elder Dragon', 'Ancient Wyrm', 'Sky Wyrm', 'Cosmic Dragon', 'Primordial Dragon'],
            'ascii': {
                0: ' {O} ',
                1: ' <o> \n  ~  ',
                2: ' <O> \n  ~~ ',
                3: ' /^^\\ \n<O  >\n  ~~ ',
                4: '  /^^\\ \n <OO> \n  ~~~~ ',
                5: '  🐲  \n /^^\\ \n<O  O>\n ~~~~ ',
                6: '  🐉  \n /^^^\\ \n<O   O>\n ~~~~~ ',
                7: '  🔥🐉🔥 \n  /^^^\\  \n <O   O> \n  ~~~~~ ',
                8: ' ✨🔥🐉🔥✨\n   /^^^\\   \n  <O   O>  \n   ~~~~~  ',
                9: '  ★ 🔥 ★  \n  🐉🔥🐉  \n  /^^^\\   \n <O   O>  \n  ~~~~~  ',
                10: '  ★ 🔥 ★  \n 🐉🔥🐉🔥🐉\n  /^^^\\   \n <O   O>  \n  ~~~~~   \nPRIMORDIAL'
            },
            'description': 'Rises from dragon egg to become a Primordial Dragon'
        },
        CompanionType.ROBOT: {
            'names': ['Parts', 'Basic Frame', 'Simple Bot', 'Advanced Bot', 'AI Unit',
                      'Smart System', 'Quantum Processor', 'Neural Network', 'Singularity Core', 'Transcendent AI',
                      'Digital God'],
            'ascii': {
                0: ' [_] ',
                1: ' [o] \n |_| ',
                2: ' [O] \n<|_|>',
                3: ' [O] \n<|||>\n |_| ',
                4: '  🤖  \n [O_O]\n <|||>\n  |_| ',
                5: '  🤖  \n[O___O]\n <|||> \n  |_|  ',
                6: '  ⚡🤖⚡ \n [O___O]\n  <|||> \n   |_|  ',
                7: '  ⚡🤖⚡ \n[O_____O]\n  <|||>  \n   |_|   ',
                8: ' ✨⚡🤖⚡✨\n [O_____O]\n  <|||||> \n   |_|    ',
                9: '  ★ ⚡ ★  \n  🤖⚡🤖  \n [O_____O]\n  <|||||> \n   |_|    ',
                10: '  ★ ⚡ ★  \n 🤖⚡🤖⚡🤖\n [O_____O]\n  <|||||> \n   |_|    \nDIGITAL GOD'
            },
            'description': 'Assembles from parts into a transcendent Digital God'
        }
    }

    def get_name(self) -> str:
        return self.EVOLUTION_DATA[self.type]['names'][min(self.stage, 10)]

    def get_ascii(self) -> str:
        return self.EVOLUTION_DATA[self.type]['ascii'][min(self.stage, 10)]

    def get_description(self) -> str:
        return self.EVOLUTION_DATA[self.type]['description']

    def can_evolve(self) -> bool:
        return self.stage < 10 and self.vitality >= 70


class StorageManager:
    """Handles persistence of user data to JSON files"""

    def __init__(self, data_dir: str = "codecompanion_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.user_file = os.path.join(data_dir, "user.json")

    def save_user(self, user: User) -> None:
        with open(self.user_file, 'w') as f:
            json.dump(user.to_dict(), f, indent=2)

    def load_user(self) -> Optional[User]:
        if not os.path.exists(self.user_file):
            return None
        try:
            with open(self.user_file, 'r') as f:
                data = json.load(f)
                return User.from_dict(data)
        except Exception as e:
            print(f"Error loading user: {e}")
            return None

    def user_exists(self) -> bool:
        return os.path.exists(self.user_file)

    def export_user_data(self, export_path: str, user: User) -> bool:
        """Export user data to a file for backup"""
        try:
            with open(export_path, 'w') as f:
                json.dump(user.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def import_user_data(self, import_path: str) -> Optional[User]:
        """Import user data from a backup file"""
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
                return User.from_dict(data)
        except Exception as e:
            print(f"Import error: {e}")
            return None


# ============================================================================
# SECTION 2: LEARNING CONTENT ENGINE
# ============================================================================

@dataclass
class CodeExample:
    code: str
    explanation: str


@dataclass
class MultipleChoiceQuestion:
    id: str
    question: str
    choices: List[str]  # List of choices (A, B, C, D)
    correct_answer: int  # Index of correct answer (0-3)
    explanation: str
    difficulty: int
    concept: str

    def check_answer(self, selected_index: int) -> bool:
        return selected_index == self.correct_answer


@dataclass
class MultiAnswerQuestion:
    id: str
    question: str
    choices: List[str]
    correct_answers: List[int]  # List of correct indices
    explanation: str
    difficulty: int
    concept: str

    def check_answer(self, selected_indices: List[int]) -> bool:
        return set(selected_indices) == set(self.correct_answers)


@dataclass
class OutputDrill:
    id: str
    code: str
    correct_output: str
    explanation: str
    difficulty: int
    concept: str

    def check_answer(self, user_answer: str) -> bool:
        # Normalize whitespace for comparison
        return user_answer.strip() == self.correct_output.strip()


@dataclass
class BugFixDrill:
    """Find and fix the bug in the code"""
    id: str
    buggy_code: str
    bug_type: str  # "syntax", "logic", "runtime", "indentation"
    bug_description: str  # What's wrong
    correct_code: str
    explanation: str
    difficulty: int
    concept: str
    hints: List[str] = field(default_factory=list)

    def check_answer(self, user_code: str) -> Tuple[bool, str]:
        """Check if the bug is fixed - run both codes and compare"""
        # Normalize whitespace
        user_clean = user_code.strip().replace('\r\n', '\n')
        correct_clean = self.correct_code.strip().replace('\r\n', '\n')
        
        # Check if code matches exactly
        if user_clean == correct_clean:
            return True, "Perfect fix!"
        
        # Try executing both to see if they produce same result
        executor = CodeExecutor()
        user_success, user_output, user_error = executor.execute_code(user_code)
        correct_success, correct_output, correct_error = executor.execute_code(self.correct_code)
        
        if user_success and correct_success:
            if user_output.strip() == correct_output.strip():
                return True, "Code works! (Alternative solution accepted)"
        
        return False, "Bug still present or code doesn't work correctly"


@dataclass
class Exercise:
    id: str
    prompt: str
    test_cases: List[Tuple[str, Any]]
    hints: List[str]
    difficulty: int
    concept: str
    starter_code: str = ""

    def validate_solution(self, user_code: str) -> Tuple[bool, str, List[str]]:
        executor = CodeExecutor()
        results = []
        for test_input, expected in self.test_cases:
            success, output, error = executor.execute_code(user_code, test_input)
            if not success:
                return False, f"Runtime Error: {error}", [error]
            # More flexible output comparison
            output_clean = output.strip().replace('\r\n', '\n')
            expected_clean = str(expected).strip().replace('\r\n', '\n')
            if output_clean != expected_clean:
                results.append(f"Expected: {expected}\nGot: {output.strip()}")

        if results:
            return False, "Some test cases failed", results
        return True, "Perfect! All tests passed! 🎉", []


@dataclass
class Lesson:
    id: str
    title: str
    concept: str
    examples: List[CodeExample]
    exercises: List[Exercise]
    prerequisites: List[str]
    xp_reward: int
    skill_path: str
    mcq_questions: List[MultipleChoiceQuestion] = field(default_factory=list)
    multi_answer_questions: List[MultiAnswerQuestion] = field(default_factory=list)
    output_drills: List[OutputDrill] = field(default_factory=list)
    bug_fix_drills: List[BugFixDrill] = field(default_factory=list)


@dataclass
class DailyChallenge:
    """Special daily bonus exercises"""
    date: str
    exercise: Exercise
    bonus_xp: int = 50

    @staticmethod
    def generate_for_date(date_str: str) -> 'DailyChallenge':
        """Generate a daily challenge based on the date (deterministic)"""
        # Use date as seed for consistent daily challenges
        random.seed(date_str)

        challenges = [
            Exercise(
                id=f"daily_{date_str}_1",
                prompt="Create a function that returns the sum of all even numbers from 1 to n.",
                test_cases=[("10", "30"), ("5", "6"), ("1", "0")],
                hints=["Use a loop from 1 to n", "Check if number % 2 == 0", "Add even numbers to a sum"],
                difficulty=2,
                concept="loops",
                starter_code="def sum_evens(n):\n    # Your code here\n    pass\n\nprint(sum_evens(10))"
            ),
            Exercise(
                id=f"daily_{date_str}_2",
                prompt="Write a function that reverses a string.",
                test_cases=[("'hello'", "olleh"), ("'Python'", "nohtyP")],
                hints=["Use string slicing [::-1]", "Or use a loop to build reversed string"],
                difficulty=2,
                concept="strings",
                starter_code="def reverse_string(s):\n    # Your code here\n    pass\n\nprint(reverse_string('hello'))"
            ),
            Exercise(
                id=f"daily_{date_str}_3",
                prompt="Create a function that counts vowels in a string.",
                test_cases=[("'hello'", "2"), ("'Python'", "1")],
                hints=["Define vowels = 'aeiouAEIOU'", "Loop through string", "Check if char in vowels"],
                difficulty=2,
                concept="strings",
                starter_code="def count_vowels(s):\n    # Your code here\n    pass\n\nprint(count_vowels('hello'))"
            ),
        ]

        exercise = random.choice(challenges)
        return DailyChallenge(date=date_str, exercise=exercise, bonus_xp=50)


class ContentEngine:
    @staticmethod
    def get_all_lessons() -> List[Lesson]:
        return [
            Lesson(
                id="basics_01_variables",
                title="Variables and Assignment",
                concept="""Variables are containers for storing data. In Python, you don't need to declare the type - Python figures it out automatically!

Creating Variables:
• Use the equals sign (=) to assign values
• Variable names should be descriptive
• Use lowercase with underscores (snake_case)

Rules:
• Names can contain letters, numbers, and underscores
• Must start with a letter or underscore
• Case-sensitive (name != Name)""",
                examples=[
                    CodeExample(
                        code="name = 'Alice'\nage = 25\nis_student = True",
                        explanation="Three variables with different types: string, integer, and boolean"
                    ),
                    CodeExample(
                        code="x = 10\nx = x + 5\nprint(x)  # Outputs: 15",
                        explanation="Variables can be updated using their current value"
                    )
                ],
                exercises=[
                    Exercise(
                        id="basics_01_ex1",
                        prompt="Create a variable called 'greeting' with the value 'Hello World' and print it.",
                        test_cases=[("", "Hello World")],
                        hints=[
                            "Use the assignment operator: greeting = ...",
                            "Use print() function to display the value",
                            "Strings need quotes: 'Hello World'"
                        ],
                        difficulty=1,
                        concept="variables",
                        starter_code="# Create your variable here\n"
                    ),
                    Exercise(
                        id="basics_01_ex2",
                        prompt="Create two variables: 'a' with value 5 and 'b' with value 3. Print their sum.",
                        test_cases=[("", "8")],
                        hints=[
                            "Create both variables first",
                            "Use + to add numbers",
                            "print(a + b)"
                        ],
                        difficulty=1,
                        concept="variables"
                    )
                ],
                prerequisites=[],
                xp_reward=10,
                skill_path="basics",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="basics_01_mcq1",
                        question="Which of the following is a valid variable name in Python?",
                        choices=["2fast", "my-variable", "my_variable", "my variable"],
                        correct_answer=2,
                        explanation="'my_variable' is valid. Variable names can't start with numbers, contain hyphens, or have spaces.",
                        difficulty=1,
                        concept="variables"
                    ),
                    MultipleChoiceQuestion(
                        id="basics_01_mcq2",
                        question="What is the output of: x = 5; x = x + 3; print(x)",
                        choices=["5", "8", "53", "Error"],
                        correct_answer=1,
                        explanation="x starts at 5, then we add 3, so x becomes 8.",
                        difficulty=1,
                        concept="variables"
                    )
                ],
                multi_answer_questions=[
                    MultiAnswerQuestion(
                        id="basics_01_multi1",
                        question="Which of the following are valid ways to assign variables? (Select all that apply)",
                        choices=["x = 10", "10 = x", "x, y = 5, 10", "x = y = 0"],
                        correct_answers=[0, 2, 3],
                        explanation="You can assign single values (x = 10), multiple values (x, y = 5, 10), or chain assignments (x = y = 0). But you can't assign to a literal (10 = x).",
                        difficulty=2,
                        concept="variables"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="basics_01_drill1",
                        code="x = 10\ny = 20\nx = y\nprint(x)",
                        correct_output="20",
                        explanation="x is assigned the value of y, which is 20.",
                        difficulty=1,
                        concept="variables"
                    )
                ],
                bug_fix_drills=[
                    BugFixDrill(
                        id="basics_01_bug1",
                        buggy_code="x = 5\nprint(X)",
                        bug_type="runtime",
                        bug_description="This code has a naming error - can you spot it?",
                        correct_code="x = 5\nprint(x)",
                        explanation="Python is case-sensitive! 'X' and 'x' are different variables. The variable was defined as lowercase 'x' but we tried to print uppercase 'X'.",
                        difficulty=1,
                        concept="variables",
                        hints=[
                            "Look carefully at the variable name",
                            "Remember: Python is case-sensitive",
                            "The variable is 'x' (lowercase) but we're printing 'X' (uppercase)"
                        ]
                    ),
                    BugFixDrill(
                        id="basics_01_bug2",
                        buggy_code="name = 'Alice\nprint(name)",
                        bug_type="syntax",
                        bug_description="There's a syntax error with the string",
                        correct_code="name = 'Alice'\nprint(name)",
                        explanation="Strings must have matching quotes. The string 'Alice' was missing its closing quote.",
                        difficulty=1,
                        concept="variables",
                        hints=[
                            "Check the quotes around 'Alice'",
                            "Every opening quote needs a closing quote",
                            "Add a closing quote after Alice"
                        ]
                    )
                ]
            ),

            Lesson(
                id="basics_02_types",
                title="Data Types",
                concept="""Python has several built-in types for different kinds of data:

Numeric Types:
• int: Whole numbers (42, -17, 0)
• float: Decimal numbers (3.14, -0.5, 2.0)

Text Type:
• str: Text/strings ('hello', "world")

Boolean Type:
• bool: True or False

Type Conversion:
• int(), float(), str() to convert between types""",
                examples=[
                    CodeExample(
                        code="x = 10        # int\ny = 3.14      # float\nname = 'Bob'  # str\nactive = True # bool",
                        explanation="Different data types in action"
                    ),
                    CodeExample(
                        code="num = '42'\nresult = int(num) + 8\nprint(result)  # 50",
                        explanation="Converting string to int for math"
                    )
                ],
                exercises=[
                    Exercise(
                        id="basics_02_ex1",
                        prompt="Convert the string '100' to an integer and add 50 to it. Print the result.",
                        test_cases=[("", "150")],
                        hints=[
                            "Use int() to convert",
                            "Then add 50",
                            "int('100') + 50"
                        ],
                        difficulty=2,
                        concept="types"
                    )
                ],
                prerequisites=["basics_01_variables"],
                xp_reward=15,
                skill_path="basics",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="basics_02_mcq1",
                        question="What is the type of: x = 3.14",
                        choices=["int", "float", "str", "bool"],
                        correct_answer=1,
                        explanation="3.14 is a decimal number, so it's a float.",
                        difficulty=1,
                        concept="types"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="basics_02_drill1",
                        code="x = '5'\ny = '3'\nprint(x + y)",
                        correct_output="53",
                        explanation="When you add strings, they concatenate rather than adding mathematically.",
                        difficulty=1,
                        concept="types"
                    )
                ]
            ),

            Lesson(
                id="control_01_if",
                title="If Statements",
                concept="""Make decisions in your code using if/elif/else:

Syntax:
if condition:
    # code if True
elif other_condition:
    # code if first is False but this is True
else:
    # code if all False

Comparison Operators:
• == equal to
• != not equal  
• < less than
• > greater than
• <= less than or equal
• >= greater than or equal""",
                examples=[
                    CodeExample(
                        code="age = 18\nif age >= 18:\n    print('Adult')\nelse:\n    print('Minor')",
                        explanation="Simple if/else decision"
                    )
                ],
                exercises=[
                    Exercise(
                        id="control_01_ex1",
                        prompt="Write code that checks if a variable 'score' (value 85) is >= 60. If yes, print 'Pass', otherwise print 'Fail'.",
                        test_cases=[("", "Pass")],
                        hints=[
                            "score = 85",
                            "if score >= 60:",
                            "Use print() in each branch"
                        ],
                        difficulty=2,
                        concept="conditionals",
                        starter_code="score = 85\n# Add your if statement\n"
                    )
                ],
                prerequisites=["basics_02_types"],
                xp_reward=20,
                skill_path="control_flow",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="control_01_mcq1",
                        question="What does == do in Python?",
                        choices=["Assigns a value", "Compares two values", "Adds two numbers", "None of the above"],
                        correct_answer=1,
                        explanation="== is the equality comparison operator. = is for assignment.",
                        difficulty=1,
                        concept="conditionals"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="control_01_drill1",
                        code="x = 10\nif x > 5:\n    print('Big')\nelse:\n    print('Small')",
                        correct_output="Big",
                        explanation="Since 10 > 5 is True, 'Big' is printed.",
                        difficulty=1,
                        concept="conditionals"
                    )
                ]
            ),

            Lesson(
                id="control_02_loops",
                title="For Loops",
                concept="""Repeat code a specific number of times or iterate over sequences.

Basic Syntax:
for variable in sequence:
    # code to repeat

Range Function:
• range(n): numbers from 0 to n-1
• range(start, stop): numbers from start to stop-1
• range(start, stop, step): with custom step""",
                examples=[
                    CodeExample(
                        code="for i in range(5):\n    print(i)  # 0, 1, 2, 3, 4",
                        explanation="Loop 5 times"
                    ),
                    CodeExample(
                        code="for num in [1, 2, 3]:\n    print(num * 2)",
                        explanation="Loop over a list"
                    )
                ],
                exercises=[
                    Exercise(
                        id="control_02_ex1",
                        prompt="Use a for loop to print numbers 1 through 5, each on a new line.",
                        test_cases=[("", "1\n2\n3\n4\n5")],
                        hints=[
                            "Use range(1, 6) for 1-5",
                            "for i in range(...):",
                            "print(i)"
                        ],
                        difficulty=2,
                        concept="loops"
                    )
                ],
                prerequisites=["control_01_if"],
                xp_reward=25,
                skill_path="control_flow",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="control_02_mcq1",
                        question="What does range(3) produce?",
                        choices=["[1, 2, 3]", "[0, 1, 2]", "[0, 1, 2, 3]", "[1, 2]"],
                        correct_answer=1,
                        explanation="range(3) generates numbers from 0 to 2 (3 is not included).",
                        difficulty=1,
                        concept="loops"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="control_02_drill1",
                        code="total = 0\nfor i in range(3):\n    total += i\nprint(total)",
                        correct_output="3",
                        explanation="Loop adds 0 + 1 + 2 = 3",
                        difficulty=2,
                        concept="loops"
                    )
                ],
                bug_fix_drills=[
                    BugFixDrill(
                        id="control_02_bug1",
                        buggy_code="for i in range(5)\n    print(i)",
                        bug_type="syntax",
                        bug_description="Missing punctuation in the for loop",
                        correct_code="for i in range(5):\n    print(i)",
                        explanation="For loops (and all control structures in Python) need a colon (:) at the end of the line.",
                        difficulty=1,
                        concept="loops",
                        hints=[
                            "What comes at the end of a for loop line?",
                            "Look for a missing colon (:)",
                            "Add : after range(5)"
                        ]
                    ),
                    BugFixDrill(
                        id="control_02_bug2",
                        buggy_code="for i in range(10):\nprint(i)",
                        bug_type="indentation",
                        bug_description="Indentation problem",
                        correct_code="for i in range(10):\n    print(i)",
                        explanation="Code inside a loop must be indented. Python uses indentation to know what code belongs to the loop.",
                        difficulty=1,
                        concept="loops",
                        hints=[
                            "Check the indentation",
                            "Code inside loops must be indented",
                            "Add 4 spaces before print(i)"
                        ]
                    ),
                    BugFixDrill(
                        id="control_02_bug3",
                        buggy_code="total = 0\nfor i in range(5):\n    total = i\nprint(total)",
                        bug_type="logic",
                        bug_description="This should sum numbers 0-4, but it doesn't work correctly",
                        correct_code="total = 0\nfor i in range(5):\n    total += i\nprint(total)",
                        explanation="Using = assigns a value, but += adds to the existing value. We need += to accumulate the sum.",
                        difficulty=2,
                        concept="loops",
                        hints=[
                            "We want to ADD to total, not replace it",
                            "Look at how total is being updated",
                            "Use += instead of = to add to total"
                        ]
                    )
                ]
            ),

            Lesson(
                id="functions_01_basics",
                title="Function Basics",
                concept="""Functions are reusable blocks of code that perform a specific task.

Syntax:
def function_name(parameters):
    # code
    return result

Why Use Functions?
• Avoid repeating code
• Make code more organized
• Easier to test and debug""",
                examples=[
                    CodeExample(
                        code="def greet(name):\n    return f'Hello, {name}!'\n\nprint(greet('Alice'))",
                        explanation="Function with parameter and return value"
                    ),
                    CodeExample(
                        code="def add(a, b):\n    return a + b\n\nresult = add(5, 3)\nprint(result)  # 8",
                        explanation="Function for addition"
                    )
                ],
                exercises=[
                    Exercise(
                        id="functions_01_ex1",
                        prompt="Create a function called 'double' that takes a number and returns it multiplied by 2. Then call it with 7 and print the result.",
                        test_cases=[("", "14")],
                        hints=[
                            "def double(num):",
                            "    return num * 2",
                            "print(double(7))"
                        ],
                        difficulty=3,
                        concept="functions"
                    )
                ],
                prerequisites=["control_02_loops"],
                xp_reward=30,
                skill_path="functions",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="functions_01_mcq1",
                        question="What keyword is used to return a value from a function?",
                        choices=["give", "return", "send", "output"],
                        correct_answer=1,
                        explanation="The 'return' keyword sends a value back from a function.",
                        difficulty=1,
                        concept="functions"
                    )
                ],
                multi_answer_questions=[
                    MultiAnswerQuestion(
                        id="functions_01_multi1",
                        question="Which statements about functions are true? (Select all that apply)",
                        choices=[
                            "Functions can take parameters",
                            "Functions must always return a value",
                            "Functions help organize code",
                            "You can call a function multiple times"
                        ],
                        correct_answers=[0, 2, 3],
                        explanation="Functions can take parameters, help organize code, and can be called many times. They don't always need to return a value (can use None or just perform actions).",
                        difficulty=2,
                        concept="functions"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="functions_01_drill1",
                        code="def triple(x):\n    return x * 3\n\nprint(triple(4))",
                        correct_output="12",
                        explanation="The function multiplies 4 by 3, returning 12.",
                        difficulty=1,
                        concept="functions"
                    )
                ]
            ),

            Lesson(
                id="data_01_lists",
                title="Lists",
                concept="""Lists store multiple items in a single variable. They're ordered and changeable.

Creating Lists:
my_list = [1, 2, 3, 4, 5]
mixed = [1, 'hello', True, 3.14]

Common Operations:
• my_list[0]: Access first item (index 0)
• my_list.append(item): Add to end
• len(my_list): Get length
• item in my_list: Check if exists""",
                examples=[
                    CodeExample(
                        code="fruits = ['apple', 'banana', 'cherry']\nprint(fruits[0])  # apple\nfruits.append('orange')\nprint(len(fruits))  # 4",
                        explanation="List operations"
                    )
                ],
                exercises=[
                    Exercise(
                        id="data_01_ex1",
                        prompt="Create a list of numbers [10, 20, 30], append 40 to it, then print the length of the list.",
                        test_cases=[("", "4")],
                        hints=[
                            "numbers = [10, 20, 30]",
                            "numbers.append(40)",
                            "print(len(numbers))"
                        ],
                        difficulty=2,
                        concept="lists"
                    )
                ],
                prerequisites=["functions_01_basics"],
                xp_reward=25,
                skill_path="data_structures",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="data_01_mcq1",
                        question="What is the index of the first element in a list?",
                        choices=["1", "0", "-1", "None"],
                        correct_answer=1,
                        explanation="Python uses 0-based indexing, so the first element is at index 0.",
                        difficulty=1,
                        concept="lists"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="data_01_drill1",
                        code="nums = [5, 10, 15]\nprint(nums[1])",
                        correct_output="10",
                        explanation="Index 1 refers to the second element, which is 10.",
                        difficulty=1,
                        concept="lists"
                    )
                ]
            ),

            Lesson(
                id="data_02_dictionaries",
                title="Dictionaries",
                concept="""Dictionaries store data in key-value pairs. They're unordered and very fast for lookups.

Creating Dictionaries:
my_dict = {'name': 'Alice', 'age': 25}
empty_dict = {}

Common Operations:
• my_dict['name']: Access value by key
• my_dict['city'] = 'NYC': Add/update key-value pair
• 'name' in my_dict: Check if key exists
• my_dict.keys(), my_dict.values()
• my_dict.get('key', default): Safe access with default""",
                examples=[
                    CodeExample(
                        code="person = {'name': 'Bob', 'age': 30}\nprint(person['name'])  # Bob\nperson['city'] = 'Boston'\nprint(person)",
                        explanation="Creating and modifying a dictionary"
                    ),
                    CodeExample(
                        code="scores = {'Alice': 95, 'Bob': 87}\nfor name, score in scores.items():\n    print(f'{name}: {score}')",
                        explanation="Iterating through dictionary items"
                    )
                ],
                exercises=[
                    Exercise(
                        id="data_02_ex1",
                        prompt="Create a dictionary with keys 'apple', 'banana', 'orange' and values 1, 2, 3. Print the value for 'banana'.",
                        test_cases=[("", "2")],
                        hints=[
                            "fruits = {'apple': 1, 'banana': 2, 'orange': 3}",
                            "Access with fruits['banana']",
                            "print(fruits['banana'])"
                        ],
                        difficulty=2,
                        concept="dictionaries"
                    )
                ],
                prerequisites=["data_01_lists"],
                xp_reward=30,
                skill_path="data_structures",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="data_02_mcq1",
                        question="How do you access a value in a dictionary?",
                        choices=["dict[0]", "dict['key']", "dict.get(0)", "dict.value"],
                        correct_answer=1,
                        explanation="Use square brackets with the key name: dict['key']",
                        difficulty=1,
                        concept="dictionaries"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="data_02_drill1",
                        code="d = {'x': 10, 'y': 20}\nprint(d['x'] + d['y'])",
                        correct_output="30",
                        explanation="Adds the values associated with keys 'x' and 'y'.",
                        difficulty=1,
                        concept="dictionaries"
                    )
                ]
            ),

            Lesson(
                id="control_03_while",
                title="While Loops",
                concept="""While loops repeat code as long as a condition is True.

Syntax:
while condition:
    # code to repeat
    # update condition to avoid infinite loop

Common Uses:
• Repeat until user input is valid
• Process data until end is reached
• Game loops that run until game over

Important: Always ensure the condition becomes False eventually!""",
                examples=[
                    CodeExample(
                        code="count = 0\nwhile count < 5:\n    print(count)\n    count += 1",
                        explanation="Loop that counts from 0 to 4"
                    ),
                    CodeExample(
                        code="total = 0\nnum = 1\nwhile num <= 10:\n    total += num\n    num += 1\nprint(total)  # 55",
                        explanation="Sum numbers 1 through 10"
                    )
                ],
                exercises=[
                    Exercise(
                        id="control_03_ex1",
                        prompt="Use a while loop to print numbers 1 through 3, each on a new line.",
                        test_cases=[("", "1\n2\n3")],
                        hints=[
                            "Start with n = 1",
                            "Loop while n <= 3",
                            "Print n, then increment: n += 1"
                        ],
                        difficulty=2,
                        concept="loops"
                    )
                ],
                prerequisites=["control_02_loops"],
                xp_reward=25,
                skill_path="control_flow",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="control_03_mcq1",
                        question="What happens if a while loop condition is always True?",
                        choices=["Loop runs once", "Loop never runs", "Infinite loop", "Syntax error"],
                        correct_answer=2,
                        explanation="If the condition never becomes False, you get an infinite loop.",
                        difficulty=1,
                        concept="loops"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="control_03_drill1",
                        code="x = 3\nwhile x > 0:\n    print(x)\n    x -= 1",
                        correct_output="3\n2\n1",
                        explanation="Counts down from 3 to 1.",
                        difficulty=1,
                        concept="loops"
                    )
                ]
            ),

            Lesson(
                id="strings_01_methods",
                title="String Methods",
                concept="""Python strings have many useful built-in methods for manipulation.

Common String Methods:
• .upper(), .lower(): Change case
• .strip(): Remove whitespace from ends
• .replace(old, new): Replace substring
• .split(): Split into list
• .join(list): Join list into string
• .startswith(), .endswith(): Check start/end
• .find(), .count(): Search within string

Strings are immutable - methods return new strings!""",
                examples=[
                    CodeExample(
                        code="text = '  Hello World  '\nprint(text.strip())  # 'Hello World'\nprint(text.upper())  # '  HELLO WORLD  '",
                        explanation="String methods return new strings"
                    ),
                    CodeExample(
                        code="words = 'apple,banana,cherry'.split(',')\nprint(words)  # ['apple', 'banana', 'cherry']",
                        explanation="Split string into list"
                    )
                ],
                exercises=[
                    Exercise(
                        id="strings_01_ex1",
                        prompt="Take the string 'python' and print it in uppercase.",
                        test_cases=[("", "PYTHON")],
                        hints=[
                            "Use the .upper() method",
                            "text = 'python'",
                            "print(text.upper())"
                        ],
                        difficulty=1,
                        concept="strings"
                    )
                ],
                prerequisites=["data_02_dictionaries"],
                xp_reward=25,
                skill_path="basics",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="strings_01_mcq1",
                        question="What does 'Hello'.lower() return?",
                        choices=["'HELLO'", "'hello'", "'Hello'", "Error"],
                        correct_answer=1,
                        explanation=".lower() converts all characters to lowercase.",
                        difficulty=1,
                        concept="strings"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="strings_01_drill1",
                        code="s = 'hello world'\nprint(s.replace('world', 'python'))",
                        correct_output="hello python",
                        explanation="Replaces 'world' with 'python' in the string.",
                        difficulty=1,
                        concept="strings"
                    )
                ]
            ),

            Lesson(
                id="advanced_01_comprehensions",
                title="List Comprehensions",
                concept="""List comprehensions provide a concise way to create lists.

Basic Syntax:
[expression for item in iterable]

With Condition:
[expression for item in iterable if condition]

Examples:
• [x*2 for x in range(5)] → [0, 2, 4, 6, 8]
• [x for x in range(10) if x % 2 == 0] → [0, 2, 4, 6, 8]

Benefits:
• More readable than loops
• Often faster
• Creates new list in one line""",
                examples=[
                    CodeExample(
                        code="squares = [x**2 for x in range(5)]\nprint(squares)  # [0, 1, 4, 9, 16]",
                        explanation="Create list of squares"
                    ),
                    CodeExample(
                        code="nums = [1, 2, 3, 4, 5, 6]\nevens = [n for n in nums if n % 2 == 0]\nprint(evens)  # [2, 4, 6]",
                        explanation="Filter even numbers"
                    )
                ],
                exercises=[
                    Exercise(
                        id="advanced_01_ex1",
                        prompt="Create a list comprehension that produces [2, 4, 6, 8, 10] and print it.",
                        test_cases=[("", "[2, 4, 6, 8, 10]")],
                        hints=[
                            "Use range(1, 6) for numbers 1-5",
                            "Multiply each by 2",
                            "[x*2 for x in range(1, 6)]"
                        ],
                        difficulty=3,
                        concept="comprehensions"
                    )
                ],
                prerequisites=["strings_01_methods"],
                xp_reward=35,
                skill_path="advanced",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="advanced_01_mcq1",
                        question="What does [x for x in range(3)] produce?",
                        choices=["[1, 2, 3]", "[0, 1, 2]", "[0, 1, 2, 3]", "Error"],
                        correct_answer=1,
                        explanation="range(3) produces 0, 1, 2",
                        difficulty=2,
                        concept="comprehensions"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="advanced_01_drill1",
                        code="result = [x*3 for x in [1, 2, 3]]\nprint(result)",
                        correct_output="[3, 6, 9]",
                        explanation="Multiplies each element by 3.",
                        difficulty=2,
                        concept="comprehensions"
                    )
                ]
            ),

            Lesson(
                id="advanced_02_exceptions",
                title="Error Handling",
                concept="""Handle errors gracefully with try/except blocks.

Syntax:
try:
    # code that might fail
except ErrorType:
    # handle the error
finally:
    # always runs (optional)

Common Exceptions:
• ValueError: Invalid value
• TypeError: Wrong type
• ZeroDivisionError: Division by zero
• KeyError: Dictionary key not found

Use 'except Exception' to catch all errors (but be specific when possible!)""",
                examples=[
                    CodeExample(
                        code="try:\n    x = int('abc')\nexcept ValueError:\n    print('Invalid number!')\n# Prints: Invalid number!",
                        explanation="Catch conversion error"
                    ),
                    CodeExample(
                        code="try:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    result = 0\nprint(result)  # 0",
                        explanation="Handle division by zero"
                    )
                ],
                exercises=[
                    Exercise(
                        id="advanced_02_ex1",
                        prompt="Write try/except that tries to convert '123' to int and prints the result. If it fails, print 'Error'.",
                        test_cases=[("", "123")],
                        hints=[
                            "try:",
                            "    print(int('123'))",
                            "except: print('Error')"
                        ],
                        difficulty=2,
                        concept="exceptions"
                    )
                ],
                prerequisites=["advanced_01_comprehensions"],
                xp_reward=35,
                skill_path="advanced",
                mcq_questions=[
                    MultipleChoiceQuestion(
                        id="advanced_02_mcq1",
                        question="What does 'finally' do in try/except?",
                        choices=["Runs only on error", "Runs only on success", "Always runs", "Never runs"],
                        correct_answer=2,
                        explanation="The 'finally' block always executes, whether an error occurred or not.",
                        difficulty=2,
                        concept="exceptions"
                    )
                ],
                output_drills=[
                    OutputDrill(
                        id="advanced_02_drill1",
                        code="try:\n    print(5 / 1)\nexcept:\n    print('Error')",
                        correct_output="5.0",
                        explanation="No error occurs, so the division result is printed.",
                        difficulty=1,
                        concept="exceptions"
                    )
                ]
            )
        ]

    @staticmethod
    def get_lesson_by_id(lesson_id: str) -> Optional[Lesson]:
        for lesson in ContentEngine.get_all_lessons():
            if lesson.id == lesson_id:
                return lesson
        return None

    @staticmethod
    def get_available_lessons(completed: Set[str]) -> List[Lesson]:
        available = []
        for lesson in ContentEngine.get_all_lessons():
            if lesson.id not in completed:
                if all(prereq in completed for prereq in lesson.prerequisites):
                    available.append(lesson)
        return available

    @staticmethod
    def get_skill_paths() -> Dict[str, List[Lesson]]:
        paths = defaultdict(list)
        for lesson in ContentEngine.get_all_lessons():
            paths[lesson.skill_path].append(lesson)
        return dict(paths)


# ============================================================================
# SECTION 3: GAMIFICATION SYSTEM
# ============================================================================

class GamificationSystem:
    LEVEL_THRESHOLDS = [0, 50, 150, 300, 500, 750, 1050, 1400, 1800, 2250, 2750, 3300, 4000, 4800, 5700, 6700]

    @staticmethod
    def calculate_level(xp: int) -> int:
        for level, threshold in enumerate(GamificationSystem.LEVEL_THRESHOLDS, start=1):
            if xp < threshold:
                return level - 1
        return len(GamificationSystem.LEVEL_THRESHOLDS) - 1

    @staticmethod
    def xp_for_next_level(current_xp: int) -> int:
        level = GamificationSystem.calculate_level(current_xp)
        if level >= len(GamificationSystem.LEVEL_THRESHOLDS):
            return 0
        return GamificationSystem.LEVEL_THRESHOLDS[level] - current_xp

    @staticmethod
    def update_streak(user: User) -> Tuple[bool, str]:
        today = datetime.now().date()
        last = datetime.fromisoformat(user.last_active).date()
        delta = (today - last).days

        if delta == 0:
            return False, "You've already checked in today! Keep learning to earn more XP."
        elif delta == 1:
            user.streak_days += 1
            # FIXED: Ensure vitality never exceeds 100
            user.companion_vitality = min(100, user.companion_vitality + 10)
            user.last_active = today.isoformat()
            user.today_xp = 0
            user.add_activity('streak', f'{user.streak_days} day streak!', 0)

            companion = Companion(CompanionType(user.companion_type), user.companion_stage, user.companion_vitality)
            if companion.can_evolve() and user.streak_days % 3 == 0:
                user.companion_stage += 1
                evolved_companion = Companion(CompanionType(user.companion_type), user.companion_stage,
                                              user.companion_vitality)
                user.add_activity('evolution', f'Companion evolved to {evolved_companion.get_name()}!', 0)
                return True, f"🎉 Amazing! {user.streak_days} day streak!\n\nYour companion evolved to {evolved_companion.get_name()}!"

            return True, f"✅ Great job! {user.streak_days} day streak!\n\nVitality +10"
        else:
            vitality_loss = min(delta * 10, 50)
            user.companion_vitality = max(0, user.companion_vitality - vitality_loss)

            stage_loss = 0
            if user.companion_vitality < 30 and user.companion_stage > 0:
                stage_loss = min(delta - 1, user.companion_stage)
                user.companion_stage -= stage_loss

            user.streak_days = 1
            user.last_active = today.isoformat()
            user.today_xp = 0

            return False, f"Welcome back! You missed {delta} days.\n\nVitality -{vitality_loss}, Stage -{stage_loss}\n\nBut you're here now - let's keep going!"

    @staticmethod
    def check_achievements(user: User) -> List[str]:
        new_achievements = []

        achievements_map = {
            'first_lesson': ('First Steps', lambda u: len(u.completed_lessons) >= 1),
            'lessons_3': ('Quick Learner', lambda u: len(u.completed_lessons) >= 3),
            'lessons_5': ('Dedicated Student', lambda u: len(u.completed_lessons) >= 5),
            'streak_7': ('Week Warrior', lambda u: u.streak_days >= 7),
            'streak_30': ('Month Master', lambda u: u.streak_days >= 30),
            'streak_100': ('Century Scholar', lambda u: u.streak_days >= 100),
            'level_5': ('Level 5 Unlocked', lambda u: u.level >= 5),
            'level_10': ('Level 10 Unlocked', lambda u: u.level >= 10),
            'xp_500': ('XP Champion', lambda u: u.xp >= 500),
            'xp_1000': ('XP Master', lambda u: u.xp >= 1000),
            'companion_stage_5': ('Rising Star', lambda u: u.companion_stage >= 5),
            'companion_max': ('Legendary Companion', lambda u: u.companion_stage >= 10),
            'vitality_100': ('Perfect Care', lambda u: u.companion_vitality == 100),
            'daily_goal_streak_5': ('Consistent Learner', lambda u: u.streak_days >= 5),
            'exercises_10': ('Practice Makes Perfect', lambda u: u.total_exercises_completed >= 10),
            'exercises_50': ('Exercise Enthusiast', lambda u: u.total_exercises_completed >= 50),
            'hints_low': ('Self Reliant', lambda u: u.total_exercises_completed >= 10 and u.total_hints_used < 5),
            'drills_10': ('Drill Master', lambda u: u.total_drills_completed >= 10),
            'drills_25': ('Drill Expert', lambda u: u.total_drills_completed >= 25),
            'bug_hunter': ('Bug Hunter', lambda u: getattr(u, 'total_bugs_fixed', 0) >= 5),
            'exterminator': ('Bug Exterminator', lambda u: getattr(u, 'total_bugs_fixed', 0) >= 15),
            'debug_master': ('Debug Master', lambda u: getattr(u, 'total_bugs_fixed', 0) >= 30),
        }

        for ach_id, (name, condition) in achievements_map.items():
            if ach_id not in user.achievements and condition(user):
                user.achievements.append(ach_id)
                new_achievements.append(name)

        return new_achievements

    @staticmethod
    def add_xp(user: User, amount: int, reason: str = "Exercise completed") -> Tuple[bool, int]:
        old_level = user.level
        user.xp += amount
        user.today_xp += amount
        user.level = GamificationSystem.calculate_level(user.xp)
        user.add_activity('xp_gain', reason, amount)

        if user.level > old_level:
            user.add_activity('level_up', f'Reached level {user.level}!', 0)

        return user.level > old_level, user.level

    @staticmethod
    def get_progress_to_next_level(user: User) -> Tuple[int, int, int]:
        level = user.level
        if level >= len(GamificationSystem.LEVEL_THRESHOLDS):
            return 0, 0, 100

        current_threshold = GamificationSystem.LEVEL_THRESHOLDS[level - 1] if level > 0 else 0
        next_threshold = GamificationSystem.LEVEL_THRESHOLDS[level]

        current_level_xp = user.xp - current_threshold
        xp_needed = next_threshold - current_threshold
        percentage = int((current_level_xp / xp_needed) * 100) if xp_needed > 0 else 100

        return current_level_xp, xp_needed, percentage


# ============================================================================
# SECTION 4: CODE EXECUTION & VALIDATION
# ============================================================================

class CodeExecutor:
    # Note: Timeout not implemented - would require threading/multiprocessing
    # For safety, we rely on blacklist instead
    TIMEOUT_SECONDS = 5  # Not currently used
    MAX_OUTPUT_LENGTH = 1000
    BLACKLIST = ['__import__', 'eval', 'exec', 'compile', 'open', 'input',
                 'file', 'os', 'sys', 'subprocess', 'globals', 'locals',
                 'vars', 'dir', '__builtins__']

    @staticmethod
    def execute_code(code: str, test_input: str = "") -> Tuple[bool, str, str]:
        code_lower = code.lower()
        for banned in CodeExecutor.BLACKLIST:
            if banned in code_lower:
                return False, "", f"Restricted keyword: {banned}"

        if 'import' in code_lower:
            return False, "", "Import statements are not allowed in exercises"

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        success = True
        error_msg = ""

        try:
            safe_globals = {
                '__builtins__': {
                    'print': print, 'len': len, 'range': range, 'str': str,
                    'int': int, 'float': float, 'bool': bool, 'list': list,
                    'dict': dict, 'set': set, 'tuple': tuple, 'sum': sum,
                    'max': max, 'min': min, 'abs': abs, 'round': round,
                    'sorted': sorted, 'enumerate': enumerate, 'zip': zip,
                    'map': map, 'filter': filter, 'reversed': reversed,
                    'all': all, 'any': any, 'True': True, 'False': False, 'None': None,
                }
            }

            exec(code, safe_globals)

        except Exception as e:
            success = False
            error_msg = f"{type(e).__name__}: {str(e)}"

        finally:
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout

        if len(output) > CodeExecutor.MAX_OUTPUT_LENGTH:
            output = output[:CodeExecutor.MAX_OUTPUT_LENGTH] + "\n... (truncated)"

        return success, output, error_msg


class HintSystem:
    @staticmethod
    def get_adaptive_hint(exercise: Exercise, attempt_count: int, last_error: str = "") -> str:
        if attempt_count == 0:
            return "💡 Think about the problem carefully. You can do this!"

        hint_index = min(attempt_count - 1, len(exercise.hints) - 1)
        base_hint = exercise.hints[hint_index] if exercise.hints else "Try reviewing the lesson examples."

        error_hints = {
            "SyntaxError": "💡 Syntax error - check your parentheses, colons, and indentation.",
            "NameError": "💡 Variable not defined - make sure you've created all necessary variables.",
            "TypeError": "💡 Type mismatch - check if you need to convert types (int, str, etc.).",
            "IndentationError": "💡 Indentation error - Python uses indentation to define code blocks.",
            "ValueError": "💡 Value error - check if you're converting types correctly.",
        }

        for error_type, hint in error_hints.items():
            if error_type in last_error:
                return f"{base_hint}\n\n{hint}"

        if attempt_count >= 3:
            return f"{base_hint}\n\n💪 Don't give up! Try breaking the problem into smaller steps."

        return base_hint


# ============================================================================
# SECTION 5: ENHANCED UI COMPONENTS
# ============================================================================

class CompanionView(CTkFrame):
    def __init__(self, parent, user: User, on_switch_companion=None):
        super().__init__(parent, corner_radius=20, fg_color="transparent")
        self.user = user
        self.on_switch_companion = on_switch_companion
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()
        companion = Companion(
            CompanionType(self.user.companion_type),
            self.user.companion_stage,
            self.user.companion_vitality
        )

        # FIXED: Use getattr for safe attribute access
        ui_font = getattr(self.user, 'ui_font', DEFAULT_FONT)
        code_font = getattr(self.user, 'code_font', CODE_FONT)

        # Animated header
        header_frame = CTkFrame(self, corner_radius=15,
                                fg_color=colors['primary'], height=60)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)

        CTkLabel(header_frame, text="Your Companion",
                 font=ctk.CTkFont(family=ui_font, size=13, weight="bold"),
                 text_color="white").pack(side='top', pady=(8, 2))

        CTkLabel(header_frame, text=companion.get_name(),
                 font=ctk.CTkFont(family=ui_font, size=16, weight="bold"),
                 text_color="white").pack(side='top')

        # Companion ASCII with enhanced styling
        art_frame = CTkFrame(self, corner_radius=15, fg_color=colors['bg_dark'],
                             border_width=2, border_color=colors['primary'])
        art_frame.pack(pady=10, fill='x', padx=10)

        CTkLabel(art_frame, text=companion.get_ascii(),
                 font=ctk.CTkFont(family=code_font, size=15, weight="bold"),
                 text_color=colors['accent']).pack(pady=25)

        # Companion Health section
        vitality_container = CTkFrame(self, corner_radius=12, fg_color=colors['bg_dark'])
        vitality_container.pack(fill='x', padx=10, pady=5)

        vitality_header = CTkFrame(vitality_container, fg_color="transparent")
        vitality_header.pack(fill='x', padx=15, pady=(12, 5))

        CTkLabel(vitality_header, text="💚 Companion Health",
                 font=ctk.CTkFont(family=ui_font, size=13, weight="bold")).pack(side='left')

        # Vitality percentage with color coding
        vitality_color = colors['success'] if self.user.companion_vitality > 70 else (
            colors['warning'] if self.user.companion_vitality > 30 else colors['error']
        )
        CTkLabel(vitality_header, text=f"{self.user.companion_vitality}%",
                 font=ctk.CTkFont(family=ui_font, size=13, weight="bold"),
                 text_color=vitality_color).pack(side='right')

        # Enhanced progress bar
        progress = CTkProgressBar(vitality_container, corner_radius=8, height=12,
                                  progress_color=vitality_color)
        progress.set(self.user.companion_vitality / 100)
        progress.pack(fill='x', padx=15, pady=(0, 12))

        # Stage info
        stage_frame = CTkFrame(self, corner_radius=12, fg_color=colors['bg_dark'])
        stage_frame.pack(fill='x', padx=10, pady=5)

        CTkLabel(stage_frame, text=f"⭐ Stage {self.user.companion_stage}/10",
                 font=ctk.CTkFont(family=ui_font, size=12),
                 text_color=colors['text_secondary']).pack(pady=10)

        # Switch companion button
        if self.on_switch_companion:
            switch_btn = CTkButton(self, text="🔄 Switch Companion",
                                   corner_radius=12, height=36,
                                   fg_color=colors['bg_light'],
                                   hover_color=colors['primary'],
                                   border_width=2,
                                   border_color=colors['bg_light'],
                                   font=ctk.CTkFont(family=ui_font, size=12),
                                   command=self.on_switch_companion)
            switch_btn.pack(pady=(10, 15), padx=10, fill='x')


class StatsCard(CTkFrame):
    """Reusable stats card component with enhanced styling"""

    def __init__(self, parent, label: str, value: str, icon: str = "", color: str = None):
        colors = get_colors()
        bg_color = color if color else colors['bg_dark']
        super().__init__(parent, corner_radius=15, fg_color=bg_color,
                         border_width=2, border_color=colors['bg_light'])

        content = CTkFrame(self, fg_color="transparent")
        content.pack(fill='both', expand=True, padx=15, pady=15)

        if icon:
            CTkLabel(content, text=icon,
                     font=ctk.CTkFont(family=DEFAULT_FONT, size=28)).pack(pady=(0, 8))

        CTkLabel(content, text=label,
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=11, weight="normal"),
                 text_color=colors['text_secondary']).pack()
        CTkLabel(content, text=value,
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=22, weight="bold")).pack(pady=(4, 0))


class DashboardView(CTkFrame):
    """Main dashboard showing user progress and daily goals"""

    def __init__(self, parent, user: User, on_lesson_start, on_daily_challenge):
        super().__init__(parent, corner_radius=20, fg_color="transparent")
        self.user = user
        self.on_lesson_start = on_lesson_start
        self.on_daily_challenge = on_daily_challenge
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        # Welcome header
        CTkLabel(self, text=f"Welcome back, {self.user.username}!",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=26, weight="bold")).pack(pady=(10, 5))

        # Daily progress bar
        daily_progress_frame = CTkFrame(self, corner_radius=15, fg_color=colors['bg_medium'])
        daily_progress_frame.pack(fill='x', pady=10)

        CTkLabel(daily_progress_frame,
                 text=f"Daily Goal: {self.user.today_xp}/{self.user.daily_goal_xp} XP",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=13)).pack(anchor='w', padx=10, pady=(10, 5))

        daily_progress = CTkProgressBar(daily_progress_frame, corner_radius=10, height=12)
        daily_progress.set(min(self.user.today_xp / self.user.daily_goal_xp, 1.0))
        daily_progress.pack(fill='x', padx=10, pady=(0, 10))

        # Stats grid
        stats_container = CTkFrame(self, fg_color="transparent")
        stats_container.pack(fill='x', pady=10)

        # Configure grid
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1, uniform="stat")

        stats = [
            ("🔥", "Streak", f"{self.user.streak_days} days"),
            ("⭐", "Level", str(self.user.level)),
            ("💎", "XP", str(self.user.xp)),
            ("📚", "Lessons", str(len(self.user.completed_lessons))),
        ]

        for i, (icon, label, value) in enumerate(stats):
            card = StatsCard(stats_container, label, value, icon)
            card.grid(row=0, column=i, padx=5, sticky="nsew")

        # Daily Challenge section with better design
        today = datetime.now().date().isoformat()
        challenge_completed = self.user.daily_challenge_completed == today

        challenge_frame = CTkFrame(self, corner_radius=20,
                                   fg_color=colors['success'] if challenge_completed else colors['primary'],
                                   border_width=0)
        challenge_frame.pack(fill='x', pady=(0, 15))

        challenge_content = CTkFrame(challenge_frame, fg_color="transparent")
        challenge_content.pack(fill='x', padx=25, pady=25)

        icon = "✅" if challenge_completed else "⭐"
        CTkLabel(challenge_content,
                 text=f"{icon} Daily Challenge",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=18, weight="bold"),
                 text_color="white").pack(anchor='w')

        if not challenge_completed:
            CTkLabel(challenge_content,
                     text="Complete today's challenge for +50 bonus XP!",
                     font=ctk.CTkFont(family=DEFAULT_FONT, size=13),
                     text_color="white").pack(anchor='w', pady=(8, 18))

            CTkButton(challenge_content, text="Start Challenge →",
                      corner_radius=12, height=40,
                      fg_color="white",
                      text_color=colors['primary'],
                      hover_color=colors['bg_light'],
                      font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
                      command=self.on_daily_challenge).pack(anchor='w')
        else:
            CTkLabel(challenge_content,
                     text="Completed! Come back tomorrow for a new challenge.",
                     font=ctk.CTkFont(family=DEFAULT_FONT, size=13),
                     text_color="white").pack(anchor='w', pady=(8, 0))

        # Recent Activity with better styling
        if self.user.activity_log:
            activity_frame = CTkFrame(self, corner_radius=20, fg_color=colors['bg_dark'],
                                      border_width=2, border_color=colors['bg_light'])
            activity_frame.pack(fill='both', expand=True, pady=(0, 15))

            header = CTkFrame(activity_frame, fg_color=colors['bg_medium'],
                              corner_radius=18)
            header.pack(fill='x', padx=2, pady=2)

            CTkLabel(header, text="📜 Recent Activity",
                     font=ctk.CTkFont(family=DEFAULT_FONT, size=16, weight="bold")).pack(anchor='w', padx=20, pady=15)

            # Show last 5 activities
            for idx, activity in enumerate(self.user.activity_log[-5:][::-1]):
                activity_item = CTkFrame(activity_frame,
                                         fg_color=colors['bg_medium'] if idx % 2 == 0 else "transparent",
                                         corner_radius=10)
                activity_item.pack(fill='x', padx=15, pady=2)

                desc_text = f"• {activity['description']}"
                if activity['xp_gained'] > 0:
                    desc_text += f"  (+{activity['xp_gained']} XP)"

                CTkLabel(activity_item, text=desc_text,
                         font=ctk.CTkFont(family=DEFAULT_FONT, size=12),
                         anchor='w').pack(anchor='w', padx=15, pady=10, fill='x')

        # Enhanced tips section
        tips = [
            "💡 Maintain your streak to help your companion evolve!",
            "💡 Complete lessons to unlock new content and skills.",
            "💡 Use hints wisely - solving problems yourself builds confidence!",
            "💡 Review completed lessons to reinforce your learning.",
            "💡 Try the daily challenge for bonus XP and practice!",
            "💡 Experiment with the code - breaking things helps you learn!",
        ]

        tips_frame = CTkFrame(self, corner_radius=20, fg_color=colors['accent'])
        tips_frame.pack(fill='x')

        CTkLabel(tips_frame, text=random.choice(tips),
                 wraplength=750, justify="left",
                 text_color="white",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=13)).pack(padx=20, pady=18)


class DailyChallengeView(CTkFrame):
    """View for daily challenge"""

    def __init__(self, parent, user: User, on_complete, on_back):
        super().__init__(parent, corner_radius=20, fg_color="transparent")
        self.user = user
        self.on_complete = on_complete
        self.on_back = on_back
        self.attempt_count = 0
        self.last_error = ""
        self.start_time = datetime.now()

        # Generate today's challenge
        today = datetime.now().date().isoformat()
        self.daily_challenge = DailyChallenge.generate_for_date(today)
        self.exercise = self.daily_challenge.exercise

        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        # Header
        header = CTkFrame(self, corner_radius=15, fg_color=colors['bg_medium'])
        header.pack(fill='x', pady=10)

        back_btn = CTkButton(header, text="← Back", corner_radius=10, width=80,
                             command=self.on_back)
        back_btn.pack(side='left', padx=10, pady=10)

        CTkLabel(header, text="⭐ Daily Challenge",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(side='left', padx=10)

        CTkLabel(header, text=f"+{self.daily_challenge.bonus_xp} Bonus XP",
                 font=ctk.CTkFont(size=14),
                 text_color=colors['warning']).pack(side='right', padx=10)

        # Exercise content
        content = CTkFrame(self, corner_radius=15, fg_color=colors['bg_dark'])
        content.pack(fill='both', expand=True, pady=10)

        CTkLabel(content, text=self.exercise.prompt,
                 wraplength=700, justify="left",
                 font=ctk.CTkFont(size=13)).pack(anchor='w', padx=15, pady=15)

        # Code editor
        self.code_editor = CTkTextbox(content, corner_radius=10, height=250,
                                      fg_color="#0e0e0e",
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.code_editor.pack(fill='both', expand=True, padx=15, pady=10)
        if self.exercise.starter_code:
            self.code_editor.insert("0.0", self.exercise.starter_code)

        # Hint section
        self.hint_label = CTkLabel(content, text="", wraplength=700,
                                   text_color=colors['warning'])
        self.hint_label.pack(anchor='w', padx=15, pady=10)

        hint_btn = CTkButton(content, text="💡 Get Hint", corner_radius=10,
                             fg_color=colors['bg_medium'],
                             command=self._show_hint)
        hint_btn.pack(anchor='w', padx=15, pady=5)

        # Output
        self.output_text = CTkTextbox(content, corner_radius=10, height=100,
                                      fg_color="#0e0e0e")
        self.output_text.configure(state="disabled")
        self.output_text.pack(fill='x', padx=15, pady=10)

        # Buttons
        btn_frame = CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15, pady=(0, 15))

        CTkButton(btn_frame, text="▶ Run Code", corner_radius=10,
                  fg_color=colors['primary'],
                  command=self._run_code).pack(side='left', padx=5)

        CTkButton(btn_frame, text="✓ Submit", corner_radius=10,
                  fg_color=colors['success'],
                  command=self._submit_code).pack(side='left', padx=5)

    def _show_hint(self):
        self.user.total_hints_used += 1
        hint = HintSystem.get_adaptive_hint(self.exercise, self.attempt_count, self.last_error)
        self.hint_label.configure(text=hint)

    def _run_code(self):
        code = self.code_editor.get("0.0", "end-1c")
        success, output, error = CodeExecutor.execute_code(code)

        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")
        if success:
            self.output_text.insert("0.0", f"Output:\n{output}")
        else:
            self.output_text.insert("0.0", f"Error:\n{error}")
            self.last_error = error
        self.output_text.configure(state="disabled")

    def _submit_code(self):
        code = self.code_editor.get("0.0", "end-1c")
        self.attempt_count += 1

        success, message, details = self.exercise.validate_solution(code)

        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")

        if success:
            completion_time = (datetime.now() - self.start_time).seconds
            self.output_text.insert("0.0",
                                    f"🎉 {message}\n\nCompleted in {completion_time}s\nBonus XP: +{self.daily_challenge.bonus_xp}")

            # Mark as completed
            today = datetime.now().date().isoformat()
            self.user.daily_challenge_completed = today

            # Award bonus XP
            leveled_up, new_level = GamificationSystem.add_xp(
                self.user,
                self.daily_challenge.bonus_xp,
                "Daily Challenge completed!"
            )

            if leveled_up:
                messagebox.showinfo("Level Up!", f"You reached level {new_level}!")

            self.after(2000, self.on_complete)
        else:
            error_text = f"❌ {message}\n\n"
            if details:
                error_text += "\n".join(details)
            self.output_text.insert("0.0", error_text)

        self.output_text.configure(state="disabled")


# FIXED: MCQ View with proper attempt tracking and immediate feedback
class MCQView(CTkFrame):
    def __init__(self, parent, question: MultipleChoiceQuestion, on_submit):
        super().__init__(parent, corner_radius=10, fg_color=get_colors()['bg_dark'])
        self.question = question
        self.on_submit = on_submit
        self.selected_answer = ctk.IntVar(value=-1)
        self.attempts = 0
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        # Question text
        CTkLabel(self, text=self.question.question,
                 wraplength=650, justify="left",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=14)).pack(anchor='w', padx=15, pady=(15, 10))

        # Answer choices
        choices_frame = CTkFrame(self, fg_color="transparent")
        choices_frame.pack(fill='both', expand=True, padx=15, pady=10)

        for i, choice in enumerate(self.question.choices):
            choice_frame = CTkFrame(choices_frame, corner_radius=8, fg_color=colors['bg_medium'])
            choice_frame.pack(fill='x', pady=3)

            radio = CTkRadioButton(choice_frame, text=f"{chr(65 + i)}. {choice}",
                                   variable=self.selected_answer, value=i,
                                   font=ctk.CTkFont(family=DEFAULT_FONT, size=13))
            radio.pack(anchor='w', padx=10, pady=10)

        # Submit button
        submit_btn = CTkButton(self, text="Submit Answer", corner_radius=10,
                               fg_color=colors['success'],
                               command=self._handle_submit)
        submit_btn.pack(pady=(10, 15))

    def _handle_submit(self):
        selected = self.selected_answer.get()
        if selected == -1:
            messagebox.showwarning("No Selection", "Please select an answer!")
            return

        self.attempts += 1
        is_correct = self.question.check_answer(selected)
        
        if not is_correct:
            # Show immediate feedback for wrong answer
            if self.attempts < 3:
                messagebox.showinfo("Try Again", "That's not quite right. Try again!")
                return
            else:
                # After 3 attempts, show explanation and move on
                messagebox.showinfo("Correct Answer", 
                                  f"The correct answer was: {chr(65 + self.question.correct_answer)}. {self.question.choices[self.question.correct_answer]}\n\n{self.question.explanation}")
        
        self.on_submit(is_correct, self.question.explanation)


# FIXED: Multi-answer view with attempt tracking
class MultiAnswerView(CTkFrame):
    def __init__(self, parent, question: MultiAnswerQuestion, on_submit):
        super().__init__(parent, corner_radius=10, fg_color=get_colors()['bg_dark'])
        self.question = question
        self.on_submit = on_submit
        self.checkboxes = []
        self.attempts = 0
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        # Question text
        CTkLabel(self, text=self.question.question,
                 wraplength=650, justify="left",
                 font=ctk.CTkFont(size=13, weight="bold")).pack(anchor='w', padx=15, pady=(15, 5))

        CTkLabel(self, text="(Select all that apply)",
                 font=ctk.CTkFont(size=11),
                 text_color=colors['text_secondary']).pack(anchor='w', padx=15, pady=(0, 10))

        # Answer choices
        choices_frame = CTkFrame(self, fg_color="transparent")
        choices_frame.pack(fill='both', expand=True, padx=15, pady=10)

        for i, choice in enumerate(self.question.choices):
            choice_frame = CTkFrame(choices_frame, corner_radius=8, fg_color=colors['bg_medium'])
            choice_frame.pack(fill='x', pady=3)

            var = ctk.BooleanVar()
            checkbox = CTkCheckBox(choice_frame, text=f"{chr(65 + i)}. {choice}",
                                   variable=var,
                                   font=ctk.CTkFont(size=12))
            checkbox.pack(anchor='w', padx=10, pady=10)
            self.checkboxes.append((i, var))

        # Submit button
        submit_btn = CTkButton(self, text="Submit Answer", corner_radius=10,
                               fg_color=colors['success'],
                               command=self._handle_submit)
        submit_btn.pack(pady=(10, 15))

    def _handle_submit(self):
        selected_indices = [i for i, var in self.checkboxes if var.get()]

        if not selected_indices:
            messagebox.showwarning("No Selection", "Please select at least one answer!")
            return

        self.attempts += 1
        is_correct = self.question.check_answer(selected_indices)
        
        if not is_correct:
            if self.attempts < 3:
                messagebox.showinfo("Try Again", "That's not quite right. Try again!")
                return
            else:
                # Show correct answers after 3 attempts
                correct_letters = [chr(65 + i) for i in self.question.correct_answers]
                messagebox.showinfo("Correct Answers",
                                  f"The correct answers were: {', '.join(correct_letters)}\n\n{self.question.explanation}")
        
        self.on_submit(is_correct, self.question.explanation)


# FIXED: Output drill view with attempt tracking
class OutputDrillView(CTkFrame):
    def __init__(self, parent, drill: OutputDrill, on_submit):
        super().__init__(parent, corner_radius=10, fg_color=get_colors()['bg_dark'])
        self.drill = drill
        self.on_submit = on_submit
        self.attempts = 0
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        # Instruction
        CTkLabel(self, text="What does this code output?",
                 font=ctk.CTkFont(size=13, weight="bold")).pack(anchor='w', padx=15, pady=(15, 10))

        # Code display
        code_frame = CTkFrame(self, corner_radius=8, fg_color="#0e0e0e")
        code_frame.pack(fill='x', padx=15, pady=10)

        code_text = CTkTextbox(code_frame, height=120,
                               fg_color="#0e0e0e",
                               font=ctk.CTkFont(family="Consolas", size=12))
        code_text.insert("0.0", self.drill.code)
        code_text.configure(state="disabled")
        code_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Answer input
        answer_label = CTkLabel(self, text="Your Answer:",
                                font=ctk.CTkFont(size=12))
        answer_label.pack(anchor='w', padx=15, pady=(10, 5))

        self.answer_entry = CTkEntry(self, height=35,
                                     font=ctk.CTkFont(size=12))
        self.answer_entry.pack(fill='x', padx=15, pady=(0, 10))
        self.answer_entry.bind('<Return>', lambda e: self._handle_submit())

        # Submit button
        submit_btn = CTkButton(self, text="Submit Answer", corner_radius=10,
                               fg_color=colors['success'],
                               command=self._handle_submit)
        submit_btn.pack(pady=(10, 15))

    def _handle_submit(self):
        user_answer = self.answer_entry.get().strip()

        if not user_answer:
            messagebox.showwarning("No Answer", "Please enter an answer!")
            return

        self.attempts += 1
        is_correct = self.drill.check_answer(user_answer)
        
        if not is_correct:
            if self.attempts < 3:
                messagebox.showinfo("Try Again", "That's not quite right. Try again!")
                return
            else:
                # Show correct answer after 3 attempts
                messagebox.showinfo("Correct Answer",
                                  f"The correct output is:\n{self.drill.correct_output}\n\n{self.drill.explanation}")
        
        self.on_submit(is_correct, self.drill.explanation, self.drill.correct_output)


class BugFixDrillView(CTkFrame):
    """Interactive bug fixing challenge"""
    def __init__(self, parent, drill: BugFixDrill, on_submit):
        super().__init__(parent, corner_radius=10, fg_color=get_colors()['bg_dark'])
        self.drill = drill
        self.on_submit = on_submit
        self.attempts = 0
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        # Header with bug icon
        header = CTkFrame(self, corner_radius=8, fg_color=colors['error'])
        header.pack(fill='x', padx=15, pady=(15, 10))
        
        CTkLabel(header, text="🐛 BUG DETECTED!",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="white").pack(pady=10)

        # Bug description
        CTkLabel(self, text=self.drill.bug_description,
                 font=ctk.CTkFont(size=12),
                 wraplength=650,
                 text_color=colors['warning']).pack(anchor='w', padx=15, pady=(0, 10))

        # Buggy code display
        CTkLabel(self, text="Buggy Code:",
                 font=ctk.CTkFont(size=11, weight="bold")).pack(anchor='w', padx=15, pady=(10, 5))

        buggy_frame = CTkFrame(self, corner_radius=8, fg_color="#1a0000",
                               border_width=2, border_color=colors['error'])
        buggy_frame.pack(fill='x', padx=15, pady=(0, 10))

        buggy_display = CTkTextbox(buggy_frame, height=120,
                                   fg_color="#1a0000",
                                   font=ctk.CTkFont(family="Consolas", size=12),
                                   text_color="#ff6b6b")
        buggy_display.insert("0.0", self.drill.buggy_code)
        buggy_display.configure(state="disabled")
        buggy_display.pack(fill='both', expand=True, padx=5, pady=5)

        # Code editor for fix
        CTkLabel(self, text="Fix the code below:",
                 font=ctk.CTkFont(size=11, weight="bold")).pack(anchor='w', padx=15, pady=(10, 5))

        editor_frame = CTkFrame(self, corner_radius=8, fg_color="#0e0e0e")
        editor_frame.pack(fill='both', expand=True, padx=15, pady=(0, 10))

        self.code_editor = CTkTextbox(editor_frame,
                                      fg_color="#0e0e0e",
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.code_editor.insert("0.0", self.drill.buggy_code)
        self.code_editor.pack(fill='both', expand=True, padx=5, pady=5)

        # Hint section
        self.hint_label = CTkLabel(self, text="",
                                   wraplength=650,
                                   text_color=colors['info'])
        self.hint_label.pack(anchor='w', padx=15, pady=5)

        # Buttons
        btn_frame = CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15, pady=(0, 15))

        CTkButton(btn_frame, text="💡 Get Hint",
                  corner_radius=10,
                  fg_color=colors['bg_medium'],
                  hover_color=colors['bg_light'],
                  command=self._show_hint).pack(side='left', padx=5)

        CTkButton(btn_frame, text="🔧 Test Fix",
                  corner_radius=10,
                  fg_color=colors['primary'],
                  command=self._test_code).pack(side='left', padx=5)

        CTkButton(btn_frame, text="✓ Submit Fix",
                  corner_radius=10,
                  fg_color=colors['success'],
                  command=self._submit_fix).pack(side='left', padx=5)

        # Output area
        self.output_label = CTkLabel(self, text="",
                                     wraplength=650,
                                     font=ctk.CTkFont(size=11))
        self.output_label.pack(anchor='w', padx=15, pady=5)

    def _show_hint(self):
        if self.attempts < len(self.drill.hints):
            hint = self.drill.hints[self.attempts]
            self.hint_label.configure(text=f"💡 Hint: {hint}")
        else:
            self.hint_label.configure(text=f"💡 Hint: {self.drill.hints[-1]}")

    def _test_code(self):
        """Test if the code runs without showing if it's correct"""
        code = self.code_editor.get("0.0", "end-1c")
        executor = CodeExecutor()
        success, output, error = executor.execute_code(code)

        if success:
            self.output_label.configure(
                text=f"✓ Code runs! Output: {output.strip()}\n(This may or may not be the correct fix)",
                text_color=get_colors()['success']
            )
        else:
            self.output_label.configure(
                text=f"✗ Error: {error}",
                text_color=get_colors()['error']
            )

    def _submit_fix(self):
        code = self.code_editor.get("0.0", "end-1c")
        self.attempts += 1

        is_correct, message = self.drill.check_answer(code)

        if is_correct:
            self.on_submit(True, self.drill.explanation)
        else:
            if self.attempts < 3:
                messagebox.showinfo("Not Quite", f"{message}\n\nTry again! Use hints if needed.")
            else:
                # Show solution after 3 attempts
                messagebox.showinfo("Solution", 
                                  f"Here's the correct code:\n\n{self.drill.correct_code}\n\n{self.drill.explanation}")
                self.on_submit(False, self.drill.explanation)


# FIXED: Lesson View with proper progress tracking and MCQ/drill handling
class LessonView(CTkFrame):
    def __init__(self, parent, user: User, lesson: Lesson, on_complete, on_back):
        super().__init__(parent, corner_radius=20, fg_color="transparent")
        self.user = user
        self.lesson = lesson
        self.on_complete = on_complete
        self.on_back = on_back
        self.current_exercise_idx = 0
        self.exercise_attempts = {}
        self.last_error = ""
        self.exercise_start_time = datetime.now()

        # Track all lesson items (exercises + MCQs + drills)
        self.lesson_items = []
        # Add exercises
        for ex in lesson.exercises:
            self.lesson_items.append(('exercise', ex))
        # Add MCQs
        for mcq in lesson.mcq_questions:
            self.lesson_items.append(('mcq', mcq))
        # Add multi-answer questions
        for maq in lesson.multi_answer_questions:
            self.lesson_items.append(('multi_answer', maq))
        # Add output drills
        for drill in lesson.output_drills:
            self.lesson_items.append(('drill', drill))
        # Add bug fix drills
        for bug_drill in lesson.bug_fix_drills:
            self.lesson_items.append(('bug_fix', bug_drill))

        self.current_item_idx = 0

        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        # Header with back button and progress bar
        header = CTkFrame(self, corner_radius=15, fg_color=colors['bg_medium'])
        header.pack(fill='x', pady=10)

        back_btn = CTkButton(header, text="← Back", corner_radius=10, width=80,
                             command=self.on_back)
        back_btn.pack(side='left', padx=10, pady=10)

        CTkLabel(header, text=self.lesson.title,
                 font=ctk.CTkFont(size=20, weight="bold")).pack(side='left', padx=10)

        # Lesson progress bar
        progress_container = CTkFrame(header, fg_color="transparent")
        progress_container.pack(side='right', padx=20, pady=10, fill='x', expand=True)

        total_items = len(self.lesson_items)
        progress_text = f"{self.current_item_idx}/{total_items}"
        CTkLabel(progress_container, text=progress_text,
                 font=ctk.CTkFont(size=11)).pack()

        self.lesson_progress_bar = CTkProgressBar(progress_container, height=8)
        if total_items > 0:
            self.lesson_progress_bar.set(self.current_item_idx / total_items)
        else:
            self.lesson_progress_bar.set(0)
        self.lesson_progress_bar.pack(fill='x', padx=0)

        # Tabview for Concept, Examples, Practice
        tabview = CTkTabview(self, corner_radius=15)
        tabview.pack(fill='both', expand=True)

        # Concept tab
        concept_tab = tabview.add("📖 Concept")
        concept_text = CTkTextbox(concept_tab, corner_radius=10, wrap="word",
                                  font=ctk.CTkFont(size=12))
        concept_text.insert("0.0", self.lesson.concept)
        concept_text.configure(state="disabled")
        concept_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Examples tab
        examples_tab = tabview.add("💡 Examples")
        examples_scroll = CTkScrollableFrame(examples_tab, corner_radius=10)
        examples_scroll.pack(fill='both', expand=True, padx=10, pady=10)

        for i, example in enumerate(self.lesson.examples):
            ex_frame = CTkFrame(examples_scroll, corner_radius=10, fg_color=colors['bg_dark'])
            ex_frame.pack(fill='x', pady=5)

            CTkLabel(ex_frame, text=f"Example {i + 1}",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))

            code_text = CTkTextbox(ex_frame, corner_radius=10, height=80,
                                   fg_color="#0e0e0e",
                                   font=ctk.CTkFont(family="Consolas", size=11))
            code_text.insert("0.0", example.code)
            code_text.configure(state="disabled")
            code_text.pack(fill='x', padx=10, pady=5)

            CTkLabel(ex_frame, text=example.explanation,
                     wraplength=650).pack(anchor='w', padx=10, pady=(5, 10))

        # Practice tab
        practice_tab = tabview.add("✏️ Practice")
        self.practice_container = CTkFrame(practice_tab, corner_radius=10, fg_color=colors['bg_dark'])
        self.practice_container.pack(fill='both', expand=True, padx=10, pady=10)

        self._show_current_item()

    def _show_current_item(self):
        colors = get_colors()

        for widget in self.practice_container.winfo_children():
            widget.destroy()

        if self.current_item_idx >= len(self.lesson_items):
            self._show_completion()
            return

        # FIXED: Update progress bar safely
        total_items = len(self.lesson_items)
        if hasattr(self, 'lesson_progress_bar') and total_items > 0:
            self.lesson_progress_bar.set(self.current_item_idx / total_items)

        item_type, item_data = self.lesson_items[self.current_item_idx]

        # Show appropriate view based on type
        if item_type == 'exercise':
            self._show_exercise(item_data)
        elif item_type == 'mcq':
            self._show_mcq(item_data)
        elif item_type == 'multi_answer':
            self._show_multi_answer(item_data)
        elif item_type == 'drill':
            self._show_drill(item_data)
        elif item_type == 'bug_fix':
            self._show_bug_fix(item_data)

    def _show_exercise(self, exercise: Exercise):
        colors = get_colors()
        self.exercise_start_time = datetime.now()

        # Exercise prompt
        CTkLabel(self.practice_container, text=f"✏️ Coding Exercise",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color=colors['primary']).pack(anchor='w', padx=15, pady=(15, 5))

        CTkLabel(self.practice_container, text=exercise.prompt,
                 wraplength=700, justify="left",
                 font=ctk.CTkFont(size=13)).pack(anchor='w', padx=15, pady=(5, 15))

        # Code editor
        editor_frame = CTkFrame(self.practice_container, fg_color="#0e0e0e", corner_radius=10)
        editor_frame.pack(fill='both', expand=True, padx=15, pady=10)

        self.code_editor = CTkTextbox(editor_frame, corner_radius=0,
                                      fg_color="#0e0e0e",
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.code_editor.pack(fill='both', expand=True, padx=5, pady=5)

        if exercise.starter_code:
            self.code_editor.insert("0.0", exercise.starter_code)

        # Hint section
        self.hint_label = CTkLabel(self.practice_container, text="",
                                   wraplength=700, text_color=colors['warning'])
        self.hint_label.pack(anchor='w', padx=15, pady=10)

        hint_btn = CTkButton(self.practice_container, text="💡 Get Hint",
                             corner_radius=10, height=32,
                             fg_color=colors['bg_medium'],
                             hover_color=colors['bg_light'],
                             command=lambda: self._show_hint(exercise))
        hint_btn.pack(anchor='w', padx=15, pady=5)

        # Output area
        CTkLabel(self.practice_container, text="Output:",
                 font=ctk.CTkFont(size=11, weight="bold")).pack(anchor='w', padx=15, pady=(10, 5))

        self.output_text = CTkTextbox(self.practice_container, corner_radius=10,
                                      height=100, fg_color="#0e0e0e")
        self.output_text.configure(state="disabled")
        self.output_text.pack(fill='x', padx=15, pady=(0, 10))

        # Action buttons
        btn_frame = CTkFrame(self.practice_container, fg_color="transparent")
        btn_frame.pack(fill='x', padx=15, pady=(0, 15))

        run_btn = CTkButton(btn_frame, text="▶ Run Code", corner_radius=10,
                            fg_color=colors['primary'],
                            hover_color="#1a5a8a",
                            command=lambda: self._run_code(exercise))
        run_btn.pack(side='left', padx=5)

        submit_btn = CTkButton(btn_frame, text="✓ Submit Solution", corner_radius=10,
                               fg_color=colors['success'],
                               hover_color="#246339",
                               command=lambda: self._submit_code(exercise))
        submit_btn.pack(side='left', padx=5)

        # Keyboard shortcuts
        self.code_editor.bind('<Control-Return>', lambda e: self._run_code(exercise))
        self.code_editor.bind('<Control-Shift-Return>', lambda e: self._submit_code(exercise))

    def _show_mcq(self, question: MultipleChoiceQuestion):
        colors = get_colors()

        CTkLabel(self.practice_container, text=f"❓ Multiple Choice Question",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
                 text_color=colors['primary']).pack(anchor='w', padx=15, pady=(15, 10))

        mcq_view = MCQView(self.practice_container, question,
                           lambda correct, explanation: self._handle_mcq_result(correct, explanation, question))
        mcq_view.pack(fill='both', expand=True, padx=0, pady=0)

    def _show_multi_answer(self, question: MultiAnswerQuestion):
        colors = get_colors()

        CTkLabel(self.practice_container, text=f"☑️ Multiple Choice (Multi-Answer)",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
                 text_color=colors['primary']).pack(anchor='w', padx=15, pady=(15, 10))

        multi_view = MultiAnswerView(self.practice_container, question,
                                     lambda correct, explanation: self._handle_mcq_result(correct, explanation, question))
        multi_view.pack(fill='both', expand=True, padx=0, pady=0)

    def _show_drill(self, drill: OutputDrill):
        colors = get_colors()

        CTkLabel(self.practice_container, text=f"🎯 Output Drill",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
                 text_color=colors['primary']).pack(anchor='w', padx=15, pady=(15, 10))

        drill_view = OutputDrillView(self.practice_container, drill,
                                     lambda correct, explanation, answer: self._handle_drill_result(correct, explanation, answer, drill))
        drill_view.pack(fill='both', expand=True, padx=0, pady=0)

    def _show_bug_fix(self, bug_drill: BugFixDrill):
        colors = get_colors()

        CTkLabel(self.practice_container, text=f"🐛 Bug Fixing Challenge",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
                 text_color=colors['error']).pack(anchor='w', padx=15, pady=(15, 10))

        bug_view = BugFixDrillView(self.practice_container, bug_drill,
                                   lambda correct, explanation: self._handle_bug_fix_result(correct, explanation, bug_drill))
        bug_view.pack(fill='both', expand=True, padx=0, pady=0)

    # FIXED: Proper MCQ result handling
    def _handle_mcq_result(self, is_correct: bool, explanation: str, question):
        if is_correct:
            xp_reward = question.difficulty * 3
            leveled_up, new_level = GamificationSystem.add_xp(
                self.user, xp_reward, f"Answered question correctly"
            )

            result_msg = f"✓ Correct! +{xp_reward} XP\n\n{explanation}"
            messagebox.showinfo("Correct!", result_msg)

            if leveled_up:
                messagebox.showinfo("Level Up!", f"You reached level {new_level}!")

            self.current_item_idx += 1
            self._show_current_item()

    # FIXED: Proper drill result handling
    def _handle_drill_result(self, is_correct: bool, explanation: str, correct_answer: str, drill: OutputDrill):
        if is_correct:
            xp_reward = drill.difficulty * 3
            leveled_up, new_level = GamificationSystem.add_xp(
                self.user, xp_reward, "Completed output drill"
            )

            # Track drill completion
            self.user.total_drills_completed += 1
            self.user.completed_drills[drill.id] = self.user.completed_drills.get(drill.id, 0) + 1

            result_msg = f"✓ Correct! +{xp_reward} XP\n\n{explanation}"
            messagebox.showinfo("Correct!", result_msg)

            if leveled_up:
                messagebox.showinfo("Level Up!", f"You reached level {new_level}!")

            self.current_item_idx += 1
            self._show_current_item()

    def _handle_bug_fix_result(self, is_correct: bool, explanation: str, bug_drill: BugFixDrill):
        """Handle bug fix drill completion"""
        if is_correct:
            xp_reward = bug_drill.difficulty * 5  # Bug fixes worth more!
            leveled_up, new_level = GamificationSystem.add_xp(
                self.user, xp_reward, "Fixed a bug!"
            )

            # Track bug fix completion
            if not hasattr(self.user, 'total_bugs_fixed'):
                self.user.total_bugs_fixed = 0
            self.user.total_bugs_fixed += 1

            result_msg = f"🎉 Bug Fixed! +{xp_reward} XP\n\n{explanation}"
            messagebox.showinfo("Success!", result_msg)

            if leveled_up:
                messagebox.showinfo("Level Up!", f"You reached level {new_level}!")

            self.current_item_idx += 1
            self._show_current_item()
        else:
            # Even if they got it wrong after 3 attempts, move on
            self.current_item_idx += 1
            self._show_current_item()

    def _show_hint(self, exercise: Exercise):
        self.user.total_hints_used += 1
        attempt_count = self.exercise_attempts.get(exercise.id, 0)
        hint = HintSystem.get_adaptive_hint(exercise, attempt_count, self.last_error)
        self.hint_label.configure(text=hint)

    def _run_code(self, exercise: Exercise):
        code = self.code_editor.get("0.0", "end-1c")
        success, output, error = CodeExecutor.execute_code(code)

        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")

        if success:
            self.output_text.insert("0.0", f"✓ Code executed successfully!\n\n{output}")
        else:
            self.output_text.insert("0.0", f"✗ Error occurred:\n\n{error}")
            self.last_error = error

        self.output_text.configure(state="disabled")

    def _submit_code(self, exercise: Exercise):
        code = self.code_editor.get("0.0", "end-1c")
        self.exercise_attempts[exercise.id] = self.exercise_attempts.get(exercise.id, 0) + 1

        success, message, details = exercise.validate_solution(code)

        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")

        if success:
            completion_time = (datetime.now() - self.exercise_start_time).seconds

            # Update user stats
            self.user.total_exercises_completed += 1
            if completion_time < self.user.fastest_completion_time:
                self.user.fastest_completion_time = completion_time

            xp_reward = exercise.difficulty * 5
            leveled_up, new_level = GamificationSystem.add_xp(
                self.user, xp_reward, f"Completed {exercise.concept} exercise"
            )

            self.output_text.insert("0.0",
                                    f"🎉 {message}\n\nTime: {completion_time}s\nXP Earned: +{xp_reward}")

            if leveled_up:
                messagebox.showinfo("Level Up!",
                                    f"Congratulations! You reached level {new_level}!")

            self.after(1500, self._next_item)
        else:
            error_display = f"❌ {message}\n\n"
            if details:
                error_display += "Failed test cases:\n" + "\n---\n".join(details)
            self.output_text.insert("0.0", error_display)

        self.output_text.configure(state="disabled")

    def _next_item(self):
        self.current_item_idx += 1
        self._show_current_item()

    def _show_completion(self):
        colors = get_colors()

        for widget in self.practice_container.winfo_children():
            widget.destroy()

        # FIXED: Set progress bar to 100%
        if hasattr(self, 'lesson_progress_bar'):
            self.lesson_progress_bar.set(1.0)

        # Completion celebration
        CTkLabel(self.practice_container, text="🎉",
                 font=ctk.CTkFont(size=48)).pack(pady=20)

        CTkLabel(self.practice_container, text="Lesson Complete!",
                 font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        # Award lesson XP
        leveled_up, new_level = GamificationSystem.add_xp(
            self.user, self.lesson.xp_reward, f"Completed lesson: {self.lesson.title}"
        )

        CTkLabel(self.practice_container,
                 text=f"You earned {self.lesson.xp_reward} XP!",
                 font=ctk.CTkFont(size=14)).pack(pady=5)

        if leveled_up:
            CTkLabel(self.practice_container,
                     text=f"🌟 Level Up! You're now level {new_level}!",
                     font=ctk.CTkFont(size=14),
                     text_color=colors['warning']).pack(pady=5)

        # Check for achievements
        new_achievements = GamificationSystem.check_achievements(self.user)
        if new_achievements:
            CTkLabel(self.practice_container,
                     text=f"🏆 New Achievement: {', '.join(new_achievements)}",
                     font=ctk.CTkFont(size=13),
                     text_color=colors['warning']).pack(pady=10)

        CTkButton(self.practice_container, text="Continue Learning",
                  corner_radius=10, height=40,
                  fg_color=colors['success'],
                  command=self.on_complete).pack(pady=20)


class StatisticsView(CTkFrame):
    """Detailed learning statistics"""

    def __init__(self, parent, user: User):
        super().__init__(parent, corner_radius=20, fg_color="transparent")
        self.user = user
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()

        CTkLabel(self, text="Learning Statistics",
                 font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        scroll = CTkScrollableFrame(self, corner_radius=15, fg_color=colors['bg_medium'])
        scroll.pack(fill='both', expand=True)

        # Overview stats
        overview = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
        overview.pack(fill='x', padx=10, pady=10)

        CTkLabel(overview, text="Overview",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        stats_data = [
            ("Total XP Earned", f"{self.user.xp} XP"),
            ("Current Level", f"Level {self.user.level}"),
            ("Lessons Completed", f"{len(self.user.completed_lessons)} lessons"),
            ("Exercises Completed", f"{self.user.total_exercises_completed} exercises"),
            ("Drills Completed", f"{self.user.total_drills_completed} drills"),
            ("Bugs Fixed", f"{getattr(self.user, 'total_bugs_fixed', 0)} bugs 🐛"),
            ("Current Streak", f"{self.user.streak_days} days"),
            ("Hints Used", f"{self.user.total_hints_used} hints"),
            ("Fastest Completion",
             f"{self.user.fastest_completion_time}s" if self.user.fastest_completion_time < 999999 else "N/A"),
        ]

        for label, value in stats_data:
            stat_row = CTkFrame(overview, fg_color=colors['bg_medium'], corner_radius=8)
            stat_row.pack(fill='x', padx=10, pady=2)

            CTkLabel(stat_row, text=label,
                     font=ctk.CTkFont(size=12)).pack(side='left', padx=10, pady=8)
            CTkLabel(stat_row, text=value,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side='right', padx=10, pady=8)

        # Progress by skill path
        paths = ContentEngine.get_skill_paths()
        if paths:
            paths_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
            paths_frame.pack(fill='x', padx=10, pady=10)

            CTkLabel(paths_frame, text="Progress by Topic",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

            for path_name, lessons in paths.items():
                completed_in_path = sum(1 for l in lessons if l.id in self.user.completed_lessons)
                total_in_path = len(lessons)

                path_row = CTkFrame(paths_frame, fg_color=colors['bg_medium'], corner_radius=8)
                path_row.pack(fill='x', padx=10, pady=5)

                CTkLabel(path_row, text=path_name.replace('_', ' ').title(),
                         font=ctk.CTkFont(size=12)).pack(anchor='w', padx=10, pady=(8, 2))

                progress_bar = CTkProgressBar(path_row, corner_radius=10, height=8)
                progress_bar.set(completed_in_path / total_in_path if total_in_path > 0 else 0)
                progress_bar.pack(fill='x', padx=10, pady=(2, 2))

                CTkLabel(path_row, text=f"{completed_in_path}/{total_in_path} lessons",
                         font=ctk.CTkFont(size=10),
                         text_color=colors['text_secondary']).pack(anchor='w', padx=10, pady=(2, 8))

        # Achievements section
        if self.user.achievements:
            ach_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
            ach_frame.pack(fill='x', padx=10, pady=10)

            CTkLabel(ach_frame, text=f"Achievements ({len(self.user.achievements)})",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

            for achievement in self.user.achievements:
                ach_row = CTkFrame(ach_frame, fg_color=colors['bg_medium'], corner_radius=8)
                ach_row.pack(fill='x', padx=10, pady=2)

                CTkLabel(ach_row, text=f"🏆 {achievement}",
                         font=ctk.CTkFont(size=11)).pack(anchor='w', padx=10, pady=6)


# FIXED: Removed duplicate SettingsView definition - keeping only one complete version
class SettingsView(CTkFrame):
    def __init__(self, parent, user: User, on_theme_change, on_font_save,
                 on_goal_save, on_switch_companion, on_export, on_import, on_reset, on_check_updates):
        super().__init__(parent, corner_radius=20, fg_color="transparent")
        self.user = user
        self.on_theme_change = on_theme_change
        self.on_font_save = on_font_save
        self.on_goal_save = on_goal_save
        self.on_switch_companion = on_switch_companion
        self.on_export = on_export
        self.on_import = on_import
        self.on_reset = on_reset
        self.on_check_updates = on_check_updates
        self.preview_label = None
        self._create_widgets()

    def _create_widgets(self):
        colors = get_colors()
        # FIXED: Safe attribute access
        user_font = getattr(self.user, 'ui_font', DEFAULT_FONT)

        CTkLabel(self, text="Settings",
                 font=ctk.CTkFont(family=user_font, size=24, weight="bold")).pack(pady=10)

        scroll = CTkScrollableFrame(self, corner_radius=15, fg_color=colors['bg_medium'])
        scroll.pack(fill='both', expand=True)

        # ===== APPEARANCE SECTION =====
        appearance_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
        appearance_frame.pack(fill='x', padx=10, pady=10)

        CTkLabel(appearance_frame, text="Appearance",
                 font=ctk.CTkFont(family=user_font, size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        # Interface Font
        CTkLabel(appearance_frame, text="Interface Font",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(anchor='w', padx=10, pady=(10, 5))

        ui_font_frame = CTkFrame(appearance_frame, fg_color=colors['bg_medium'], corner_radius=8)
        ui_font_frame.pack(fill='x', padx=10, pady=(0, 10))

        current_ui_font = getattr(self.user, 'ui_font', DEFAULT_FONT)
        for font_name in UI_FONTS:
            is_selected = font_name == current_ui_font
            font_btn = CTkButton(ui_font_frame,
                                 text=font_name,
                                 corner_radius=8,
                                 height=32,
                                 fg_color=colors['primary'] if is_selected else colors['bg_light'],
                                 hover_color=colors['primary_hover'],
                                 font=ctk.CTkFont(family=user_font, size=11),
                                 command=lambda f=font_name: self._change_ui_font(f))
            font_btn.pack(side='left', padx=3, pady=5)
            font_btn.bind('<Enter>', lambda e, f=font_name: self._show_font_preview(e, f, 'ui'))
            font_btn.bind('<Leave>', lambda e: self._hide_font_preview())

        # Code Font
        CTkLabel(appearance_frame, text="Code Editor Font",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(anchor='w', padx=10, pady=(10, 5))

        code_font_frame = CTkFrame(appearance_frame, fg_color=colors['bg_medium'], corner_radius=8)
        code_font_frame.pack(fill='x', padx=10, pady=(0, 10))

        current_code_font = getattr(self.user, 'code_font', CODE_FONT)
        for font_name in CODE_FONTS:
            is_selected = font_name == current_code_font
            font_btn = CTkButton(code_font_frame,
                                 text=font_name,
                                 corner_radius=8,
                                 height=32,
                                 fg_color=colors['primary'] if is_selected else colors['bg_light'],
                                 hover_color=colors['primary_hover'],
                                 font=ctk.CTkFont(family=user_font, size=11),
                                 command=lambda f=font_name: self._change_code_font(f))
            font_btn.pack(side='left', padx=3, pady=5)
            font_btn.bind('<Enter>', lambda e, f=font_name: self._show_font_preview(e, f, 'code'))
            font_btn.bind('<Leave>', lambda e: self._hide_font_preview())

        # Font Size
        CTkLabel(appearance_frame, text="Font Size",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(anchor='w', padx=10, pady=(10, 5))

        font_row = CTkFrame(appearance_frame, fg_color="transparent")
        font_row.pack(fill='x', padx=10, pady=(0, 10))

        font_entry = CTkEntry(font_row, width=80, height=32,
                              font=ctk.CTkFont(family=user_font, size=12))
        font_entry.insert(0, str(self.user.font_size))
        font_entry.pack(side='left', padx=(0, 10))

        CTkButton(font_row, text="Apply", corner_radius=10,
                  height=32, width=80, fg_color=colors['primary'],
                  font=ctk.CTkFont(family=user_font, size=11),
                  command=lambda: self.on_font_save(font_entry.get())).pack(side='left')

        # ===== ACCESSIBILITY SECTION =====
        accessibility_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
        accessibility_frame.pack(fill='x', padx=10, pady=10)

        CTkLabel(accessibility_frame, text="Accessibility",
                 font=ctk.CTkFont(family=user_font, size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        contrast_row = CTkFrame(accessibility_frame, fg_color="transparent")
        contrast_row.pack(fill='x', padx=10, pady=5)
        CTkLabel(contrast_row, text="High Contrast Mode",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(side='left')
        contrast_switch = CTkSwitch(contrast_row, text="", command=lambda: self._toggle_high_contrast())
        if getattr(self.user, 'high_contrast', False):
            contrast_switch.select()
        contrast_switch.pack(side='right')

        anim_row = CTkFrame(accessibility_frame, fg_color="transparent")
        anim_row.pack(fill='x', padx=10, pady=(5, 10))
        CTkLabel(anim_row, text="Reduce Animations",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(side='left')
        anim_switch = CTkSwitch(anim_row, text="", command=lambda: self._toggle_animations())
        if getattr(self.user, 'reduce_animations', False):
            anim_switch.select()
        anim_switch.pack(side='right')

        # ===== LEARNING SECTION =====
        learning_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
        learning_frame.pack(fill='x', padx=10, pady=10)

        CTkLabel(learning_frame, text="Learning",
                 font=ctk.CTkFont(family=user_font, size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        CTkLabel(learning_frame, text="Daily XP Goal",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(anchor='w', padx=10, pady=(10, 5))

        goal_row = CTkFrame(learning_frame, fg_color="transparent")
        goal_row.pack(fill='x', padx=10, pady=(0, 10))

        goal_entry = CTkEntry(goal_row, width=80, height=32,
                              font=ctk.CTkFont(family=user_font, size=12))
        goal_entry.insert(0, str(self.user.daily_goal_xp))
        goal_entry.pack(side='left', padx=(0, 10))

        CTkButton(goal_row, text="Apply", corner_radius=10,
                  height=32, width=80, fg_color=colors['primary'],
                  font=ctk.CTkFont(family=user_font, size=11),
                  command=lambda: self.on_goal_save(goal_entry.get())).pack(side='left')

        # ===== COMPANION SECTION =====
        companion_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
        companion_frame.pack(fill='x', padx=10, pady=10)

        CTkLabel(companion_frame, text="Companion",
                 font=ctk.CTkFont(family=user_font, size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        current_companion = Companion(CompanionType(self.user.companion_type),
                                      self.user.companion_stage, self.user.companion_vitality)

        CTkLabel(companion_frame,
                 text=f"Current: {current_companion.get_name()} ({self.user.companion_type.title()})",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(padx=10, pady=5)

        CTkLabel(companion_frame,
                 text="⚠️ Switching will reset your companion's stage!",
                 font=ctk.CTkFont(family=user_font, size=10),
                 text_color=colors['warning']).pack(padx=10, pady=5)

        CTkButton(companion_frame, text="Switch Companion Type", corner_radius=10,
                  height=28, fg_color=colors['warning'],
                  font=ctk.CTkFont(family=user_font, size=11),
                  command=self.on_switch_companion).pack(padx=10, pady=10)

        # ===== UPDATES SECTION =====
        updates_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
        updates_frame.pack(fill='x', padx=10, pady=10)

        CTkLabel(updates_frame, text="Updates",
                 font=ctk.CTkFont(family=user_font, size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        CTkLabel(updates_frame, text=f"Current Version: {CURRENT_VERSION}",
                 font=ctk.CTkFont(family=user_font, size=12)).pack(anchor='w', padx=10, pady=5)

        CTkButton(updates_frame, text="Check for Updates", corner_radius=10,
                  height=32, fg_color=colors['primary'],
                  font=ctk.CTkFont(family=user_font, size=11),
                  command=self.on_check_updates).pack(fill='x', padx=10, pady=10)

        # ===== DATA MANAGEMENT SECTION =====
        data_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['bg_dark'])
        data_frame.pack(fill='x', padx=10, pady=10)

        CTkLabel(data_frame, text="Data Management",
                 font=ctk.CTkFont(family=user_font, size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        CTkButton(data_frame, text="📤 Export Progress", corner_radius=10,
                  height=32, fg_color=colors['primary'],
                  font=ctk.CTkFont(family=user_font, size=11),
                  command=self.on_export).pack(fill='x', padx=10, pady=5)

        CTkButton(data_frame, text="📥 Import Progress", corner_radius=10,
                  height=32, fg_color=colors['primary'],
                  font=ctk.CTkFont(family=user_font, size=11),
                  command=self.on_import).pack(fill='x', padx=10, pady=5)

        CTkLabel(data_frame,
                 text="Export your progress to backup or transfer to another device.",
                 font=ctk.CTkFont(family=user_font, size=10),
                 text_color=colors['text_secondary'],
                 wraplength=600).pack(padx=10, pady=(0, 10))

        # ===== DANGER ZONE =====
        danger_frame = CTkFrame(scroll, corner_radius=10, fg_color=colors['error'])
        danger_frame.pack(fill='x', padx=10, pady=10)

        CTkLabel(danger_frame, text="⚠️ Danger Zone",
                 font=ctk.CTkFont(family=user_font, size=16, weight="bold")).pack(anchor='w', padx=10, pady=10)

        CTkLabel(danger_frame,
                 text="This will delete all your progress permanently!",
                 font=ctk.CTkFont(family=user_font, size=11)).pack(padx=10, pady=5)

        CTkButton(danger_frame, text="Reset All Progress", corner_radius=10,
                  height=32, fg_color="#8b0000", hover_color="#660000",
                  font=ctk.CTkFont(family=user_font, size=11),
                  command=self.on_reset).pack(padx=10, pady=10)

    def _show_font_preview(self, event, font_name, font_type):
        if self.preview_label:
            self.preview_label.destroy()

        colors = get_colors()
        x = event.widget.winfo_rootx() + event.widget.winfo_width() // 2
        y = event.widget.winfo_rooty() - 60

        self.preview_label = CTkFrame(self.master, fg_color=colors['bg_dark'],
                                      corner_radius=10, border_width=2,
                                      border_color=colors['primary'])
        self.preview_label.place(x=x - 100, y=y)

        preview_text = "The quick brown fox" if font_type == 'ui' else "def hello():\n    print('Hi')"

        CTkLabel(self.preview_label, text=preview_text,
                 font=ctk.CTkFont(family=font_name, size=12),
                 justify='left').pack(padx=15, pady=10)

    def _hide_font_preview(self):
        if self.preview_label:
            self.preview_label.destroy()
            self.preview_label = None

    def _change_ui_font(self, font_name):
        self.user.ui_font = font_name
        messagebox.showinfo("Font Changed", f"UI font changed to {font_name}!\nRestart the app to see changes.")

    def _change_code_font(self, font_name):
        self.user.code_font = font_name
        messagebox.showinfo("Font Changed", f"Code font changed to {font_name}!\nRestart the app to see changes.")

    def _toggle_high_contrast(self):
        if not hasattr(self.user, 'high_contrast'):
            self.user.high_contrast = False
        self.user.high_contrast = not self.user.high_contrast

    def _toggle_animations(self):
        if not hasattr(self.user, 'reduce_animations'):
            self.user.reduce_animations = False
        self.user.reduce_animations = not self.user.reduce_animations


# ============================================================================
# SECTION 6: APPLICATION CONTROLLER
# ============================================================================

class CodeCompanionApp:
    def __init__(self):
        self.root = CTk()
        self.root.title("CodeCompanion - Learn Python with Your Growing Companion")
        # FIXED: Make window geometry consistent with minsize
        self.root.geometry("1400x900")
        self.root.minsize(1400, 900)

        # Try to set custom icon
        try:
            icon_path = "CCAppIcon.png"
            if os.path.exists(icon_path):
                self.icon_image = Image.open(icon_path)
                self.icon_photo = ImageTk.PhotoImage(self.icon_image)
                self.root.iconphoto(False, self.icon_photo)
        except:
            pass  # Icon optional

        self.storage = StorageManager()
        self.user = self.storage.load_user()

        if self.user is None:
            self._show_onboarding()
        else:
            # Check for updates on startup (non-blocking)
            self._auto_update_check()
            self._create_ui()
            self._check_daily_streak()

    def _auto_update_check(self):
        """Check for updates automatically on startup"""
        if not hasattr(self.user, 'auto_check_updates') or self.user.auto_check_updates:
            try:
                has_update, latest_version, download_url = auto_update_check_and_install()
                if has_update:
                    # Show non-intrusive notification
                    self.root.after(2000, lambda: self._show_update_notification(latest_version, download_url))
            except:
                pass  # Silently fail

    def _show_update_notification(self, latest_version, download_url):
        """Show a friendly update notification"""
        response = messagebox.askyesno(
            "Update Available! 🎉",
            f"CodeCompanion {latest_version} is available!\n\n"
            f"You're currently on version {CURRENT_VERSION}.\n\n"
            f"Would you like to download the update?\n"
            f"(It will open in your browser)",
            icon='info'
        )
        if response:
            webbrowser.open(download_url)

    def _check_daily_streak(self):
        """Check and update streak on app startup"""
        streak_increased, message = GamificationSystem.update_streak(self.user)
        if message and "already checked in" not in message:
            messagebox.showinfo("Daily Check-in", message)
            self.storage.save_user(self.user)
            self._refresh_current_view()

    def _show_onboarding(self):
        """Initial setup for new users"""
        colors = get_colors()
        self.root.geometry("500x650")
        frame = CTkFrame(self.root, corner_radius=20)
        frame.pack(pady=20, padx=20, fill='both', expand=True)

        CTkLabel(frame, text="Welcome to CodeCompanion!",
                 font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

        CTkLabel(frame, text="Learn Python while growing your companion",
                 font=ctk.CTkFont(size=14)).pack(pady=5)

        # Username
        CTkLabel(frame, text="Choose Your Username",
                 font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=20, pady=(20, 5))
        self.username_entry = CTkEntry(frame, height=35,
                                       font=ctk.CTkFont(size=13))
        self.username_entry.pack(fill='x', padx=20, pady=5)
        self.username_entry.insert(0, "Learner")

        # Companion selection
        CTkLabel(frame, text="Choose Your Companion",
                 font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=20, pady=(20, 5))

        # Show all companion options with descriptions
        companions_frame = CTkFrame(frame, fg_color="transparent")
        companions_frame.pack(fill='x', padx=20, pady=10)

        self.selected_companion = ctk.StringVar(value="plant")

        for comp_type in CompanionType:
            companion = Companion(comp_type, 0, 100)
            radio_frame = CTkFrame(companions_frame, corner_radius=10,
                                   fg_color=colors['bg_dark'])
            radio_frame.pack(fill='x', pady=5)

            radio = CTkRadioButton(radio_frame, text="",
                                   variable=self.selected_companion,
                                   value=comp_type.value)
            radio.pack(side='left', padx=10)

            info_frame = CTkFrame(radio_frame, fg_color="transparent")
            info_frame.pack(side='left', fill='x', expand=True, pady=10)

            CTkLabel(info_frame, text=comp_type.value.title(),
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w')
            CTkLabel(info_frame, text=companion.get_description(),
                     font=ctk.CTkFont(size=10),
                     text_color=colors['text_secondary'],
                     wraplength=300).pack(anchor='w')

        # Start button
        start_btn = CTkButton(frame, text="Start Learning!",
                              corner_radius=10, height=40,
                              font=ctk.CTkFont(size=14, weight="bold"),
                              fg_color=colors['success'],
                              command=self._create_user)
        start_btn.pack(pady=30)

    def _create_user(self):
        """Create new user profile"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Invalid Username", "Please enter a username!")
            return

        companion_type = self.selected_companion.get()
        self.user = User(username=username, companion_type=companion_type)
        self.storage.save_user(self.user)

        # FIXED: Consistent window size
        self.root.geometry("1400x900")
        self._create_ui()

        messagebox.showinfo("Welcome!",
                            f"Welcome, {username}! Your {companion_type} companion awaits. Let's start learning Python!")

    def _create_ui(self):
        """Create main application interface"""
        colors = get_colors()

        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_container = CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill='both', expand=True)

        # Left sidebar (300px fixed width)
        sidebar = CTkFrame(main_container, width=300, corner_radius=0,
                           fg_color=colors['bg_medium'])
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # Companion view in sidebar
        companion_view = CompanionView(sidebar, self.user,
                                       on_switch_companion=self._show_companion_switcher)
        companion_view.pack(pady=20, padx=10)

        # Navigation buttons
        nav_frame = CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill='x', padx=10, pady=10)

        nav_buttons = [
            ("🏠 Dashboard", self._show_dashboard),
            ("📊 Statistics", self._show_statistics),
            ("⚙️ Settings", self._show_settings),
        ]

        for text, command in nav_buttons:
            btn = CTkButton(nav_frame, text=text, corner_radius=12,
                            fg_color="transparent",
                            hover_color=colors['primary'],
                            anchor='w', height=42,
                            font=ctk.CTkFont(family=DEFAULT_FONT, size=13, weight="bold"),
                            command=command)
            btn.pack(fill='x', pady=4)

        # Lessons section with enhanced header
        lessons_header = CTkFrame(sidebar, corner_radius=12, fg_color=colors['primary'])
        lessons_header.pack(fill='x', padx=10, pady=(25, 10))

        CTkLabel(lessons_header, text="📚 Lessons",
                 font=ctk.CTkFont(family=DEFAULT_FONT, size=15, weight="bold"),
                 text_color="white").pack(pady=12)

        lessons_frame = CTkScrollableFrame(sidebar, corner_radius=12,
                                           fg_color=colors['bg_dark'])
        lessons_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Render lessons with better visual hierarchy
        all_lessons = ContentEngine.get_all_lessons()
        for lesson in all_lessons:
            completed = lesson.id in self.user.completed_lessons
            prerequisites_satisfied = all(pr in self.user.completed_lessons
                                          for pr in lesson.prerequisites)
            locked = not prerequisites_satisfied and not completed

            if completed:
                btn = CTkButton(lessons_frame, text=f"✓ {lesson.title}",
                                corner_radius=10, fg_color=colors['success'],
                                hover_color=colors['success_hover'],
                                text_color="white",
                                anchor='w', height=40,
                                font=ctk.CTkFont(family=DEFAULT_FONT, size=12, weight="bold"),
                                command=lambda l=lesson: self._start_lesson(l))
                btn.pack(fill='x', pady=4, padx=4)
            elif locked:
                lock_frame = CTkFrame(lessons_frame, corner_radius=10,
                                      fg_color=colors['bg_medium'])
                lock_frame.pack(fill='x', pady=4, padx=4)

                CTkLabel(lock_frame, text=f"🔒 {lesson.title}",
                         anchor='w', text_color=colors['text_secondary'],
                         font=ctk.CTkFont(family=DEFAULT_FONT, size=12)).pack(side='left', padx=12, pady=10)
            else:
                btn = CTkButton(lessons_frame, text=f"▶ {lesson.title}",
                                corner_radius=10, fg_color=colors['primary'],
                                hover_color=colors['primary_hover'],
                                text_color="white",
                                anchor='w', height=40,
                                font=ctk.CTkFont(family=DEFAULT_FONT, size=12),
                                command=lambda l=lesson: self._start_lesson(l))
                btn.pack(fill='x', pady=4, padx=4)

        # Right content area
        self.content_area = CTkFrame(main_container, corner_radius=20,
                                     fg_color="transparent")
        self.content_area.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Header
        self.header_frame = CTkFrame(self.content_area, corner_radius=15,
                                     fg_color=colors['bg_dark'])
        self.header_frame.pack(fill='x', pady=(0, 10))

        header_inner = CTkFrame(self.header_frame, fg_color="transparent")
        header_inner.pack(fill='x', padx=20, pady=14)

        self.header_title = CTkLabel(header_inner, text="Dashboard",
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.header_title.pack(side='left')

        # Content body
        self.content_body = CTkFrame(self.content_area, corner_radius=15,
                                     fg_color="transparent")
        self.content_body.pack(fill='both', expand=True)

        # Show dashboard initially
        self._show_dashboard()

    def _set_content_title(self, title: str):
        """Update header title"""
        self.header_title.configure(text=title)

    def _clear_content(self):
        """Clear content body"""
        for widget in self.content_body.winfo_children():
            widget.destroy()

    def _refresh_current_view(self):
        """Refresh the current view to reflect updated data"""
        self._show_dashboard()

    def _show_dashboard(self):
        self._clear_content()
        self._set_content_title("Dashboard")
        dashboard = DashboardView(self.content_body, self.user,
                                  self._start_lesson, self._show_daily_challenge)
        dashboard.pack(fill='both', expand=True)

    def _show_daily_challenge(self):
        self._clear_content()
        self._set_content_title("Daily Challenge")
        challenge = DailyChallengeView(self.content_body, self.user,
                                       on_complete=self._on_daily_challenge_complete,
                                       on_back=self._show_dashboard)
        challenge.pack(fill='both', expand=True)

    def _on_daily_challenge_complete(self):
        self.storage.save_user(self.user)
        self._show_dashboard()

    def _start_lesson(self, lesson: Lesson):
        self._clear_content()
        self._set_content_title(lesson.title)
        lesson_view = LessonView(self.content_body, self.user, lesson,
                                 on_complete=lambda l=lesson: self._on_lesson_complete(l),
                                 on_back=self._show_dashboard)
        lesson_view.pack(fill='both', expand=True)

    def _on_lesson_complete(self, lesson: Lesson):
        self.user.completed_lessons.add(lesson.id)
        self.storage.save_user(self.user)

        # Check achievements
        new_achievements = GamificationSystem.check_achievements(self.user)
        if new_achievements:
            messagebox.showinfo("Achievements Unlocked!",
                                f"🏆 {', '.join(new_achievements)}")
            self.storage.save_user(self.user)

        # FIXED: Refresh the entire UI to update sidebar lesson list
        self._create_ui()

        # Show next available lesson or dashboard
        available = ContentEngine.get_available_lessons(self.user.completed_lessons)
        if available:
            if messagebox.askyesno("Lesson Complete!",
                                   "Great job! Continue to next lesson?"):
                self._start_lesson(available[0])
            else:
                self._show_dashboard()
        else:
            messagebox.showinfo("Amazing!", "You've completed all available lessons!")
            self._show_dashboard()

    def _show_statistics(self):
        self._clear_content()
        self._set_content_title("Statistics")
        stats = StatisticsView(self.content_body, self.user)
        stats.pack(fill='both', expand=True)

    def _show_settings(self):
        self._clear_content()
        self._set_content_title("Settings")
        settings = SettingsView(self.content_body, self.user,
                                on_theme_change=self._change_theme,
                                on_font_save=self._save_font,
                                on_goal_save=self._save_goal,
                                on_switch_companion=self._show_companion_switcher,
                                on_export=self._export_data,
                                on_import=self._import_data,
                                on_reset=self._reset_progress,
                                on_check_updates=self._check_for_updates)
        settings.pack(fill='both', expand=True)

    # FIXED: Implement update check
    def _check_for_updates(self):
        """Check for app updates"""
        try:
            has_update, latest_version, download_url = check_for_updates()
            if has_update:
                if messagebox.askyesno("Update Available",
                                      f"Version {latest_version} is available!\n\nWould you like to download it?"):
                    webbrowser.open(download_url)
            else:
                messagebox.showinfo("Up to Date", f"You're running the latest version ({CURRENT_VERSION})!")
        except Exception as e:
            messagebox.showinfo("Update Check", "Unable to check for updates at this time.")

    def _change_theme(self):
        """Theme switching (dark mode only for now)"""
        messagebox.showinfo("Theme", "Dark mode is the only theme available in this version.")

    def _save_font(self, new_size):
        try:
            self.user.font_size = int(new_size)
            self.storage.save_user(self.user)
            messagebox.showinfo("Saved", "Font size updated! Restart the app to see changes.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")

    def _save_goal(self, new_goal):
        try:
            self.user.daily_goal_xp = int(new_goal)
            self.storage.save_user(self.user)
            messagebox.showinfo("Saved", "Daily goal updated!")
            self._show_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")

    def _show_companion_switcher(self):
        """Show dialog to switch companion type"""
        colors = get_colors()

        # FIXED: Use CTkToplevel (now properly imported)
        dialog = CTkToplevel(self.root)
        dialog.title("Switch Companion")
        dialog.geometry("500x600")
        dialog.grab_set()

        CTkLabel(dialog, text="Choose New Companion",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        CTkLabel(dialog, text="⚠️ This will reset your companion's stage to 0!",
                 font=ctk.CTkFont(size=12),
                 text_color=colors['warning']).pack(pady=10)

        selected = ctk.StringVar(value=self.user.companion_type)

        for comp_type in CompanionType:
            if comp_type.value == self.user.companion_type:
                continue  # Skip current companion

            companion = Companion(comp_type, 0, 100)
            radio_frame = CTkFrame(dialog, corner_radius=10, fg_color=colors['bg_dark'])
            radio_frame.pack(fill='x', padx=20, pady=5)

            radio = CTkRadioButton(radio_frame, text="",
                                   variable=selected, value=comp_type.value)
            radio.pack(side='left', padx=10, pady=10)

            info = CTkFrame(radio_frame, fg_color="transparent")
            info.pack(side='left', fill='x', expand=True, pady=10)

            CTkLabel(info, text=comp_type.value.title(),
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor='w')
            CTkLabel(info, text=companion.get_description(),
                     font=ctk.CTkFont(size=10),
                     text_color=colors['text_secondary'],
                     wraplength=300).pack(anchor='w')

        def confirm_switch():
            new_type = selected.get()
            if new_type != self.user.companion_type:
                self.user.companion_type = new_type
                self.user.companion_stage = 0
                self.user.companion_vitality = 100
                self.storage.save_user(self.user)
                messagebox.showinfo("Success", f"Switched to {new_type.title()} companion!")
                dialog.destroy()
                self._create_ui()  # Refresh UI
            else:
                dialog.destroy()

        CTkButton(dialog, text="Confirm Switch", corner_radius=10, height=40,
                  fg_color=colors['warning'], command=confirm_switch).pack(pady=20)

    def _export_data(self):
        """Export user progress to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"codecompanion_backup_{self.user.username}.json"
        )

        if file_path:
            if self.storage.export_user_data(file_path, self.user):
                messagebox.showinfo("Success", "Progress exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export progress.")

    def _import_data(self):
        """Import user progress from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            if messagebox.askyesno("Confirm Import",
                                   "This will overwrite your current progress. Continue?"):
                imported_user = self.storage.import_user_data(file_path)
                if imported_user:
                    self.user = imported_user
                    self.storage.save_user(self.user)
                    messagebox.showinfo("Success", "Progress imported successfully!")
                    self._create_ui()  # Refresh UI
                else:
                    messagebox.showerror("Error", "Failed to import progress.")

    def _reset_progress(self):
        """Reset all user progress"""
        if messagebox.askyesno("Confirm Reset",
                               "Are you sure? This will delete ALL your progress permanently!"):
            if messagebox.askyesno("Final Confirmation",
                                   "This action cannot be undone. Continue?"):
                try:
                    os.remove(self.storage.user_file)
                    messagebox.showinfo("Reset Complete", "Progress has been reset.")
                    self.root.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to reset: {e}")

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    app = CodeCompanionApp()
    app.run()


if __name__ == "__main__":
    main()
