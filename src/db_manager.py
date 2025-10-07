import sqlite3
from datetime import datetime
import logging

# --- CONFIGURATION ---
DB_FILE = "ida_app.db"
logging.basicConfig(level=logging.INFO)

# --- DATABASE INITIALIZATION ---
def init_db():
    """
    Initializes the database with users, projects, and storyboards tables.
    Establishes foreign key relationships for data integrity.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            # Enable foreign key support in SQLite
            c.execute("PRAGMA foreign_keys = ON;")

            # 1. Users table: The top-level entity.
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    google_id TEXT,
                    created_at TEXT NOT NULL
                )
            ''')

            # 2. Projects table: Each project must belong to a user.
            c.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    project_title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # 3. Storyboards table: Each storyboard must belong to a project.
            c.execute('''
                CREATE TABLE IF NOT EXISTS storyboards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    storyboard_title TEXT NOT NULL,
                    file_path TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            logging.info("Database with users, projects, and storyboards initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
        raise

# --- USER MANAGEMENT ---
def register_user_if_new(email, name, google_id=None):
    """Registers a new user if they don't exist and returns their database ID."""
    created_at = datetime.now().isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (email, name, google_id, created_at) VALUES (?, ?, ?, ?)",
                      (email, name, google_id or "", created_at))
            c.execute("SELECT id FROM users WHERE email = ?", (email,))
            user_id = c.fetchone()[0]
            conn.commit()
            return user_id
    except sqlite3.Error as e:
        logging.error(f"Failed to register or find user '{email}': {e}")
        return None

# --- PROJECT MANAGEMENT ---
def save_project(user_id, project_title):
    """Saves a new project for a user and returns the new project's ID."""
    created_at = datetime.now().isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO projects (user_id, project_title, created_at) VALUES (?, ?, ?)",
                      (user_id, project_title, created_at))
            conn.commit()
            logging.info(f"Saved project '{project_title}' for user ID {user_id}.")
            return c.lastrowid # Return the ID of the newly created project
    except sqlite3.Error as e:
        logging.error(f"Failed to save project for user ID {user_id}: {e}")
        return None

def get_user_projects(user_id):
    """Retrieves all projects for a specific user."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT id, project_title, created_at FROM projects WHERE user_id = ? ORDER BY created_at DESC",
                      (user_id,))
            return c.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Failed to get projects for user ID {user_id}: {e}")
        return []

# --- STORYBOARD MANAGEMENT ---
def save_storyboard(project_id, storyboard_title, file_path):
    """Saves a new storyboard for a specific project."""
    created_at = datetime.now().isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO storyboards (project_id, storyboard_title, file_path, created_at) VALUES (?, ?, ?, ?)",
                      (project_id, storyboard_title, file_path, created_at))
            conn.commit()
            logging.info(f"Saved storyboard '{storyboard_title}' for project ID {project_id}.")
    except sqlite3.Error as e:
        logging.error(f"Failed to save storyboard for project ID {project_id}: {e}")

def get_project_storyboards(project_id):
    """Retrieves all storyboards for a specific project."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT id, storyboard_title, file_path, created_at FROM storyboards WHERE project_id = ? ORDER BY created_at DESC",
                      (project_id,))
            return c.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Failed to get storyboards for project ID {project_id}: {e}")
        return []

def get_user_storyboards(user_email):
    """Retrieves all storyboards for a specific user based on their email."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT s.id, s.storyboard_title, s.file_path, s.created_at
                FROM storyboards s
                JOIN projects p ON s.project_id = p.id
                JOIN users u ON p.user_id = u.id
                WHERE u.email = ?
                ORDER BY s.created_at DESC
            ''', (user_email,))
            return c.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Failed to get storyboards for user '{user_email}': {e}")
        return []