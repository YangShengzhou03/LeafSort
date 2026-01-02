<div align="center">
  <h1>LeafSort - Maple Leaf Photo Gallery</h1>
  <p>Efficient and intelligent image management tool</p>
  
  <p>
    <a href="https://github.com/YangShengzhou03/LeafSort/stargazers">
<img src="https://img.shields.io/github/stars/YangShengzhou03/LeafSort?style=for-the-badge&logo=github&color=ffd33d&labelColor=000000" alt="GitHub Stars">
<a href="https://github.com/YangShengzhou03/LeafSort/forks">
<img src="https://img.shields.io/github/forks/YangShengzhou03/LeafSort?style=for-the-badge&logo=github&color=green&labelColor=000000" alt="GitHub Forks">
<a href="https://github.com/YangShengzhou03/LeafSort/issues">
<img src="https://img.shields.io/github/issues/YangShengzhou03/LeafSort?style=for-the-badge&logo=github&color=purple&labelColor=000000" alt="GitHub Issues">
<a href="https://github.com/YangShengzhou03/LeafSort/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&logo=open-source-initiative&color=blue&labelColor=000000" alt="MIT License">
    </a>
  </p>
</div>

## Project Introduction

LeafSort is a powerful image management tool focused on efficiently managing, intelligently organizing, and batch processing various image files.

### Core Features

- **Efficient Image Management**: Supports multiple image formats, quick browsing and management of large numbers of images
- **Intelligent Organization**: Automatically classify and organize files by time, location, device, type, and other dimensions
- **Duplicate Detection**: Precisely identify identical files based on MD5 hash algorithm
- **EXIF Editing**: View and modify image metadata information, supports multiple formats
- **Batch Processing**: Supports batch renaming, EXIF writing, and other operations
- **Geocoding**: Automatically convert GPS coordinates to address information
- **Multi-format Support**: Supports various file types including images, videos, audio, documents, and archives

## Technical Architecture

### Tech Stack

- **Programming Language**: Python 3.11+
- **GUI Framework**: PyQt6 6.5.0+
- **Image Processing**: Pillow 11.3.0+, opencv-python 4.8.0+, scikit-image 0.24.0+, numpy 1.24.0+
- **Metadata Processing**: piexif 1.1.3+, exifread 3.0.0+
- **HEIC/HEIF Support**: pillow-heif 0.16.0+
- **Network Requests**: requests 2.31.0+
- **Browser Automation**: playwright 1.40.0+ (for obtaining geocoding API credentials)
- **Configuration Management**: JSON format configuration files with thread-safe operations

### Architecture Design

LeafSort adopts a three-tier architecture design to ensure code maintainability and scalability:

1. **User Interface Layer**: Modern GUI interface built on PyQt6
2. **Business Logic Layer**: Handles core business logic and feature implementation
3. **Data Processing Layer**: Responsible for file operations, metadata processing, and database interactions

#### System Architecture Details

**Module Dependency Diagram**:

```
App.py (Application Entry)
    └── main_window.py (Main Window)
            ├── Ui_MainWindow.py (UI Interface, Auto-generated)
            ├── add_folder.py (Folder Management)
            │       └── config_manager.py (Configuration Manager)
            ├── smart_arrange.py (Smart Arrange Manager)
            │       └── smart_arrange_thread.py (Smart Arrange Worker Thread)
            │               └── common.py (Common Utilities)
            ├── write_exif.py (EXIF Edit Manager)
            │       └── write_exif_thread.py (EXIF Edit Worker Thread)
            │               └── common.py (Common Utilities)
            ├── file_deduplication.py (File Deduplication Manager)
            │       └── file_deduplication_thread.py (File Deduplication Worker Thread)
            └── update_dialog.py (Update Check)
```

**Core Module Responsibilities**:

1. **App.py** - Application Entry Point
   - Initialize QApplication
   - Create main window instance
   - Set up global exception handling
   - Single instance detection (via port binding)

2. **main_window.py** - Main Window Controller
   - Manage all feature pages
   - Handle window events (minimize, maximize, close)
   - Manage system tray icon
   - Coordinate communication between feature modules

3. **Ui_MainWindow.py** - UI Interface Definition
   - Auto-generated from Qt Designer's .ui file
   - Define all UI components and layouts
   - **Warning**: Do not modify manually, will be overwritten by regeneration

