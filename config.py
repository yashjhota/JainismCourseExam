import os

# Config options for the Quiz App
ADMIN_PASSWORD = "YASHJHOTA"
TIME_LIMIT_MINUTES = 100

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "quiz_database.db")
ENGLISH_QUESTIONS_PATH = os.path.join(BASE_DIR, "english_questions.json")
HINDI_QUESTIONS_PATH = os.path.join(BASE_DIR, "hindi_questions.json")
