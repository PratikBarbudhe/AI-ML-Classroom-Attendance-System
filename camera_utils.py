"""
Camera utilities for face detection and recognition.
Handles camera initialization, frame capture, and fallback strategies.
"""

import cv2
import logging
import config

logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT
)
LOGGER = logging.getLogger(__name__)


def open_camera(camera_index, backends=None, width=None, height=None):
    """
    Open camera with fallback backends and return capture object.
    
    Args:
        camera_index: Camera device index
        backends: List of OpenCV backends to try (uses defaults if None)
        width: Frame width (uses config default if None)
        height: Frame height (uses config default if None)
    
    Returns:
        tuple: (VideoCapture object or None, backend used)
    """
    if backends is None:
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY]
    
    if width is None:
        width = config.CAMERA_WIDTH
    
    if height is None:
        height = config.CAMERA_HEIGHT

    for backend in backends:
        try:
            cap = cv2.VideoCapture(camera_index, backend)
            
            if not cap.isOpened():
                cap.release()
                LOGGER.debug(f"Camera not opened with backend {backend}")
                continue

            # Try to read a frame to verify camera works
            ret, _ = cap.read()
            if not ret:
                cap.release()
                LOGGER.debug(f"Cannot read frame with backend {backend}")
                continue

            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
            
            LOGGER.info(f"Camera opened successfully with backend {backend} (index {camera_index})")
            return cap, backend
            
        except cv2.error as err:
            LOGGER.warning(f"OpenCV error for backend {backend}: {err}")
        except Exception as err:
            LOGGER.warning(f"Camera open error for backend {backend}: {err}")
    
    LOGGER.error(f"Failed to open camera at index {camera_index} with any backend")
    return None, None


def test_camera_frame(camera_index):
    """
    Test if camera works by trying to capture one frame.
    
    Args:
        camera_index: Camera device index
    
    Returns:
        tuple: (success, frame, backend)
    """
    try:
        cap, backend = open_camera(camera_index)
        
        if cap is None:
            LOGGER.error(f"Cannot open camera at index {camera_index}")
            return False, None, None

        try:
            ret, frame = cap.read()
            
            if not ret:
                LOGGER.error(f"Cannot read frame from camera at index {camera_index}")
                return False, None, backend
            
            LOGGER.info(f"Successfully captured test frame from camera {camera_index}")
            return True, frame, backend
            
        finally:
            cap.release()
    
    except Exception as e:
        LOGGER.error(f"Error testing camera: {e}")
        return False, None, None


def get_available_cameras(max_index=5):
    """
    Scan for available camera devices.
    
    Args:
        max_index: Maximum camera index to check
    
    Returns:
        list: Indices of available cameras
    """
    available = []
    
    for i in range(max_index):
        success, _, _ = test_camera_frame(i)
        if success:
            available.append(i)
    
    LOGGER.info(f"Found {len(available)} available camera(s): {available}")
    return available
