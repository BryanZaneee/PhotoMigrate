# PhotoMigrate

macOS Photos library backup and organization tool.

## Overview

PhotoMigrate creates organized backups of your iCloud Photos library to external drives. It reads photo metadata directly from the Photos database to organize files by actual capture date.

## Problem Statement

- iCloud storage is expensive ($0.99-$9.99/month)
- Large photo libraries (100GB+) are difficult to backup
- Photos are hard to browse outside macOS Photos app
- File modification dates don't reflect when photos were taken

## Solution

PhotoMigrate creates two backup types:
1. Complete Photos library backup (for Mac recovery)
2. Organized year/month folder structure (for cross-platform browsing)

## Languages & Technologies

- **Python 3.6+**: Core logic, database queries, file operations
- **SQL**: SQLite queries for Photos database
- **Shell**: System integration, background processes
- **Tkinter**: GUI interface (built-in with Python)

## Architecture

### Core Components

**icloud_photos_migrator.py**
GUI application for end users. Features: library detection, drive selection, progress tracking, background process management.

**export_photos_database.py**
Command-line tool for photo organization. Queries Photos SQLite database for accurate metadata.

### How It Works

1. **Database Query**: Reads `Photos.sqlite` database
2. **Metadata Extraction**: Queries `ZASSET` table for `ZDATECREATED` (photo capture date)
3. **Timestamp Conversion**: Converts Apple Core Data timestamps (seconds since 2001-01-01)
4. **File Organization**: Creates `YYYY/MM-MonthName/` structure
5. **File Copy**: Uses `shutil.copy2()` to preserve timestamps

### Why Database Method

Three approaches were evaluated:

| Method | Accuracy | Speed | Reliability |
|--------|----------|-------|-------------|
| File modification time | Low | Fast | Works |
| EXIF from files | High | Slow | Fails on ExFAT |
| Database query | High | Medium | Always works |

Database method chosen for accuracy and reliability across file systems.

## Prerequisites

- macOS 10.13+
- Python 3.6+
- Photos app with iCloud Photos enabled
- External drive (ExFAT, APFS, or HFS+)
- **IMPORTANT**: iCloud Photos must have "Download Originals to this Mac" enabled

## Installation

```bash
git clone https://github.com/yourusername/PhotoMigrate.git
cd PhotoMigrate
pip3 install -r requirements.txt
```

## Usage

### GUI Application

```bash
python3 src/icloud_photos_migrator.py
```

### Command Line

```bash
python3 src/export_photos_database.py
```

### Build Mac .app

```bash
python3 setup.py py2app
# App will be in dist/iCloud Photos Migrator.app
```

## Configuration

Edit script constants for custom settings:

```python
library_path = "/Users/yourname/Pictures/Photos Library.photoslibrary"
export_folder_name = "PHOTOS 16-26"
destination = "/Volumes/YourDrive"
```

## Output Structure

```
/Volumes/ExternalDrive/
├── Photos Library.photoslibrary/    # Complete backup
└── PHOTOS 16-26/                     # Organized export
    ├── 2016/
    │   ├── 01-January/
    │   ├── 02-February/
    │   └── ...
    ├── 2017/
    └── ...
```

## Technical Details

### Photos Database Schema

Relevant tables and columns:
- `ZASSET`: Main asset table
  - `ZDATECREATED`: Photo capture timestamp (Apple Core Data format)
  - `ZFILENAME`: Original filename
  - `ZDIRECTORY`: Path within originals folder

### Timestamp Conversion

```python
APPLE_EPOCH = datetime(2001, 1, 1)
photo_date = APPLE_EPOCH + timedelta(seconds=apple_timestamp)
```

Apple stores dates as seconds since 2001-01-01 (not Unix epoch 1970-01-01).

### File System Compatibility

Tested on:
- APFS (Mac internal drives)
- HFS+ (Mac formatted external drives)
- ExFAT (Windows/Mac compatible drives)

EXIF metadata not reliable on ExFAT, hence database approach.

## Limitations

- macOS only (Photos app dependency)
- Requires manual iCloud download step
- Does not preserve Photos app albums/faces/memories
- Videos may not include all metadata fields

## Performance

- Database query: <1 second
- File copy: ~200 photos/minute (depends on drive speed)
- 10,000 photos: ~50 minutes

Optimization possible via parallel processing (4x speedup).

## Development

### Running Tests

```bash
cd tests
python3 test_database.py
python3 test_export.py
```

### Project Structure

```
PhotoMigrate/
├── src/
│   ├── icloud_photos_migrator.py
│   └── export_photos_database.py
├── tests/
├── docs/
├── setup.py
├── requirements.txt
├── LICENSE
└── README.md
```

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

MIT License - see LICENSE file

## Troubleshooting

**"No Photos library found"**
Check path: `/Users/YourName/Pictures/Photos Library.photoslibrary`

**"Database not found"**
Ensure library backup completed successfully.

**Photos show wrong dates**
Check if files have proper creation dates in database. Some imports may not preserve metadata.

**Slow performance**
External drive speed is limiting factor. USB 3.0+ recommended.

## Support

File issues at: https://github.com/yourusername/PhotoMigrate/issues

## Credits

Developed to solve iCloud storage costs and cross-platform photo access.
