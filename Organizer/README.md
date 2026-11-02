# Automated File Organizer & Cleanup Utility

A Python automation script that tidies cluttered folders (like Downloads) by sorting files into category subfolders based on their extensions.

## Features

- Inspects every file's extension and sorts it into `Documents`, `Images`, `Videos`, `Archives`, `Code`, or `Others`
- Creates category folders automatically, only when needed
- Handles **naming collisions** by renaming (`report.pdf` -> `report_1.pdf`) so nothing is overwritten
- Handles `PermissionError`, `FileExistsError`, and other `OSError`s without crashing
- **Dry-run mode** to preview changes safely
- Logs every action to the console and to `organizer.log`
- Prints a formatted execution summary with total files relocated

## Tech Stack

Python 3 - standard library only: `os`, `shutil`, `pathlib`, `argparse`, `logging`

## Project Structure

```
file-organizer/
├── organizer.py    # main script
├── README.md       # this file
└── organizer.log   # created on first run
```

## Usage

```bash
# Organize your Downloads folder (default)
python organizer.py

# Organize a specific folder
python organizer.py "C:\Users\You\Desktop\Messy"

# Preview only, nothing is moved
python organizer.py --dry-run
```

## Example Output

```
==============================================
  EXECUTION SUMMARY
==============================================
  Directory : /home/user/Downloads
  Archives    :    3 file(s)
  Documents   :   12 file(s)
  Images      :    8 file(s)
----------------------------------------------
  Total relocated : 23
  Renamed (collisions) : 2
  Skipped              : 1
  Errors               : 0
==============================================
```

## Customizing

Edit `EXTENSION_MAP` at the top of `organizer.py` to add extensions or categories, for example:

```python
".epub": "Books",
```

## How It Works

1. `os.scandir()` lists the files in the target directory (subfolders are left untouched)
2. Each file's extension is looked up in `EXTENSION_MAP`
3. The destination folder is created if missing; a unique filename is chosen if one already exists
4. `shutil.move()` relocates the file inside a `try/except` block
5. A summary of moved, renamed, skipped, and failed files is printed

## Notes

- Only files directly inside the target folder are organized (not recursive)
- Close files that are open in other programs, or they may be skipped with a permission error
- Try `--dry-run` first on any important folder
