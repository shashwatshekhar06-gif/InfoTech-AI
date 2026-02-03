import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import os

DB_PATH = "infofetch_ai.db"

def init_db():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Search history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            result_json TEXT NOT NULL,
            confidence TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_demo_accounts():
    """Create demo accounts for testing"""
    accounts = [
        ("admin", "secure123", "admin@infofetch.ai"),
        ("user1", "pass123", "user1@infofetch.ai"),
        ("test", "demo456", "test@infofetch.ai"),
        ("demo1", "password123", "demo1@infofetch.ai"),
        ("demo2", "password123", "demo2@infofetch.ai")
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for username, password, email in accounts:
        try:
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
        except Exception as e:
            print(f"Error creating account {username}: {e}")
    
    conn.commit()
    conn.close()

def verify_user(username: str, password: str) -> Optional[int]:
    """Verify user credentials and return user_id if valid"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
        (username, password_hash)
    )
    
    result = cursor.fetchone()
    if result:
        user_id = result[0]
        # Update last login
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return user_id
    
    conn.close()
    return None

def save_search_history(user_id: int, query: str, result: Dict) -> bool:
    """Save search history to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        result_json = json.dumps(result, ensure_ascii=False, default=str)
        confidence = result.get('confidence', 'medium')
        
        cursor.execute(
            "INSERT INTO search_history (user_id, query, result_json, confidence) VALUES (?, ?, ?, ?)",
            (user_id, query, result_json, confidence)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving search: {e}")
        conn.close()
        return False

def get_user_history(user_id: int, limit: int = 50) -> List[Dict]:
    """Get user's search history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, query, result_json, confidence, timestamp FROM search_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )
    
    results = []
    for row in cursor.fetchall():
        try:
            result = json.loads(row[2])
        except:
            result = {"error": "Failed to parse result"}
        
        results.append({
            'id': row[0],
            'query': row[1],
            'result': result,
            'confidence': row[3] or 'medium',
            'timestamp': row[4]
        })
    
    conn.close()
    return results

def save_chat_message(user_id: int, role: str, content: str) -> bool:
    """Save chat message to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving chat message: {e}")
        conn.close()
        return False

def get_chat_history(user_id: int, limit: int = 100) -> List[Dict]:
    """Get user's chat history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT role, content, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC LIMIT ?",
        (user_id, limit)
    )
    
    history = []
    for row in cursor.fetchall():
        history.append({
            'role': row[0],
            'content': row[1],
            'timestamp': row[2]
        })
    
    conn.close()
    return history

def get_user_stats(user_id: int) -> Dict:
    """Get user statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total searches
    cursor.execute("SELECT COUNT(*) FROM search_history WHERE user_id = ?", (user_id,))
    total_searches = cursor.fetchone()[0]
    
    # Total chat messages
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE user_id = ?", (user_id,))
    total_chats = cursor.fetchone()[0]
    
    # Average confidence
    cursor.execute("""
        SELECT AVG(CASE 
            WHEN confidence = 'high' THEN 3 
            WHEN confidence = 'medium' THEN 2 
            WHEN confidence = 'low' THEN 1 
            ELSE 2
        END) FROM search_history WHERE user_id = ?
    """, (user_id,))
    
    avg_conf = cursor.fetchone()[0] or 2.0
    avg_confidence = "High" if avg_conf >= 2.5 else "Medium" if avg_conf >= 1.5 else "Low"
    
    conn.close()
    
    return {
        'total_searches': total_searches,
        'total_chats': total_chats,
        'avg_confidence': avg_confidence
    }

def clear_user_history(user_id: int) -> bool:
    """Clear all user history (searches and chats)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing history: {e}")
        conn.close()
        return False

def delete_search_item(search_id: int) -> bool:
    """Delete a specific search item"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM search_history WHERE id = ?", (search_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting search: {e}")
        conn.close()
        return False

def clear_chat_history(user_id: int) -> bool:
    """Clear only chat history for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        conn.close()
        return False

# Auto-initialize database on import
init_db()
create_demo_accounts()