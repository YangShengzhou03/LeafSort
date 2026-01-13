# LeafSort Media Management

![GitHub Stars](https://img.shields.io/github/stars/YangShengzhou03/LeafSort?style=flat-square) ![GitHub Forks](https://img.shields.io/github/forks/YangShengzhou03/LeafSort?style=flat-square) ![GitHub Issues](https://img.shields.io/github/issues/YangShengzhou03/LeafSort?style=flat-square) ![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

<a href="https://apps.microsoft.com/detail/9p3mkv4xslj8?referrer=appbadge&mode=direct">
 <img src="https://get.microsoft.com/images/en-us%20dark.svg" width="200"/>
</a>

LeafSort is a Python-based image management tool focused on efficient management, intelligent organization, and batch processing of various image files. The software supports fast browsing and management of multiple image formats, provides automatic classification and organization based on multiple dimensions such as time, location, device, and type, performs file deduplication based on MD5 hash algorithm, supports viewing and editing EXIF metadata, as well as batch renaming and geocoding operations.

## Software Features

### Image Management

Supports fast browsing and management of multiple image formats, including JPEG, PNG, WebP, HEIC, HEIF, and other mainstream formats, capable of quickly loading and displaying large numbers of image files.

### Smart Organization

Provides intelligent organization functionality that can automatically classify and organize files based on multiple dimensions such as image capture time, GPS location, capture device, and file type. Users can customize classification rules and file naming rules. The software automatically reads image EXIF metadata, constructs target paths and filenames, and performs file copy or move operations.

### File Deduplication

Identifies completely identical files based on MD5 hash algorithm with high precision. Supports two-stage filtering mechanism: first stage groups files by size to quickly exclude non-duplicate files, second stage calculates MD5 only for files of the same size, significantly reducing computational load. Uses thread pool for concurrent MD5 calculation, supports caching of calculated hash values to improve processing efficiency.

### EXIF Editing

Supports viewing and modifying image EXIF metadata information, including title, author, rating, camera brand, model, lens information, etc. The software includes built-in camera brand model database and lens model database that can automatically match lens information. Supports EXIF read/write for multiple formats such as JPEG, PNG, WebP, and uses exiftool as a backup solution for complex formats.

### Geocoding

Automatically converts GPS coordinates to address information using Amap API for reverse geocoding. The software caches geocoding results to avoid repeated API calls, supports batch processing of files at the same location, and improves processing efficiency.

### Multi-format Support

In addition to image formats, also supports management and processing of video, audio, document, archive, and other file types.

## Technical Architecture

### Development Environment

- Python 3.11+
- PyQt6 6.5.0+
- Pillow 11.3.0+
- opencv-python 4.8.0+
- scikit-image 0.24.0+
- numpy 1.24.0+
- piexif 1.1.3+
- exifread 3.0.0+
- pillow-heif 0.16.0+
- requests 2.31.0+
- playwright 1.40.0+

### Architecture Design

The software adopts a three-layer architecture design, including user interface layer, business logic layer, and data processing layer. The user interface layer builds a modern GUI interface based on PyQt6, the business logic layer handles core business logic and feature implementation, and the data processing layer is responsible for file operations, metadata processing, and configuration management.

### Core Modules

- App.py: Application entry point, responsible for initializing QApplication, creating main window instance, setting up global exception handling, and single instance detection
- main_window.py: Main window controller, manages all feature pages, handles window events, manages system tray icon
- add_folder.py: Folder management page, manages source folder and target folder selection, validates folder path validity
- smart_arrange.py: Smart organization business logic manager, manages smart organization UI interaction, collects user configuration
- smart_arrange_thread.py: Smart organization worker thread, executes organization tasks in independent thread to avoid blocking UI
- write_exif.py: EXIF editing business logic manager, manages EXIF editing UI interaction, collects user configuration
- write_exif_thread.py: EXIF writing worker thread, executes EXIF writing tasks in independent thread
- file_deduplication.py: File deduplication business logic manager, manages file deduplication UI interaction
- file_deduplication_thread.py: File deduplication worker thread, scans files and calculates MD5, deletes duplicate files
- common.py: Common utility library, provides resource path management, file type detection, media type detection, geocoding service, and other functions
- config_manager.py: Configuration manager, thread-safe configuration read/write operations, manages geocoding cache and API call rate limiting
- update_dialog.py: Update check dialog, checks latest version on GitHub

### Thread Model

The software uses Qt signal-slot mechanism for thread communication. The main thread handles all UI interaction and responses, while worker threads execute time-consuming file operation tasks. All worker threads inherit from QThread, support stopping operations at any time, and maintain UI responsiveness.

## Usage

### Installing Software

#### For Windows Users

You can download and install directly from Microsoft Store by searching "LeafSort" or visiting the app store page.

#### For Developers

1. Clone the repository

```bash
git clone https://github.com/YangShengzhou03/LeafSort.git
cd LeafSort
```

2. Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Install Playwright browser

```bash
playwright install chromium
```

5. Run the application

```bash
python App.py
```

### Folder Management

After starting the software, you first need to set up the source folder and target folder. Click the "Add Folder" button to select the folder containing the images to be organized as the source folder, and select the location where organized images will be stored as the target folder. The software will display basic information about the folder, including the number of files and total size.

### Smart Organization

On the smart organization page, you can configure classification rules and file naming rules. Supports classification by time dimensions such as year, year-month, year-month-day, year-month-day-hour-minute-second, supports classification by geographic location such as province, city, district, supports classification by device type, and supports classification by file type. After configuration is complete, click the "Start Organization" button, and the software will automatically traverse the folder, read image EXIF metadata, construct target paths and filenames, and perform file copy or move operations.

### EXIF Editing

On the EXIF editing page, you can add or modify EXIF metadata for images. Supports setting title, author, rating, camera brand, model, lens information, etc. The software includes built-in camera brand model database and lens model database. When you select camera brand and model, it will automatically match lens information. After configuration is complete, click the "Start Writing" button, and the software will traverse the folder and update image EXIF data.

### File Deduplication

On the file deduplication page, you can find and delete duplicate files. Click the "Start Deduplication" button, and the software will scan the folder, calculate file MD5 hash values, and find completely identical files. After deduplication is complete, a list of duplicate files will be displayed. Users can manually select files to keep, or let the software randomly select. After selection is complete, click the "Start Deletion" button, and the software will delete the selected duplicate files.

### Geocoding

The software automatically converts image GPS coordinates to address information. Uses Amap API for reverse geocoding, supports caching geocoding results to avoid repeated API calls. If API call fails, offline geographic data will be used as a backup solution.

## Project Structure

```
LeafSort/
├── App.py                   # Application entry point
├── main_window.py           # Main window implementation
├── Ui_MainWindow.py         # UI interface file (auto-generated)
├── Ui_MainWindow.ui         # Qt Designer interface file
├── add_folder.py            # Folder management feature
├── smart_arrange.py         # Smart organization service manager
├── smart_arrange_thread.py  # Smart organization worker thread
├── write_exif.py            # EXIF editing manager
├── write_exif_thread.py     # EXIF writing worker thread
├── file_deduplication.py    # File deduplication manager
├── file_deduplication_thread.py # File deduplication worker thread
├── common.py                # Common functions and utility classes
├── config_manager.py        # Configuration manager (thread-safe)
├── update_dialog.py         # Update check dialog
├── UI_UpdateDialog.py       # Update dialog UI (auto-generated)
├── UI_UpdateDialog.ui       # Qt Designer interface file
├── requirements.txt         # Python dependency list
├── App.spec                 # PyInstaller packaging configuration
├── README.md                # Project documentation (Chinese)
├── README_EN.md             # Project documentation (English)
├── license.txt              # License text
├── .gitignore               # Git ignore file configuration
├── License/                 # Digital signature related files
│   ├── Y.cer                # Certificate file
│   ├── Y.pfx                # Private key file
│   ├── Y.pvk                # Private key container
│   ├── Y.spc                # Software publisher certificate
│   ├── cert2spc.exe         # Certificate conversion tool
│   └── certmgr.exe          # Certificate management tool
└── resources/               # Resource files
    ├── cv2_date/            # OpenCV related files
    │   └── haarcascade_frontalface_alt2.xml  # Face detection model
    ├── exiftool/            # EXIF tool
    │   ├── exiftool.exe     # EXIF tool executable
    │   ├── exiftool(-k).exe # EXIF tool (keep window)
    │   └── exiftool_files/  # EXIF tool dependency files
    ├── img/                 # Image resources
    │   ├── activity/        # Activity related icons
    │   ├── list/            # List icons
    │   ├── page_0/          # Page 0 icons
    │   ├── page_1/          # Page 1 icons
    │   ├── page_2/          # Page 2 icons
    │   ├── page_3/          # Page 3 icons
    │   ├── page_4/          # Page 4 icons
    │   ├── 头标/            # Member badges
    │   ├── 窗口控制/        # Window control icons
    │   ├── icon.ico         # Application icon
    │   └── setup.ico        # Installation icon
    ├── json/                # JSON data files
    │   ├── City_Reverse_Geocode.json         # City geocoding data
    │   ├── Province_Reverse_Geocode.json     # Province geocoding data
    │   ├── camera_brand_model.json           # Camera brand model database
    │   ├── camera_lens_mapping.json          # Camera lens mapping database
    │   └── lens_model.json                  # Lens model database
    └── stylesheet/          # Stylesheet files
        └── menu.setStyleSheet.css  # Menu stylesheet
```

## Development Guide

### Code Standards

Class names use PascalCase naming convention, such as SmartArrangeManager. Function names use lowercase with underscores, such as get_exif_data. Variable names use lowercase with underscores, such as file_path. Constants use uppercase with underscores, such as IMAGE_EXTENSIONS. Private methods use single underscore prefix, such as _process_file.

### Error Handling

Use try-except to catch exceptions, log detailed error information, and display friendly error messages to users. Provide recovery suggestions when critical operations fail. For file operation errors: if file does not exist, skip and log; if permission is insufficient, log error and continue processing other files; if file is corrupted, log error and skip. For EXIF reading errors: if format is not supported, use file system time; if data is corrupted, log warning and use default values; if field is missing, use empty or default values. For network request errors: if API call fails, use cached data; if Cookie expires, re-fetch Cookie; if timeout occurs, retry 3 times before giving up.

### Performance Optimization

The software uses caching mechanisms to improve performance, including thumbnail cache, metadata cache, geocoding cache, and file hash cache. Uses thread pool for concurrent MD5 calculation, processes multiple files simultaneously, with maximum thread count limited to CPU core count. Reads large files in chunks to avoid loading all at once, releases unused resources in a timely manner, limits cache size to prevent memory overflow. During file deduplication, groups by size first, skips empty and oversized files, skips system folders and hidden files.

## License

This project is licensed under the MIT License, see license.txt file for details.

## Contact

GitHub: https://github.com/YangShengzhou03/LeafSort
Microsoft Store: https://apps.microsoft.com/detail/9p3mkv4xslj8