4. **add_folder.py** - Folder Management Page
   - Manage source folder and target folder selection
   - Validate folder path validity
   - Save and load folder configuration
   - Display folder information (file count, size, etc.)

5. **smart_arrange.py** - Smart Arrange Business Logic Manager
   - Manage smart arrange UI interactions
   - Collect user configuration (classification rules, filename rules, etc.)
   - Start and stop smart arrange thread
   - Handle logs and progress returned by thread

6. **smart_arrange_thread.py** - Smart Arrange Worker Thread
   - Execute arrange tasks in independent thread to avoid blocking UI
   - Traverse folders, collect files
   - Read EXIF metadata
   - Build target path and filename
   - Execute file copy or move operations
   - Send progress and log signals to main thread

7. **write_exif.py** - EXIF Edit Business Logic Manager
   - Manage EXIF edit UI interactions
   - Collect user configuration (title, author, rating, etc.)
   - Manage camera brand and model selection
   - Auto-match lens information
   - Start and stop EXIF write thread

8. **write_exif_thread.py** - EXIF Write Worker Thread
   - Execute EXIF write tasks in independent thread
   - Select processing strategy based on file format
   - Use piexif library to write EXIF data
   - Use exiftool for complex formats
   - Send progress and log signals to main thread

9. **file_deduplication.py** - File Deduplication Business Logic Manager
   - Manage file deduplication UI interactions
   - Display duplicate file list
   - Handle user selection (manual selection, random selection)
   - Start and stop deduplication thread

10. **file_deduplication_thread.py** - File Deduplication Worker Thread
    - **FileScanThread**: Scan files and calculate MD5
      - Two-stage filtering: group by file size first, then calculate MD5
      - Use thread pool for concurrent MD5 calculation
      - Cache file hash values
    - **FileDeduplicateThread**: Delete duplicate files
      - Delete files based on user selection
      - Send progress signals

11. **common.py** - Common Utilities Library
    - **ResourceManager**: Resource path management
      - Handle path differences between development and packaged environments
    - **FileMagicNumberDetector**: File type detection
      - Identify actual file type via file header magic numbers
      - Verify if file extension is correct
    - **MediaTypeDetector**: Media type detection
      - Determine if file is image, video, or audio
    - **GeocodingService**: Geocoding service
      - Use Amap (Gaode) API for reverse geocoding
      - Manage Cookie and API Key
      - Cache geocoding results

12. **config_manager.py** - Configuration Manager (Thread-Safe)
    - Manage all configuration items (folder paths, window settings, etc.)
    - Thread-safe read/write operations
    - Auto-save and load configuration
    - Manage geocoding cache
    - API call rate limiting

13. **update_dialog.py** - Update Check Dialog
    - Check for latest version on GitHub
    - Display update information
    - Provide download links

**Data Flow**:

1. **Smart Arrange Flow**:
   ```
   User selects folders → add_folder.py
       ↓
   User configures classification rules → smart_arrange.py
       ↓
   Start worker thread → smart_arrange_thread.py
       ↓
   Traverse files → Read EXIF → Build path → Copy/Move files
       ↓
   Send progress/logs → smart_arrange.py → Update UI
   ```

2. **File Deduplication Flow**:
   ```
   User selects folders → add_folder.py
       ↓
   Click deduplication → file_deduplication.py
       ↓
   Start scan thread → FileScanThread
       ↓
   Collect files → Group by size → Calculate MD5 → Group duplicates
       ↓
   Display duplicate list → file_deduplication.py
       ↓
   User selects → Start delete thread → FileDeduplicateThread
       ↓
   Delete files → Send progress → Update UI
   ```

3. **EXIF Edit Flow**:
   ```
   User selects folders → add_folder.py
       ↓
   User configures EXIF info → write_exif.py
       ↓
   Start write thread → write_exif_thread.py
       ↓
   Traverse files → Read existing EXIF → Update EXIF → Write to file
       ↓
   Send progress/logs → write_exif.py → Update UI
   ```

**Thread Model**:

- **Main Thread (UI Thread)**:
  - Handle all UI interactions
  - Respond to user actions
  - Update interface display
  - Receive signals from worker threads

- **Worker Threads**:
  - SmartArrangeThread: Smart arrange tasks
  - WriteExifThread: EXIF write tasks
  - FileScanThread: File scan tasks
  - FileDeduplicateThread: File delete tasks
  - All worker threads inherit from QThread

