#!/usr/bin/env python3
"""
Test photo export functionality
"""

import sys
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from export_photos_database import convert_apple_timestamp
from datetime import datetime

def test_apple_timestamp_conversion():
    """Test Apple Core Data timestamp conversion"""
    print("=" * 80)
    print("Apple Timestamp Conversion Tests")
    print("=" * 80)
    print()

    # Test case 1: Known date (Jan 1, 2020 = 599529600 seconds since 2001-01-01)
    timestamp_2020 = 599529600
    result = convert_apple_timestamp(timestamp_2020)
    expected = datetime(2020, 1, 1)

    if result and result.date() == expected.date():
        print(f"PASS: 2020-01-01 conversion")
        print(f"  Input: {timestamp_2020}")
        print(f"  Output: {result}")
    else:
        print(f"FAIL: Expected {expected}, got {result}")
        return False

    print()

    # Test case 2: None handling
    result = convert_apple_timestamp(None)
    if result is None:
        print("PASS: None timestamp handled correctly")
    else:
        print(f"FAIL: None should return None, got {result}")
        return False

    print()

    # Test case 3: Zero handling
    result = convert_apple_timestamp(0)
    if result is None:
        print("PASS: Zero timestamp handled correctly")
    else:
        print(f"FAIL: Zero should return None, got {result}")
        return False

    print()

    # Test case 4: Recent date (2024)
    timestamp_2024 = 725846400  # Approximate 2024-01-01
    result = convert_apple_timestamp(timestamp_2024)

    if result and result.year == 2024:
        print(f"PASS: 2024 conversion")
        print(f"  Input: {timestamp_2024}")
        print(f"  Output: {result}")
    else:
        print(f"FAIL: Expected year 2024, got {result}")
        return False

    print()
    print("=" * 80)
    print("All timestamp conversion tests passed!")
    print("=" * 80)
    return True

def test_export_dry_run():
    """Test export process with dry run (no actual copying)"""
    print()
    print("=" * 80)
    print("Export Dry Run Test")
    print("=" * 80)
    print()

    library_path = "/Volumes/T7/Photos Library.photoslibrary"

    if not Path(library_path).exists():
        print(f"SKIP: Test library not found at {library_path}")
        print("This test requires the Photos library to be present on T7")
        return True

    db_path = Path(library_path) / "database" / "Photos.sqlite"
    if not db_path.exists():
        print(f"SKIP: Database not found at {db_path}")
        return True

    import sqlite3

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Query first 10 photos
        cursor.execute("""
            SELECT ZDATECREATED, ZFILENAME, ZDIRECTORY
            FROM ZASSET
            WHERE ZFILENAME IS NOT NULL
            LIMIT 10
        """)

        results = cursor.fetchall()
        conn.close()

        print(f"PASS: Successfully queried {len(results)} sample photos")
        print()
        print("Sample photo dates:")
        print("-" * 80)

        for apple_timestamp, filename, directory in results:
            photo_date = convert_apple_timestamp(apple_timestamp)
            if photo_date:
                date_str = photo_date.strftime("%Y-%m-%d")
                year = photo_date.strftime("%Y")
                month = photo_date.strftime("%m-%B")
                print(f"  {date_str} | {year}/{month} | {filename}")

        print()
        print("=" * 80)
        print("Dry run test passed!")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"FAIL: Error during dry run: {e}")
        return False

if __name__ == "__main__":
    success = True

    if not test_apple_timestamp_conversion():
        success = False

    if not test_export_dry_run():
        success = False

    sys.exit(0 if success else 1)
