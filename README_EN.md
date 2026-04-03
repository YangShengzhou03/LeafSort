# LeafSort - Image Management, Smart Organization, File Deduplication, EXIF Editing & Batch Processing

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/YangShengzhou03/LeafSort?style=for-the-badge&logo=github)](https://github.com/YangShengzhou03/LeafSort/stargazers)&nbsp;[![GitHub forks](https://img.shields.io/github/forks/YangShengzhou03/LeafSort?style=for-the-badge&logo=github)](https://github.com/YangShengzhou03/LeafSort/network/members)&nbsp;[![GitHub issues](https://img.shields.io/github/issues/YangShengzhou03/LeafSort?style=for-the-badge&logo=github)](https://github.com/YangShengzhou03/LeafSort/issues)&nbsp;[![GitHub license](https://img.shields.io/github/license/YangShengzhou03/LeafSort?style=for-the-badge)](https://github.com/YangShengzhou03/LeafSort/LICENSE)&nbsp;[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)&nbsp;[![PyQt6](https://img.shields.io/badge/PyQt6-6.10.2-41CD52?style=for-the-badge&logo=qt)](https://www.riverbankcomputing.com/software/pyqt/)

<a href="https://apps.microsoft.com/detail/9p3mkv4xslj8?referrer=appbadge&mode=direct">
 <img src="https://get.microsoft.com/images/en-us%20dark.svg" width="200"/>
</a>

<div align="center">
  <h3>A modern media file management tool focused on efficient management and smart organization</h3>
  <p>Supports fast browsing and management of multiple image formats, provides automatic classification and organization based on time, location, device, and type</p>
</div>

[Quick Start](#quick-start) • [Features](#features) • [Technical Architecture](#technical-architecture) • [User Guide](#user-guide)

</div>

## Introduction

![LeafSort Poster](https://raw.githubusercontent.com/YangShengzhou03/LeafSort/master/assets/LeafSort_poster.jpg)

LeafSort is a Python-based image management tool focused on efficient management, smart organization, and batch processing of various image files. The software supports fast browsing and management of multiple image formats, provides automatic classification and organization based on multiple dimensions such as capture time, GPS location, capture device, and file type. It supports file deduplication based on MD5 hash algorithm, viewing and editing EXIF metadata, and geocoding operations.

The software adopts a three-layer architecture design, including the user interface layer, business logic layer, and data processing layer. The user interface layer builds a modern GUI based on PyQt6, the business logic layer handles core business logic and feature implementation, and the data processing layer is responsible for file operations, metadata processing, and configuration management. Through modern technical architecture and user-friendly interaction design, it provides users with convenient, efficient, and secure media file management services.

The software's design philosophy is simple, efficient, and intelligent. Simplicity is reflected in the clean and clear user interface, clear and easy-to-understand operation process, users can quickly get started without complex learning costs. Efficiency is reflected in fast file processing speed, support for multi-threaded concurrent processing, able to quickly process large numbers of files. Intelligence is reflected in automatic recognition of image metadata, smart classification and organization, reducing manual operations.

The software's technical architecture adopts modular design, dividing the system into multiple independent functional modules, each responsible for specific functions. This architecture design makes the system have good scalability and maintainability, can easily add new features or modify existing features.

The software is committed to providing a free and efficient media file management tool for photography enthusiasts and professional photographers, helping users quickly organize and manage large numbers of photos and video files, improving work efficiency. The software supports multiple image formats, including mainstream formats such as JPEG, PNG, WebP, HEIC, HEIF, and can quickly load and display large numbers of image files.

## Features

### Image Management

Supports fast browsing and management of multiple image formats, including mainstream formats such as JPEG, PNG, WebP, HEIC, HEIF, able to quickly load and display large numbers of image files.

![Media Import](https://raw.githubusercontent.com/YangShengzhou03/LeafSort/master/assets/media_import.png)

### Smart Organization

Provides smart organization features, can automatically classify and organize files based on multiple dimensions such as image capture time, GPS location, capture device, and file type. Users can customize classification rules and file naming rules. The software automatically reads image EXIF metadata, builds target paths and filenames, and performs file copy or move operations.

![Smart Organize](https://raw.githubusercontent.com/YangShengzhou03/LeafSort/master/assets/smart_organize.png)

Supports classification by time dimension, including year, year-month, year-month-day, year-month-day-hour-minute-second and other formats. Supports classification by geographic location, including province, city, district and other levels. Supports classification by device type, including camera brand, model, etc. Supports classification by file type, including image, video, audio, document and other types.

### File Deduplication

High-precision identification of identical files based on MD5 hash algorithm. Supports two-stage filtering mechanism: the first stage groups by file size, quickly excluding non-duplicate files; the second stage only calculates MD5 for files of the same size, significantly reducing computation. Uses thread pool for concurrent MD5 calculation, supports caching of calculated hash values, improving processing efficiency.

![File Deduplication](https://raw.githubusercontent.com/YangShengzhou03/LeafSort/master/assets/file_deduplication.png)

Supports batch deduplication, can scan entire folders or specified folders, automatically identify duplicate files. Supports manual selection of files to keep, or let the software randomly select. Supports preview of duplicate files, view file details, ensure correct files are deleted.

### EXIF Editing

Supports viewing and modifying image EXIF metadata information, including title, author, rating, camera brand, model, lens information, etc. The software has built-in camera brand model database and lens model database, can automatically match lens information. Supports EXIF reading and writing for multiple formats such as JPEG, PNG, WebP, uses exiftool as a backup solution for complex formats.

![EXIF Editing](https://raw.githubusercontent.com/YangShengzhou03/LeafSort/master/assets/attribute_write.png)

Supports batch EXIF editing, can modify EXIF information of multiple files at once. Supports custom fields, including title, author, keywords, description, etc. Supports rating system, can set 1-5 star rating for files. Supports viewing complete EXIF information, including shooting parameters, GPS location, camera settings, etc.

### Geocoding

Uses offline geographic data to convert GPS coordinates to address information. Supports batch processing of files with the same location, improving processing efficiency.

Supports reverse geocoding, converting latitude and longitude coordinates to address information such as province, city, district. Supports batch processing, can process GPS information of multiple files at once. Supports custom address format, including province, city, district, street and other levels.

### Multi-Format Support

In addition to image formats, also supports management and processing of video, audio, document, archive and other file types. Supports file type detection, automatically identifies file types. Supports file extension filtering, can filter files by file type.

## Download

| Platform | Link |
| --- | --- |
| Microsoft Store | [https://apps.microsoft.com/detail/9p3mkv4xslj8](https://apps.microsoft.com/detail/9p3mkv4xslj8) |
| Onlinedown | [https://www.onlinedown.net/soft/20269802.htm](https://www.onlinedown.net/soft/20269802.htm) |
| Lenovo App Store | [https://lestore.lenovo.com/detail/L120850](https://lestore.lenovo.com/detail/L120850) |

## Quick Start

### Requirements

#### Development Environment

- **Python**: 3.11+
- **PyQt6**: 6.10.2 (GUI Framework)
- **Pillow**: 11.3.0 (Image Processing)
- **piexif**: 1.1.3 (EXIF Processing)
- **exifread**: 3.0.0 (EXIF Reading)
- **pillow-heif**: 0.16.0 (HEIC/HEIF Support)
- **requests**: 2.31.0 (HTTP Requests)

#### Production Environment

- **Operating System**: Windows 10/11
- **Memory**: 4GB+ RAM
- **Storage**: 2GB+ available space

### Environment Configuration

#### Python Environment Configuration

Python 3.11+ is the basic environment for software development, PyQt6 6.10.2 framework requires Python 3.11 or higher version. After installing Python 3.11, you need to configure the PATH environment variable, add Python's Scripts directory to PATH. You can verify if Python is correctly installed by running the `python --version` command.

#### PyQt6 Environment Configuration

PyQt6 6.10.2 is the basic GUI framework for software development, used to build modern user interfaces. After installing PyQt6, you can check if PyQt6 is correctly installed by running the `pip list` command. PyQt6 supports multiple platforms including Windows, macOS, Linux.

#### Dependency Library Configuration

The project depends on multiple third-party libraries, including image processing libraries (Pillow), EXIF processing libraries (piexif, exifread), HTTP request libraries (requests), etc. After installing dependency libraries, you can check if all dependency libraries are correctly installed by running the `pip list` command.

## Installation

### 1. Clone the Project

```bash
git clone https://github.com/YangShengzhou03/LeafSort.git
cd LeafSort
```

After cloning the project, the project directory contains multiple Python source files, resource files, configuration files, etc. Main files include App.py (application entry), main_window.py (main window), smart_arrange.py (smart organization), write_exif.py (EXIF editing), file_deduplication.py (file deduplication), etc.

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

Creating a virtual environment can isolate project dependencies and avoid conflicts with dependencies of other projects. After activating the virtual environment, the command line prompt will display the virtual environment name, indicating that you have entered the virtual environment.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements.txt file lists all third-party libraries that the project depends on and their version requirements. Running this command will automatically download and install all dependency libraries. After installation is complete, you can check if all dependency libraries are correctly installed by running the `pip list` command.

### 4. Run the Application

```bash
python App.py
```

Running this command will start the application and display the main window. The application will automatically check for updates, if there is a new version, it will prompt the user to download and install. The application supports single instance running, if an instance is already running, the new instance will automatically exit.

## User Guide

### Folder Management

After starting the software, you first need to set the source folder and destination folder. Click the "Browse" button, select the folder containing the images to be organized as the source folder, and select the storage location for the organized images as the destination folder. The software will display basic information about the folder, including the number of files.

### Smart Organization

On the smart organization page, you can configure classification rules and file naming rules. Supports classification by time dimension, including year, year-month, year-month-day, year-month-day-hour-minute-second and other formats. Supports classification by geographic location, including province, city, district and other levels. Supports classification by device type, including camera brand, model, etc. Supports classification by file type, including image, video, audio, document and other types.

After configuration is complete, click the "Start Organization" button, the software will automatically traverse the folder, read image EXIF metadata, build target paths and filenames, and perform file copy or move operations. During the organization process, the software will display progress information, including processed file count, total file count, processing speed, etc.

### EXIF Editing

On the EXIF editing page, you can add or modify EXIF metadata for images. Supports setting title, author, rating, camera brand, model, lens information, etc. The software has built-in camera brand model database and lens model database, after selecting camera brand and model, it will automatically match lens information.

After configuration is complete, click the "Start Writing" button, the software will traverse the folder and update image EXIF data. During the writing process, the software will display progress information, including processed file count, total file count, processing speed, etc.

### File Deduplication

On the file deduplication page, you can find and delete duplicate files. Click the "Start Deduplication" button, the software will scan the folder, calculate file MD5 hash values, and find identical files. After deduplication is complete, the duplicate file list will be displayed. Users can manually select files to keep, or let the software randomly select.

After selection is complete, click the "Move to Recycle Bin" button, the software will move the selected duplicate files to the recycle bin. During the moving process, the software will display progress information, including moved file count, total file count, moving speed, etc.

### Geocoding

The software automatically converts image GPS coordinates to address information. Uses offline geographic data for reverse geocoding.

Supports reverse geocoding, converting latitude and longitude coordinates to address information such as province, city, district. Supports batch processing, can process GPS information of multiple files at once. Supports custom address format, including province, city, district, street and other levels.

## Technical Architecture

### System Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Interface │    │ Business Logic  │    │ Data Processing │
│      Layer      │    │      Layer      │    │      Layer      │
│                 │    │                 │    │                 │
│  PyQt6 6.10.2   │◄──►│  Python 3.11+   │◄──►│  File System    │
│  Qt Designer    │    │ Multi-threading │    │  EXIF Data      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Graphical UI   │    │  Core Features  │    │ External Services│
│                 │    │                 │    │                 │
│  Main Window    │    │ Smart Organize  │    │   ExifTool      │
│Folder Management│    │  EXIF Editing   │    │                 │
│Progress Display │    │File Deduplication│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack Details

| Technology  | Version  | Purpose          |
| ----------- | -------- | ---------------- |
| Python      | 3.11+    | Programming Language |
| PyQt6       | 6.10.2   | GUI Framework    |
| Pillow      | 11.3.0  | Image Processing |
| piexif      | 1.1.3   | EXIF Processing  |
| exifread    | 3.0.0   | EXIF Reading     |
| pillow-heif | 0.16.0  | HEIC/HEIF Support|
| requests    | 2.31.0  | HTTP Requests    |

### Project Structure

```
LeafSort/
├── Application.py                  # Application entry
├── Application.spec                # PyInstaller packaging config
├── requirements.txt                # Python dependency list
├── README.md                       # Project documentation (Chinese)
├── README_EN.md                    # Project documentation (English)
├── LICENSE                         # License file
├── .gitignore                      # Git ignore file config
├── app/                            # Application layer
│   ├── __init__.py
│   ├── main_window.py              # Main window implementation
│   ├── dialogs/                    # Dialogs
│   │   ├── __init__.py
│   │   ├── update_dialog.py        # Update check dialog
│   │   ├── UI_UpdateDialog.py      # Update dialog UI (auto-generated)
│   │   └── UI_UpdateDialog.ui      # Qt Designer interface file
│   └── pages/                      # Feature pages
│       ├── __init__.py
│       ├── add_folder.py           # Folder management feature
│       ├── smart_arrange.py        # Smart organization service manager
│       ├── write_exif.py           # EXIF editing manager
│       └── file_deduplication.py   # File deduplication manager
├── core/                           # Core layer
│   ├── __init__.py
│   ├── common.py                   # Common functions and utilities
│   └── config_manager.py           # Configuration manager (thread-safe)
├── threads/                        # Thread layer
│   ├── __init__.py
│   ├── smart_arrange_thread.py     # Smart organization worker thread
│   ├── write_exif_thread.py        # EXIF writing worker thread
│   └── file_deduplication_thread.py # File deduplication worker thread
├── ui/                             # UI layer
│   ├── __init__.py
│   ├── Ui_MainWindow.py            # UI interface file (auto-generated)
│   └── Ui_MainWindow.ui            # Qt Designer interface file
├── cer/                            # Digital signature files
│   ├── Y.cer                       # Certificate file
│   ├── Y.pfx                       # Private key file
│   ├── Y.pvk                       # Private key container
│   ├── Y.spc                       # Software publisher certificate
│   ├── cert2spc.exe                # Certificate conversion tool
│   └── certmgr.exe                 # Certificate management tool
└── resources/                      # Resource files
    ├── exiftool/                   # EXIF tool
    │   ├── exiftool.exe            # EXIF tool executable
    │   ├── exiftool(-k).exe        # EXIF tool (keep window)
    │   └── exiftool_files/         # EXIF tool dependencies
    ├── fonts/                      # Font files
    │   └── Microsoft YaHei UI Light.ttf
    ├── img/                        # Image resources
    │   ├── list/                   # List icons
    │   ├── page_2/                 # Page icons
    │   ├── page_4/                 # Page icons
    │   ├── 窗口控制/               # Window control icons
    │   ├── icon.ico                # Application icon
    │   └── setup.ico               # Installation icon
    ├── json/                       # JSON data files
    │   ├── City_Reverse_Geocode.json         # City geocoding data
    │   ├── Province_Reverse_Geocode.json     # Province geocoding data
    │   ├── camera_brand_model.json           # Camera brand model database
    │   └── camera_lens_mapping.json          # Camera lens mapping database
    └── stylesheet/                 # Stylesheet files
        └── menu.setStyleSheet.css  # Menu stylesheet
```

### Core Module Description

- **Application.py**: Application entry, responsible for initializing QApplication, creating main window instance, setting up global exception handling and single instance detection
- **app/main_window.py**: Main window controller, manages all feature pages, handles window events, manages system tray icon
- **app/pages/add_folder.py**: Folder management page, manages source folder and destination folder selection, validates folder path validity
- **app/pages/smart_arrange.py**: Smart organization business logic manager, manages smart organization UI interaction, collects user configuration
- **threads/smart_arrange_thread.py**: Smart organization worker thread, executes organization tasks in separate thread, avoids blocking UI
- **app/pages/write_exif.py**: EXIF editing business logic manager, manages EXIF editing UI interaction, collects user configuration
- **threads/write_exif_thread.py**: EXIF writing worker thread, executes EXIF writing tasks in separate thread
- **app/pages/file_deduplication.py**: File deduplication business logic manager, manages file deduplication UI interaction
- **threads/file_deduplication_thread.py**: File deduplication worker thread, scans files and calculates MD5, deletes duplicate files
- **core/common.py**: Common utility library, provides resource path management, file type detection, media type detection and other functions
- **core/config_manager.py**: Configuration manager, thread-safe configuration read/write operations
- **app/dialogs/update_dialog.py**: Update check dialog, checks for latest version on GitHub

### Threading Model

The software uses Qt signal-slot mechanism for thread communication. The main thread handles all UI interactions and responses, worker threads execute time-consuming file operation tasks. All worker threads inherit from QThread, support stopping operations at any time, maintain UI responsiveness.

## Development Guide

### Code Standards

Class names use PascalCase naming convention, such as SmartArrangeManager. Function names use lowercase letters with underscores, such as get_exif_data. Variable names use lowercase letters with underscores, such as file_path. Constants use uppercase letters with underscores, such as IMAGE_EXTENSIONS. Private methods use single underscore prefix, such as \_process_file.

### Error Handling

All operations that may throw exceptions should be caught and handled using try-except blocks. Exception information should be logged and, when necessary, displayed to users with friendly error messages. For critical operation failures, retry mechanisms or rollback mechanisms should be provided.

### Logging

Use Python standard library logging for log recording. Log levels are divided into DEBUG, INFO, WARNING, ERROR, CRITICAL five levels. DEBUG level is used for detailed debugging information, INFO level is used for general information, WARNING level is used for warning information, ERROR level is used for error information, CRITICAL level is used for serious error information.

### Testing Recommendations

When developing new features, unit tests and integration tests should be written. Tests should cover normal flows and exception flows. Test data should use mock data, avoid using real user data.

## License

This project is licensed under the Academic Free License (AFL) v. 3.0, see [LICENSE](LICENSE) file for details.

## Contributing Guide

We welcome all forms of contributions, including but not limited to:

- Submitting bug reports or feature suggestions
- Submitting code improvements or new features
- Improving documentation
- Sharing usage experience

### How to Contribute

1. Fork this repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## Acknowledgments

Thanks to all developers who contributed to this project, and all open source projects that provide support.

---

<div align="center">
  <p>© 2026 Yangshengzhou. All Rights Reserved.</p>
</div>