- **Thread Communication**:
  - Use Qt's signal-slot mechanism (Signal/Slot)
  - Worker threads send signals, main thread receives and updates UI
  - Thread-safe, won't block UI

**Key Design Decisions**:

1. **Why use MD5 instead of perceptual hash?**
   - MD5 is an exact hash that can 100% identify identical files
   - Perceptual hash can identify similar files but may produce false positives
   - The goal of file deduplication is to delete completely duplicate files, not similar files
   - MD5 calculation is fast, suitable for processing large numbers of files

2. **Why use piexif instead of other libraries?**
   - piexif is specifically for EXIF read/write with simple API
   - Supports mainstream formats like JPEG, PNG, WebP
   - Well-documented and active community
   - Use exiftool as backup for complex formats

3. **Why use Playwright to get Cookie?**
   - Amap (Gaode) API requires Cookie and Key to call
   - Cookie and Key change periodically, need dynamic acquisition
   - Playwright can simulate browser access and automatically extract Cookie
   - More stable and reliable than manual scraping

4. **Why use independent threads for task processing?**
   - File operations are IO-intensive and will block UI
   - Independent threads can keep UI responsive
   - Support stopping operations at any time, improving user experience
   - Qt's signal-slot mechanism ensures thread safety

5. **Why use two-stage filtering for file deduplication?**
   - First stage: group by file size, quickly exclude non-duplicate files
   - Second stage: calculate MD5 only for same-size files, significantly reducing computation
   - Significant performance improvement, especially when file count is large
   - Cache mechanism avoids repeated calculations

**Thread Safety Mechanisms**:

1. **ConfigManager's Thread Safety**:
   - Use threading.RLock to protect all configuration reads/writes
   - Use decorator `@_thread_safe_method` to ensure method thread safety
   - All public methods are lock-protected

2. **Geocoding Cache's Thread Safety**:
   - Cache reads and writes both use RLock protection
   - Support multi-threaded concurrent access
   - Automatically clean expired cache

3. **Worker Thread Stop Mechanism**:
   - Use `_stop_flag` flag to control thread stop
   - Periodically check flag, respond to stop request in time
   - Use `isInterruptionRequested()` to check interruption

**Error Handling Strategies**:

1. **File Operation Errors**:
   - File not found: Skip and log
   - Insufficient permissions: Log error and continue processing other files
   - File corrupted: Log error and skip

2. **EXIF Read Errors**:
   - Format not supported: Use file system time
   - Data corrupted: Log warning and use default values
   - Missing fields: Use empty or default values

3. **Network Request Errors**:
   - API call failed: Use cached data
   - Cookie expired: Re-acquire Cookie
   - Timeout: Retry 3 times then give up

4. **Thread Errors**:
   - Thread crash: Catch exception and log
   - Stop failed: Force terminate thread
   - Resource leak: Use try-finally to ensure release

**Performance Optimization Strategies**:

1. **Cache Mechanisms**:
   - Thumbnail cache: Avoid regenerating thumbnails
   - Metadata cache: Avoid repeated EXIF reading
   - Geocoding cache: Avoid repeated API calls
   - File hash cache: Avoid repeated MD5 calculation

2. **Concurrent Processing**:
   - Use thread pool for concurrent MD5 calculation
   - Process multiple files simultaneously
   - Limit max threads to CPU core count

3. **Memory Management**:
   - Read large files in chunks, avoid loading all at once
   - Release unused resources in time
   - Limit cache size to prevent memory overflow

4. **Smart Filtering**:
   - Group by file size first for file deduplication
   - Skip empty files and oversized files (>2GB)
   - Skip system folders and hidden files

**Configuration Data Structure**:

```json
{
  "version": "1.1",
  "last_modified": "2025-01-03T12:00:00",
  "folders": [
    "D:/Photos",
    "D:/Videos"
  ],
  "settings": {
    "thumbnail_size": 200,
    "max_cache_size": 10000,
    "default_view": "grid",
    "dark_mode": false,
    "auto_update_metadata": true,
    "use_gps_cache": true,
    "map_provider": "gaode",
    "show_thumbnails": true,
    "enable_exif_edit": true,
    "remember_window_size": true,
    "max_threads": 4,
    "memory_limit_mb": 2048,
    "last_opened_folder": "",
    "window_position": {"x": 100, "y": 100},
    "window_size": {"width": 942, "height": 580},
    "location_cache_tolerance": 0.027,
    "source_folder": "",
    "target_folder": ""
  },
  "api_limits": {
    "gaode": {
      "daily_calls": 50,
      "max_daily_calls": 100,
      "last_reset_date": "2025-01-03",
      "last_call_time": "2025-01-03T12:00:00"
    }
  },
  "cache_settings": {
    "max_location_cache_size": 500000,
    "cache_expiry_days": 0
  }
}
```

