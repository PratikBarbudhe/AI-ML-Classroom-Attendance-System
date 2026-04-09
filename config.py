"""
Configuration module for AI Classroom Attendance System.
Centralizes all settings, constants, and configuration values.
"""

import os
from pathlib import Path
import cv2

# ============================================================================
# Directory Paths
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
FACES_DIR = DATA_DIR / "faces"
MODELS_DIR = DATA_DIR / "models"
ATTENDANCE_DIR = DATA_DIR / "attendance"
EXPORTS_DIR = ATTENDANCE_DIR / "exports"
STUDENTS_CSV = DATA_DIR / "students.csv"
ATTENDANCE_DB = ATTENDANCE_DIR / "attendance.db"

# Create all directories on import
for directory in [DATA_DIR, FACES_DIR, MODELS_DIR, ATTENDANCE_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Camera Settings
# ============================================================================
DEFAULT_CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
CAMERA_TIMEOUT = 5  # seconds

# ============================================================================
# Face Recognition Settings
# ============================================================================
# Number of samples needed per person during capture
FACE_SAMPLES_REQUIRED = 30

# Minimum confidence threshold for face detection
FACE_DETECTION_CONFIDENCE = 0.4

# Tolerance for face matching (lower = stricter matching)
FACE_MATCH_TOLERANCE = 0.6

# Number of times to upsample the image for faster face detection
FACE_DETECTION_UPSAMPLE = 1

# Model path for LBPH (Local Binary Patterns Histograms)
LBPH_MODEL_PATH = MODELS_DIR / "lbph_model.xml"

# Model path for face encodings (dlib/face_recognition)
FACE_ENCODING_MODEL_PATH = MODELS_DIR / "face_model.pkl"

# ============================================================================
# Attendance Logging Settings
# ============================================================================
# Minimum seconds between marking same person as present again (deduplication)
ATTENDANCE_MIN_INTERVAL = 60  # seconds

# Auto-capture interval for face detection
AUTO_CAPTURE_INTERVAL = 0.5  # seconds

# Default source for attendance marking
ATTENDANCE_SOURCE = "webcam"

# ============================================================================
# GUI Settings
# ============================================================================
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "AI Classroom Attendance System"

# Display settings
IMAGE_DISPLAY_WIDTH = 400
IMAGE_DISPLAY_HEIGHT = 300
DISPLAY_FPS = 30

# Font settings
FONT_FAMILY = "Arial"
FONT_SIZE_TITLE = 24
FONT_SIZE_NORMAL = 10
FONT_SIZE_SMALL = 8

# ============================================================================
# Logging Settings
# ============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_FILE = PROJECT_ROOT / "logs" / "attendance_system.log"

# Create logs directory
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Face Detection (OpenCV Cascade Classifiers)
# ============================================================================
FACE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
EYE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_eye.xml'

# ============================================================================
# Performance Optimization Settings (NEW)
# ============================================================================
# Dashboard polling interval (milliseconds)
DASHBOARD_UPDATE_INTERVAL = 5000  # 5 seconds

# Cache settings
CACHE_ENABLED = True
CACHE_EXPIRY_SECONDS = 600  # 10 minutes
IMAGE_CACHE_MAX_MB = 500    # Max memory for image cache
BATCH_IMAGE_LOAD = True     # Load images in batches

# Smart polling settings
SMART_POLLING_ENABLED = True
IDLE_TIMEOUT_SECONDS = 300  # 5 minutes
MAX_POLLING_INTERVAL = 30000  # 30 seconds when idle
MIN_POLLING_INTERVAL = 2000   # 2 seconds minimum

# Memory management
ENABLE_GARBAGE_COLLECTION = True
WEAK_REFERENCES_FOR_CACHE = True

# ============================================================================
# Export Settings
# ============================================================================
EXPORT_DATE_FORMAT = "%Y-%m-%d"
EXPORT_TIME_FORMAT = "%H:%M:%S"
EXPORT_CSV_COLUMNS = ["Name", "Time", "Confidence", "Source"]

# ============================================================================
# Validation Settings
# ============================================================================
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100
VALID_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}

# ============================================================================
# Performance Settings
# ============================================================================
# Process every Nth frame for faster detection (1 = every frame, 2 = every 2nd frame)
FRAME_SKIP = 1

# Maximum number of faces to process per frame
MAX_FACES_PER_FRAME = 10

# ============================================================================
# Error Messages
# ============================================================================
ERROR_MESSAGES = {
    'camera_not_found': 'Error: Could not open camera. Check if camera is available and permissions are granted.',
    'invalid_name': 'Invalid person name. Must be 2-100 characters.',
    'no_faces_detected': 'No faces detected. Please adjust lighting and try again.',
    'insufficient_samples': 'Insufficient face samples captured. More samples needed for accurate training.',
    'model_not_trained': 'Model not trained yet. Please capture samples and train first.',
    'invalid_image_path': 'Invalid image file path or file does not exist.',
    'no_faces_in_image': 'No faces detected in the selected image.',
}

# ============================================================================
# Success Messages
# ============================================================================
SUCCESS_MESSAGES = {
    'capture_complete': 'Successfully captured {} samples for {}',
    'model_trained': 'Model trained successfully with {} face samples from {} people',
    'recognition_started': 'Face recognition started',
    'recognition_stopped': 'Face recognition stopped',
    'attendance_marked': 'Attendance marked for {}',
    'export_complete': 'Attendance exported to {}',
}

# Import cv2 for cascade paths
try:
    import cv2
except ImportError:
    pass
