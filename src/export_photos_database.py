#!/usr/bin/env python3
"""
Export photos from Photos library to organized year/month structure
Uses Photos database for accurate photo capture dates
"""

import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Apple Core Data timestamp is seconds since 2001-01-01 00:00:00
APPLE_EPOCH = datetime(2001, 1, 1)

def convert_apple_timestamp(apple_timestamp):
    """Convert Apple Core Data timestamp to Python datetime"""
    if apple_timestamp is None or apple_timestamp == 0:
        return None
    try:
        return APPLE_EPOCH + timedelta(seconds=apple_timestamp)
    except:
        return None

def export_photos_from_database(library_path, export_folder_name, destination):
    """Export photos using dates from Photos database"""

    print(f"Starting database-based photo export...")
    print(f"Library: {library_path}")
    print(f"Destination: {destination}/{export_folder_name}")
    print(f"")
    print(f"Reading actual photo capture dates from Photos database...")
    print(f"")

    # Create export folder
    export_path = Path(destination) / export_folder_name
    export_path.mkdir(exist_ok=True)
    print(f"✓ Created export folder: {export_path}")

    # Connect to Photos database
    db_path = Path(library_path) / "database" / "Photos.sqlite"
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return

    print(f"✓ Connected to Photos database")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Query all photos with their capture dates
    query = """
        SELECT ZDATECREATED, ZFILENAME, ZDIRECTORY
        FROM ZASSET
        WHERE ZFILENAME IS NOT NULL
        ORDER BY ZDATECREATED
    """

    print(f"✓ Querying photo metadata...")
    cursor.execute(query)
    results = cursor.fetchall()
    print(f"✓ Found {len(results)} photos in database")
    print()

    copied = 0
    skipped = 0
    errors = 0
    no_date = 0
    total_size = 0

    originals_path = Path(library_path) / "originals"

    print("Copying and organizing photos...")
    print("-" * 60)

    for apple_timestamp, filename, directory in results:
        try:
            # Convert Apple timestamp to datetime
            photo_date = convert_apple_timestamp(apple_timestamp)

            if photo_date:
                year = photo_date.strftime("%Y")
                month = photo_date.strftime("%m-%B")

                # Find the source file
                if directory:
                    source_file = originals_path / directory / filename
                else:
                    # Try to find file in originals
                    matches = list(originals_path.rglob(filename))
                    source_file = matches[0] if matches else None

                if source_file and source_file.exists():
                    # Create year/month folder
                    dest_folder = export_path / year / month
                    dest_folder.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    dest_file = dest_folder / filename

                    if not dest_file.exists():
                        shutil.copy2(source_file, dest_file)
                        file_size = source_file.stat().st_size
                        total_size += file_size
                        copied += 1

                        # Progress update every 100 files
                        if copied % 100 == 0:
                            size_mb = total_size / (1024 * 1024)
                            print(f"  Copied {copied}/{len(results)} files ({size_mb:.1f} MB)...")
                    else:
                        skipped += 1
                else:
                    if filename:
                        errors += 1
                        if errors <= 5:  # Only print first 5 errors
                            print(f"  File not found: {filename}")
            else:
                no_date += 1

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ERROR processing {filename}: {e}")

    conn.close()

    print()
    print("=" * 60)
    print("EXPORT COMPLETE!")
    print("=" * 60)
    print(f"✓ Copied: {copied} files")
    print(f"⊘ Skipped (already exist): {skipped} files")
    print(f"⚠ No date in database: {no_date} files")
    print(f"✗ Errors/Not found: {errors} files")
    print(f"📦 Total size: {total_size / (1024**3):.2f} GB")
    print(f"📁 Location: {export_path}")
    print()
    print(f"✅ Photos are organized by actual capture date from database!")
    print()

if __name__ == "__main__":
    # Configuration
    library_path = "/Volumes/T7/Photos Library.photoslibrary"
    export_folder_name = "PHOTOS 16-26"
    destination = "/Volumes/T7"

    # Check if library exists
    if not Path(library_path).exists():
        print(f"ERROR: Library not found at {library_path}")
        sys.exit(1)

    # Run export
    export_photos_from_database(library_path, export_folder_name, destination)
