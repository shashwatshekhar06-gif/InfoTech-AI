"""
Database Migration Script for InfoFetch AI
Adds the 'plan' column to existing users table
"""

import sqlite3
import os

DB_PATH = "infofetch_ai.db"

def migrate_database():
    """Add missing 'plan' column to users table"""
    
    print("\n" + "="*70)
    print("🔧 DATABASE MIGRATION SCRIPT")
    print("="*70 + "\n")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found: {DB_PATH}")
        print("   The database will be created automatically when you run the app.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if 'plan' column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📊 Current columns in 'users' table: {columns}\n")
        
        if 'plan' in columns:
            print("✅ 'plan' column already exists - no migration needed!")
        else:
            print("🔄 Adding 'plan' column to users table...")
            
            # Add the 'plan' column with default value 'Free'
            cursor.execute("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'Free'")
            
            # Update all existing users to have 'Free' plan
            cursor.execute("UPDATE users SET plan = 'Free' WHERE plan IS NULL")
            
            conn.commit()
            
            print("✅ Successfully added 'plan' column!")
            print("✅ All existing users set to 'Free' plan\n")
            
            # Verify the change
            cursor.execute("PRAGMA table_info(users)")
            new_columns = [column[1] for column in cursor.fetchall()]
            print(f"📊 Updated columns: {new_columns}\n")
        
        # Display user data
        cursor.execute("SELECT id, username, plan FROM users")
        users = cursor.fetchall()
        
        if users:
            print("👥 Current users in database:")
            print("-" * 70)
            for user_id, username, plan in users:
                print(f"   ID: {user_id} | Username: {username} | Plan: {plan}")
            print()
        else:
            print("ℹ️  No users in database yet\n")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("="*70)
    print("✅ MIGRATION COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    migrate_database()