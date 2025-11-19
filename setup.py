"""
Setup script for creating iCloud Photos Migrator Mac app
Usage: python setup.py py2app
"""

from setuptools import setup

APP = ['icloud_photos_migrator.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app_icon.icns',  # Optional: add your own icon
    'plist': {
        'CFBundleName': 'iCloud Photos Migrator',
        'CFBundleDisplayName': 'iCloud Photos Migrator',
        'CFBundleIdentifier': 'com.icloudphotos.migrator',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'MIT License',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
    },
    'packages': ['tkinter'],
    'includes': ['subprocess', 'shutil', 'pathlib', 'datetime', 'threading', 'json'],
}

setup(
    name='iCloud Photos Migrator',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
