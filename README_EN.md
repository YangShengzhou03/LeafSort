<div align="center">
  <h1>🍁 LeafSort - Maple Leaf Photo Gallery</h1>
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

## 📋 Project Introduction

LeafSort is a powerful image management tool focused on efficiently managing, intelligently organizing, and batch processing various image files.

### ✨ Core Features

- **Efficient Image Management**: Supports multiple image formats, quick browsing and management of large numbers of images
- **Intelligent Organization**: Automatically classify and organize images by time, location, device, and other dimensions
- **Duplicate Detection**: Intelligently identify similar images based on perceptual hash algorithms
- **EXIF Editing**: View and modify image metadata information
- **OCR Text Recognition**: Extract text content from images
- **Batch Processing**: Supports batch renaming, format conversion, applying filters, and other operations

## 🛠️ Technical Architecture

### Tech Stack

- **Programming Language**: Python 3.11+
- **GUI Framework**: PyQt6 6.5.0+
- **Image Processing**: Pillow 11.3.0+
- **OCR Engine**: Tesseract OCR 5.3.0+
- **Metadata Processing**: piexif, exiftool
- **Other Dependencies**: numpy, scikit-image, opencv-python

### Architecture Design

LeafSort adopts a three-tier architecture design to ensure code maintainability and scalability:

1. **User Interface Layer**: Modern GUI interface built on PyQt6
2. **Business Logic Layer**: Handles core business logic and feature implementation
3. **Data Processing Layer**: Responsible for file operations, metadata processing, and database interactions

## 📁 Project Structure

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
├── _internal/               # Internal configuration directory
│   ├── cache_location.json  # Cache location configuration
│   └── config.json          # Main configuration file
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

## 🚀 Installation and Deployment

### Environment Requirements

- Python 3.11 or higher
- Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)
- Tesseract OCR (for text recognition functionality)

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

## 💡 User Guide

### Basic Operations

1. **Import Images**: Import images through the "File" menu or by dragging and dropping
2. **Browse Images**: Use mouse wheel, arrow keys, or thumbnail list to browse
3. **View Details**: Click the "Details" button to view image metadata
4. **Batch Processing**: Select multiple images and use the right-click menu for batch operations

### Intelligent Organization

The intelligent organization feature supports the following classification methods:

- **By Time**: Year/Month/Day hierarchical structure
- **By Location**: Automatic classification based on GPS information
- **By Device**: Classification by camera model, phone brand
- **By Type**: Classification by image format or content type
- **Custom Rules**: Supports custom organization rules based on regular expressions

Operation steps:
1. Select the images you want to organize
2. Click the "Intelligent Organization" button
3. Choose the organization method and target location
4. Click "Start Organization" to execute the operation

### Duplicate Detection

1. Select the folder or image set you want to deduplicate
2. Click the "Find Duplicates" button
3. Set the similarity threshold (0-100%)
4. View duplicate results and choose to keep or delete

### EXIF Editing

1. Select the image you want to edit
2. Click the "Edit EXIF" button
3. Modify the metadata you want to update (such as title, author, rating, etc.)
4. Click "Save" to apply the changes

### Text Recognition

1. Select the image containing text
2. Click the "OCR Recognition" button
3. Select the recognition language (multilingual support)
4. Wait for recognition to complete, view or copy the recognition results



## ⚙️ Advanced Features



### Cloud Storage Integration

Supports integration with cloud storage services such as AWS S3, Alibaba Cloud OSS, etc., for convenient image backup and synchronization.

### Performance Optimization

- **Cache Mechanism**: Thumbnail and metadata caching
- **Batch Processing**: Process large image collections in batches
- **Concurrent Processing**: Use multi-threading to optimize IO-intensive tasks

## 🆘 Troubleshooting

### Common Issues

1. **Module Import Error**
   - Ensure all dependencies are correctly installed: `pip install -r requirements.txt --upgrade`

2. **HEIC/HEIF Format Support**
   - Install pillow-heif library: `pip install pillow-heif --upgrade`

3. **OCR Function Cannot Be Used**
   - Ensure Tesseract OCR is correctly installed and added to system PATH

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

## 🤝 Community Support

### Contact Information

- **Author**: YangShengzhou03
- **GitHub**: [https://github.com/YangShengzhou03](https://github.com/YangShengzhou03)
- **Issue Feedback**: [GitHub Issues](https://github.com/YangShengzhou03/LeafSort/issues)
- **Discussion Area**: [GitHub Discussions](https://github.com/YangShengzhou03/LeafSort/discussions)

## 📄 License

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

## 🔄 Update Log

### v1.0.0 (2024-XX-XX)

#### ✨ New Features
- Initial version release
- Implemented basic image browsing and management functions
- Intelligent organization feature: supports multi-dimensional classification by time, device, etc.
- Deduplication feature: detects duplicate images based on perceptual hash algorithm
- EXIF editing feature: view and modify image metadata
- Text recognition feature: based on Tesseract OCR engine

#### 🐛 Fixed Issues
- Fixed issue where HEIC/HEIF format images cannot be opened
- Fixed memory leak issue when processing large files
- Fixed race conditions in multi-threaded processing

#### 🚀 Performance Optimization
- Optimized thumbnail generation and caching mechanism
- Improved large batch file processing performance
- Reduced memory usage and improved operational stability

<div align="center">
  <p>Built with ❤️ using Python and PyQt6</p>
</div>