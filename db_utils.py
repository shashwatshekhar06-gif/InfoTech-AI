import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import os

DB_PATH = "infofetch_ai.db"

def init_db():
    """Initialize database with all required tables - IMPROVED VERSION"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\n{'='*70}")
    print("🔧 INITIALIZING DATABASE")
    print(f"{'='*70}\n")
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_exists = cursor.fetchone() is not None
    
    if users_exists:
        print("✓ Users table exists - checking for 'plan' column...")
        
        # Check if 'plan' column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'plan' not in columns:
            print("🔄 Adding 'plan' column (migration)...")
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'Free'")
                cursor.execute("UPDATE users SET plan = 'Free' WHERE plan IS NULL")
                conn.commit()
                print("✅ Migration complete - 'plan' column added!")
            except Exception as e:
                print(f"⚠️ Migration warning: {e}")
        else:
            print("✓ 'plan' column already exists")
    else:
        print("📋 Creating users table from scratch...")
        # Users table with plan column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                plan TEXT DEFAULT 'Free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        print("✅ Users table created!")
    
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
    
    # Payment history table for Razorpay transactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            razorpay_order_id TEXT NOT NULL,
            razorpay_payment_id TEXT,
            razorpay_signature TEXT,
            plan_name TEXT NOT NULL,
            amount INTEGER NOT NULL,
            currency TEXT DEFAULT 'INR',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 🆕 Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            rating INTEGER NOT NULL,
            category TEXT NOT NULL,
            feedback_text TEXT,
            ai_understanding TEXT,
            accuracy_score INTEGER,
            speed_score INTEGER,
            ui_score INTEGER,
            feature_requests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_public BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"{'='*70}")
    print("✅ DATABASE INITIALIZED SUCCESSFULLY")
    print(f"{'='*70}\n")

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_demo_accounts():
    """Create demo accounts for testing - NOW WITH 9 ACCOUNTS TOTAL"""
    accounts = [
        ("admin", "secure123", "admin@infofetch.ai"),
        ("user1", "pass123", "user1@infofetch.ai"),
        ("test", "demo456", "test@infofetch.ai"),
        ("demo1", "password123", "demo1@infofetch.ai"),
        ("demo2", "password123", "demo2@infofetch.ai"),
        # 4 Additional demo accounts as requested
        ("researcher", "research2024", "researcher@infofetch.ai"),
        ("analyst", "analyst2024", "analyst@infofetch.ai"),
        ("manager", "manager2024", "manager@infofetch.ai"),
        ("executive", "exec2024", "executive@infofetch.ai")
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("👥 Creating demo accounts...")
    created_count = 0
    
    for username, password, email in accounts:
        try:
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password_hash, email, plan) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, 'Free')
            )
            if cursor.rowcount > 0:
                created_count += 1
        except Exception as e:
            print(f"   ⚠️ Error creating account {username}: {e}")
    
    conn.commit()
    conn.close()
    
    if created_count > 0:
        print(f"✅ Created {created_count} new demo accounts")
    else:
        print(f"✓ All {len(accounts)} demo accounts already exist")

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

def get_user_plan(user_id: int) -> str:
    """Get user's current plan"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT plan FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 'Free'
    except sqlite3.OperationalError as e:
        # Handle case where 'plan' column doesn't exist
        print(f"⚠️ Database error in get_user_plan: {e}")
        conn.close()
        return 'Free'