**Geocoding Cache Data Structure**:

```json
{
  "39.916527,116.397128": {
    "address": "Beijing Dongcheng District Tiananmen Square",
    "last_access": "2025-01-03T12:00:00"
  },
  "30.274085,120.15507": {
    "address": "Zhejiang Province Hangzhou City Xihu District West Lake",
    "last_access": "2025-01-03T12:00:00"
  }
}
```

**Performance Bottleneck Analysis**:

1. **MD5 Calculation for File Deduplication**:
   - Bottleneck: MD5 calculation time for large files
   - Optimization: Use two-stage filtering to reduce MD5 calculations
   - Optimization: Use thread pool for concurrent calculation
   - Optimization: Cache calculated MD5 values

2. **Geocoding API Calls**:
   - Bottleneck: Network request latency and API rate limiting
   - Optimization: Use cache to reduce API calls
   - Optimization: Batch process files at same location
   - Optimization: Use offline geocoding data as backup

3. **EXIF Data Reading**:
   - Bottleneck: EXIF reading for large numbers of files
   - Optimization: Cache read EXIF data
   - Optimization: Skip files that don't support EXIF
   - Optimization: Use efficient EXIF libraries

4. **File Copy/Move**:
   - Bottleneck: IO operations for large files
   - Optimization: Use async IO (future consideration)
   - Optimization: Process in batches to avoid memory overflow
   - Optimization: Show progress to improve user experience

**Future Optimization Directions**:

1. **Use Async IO**: Improve file operation performance
2. **Incremental Processing**: Support resume capability
3. **Distributed Processing**: Support multi-machine parallel processing
4. **Machine Learning**: Use perceptual hash to identify similar files
5. **Cloud Sync**: Support cloud storage integration

## Project Structure

```
LeafSort/                    # Project root directory
├── App.py                   # Application entry point
├── main_window.py           # Main window implementation
├── Ui_MainWindow.py         # UI interface file
├── Ui_MainWindow.ui         # Qt designer interface file
├── add_folder.py            # Folder management functionality
├── smart_arrange.py         # Smart arrangement service
├── smart_arrange_thread.py  # Smart arrangement thread
├── write_exif.py            # EXIF editing functionality
├── write_exif_thread.py     # EXIF editing thread
├── file_deduplication.py    # File deduplication functionality
├── file_deduplication_thread.py # File deduplication thread
├── common.py                # Common functions
├── config_manager.py        # Configuration manager
├── update_dialog.py         # Update dialog
├── UI_UpdateDialog.py       # Update dialog UI
├── UI_UpdateDialog.ui       # Qt designer interface file
├── License\                 # License related files
├── resources/               # Resource files
│   ├── cv2_date/            # OpenCV related files
│   ├── exiftool/            # EXIF tool
│   ├── img/                 # Image resources
│   ├── json/                # JSON data files
│   └── stylesheet/          # Stylesheet files
├── requirements.txt         # Dependency list
├── README.md                # Project description (Chinese)
└── README_EN.md             # Project description (English)
```

## Installation and Deployment

### Environment Requirements

- Python 3.11 or higher
- Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)


### Source Installation

1. Clone the repository
   ```bash
   git clone https://github.com/YangShengzhou03/LeafSort.git
   cd LeafSort
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   python App.py
   ```

### Pre-compiled Version

