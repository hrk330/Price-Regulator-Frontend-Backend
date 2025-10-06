#!/usr/bin/env python3
"""
Test script to verify Neon database connection
"""

import psycopg2
import sys

# Your Neon database connection details
DB_CONFIG = {
    'host': 'ep-divine-art-adw2ivpe-pooler.c-2.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_iZGzN6wpy8td',
    'port': 5432,
    'sslmode': 'require',
    'channel_binding': 'require'
}

def test_connection():
    """Test the Neon database connection"""
    try:
        print("🔍 Testing Neon database connection...")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"User: {DB_CONFIG['user']}")
        print(f"Port: {DB_CONFIG['port']}")
        print()
        
        # Attempt to connect
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL version: {version[0]}")
        
        # Test database info
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"📊 Current database: {db_info[0]}")
        print(f"📊 Current user: {db_info[1]}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("✅ All tests passed! Your Neon database is ready to use.")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
