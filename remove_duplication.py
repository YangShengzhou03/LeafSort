import os
import shutil

import pillow_heif
import send2trash
from PIL import Image
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, QRunnable, QObject, Qt, QThreadPool
from PyQt6.QtGui import QPixmap, QImage

from remove_duplication_thread import HashWorker, ContrastWorker