You can download pre-compiled executable files for your platform from the [GitHub Releases](https://github.com/YangShengzhou03/LeafSort/releases) page.

### Packaging as Executable

```bash
# Windows
pyinstaller -w -F --icon=resources/img/icon.ico App.py
```

## User Guide

### Basic Operations

1. **Import Images**: Import images through the "File" menu or by dragging and dropping
2. **Browse Images**: Use mouse wheel, arrow keys, or thumbnail list to browse
3. **View Details**: Click the "Details" button to view image metadata
4. **Batch Processing**: Select multiple images and use the right-click menu for batch operations

### Intelligent Organization

The intelligent organization feature supports the following classification methods and file formats:

#### Supported File Formats
- **Image Formats**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`, `.tiff`, `.heic`, `.heif`, `.svg`
- **Video Formats**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.mkv`, `.webm`, `.m4v`, `.3gp`
- **Audio Formats**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a`

#### Classification Methods and Extracted Information

**By Time**:
- Reads EXIF `DateTimeOriginal` field
- Supports Year/Month/Day hierarchical structure
- Example: `2024/01/15_filename.jpg`

**By Location**:
- Based on GPS coordinates for geocoding
- Supports automatic province/city recognition
- Example: `Beijing/Chaoyang_filename.jpg`

**By Device**:
- **Camera Brand**: Reads EXIF `Make` field (camera brand, phone brand)
- **Camera Model**: Reads EXIF `Model` field (specific device model)
- Supports mainstream camera and phone brand recognition
- Example: `Apple/iPhone_15_Pro_filename.jpg`

**By File Type**:
- Uses file extension for classification
- Example: `JPEG/PNG/HEIC/filename.jpg`

**Multi-level Classification**:
- Supports up to 5-level classification combinations
- Customizable separators (-, _, space, none, etc.)
- Example: `2024/Apple/iPhone_15_Pro/JPEG/filename.jpg`

#### Operation Steps
1. Select images or folders to organize
2. Click the "Intelligent Organization" button
3. Choose target folder path
4. Configure classification rules (supports multi-level combinations)
5. Click "Start Organization" to execute the operation

### File Deduplication

The deduplication feature can intelligently identify and remove duplicate files, supporting:

#### Supported Formats and Detection Method
- **Supported Formats**: All file formats (based on file content detection)
- **Algorithm**: MD5 hash algorithm
- **Exact Identification**: Precise hash calculation based on file content
- **Format Independent**: Ignores file format differences, identifies identical content regardless of format

#### Detection Principle
- **Two-Stage Filtering Mechanism**:
  1. First stage: Group by file size, only calculate hash for same-size files, significantly improving performance
  2. Second stage: Calculate MD5 hash for same-size files to precisely identify files with identical content
- **MD5 Algorithm Characteristics**:
  - Hash value calculated based on file binary content
  - MD5 values are guaranteed to be identical when file content is completely the same
  - MD5 values are completely different if file content has any difference (even one byte)
  - Cannot identify similar but not identical files (this is the key difference from perceptual hash algorithms)
- **Cache Mechanism**:
  - Cache file size, modification time, and MD5 values
  - Avoid repeated calculations for already processed files
  - Support multi-threaded concurrent processing to improve large file processing efficiency

#### Operation Steps
1. Select the folder containing files to scan
2. Click "Find Duplicates" button
3. Wait for scanning to complete, system will automatically find all identical files
4. Review detected duplicate groups:
   - **Auto-grouping**: Automatically groups files with same MD5 value
   - **Preview Comparison**: Side-by-side comparison of duplicate files
   - **Manual Selection**: Support manual selection of files to keep or delete
5. Select files to delete or move to trash

#### Duplicate File Handling Features
- **Random Selection**: Randomly keep one file per group, delete the rest
- **Safe Deletion**: Directly delete selected duplicate files (Note: deletion is irreversible, please use with caution)
- **Preview Before Deletion**: Visual confirmation before removing files
- **Progress Display**: Real-time display of deletion progress and status

### EXIF Editing

#### Supported File Formats and Editable Properties

**JPEG/PNG/WebP Formats**:
- **Title** (Title/ImageDescription)
- **Author** (Artist/Creator)
- **Rating** (Rating) - 1-5 star rating system
- **Capture Time** (DateTimeOriginal) - Supports custom time source
- **Device Information** (Make/Model) - Supports mainstream camera and phone brands
- **Lens Information** (LensModel/LensMake) - Automatic matching based on device
- **Geographic Location** (GPS related tags) - Supports latitude/longitude writing
- **Copyright Information** (Copyright)
- **Keywords/Tags** (XPKeywords, etc.)

**HEIC/HEIF Formats**:
- **Title and Description** (partial support)
- **Author Information** (limited support)
- **Rating** (partial device support)
- **Capture Time**
- **Device Information**
- *Note: Some property support may be limited depending on device compatibility*

**Video Formats (MOV/MP4/AVI/MKV)**:
- **Title** (Title)
- **Author/Creator** (Author/Creator)
- **Rating** (limited support)
- **Capture Time**
- **Basic Device Information**
- *Note: Video metadata support is relatively simple, mainly for basic identification*

**RAW Formats (CR2/CR3/NEF/ARW/ORF/DNG/RAF)**:
- **Title** (Title)
- **Author Information**
- **Rating** (limited by format specifications)
- **Capture Time**
- **Partial Device Information**
- *Note: RAW format metadata writing is restricted by camera manufacturer format limitations*

#### Device Information Database
Built-in rich device information database, supporting:
- **Camera Brands**: Canon, Nikon, Sony, Fujifilm, Leica, Panasonic, Olympus, Pentax, Sigma, etc.
- **Phone Brands**: Apple, Xiaomi, Huawei, OPPO, vivo, OnePlus, Samsung, Google, etc.
- **Automatic Lens Matching**: Automatically matches corresponding lens information based on camera model

#### Operation Steps
1. Select the images you want to edit
2. Click the "Edit EXIF" button
3. Configure editing options:
   - **Time Setting**: Use file time/EXIF time/custom time
   - **Device Information**: Select camera brand and model (automatic lens matching)
   - **Rating Setting**: 1-5 star rating
   - **Basic Information**: Title, author, copyright, etc.
4. Click "Start Writing EXIF Information" to apply modifications

#### Important Reminders
- **Irreversible Operation**: EXIF writing cannot be undone once completed, recommend backing up original files first
- **Format Compatibility**: Different formats have varying levels of EXIF support with compatibility differences
- **HEIC Support**: Requires additional decoder support (pillow-heif library)
- **Geographic Information**: Requires images to contain GPS data to retrieve and set location informationchanges





## Advanced Features



### Performance Optimization

- **Cache Mechanism**: Thumbnail and metadata caching
- **Batch Processing**: Process large image collections in batches
- **Concurrent Processing**: Use multi-threading to optimize IO-intensive tasks

## Troubleshooting

### Common Issues

1. **Module Import Error**
   - Ensure all dependencies are correctly installed: `pip install -r requirements.txt --upgrade`

2. **HEIC/HEIF Format Support**
   - Install pillow-heif library: `pip install pillow-heif --upgrade`



4. **High Memory Usage**
   - Reduce cache size or process images in batches

### Error Code Reference

| Error Code | Description | Solution |
|----------|------|----------|
| ERR-001 | File does not exist or cannot be accessed | Check file path and permissions |
| ERR-002 | Unsupported file format | Install the corresponding decoder library |
| ERR-003 | Insufficient memory | Reduce processing batch or increase memory |
| ERR-004 | Insufficient disk space | Clean up disk space |
| ERR-005 | Network connection failure | Check network settings |
| ERR-006 | Permission denied | Run with administrator privileges |
| ERR-007 | Missing dependency libraries | Reinstall dependency libraries |
| ERR-008 | Configuration file corrupted | Delete configuration file and regenerate |

## Community Support

### Contact Information

- **Author**: YangShengzhou03
- **GitHub**: [https://github.com/YangShengzhou03](https://github.com/YangShengzhou03)
- **Issue Feedback**: [GitHub Issues](https://github.com/YangShengzhou03/LeafSort/issues)
- **Discussion Area**: [GitHub Discussions](https://github.com/YangShengzhou03/LeafSort/discussions)

## License

```
MIT License

Copyright (c) 2024 YangShengzhou03

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Update Log

### v2.0.2 (2024-12-25)

#### New Features
- Initial version release
- Implemented basic image browsing and management functions
- Intelligent organization feature: supports multi-dimensional classification by time, device, etc.
- Deduplication feature: detects duplicate files based on MD5 hash algorithm
- EXIF editing feature: view and modify image metadata


#### Fixed Issues
- Fixed issue where HEIC/HEIF format images cannot be opened
- Fixed memory leak issue when processing large files
- Fixed race conditions in multi-threaded processing

#### Performance Optimization
- Optimized thumbnail generation and caching mechanism
- Improved large batch file processing performance
- Reduced memory usage and improved operational stability

<div align="center">
  <p>Built with Python and PyQt6</p>
</div>