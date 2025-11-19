#!/usr/bin/env python3
"""
Test database connectivity and queries
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Apple Core Data epoch
APPLE_EPOCH = datetime(2001, 1, 1)

def test_database_connection(library_path):
    """Test if we can connect to Photos database"""
    db_path = Path(library_path) / "database" / "Photos.sqlite"

    print(f"Testing database: {db_path}")

    if not db_path.exists():
        print(f"FAIL: Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        print("PASS: Database connection successful")
        return conn
    except Exception as e:
        print(f"FAIL: Could not connect to database: {e}")
        return False

def test_asset_table(conn):
    """Test ZASSET table structure"""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ZASSET'")
        result = cursor.fetchone()

        if result:
            print("PASS: ZASSET table exists")
        else:
            print("FAIL: ZASSET table not found")
            return False

        # Check for required columns
        cursor.execute("PRAGMA table_info(ZASSET)")
        columns = {row[1] for row in cursor.fetchall()}

        required = {'ZDATECREATED', 'ZFILENAME', 'ZDIRECTORY'}
        if required.issubset(columns):
            print(f"PASS: All required columns present: {required}")
            return True
        else:
            missing = required - columns
            print(f"FAIL: Missing columns: {missing}")
            return False

    except Exception as e:
        print(f"FAIL: Error querying table: {e}")
        return False

def test_photo_count(conn):
    """Test photo count in database"""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM ZASSET WHERE ZFILENAME IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"PASS: Found {count} photos in database")
        return count
    except Exception as e:
        print(f"FAIL: Could not count photos: {e}")
        return 0

def test_sample_photos(conn, limit=5):
    """Test querying sample photos"""
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT ZDATECREATED, ZFILENAME, ZDIRECTORY
            FROM ZASSET
            WHERE ZFILENAME IS NOT NULL
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        print(f"\nSample of {len(results)} photos:")
        print("-" * 80)

        for apple_timestamp, filename, directory in results:
            if apple_timestamp:
                photo_date = APPLE_EPOCH + timedelta(seconds=apple_timestamp)
                date_str = photo_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = "No date"

            print(f"  {date_str} | {filename} | {directory}")

        print("PASS: Successfully queried sample photos")
        return True

    except Exception as e:
        print(f"FAIL: Could not query photos: {e}")
        return False

def run_tests(library_path):
    """Run all database tests"""
    print("=" * 80)
    print("PhotoMigrate Database Tests")
    print("=" * 80)
    print()

    conn = test_database_connection(library_path)
    if not conn:
        return False

    print()
    if not test_asset_table(conn):
        return False

    print()
    count = test_photo_count(conn)
    if count == 0:
        return False

    print()
    test_sample_photos(conn)

    conn.close()

    print()
    print("=" * 80)
    print("All tests passed!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    # Default to T7 backup
    library_path = "/Volumes/T7/Photos Library.photoslibrary"

    if len(sys.argv) > 1:
        library_path = sys.argv[1]

    success = run_tests(library_path)
    sys.exit(0 if success else 1)
