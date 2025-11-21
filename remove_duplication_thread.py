import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

import numpy as np
import pillow_heif
from PIL import Image
from PyQt6 import QtCore
from PyQt6.QtCore import QThread, pyqtSignal