def update_user_plan(user_id: int, plan: str) -> bool:
    """Update user's plan after successful payment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET plan = ? WHERE id = ?", (plan, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating plan: {e}")
        conn.close()
        return False

def create_payment_order(user_id: int, plan_name: str, amount: int, order_id: str) -> bool:
    """Create a payment order record"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO payment_history 
            (user_id, razorpay_order_id, plan_name, amount, status) 
            VALUES (?, ?, ?, ?, 'pending')""",
            (user_id, order_id, plan_name, amount)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating payment order: {e}")
        conn.close()
        return False

def complete_payment(order_id: str, payment_id: str, signature: str) -> bool:
    """Mark payment as completed and update user plan"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Update payment record
        cursor.execute(
            """UPDATE payment_history 
            SET razorpay_payment_id = ?, razorpay_signature = ?, 
                status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE razorpay_order_id = ?""",
            (payment_id, signature, order_id)
        )
        
        # Get user_id and plan from payment
        cursor.execute(
            "SELECT user_id, plan_name FROM payment_history WHERE razorpay_order_id = ?",
            (order_id,)
        )
        result = cursor.fetchone()
        
        if result:
            user_id, plan_name = result
            # Update user plan
            cursor.execute("UPDATE users SET plan = ? WHERE id = ?", (plan_name, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error completing payment: {e}")
        conn.close()
        return False

def get_user_payments(user_id: int) -> List[Dict]:
    """Get user's payment history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT plan_name, amount, currency, status, created_at, completed_at 
        FROM payment_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10""",
        (user_id,)
    )
    
    payments = []
    for row in cursor.fetchall():
        payments.append({
            'plan': row[0],
            'amount': row[1],
            'currency': row[2],
            'status': row[3],
            'created': row[4],
            'completed': row[5]
        })
    
    conn.close()
    return payments

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

# ============================================================================
# 🆕 FEEDBACK FUNCTIONS
# ============================================================================

def save_feedback(user_id: int, username: str, rating: int, category: str, 
                  feedback_text: str, ai_understanding: str, accuracy: int, 
                  speed: int, ui: int, feature_requests: str, is_public: bool = True) -> bool:
    """Save user feedback to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO feedback 
            (user_id, username, rating, category, feedback_text, ai_understanding, 
             accuracy_score, speed_score, ui_score, feature_requests, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, rating, category, feedback_text, ai_understanding,
              accuracy, speed, ui, feature_requests, is_public))
        
        conn.commit()
        conn.close()
        print(f"✅ Feedback saved from user {username}")
        return True
    except Exception as e:
        print(f"❌ Error saving feedback: {e}")
        conn.close()
        return False

def get_public_feedback(limit: int = 6) -> List[Dict]:
    """Get public positive feedback for landing page (4+ star reviews)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT username, rating, feedback_text, created_at 
        FROM feedback 
        WHERE is_public = 1 AND rating >= 4
        ORDER BY rating DESC, created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    reviews = []
    for row in cursor.fetchall():
        reviews.append({
            'username': row[0],
            'rating': row[1],
            'text': row[2],
            'date': row[3]
        })
    
    conn.close()
    return reviews

def get_user_feedback_stats(user_id: int) -> Dict:
    """Get feedback statistics for a specific user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total feedback count
    cursor.execute('SELECT COUNT(*) FROM feedback WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()[0]
    
    # Average rating
    cursor.execute('SELECT AVG(rating) FROM feedback WHERE user_id = ?', (user_id,))
    avg_rating = cursor.fetchone()[0] or 0
    
    conn.close()
    return {
        'total_feedback': total,
        'avg_rating': round(avg_rating, 1)
    }

def get_all_feedback_summary() -> Dict:
    """Get platform-wide feedback summary for analytics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total feedback
    cursor.execute('SELECT COUNT(*) FROM feedback')
    total = cursor.fetchone()[0]
    
    # Average rating
    cursor.execute('SELECT AVG(rating) FROM feedback')
    avg_rating = cursor.fetchone()[0] or 0
    
    # Average scores
    cursor.execute('SELECT AVG(accuracy_score), AVG(speed_score), AVG(ui_score) FROM feedback')
    scores = cursor.fetchone()
    
    # Category breakdown
    cursor.execute('''
        SELECT category, COUNT(*) 
        FROM feedback 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
    ''')
    categories = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        'total_feedback': total,
        'avg_rating': round(avg_rating, 1),
        'avg_accuracy': round(scores[0] or 0, 1),
        'avg_speed': round(scores[1] or 0, 1),
        'avg_ui': round(scores[2] or 0, 1),
        'category_breakdown': categories
    }

# Auto-initialize database on import
print("\n🚀 Loading db_utils module...")
init_db()
create_demo_accounts()
print()