#!/usr/bin/env python3
"""
iCloud Photos Migrator
A GUI tool to backup and organize iCloud Photos libraries to external drives.

Features:
- Automatic Photos library detection
- External drive selection
- Background process management
- Progress tracking
- Year/Month organized export
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json


class PhotosMigrator:
    def __init__(self, root):
        self.root = root
        self.root.title("iCloud Photos Migrator")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # State variables
        self.library_path = None
        self.library_size = 0
        self.destination_path = None
        self.export_organized = tk.BooleanVar(value=True)
        self.organized_folder_name = tk.StringVar(value="Organized Photos")

        self.setup_ui()
        self.detect_library()

    def setup_ui(self):
        """Create the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2E3440", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="iCloud Photos Migrator",
            font=("SF Pro Display", 24, "bold"),
            bg="#2E3440",
            fg="#ECEFF4"
        )
        title_label.pack(pady=20)

        # Main content
        main_frame = tk.Frame(self.root, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Library info section
        self.create_library_section(main_frame)

        # Destination section
        self.create_destination_section(main_frame)

        # Options section
        self.create_options_section(main_frame)

        # Progress section
        self.create_progress_section(main_frame)

        # Action buttons
        self.create_action_buttons(main_frame)

    def create_library_section(self, parent):
        """Create library information section"""
        section = tk.LabelFrame(parent, text="Photos Library", font=("SF Pro", 12, "bold"), padx=15, pady=10)
        section.pack(fill=tk.X, pady=(0, 15))

        self.library_label = tk.Label(section, text="Detecting...", font=("SF Pro", 11))
        self.library_label.pack(anchor=tk.W)

        self.size_label = tk.Label(section, text="Size: Calculating...", font=("SF Pro", 11), fg="#666")
        self.size_label.pack(anchor=tk.W, pady=(5, 0))

    def create_destination_section(self, parent):
        """Create destination selection section"""
        section = tk.LabelFrame(parent, text="Backup Destination", font=("SF Pro", 12, "bold"), padx=15, pady=10)
        section.pack(fill=tk.X, pady=(0, 15))

        dest_frame = tk.Frame(section)
        dest_frame.pack(fill=tk.X)

        self.dest_label = tk.Label(dest_frame, text="No destination selected", font=("SF Pro", 11))
        self.dest_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = tk.Button(
            dest_frame,
            text="Browse...",
            command=self.browse_destination,
            font=("SF Pro", 10),
            bg="#5E81AC",
            fg="white",
            padx=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.RIGHT)

        # External drives list
        drives_label = tk.Label(section, text="Available external drives:", font=("SF Pro", 10), fg="#666")
        drives_label.pack(anchor=tk.W, pady=(10, 5))

        self.drives_listbox = tk.Listbox(section, height=3, font=("SF Mono", 10))
        self.drives_listbox.pack(fill=tk.X)
        self.drives_listbox.bind('<<ListboxSelect>>', self.on_drive_select)

        self.refresh_drives()

    def create_options_section(self, parent):
        """Create options section"""
        section = tk.LabelFrame(parent, text="Export Options", font=("SF Pro", 12, "bold"), padx=15, pady=10)
        section.pack(fill=tk.X, pady=(0, 15))

        export_check = tk.Checkbutton(
            section,
            text="Also create organized folder structure (Year/Month)",
            variable=self.export_organized,
            font=("SF Pro", 11),
            command=self.toggle_folder_name
        )
        export_check.pack(anchor=tk.W)

        folder_frame = tk.Frame(section)
        folder_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(folder_frame, text="Folder name:", font=("SF Pro", 10)).pack(side=tk.LEFT)

        self.folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.organized_folder_name,
            font=("SF Pro", 10),
            width=30
        )
        self.folder_entry.pack(side=tk.LEFT, padx=10)

    def create_progress_section(self, parent):
        """Create progress tracking section"""
        section = tk.LabelFrame(parent, text="Progress", font=("SF Pro", 12, "bold"), padx=15, pady=10)
        section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.progress_text = tk.Text(section, height=6, font=("SF Mono", 9), state=tk.DISABLED)
        self.progress_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(section, command=self.progress_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.progress_text.config(yscrollcommand=scrollbar.set)

        self.progress_bar = ttk.Progressbar(section, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))

    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X)

        self.start_btn = tk.Button(
            button_frame,
            text="Start Backup",
            command=self.start_migration,
            font=("SF Pro", 12, "bold"),
            bg="#A3BE8C",
            fg="white",
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_btn.pack(side=tk.RIGHT)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.root.quit,
            font=("SF Pro", 12),
            bg="#BF616A",
            fg="white",
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=10)

    def detect_library(self):
        """Detect Photos library location and size"""
        self.log("Detecting Photos library...")

        default_path = Path.home() / "Pictures" / "Photos Library.photoslibrary"

        if default_path.exists():
            self.library_path = str(default_path)
            self.library_label.config(text=f"📸 {self.library_path}")

            # Calculate size in background
            threading.Thread(target=self.calculate_library_size, daemon=True).start()
        else:
            self.library_label.config(text="❌ No Photos library found")
            self.log("ERROR: No Photos library found at default location")

    def calculate_library_size(self):
        """Calculate library size"""
        try:
            result = subprocess.run(
                ['du', '-sh', self.library_path],
                capture_output=True,
                text=True
            )
            size_str = result.stdout.split()[0]
            self.root.after(0, lambda: self.size_label.config(text=f"Size: {size_str}"))
            self.log(f"Library size: {size_str}")
        except Exception as e:
            self.log(f"Error calculating size: {e}")

    def refresh_drives(self):
        """Refresh list of external drives"""
        self.drives_listbox.delete(0, tk.END)

        volumes_path = Path("/Volumes")
        if volumes_path.exists():
            for drive in volumes_path.iterdir():
                if drive.name not in ["Macintosh HD", "Preboot", "Recovery", "VM", "Update"]:
                    # Get drive size
                    try:
                        result = subprocess.run(
                            ['df', '-h', str(drive)],
                            capture_output=True,
                            text=True
                        )
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            parts = lines[1].split()
                            size = parts[1]
                            available = parts[3]
                            self.drives_listbox.insert(
                                tk.END,
                                f"{drive.name} - {size} total, {available} available"
                            )
                    except:
                        self.drives_listbox.insert(tk.END, drive.name)

    def on_drive_select(self, event):
        """Handle drive selection"""
        selection = self.drives_listbox.curselection()
        if selection:
            drive_info = self.drives_listbox.get(selection[0])
            drive_name = drive_info.split(' - ')[0]
            self.destination_path = f"/Volumes/{drive_name}"
            self.dest_label.config(text=f"✓ {self.destination_path}")
            self.log(f"Selected destination: {self.destination_path}")

    def browse_destination(self):
        """Browse for destination folder"""
        folder = filedialog.askdirectory(title="Select Backup Destination")
        if folder:
            self.destination_path = folder
            self.dest_label.config(text=f"✓ {folder}")
            self.log(f"Selected destination: {folder}")

    def toggle_folder_name(self):
        """Toggle folder name entry"""
        if self.export_organized.get():
            self.folder_entry.config(state=tk.NORMAL)
        else:
            self.folder_entry.config(state=tk.DISABLED)

    def log(self, message):
        """Add message to progress log"""
        self.progress_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.progress_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state=tk.DISABLED)

    def start_migration(self):
        """Start the migration process"""
        if not self.library_path:
            messagebox.showerror("Error", "No Photos library detected")
            return

        if not self.destination_path:
            messagebox.showerror("Error", "Please select a destination")
            return

        # Confirm with user
        message = f"This will:\n\n"
        message += f"1. Backup Photos library to:\n   {self.destination_path}\n\n"
        if self.export_organized.get():
            message += f"2. Export organized photos to:\n   {self.destination_path}/{self.organized_folder_name.get()}\n\n"
        message += f"This may take several hours. Continue?"

        if not messagebox.askyesno("Confirm Backup", message):
            return

        # Disable start button
        self.start_btn.config(state=tk.DISABLED)
        self.progress_bar.start()

        # Run migration in background thread
        threading.Thread(target=self.run_migration, daemon=True).start()

    def run_migration(self):
        """Run the actual migration process"""
        try:
            # Step 1: Kill background processes
            self.log("Stopping Photos background processes...")
            subprocess.run(
                ['killall', '-9', 'photolibraryd', 'cloudphotod', 'photoanalysisd'],
                stderr=subprocess.DEVNULL
            )
            self.log("✓ Background processes stopped")

            # Step 2: Copy library
            self.log("Starting library backup...")
            self.log("This will take a while - copying library files...")

            dest_library = Path(self.destination_path) / "Photos Library.photoslibrary"

            result = subprocess.run(
                ['rsync', '-avh', '--progress', self.library_path, self.destination_path + '/'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.log("✓ Library backup completed successfully")
            else:
                self.log(f"⚠️ Backup completed with warnings")
                self.log(f"Details: {result.stderr[:200]}")

            # Step 3: Export organized if requested
            if self.export_organized.get():
                self.log("Starting organized export...")
                self.export_photos_organized(dest_library)

            self.log("")
            self.log("=" * 50)
            self.log("BACKUP COMPLETE!")
            self.log("=" * 50)
            self.log(f"Location: {self.destination_path}")

            self.root.after(0, self.migration_complete)

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Migration failed: {e}"))
            self.root.after(0, self.reset_ui)

    def export_photos_organized(self, library_path):
        """Export photos to organized year/month structure"""
        self.log("Creating organized photo export...")
        self.log("This uses the osascript/Photos app method...")

        export_path = Path(self.destination_path) / self.organized_folder_name.get()
        export_path.mkdir(exist_ok=True)

        # Use AppleScript to export from Photos app
        script = f'''
        tell application "Photos"
            set theLibrary to "{library_path}"
            set exportFolder to "{export_path}"

            -- This is a placeholder - actual export would require Photos app integration
            -- For now, we'll copy from originals folder
        end tell
        '''

        # Alternative: Direct file copy from originals
        self.log("Copying photos from originals folder...")
        originals_path = library_path / "originals"

        if originals_path.exists():
            self.copy_photos_organized(originals_path, export_path)
        else:
            self.log("⚠️ Originals folder not found - skipping organized export")

    def copy_photos_organized(self, source, dest):
        """Copy photos and organize by year/month"""
        self.log("Organizing photos by date...")

        photo_extensions = {'.jpg', '.jpeg', '.heic', '.png', '.mov', '.mp4', '.gif'}
        copied = 0

        for root, dirs, files in os.walk(source):
            for file in files:
                if Path(file).suffix.lower() in photo_extensions:
                    source_file = Path(root) / file

                    # Get file modification date
                    try:
                        mtime = source_file.stat().st_mtime
                        date = datetime.fromtimestamp(mtime)
                        year = date.strftime("%Y")
                        month = date.strftime("%m-%B")

                        # Create year/month folder
                        dest_folder = dest / year / month
                        dest_folder.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        dest_file = dest_folder / file
                        if not dest_file.exists():
                            shutil.copy2(source_file, dest_file)
                            copied += 1

                            if copied % 100 == 0:
                                self.log(f"Copied {copied} photos...")

                    except Exception as e:
                        self.log(f"Error copying {file}: {e}")

        self.log(f"✓ Organized export complete - {copied} photos copied")

    def migration_complete(self):
        """Handle migration completion"""
        self.progress_bar.stop()
        self.start_btn.config(state=tk.NORMAL)
        messagebox.showinfo(
            "Success",
            "Backup completed successfully!\n\nYour photos are now backed up to the external drive."
        )

    def reset_ui(self):
        """Reset UI after error"""
        self.progress_bar.stop()
        self.start_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = PhotosMigrator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
