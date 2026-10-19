import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Resolve local database file path in the project root folder
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "aura.db"))

def get_db_connection():
    """Establish and return a direct connection to the SQLite database."""
    # SQLite automatically creates the file if it does not exist
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the SQLite database and create the 4 required tables if they are missing."""
    try:
        # SQLite creates the database file automatically on connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Create calendar_events table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                event_time VARCHAR(100) NOT NULL,
                action VARCHAR(50) DEFAULT 'add',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create execution_logs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command_text TEXT NOT NULL,
                tool_name VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                result TEXT
            )
        """)

        # Create security_logs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command_text TEXT NOT NULL,
                violation_type VARCHAR(100) NOT NULL,
                target_resource TEXT NOT NULL
            )
        """)

        # Create system_configs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_configs (
                config_key VARCHAR(100) PRIMARY KEY,
                config_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Verify system configs seeding
        cur.execute("SELECT COUNT(*) FROM system_configs")
        count = cur.fetchone()[0]
        if count == 0:
            # Seed default values (sandbox_dir will point to local workspace)
            default_workspace = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workspace"))
            cur.executemany("""
                INSERT INTO system_configs (config_key, config_value) VALUES (?, ?)
            """, [
                ('llm_provider', 'GROQ'),
                ('sandbox_dir', default_workspace),
                ('safe_mode', 'True')
            ])
            conn.commit()
            print("[DB] Seeded default configs table in SQLite.")

        cur.close()
        conn.close()
        print(f"[DB] SQLite schemas and tables checked/initialized at: {DB_PATH}")
    except Exception as e:
        print(f"[DB ERROR] Table initialization failed: {e}")

# ════════════════════════════════════════════
# HELPER OPERATIONS
# ════════════════════════════════════════════

def to_iso(val):
    """Formats timestamp string/object to ISO-like format string."""
    if not val:
        return ""
    if isinstance(val, str):
        # SQLite default timestamp format: YYYY-MM-DD HH:MM:SS
        return val.replace(" ", "T")
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)

def log_execution(command_text, tool_name, status, result):
    """Log helper to write execution traces to execution_logs."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO execution_logs (command_text, tool_name, status, result)
            VALUES (?, ?, ?, ?)
        """, (command_text, tool_name, status, result))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Execution logging failed: {e}")

def log_security_violation(command_text, violation_type, target_resource):
    """Log helper to write security boundary escape attempts to security_logs."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO security_logs (command_text, violation_type, target_resource)
            VALUES (?, ?, ?)
        """, (command_text, violation_type, target_resource))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Security logging failed: {e}")

def add_calendar_event(title, event_time, action='add'):
    """Inserts scheduled calendar details."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO calendar_events (title, event_time, action)
            VALUES (?, ?, ?)
        """, (title, event_time, action))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Calendar logging failed: {e}")
        return False

def get_calendar_events():
    """Queries all calendar events."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, event_time, action, created_at FROM calendar_events ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "title": r[1], "event_time": r[2], "action": r[3], "created_at": to_iso(r[4])} for r in rows]
    except Exception as e:
        print(f"[DB ERROR] Get calendar events failed: {e}")
        return []

def get_execution_logs():
    """Queries execution logs."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, timestamp, command_text, tool_name, status, result FROM execution_logs ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "timestamp": to_iso(r[1]), "command_text": r[2], "tool_name": r[3], "status": r[4], "result": r[5]} for r in rows]
    except Exception as e:
        print(f"[DB ERROR] Get execution logs failed: {e}")
        return []

def get_security_logs():
    """Queries security logs."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, timestamp, command_text, violation_type, target_resource FROM security_logs ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{"id": r[0], "timestamp": to_iso(r[1]), "command_text": r[2], "violation_type": r[3], "target_resource": r[4]} for r in rows]
    except Exception as e:
        print(f"[DB ERROR] Get security logs failed: {e}")
        return []

def get_system_configs():
    """Queries system configs."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT config_key, config_value, updated_at FROM system_configs ORDER BY config_key ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {r[0]: {"value": r[1], "updated_at": to_iso(r[2])} for r in rows}
    except Exception as e:
        print(f"[DB ERROR] Get system configs failed: {e}")
        return {}

def update_system_config(key, value):
    """Updates config key and value."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO system_configs (config_key, config_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (config_key) DO UPDATE
            SET config_value = excluded.config_value, updated_at = CURRENT_TIMESTAMP
        """, (key, value))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Config update failed: {e}")
        return False
