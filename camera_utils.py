import cv2
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOGGER = logging.getLogger("camera_utils")


def open_camera(camera_index, backends=None, width=640, height=480):
    """Open camera with fallback backends and return capture object."""
    if backends is None:
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY]

    for backend in backends:
        try:
            cap = cv2.VideoCapture(camera_index, backend)
            if not cap.isOpened():
                cap.release()
                continue

            ret, _ = cap.read()
            if not ret:
                cap.release()
                continue

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            return cap, backend
        except cv2.error as err:
            LOGGER.warning("OpenCV camera error for backend %s: %s", backend, err)
        except Exception as err:
            LOGGER.warning("Camera open error for backend %s: %s", backend, err)
    return None, None


def test_camera_frame(camera_index):
    """Return success flag and one frame if camera opens."""
    cap, backend = open_camera(camera_index)
    if cap is None:
        return False, None, None

    try:
        ret, frame = cap.read()
        if not ret:
            return False, None, backend
        return True, frame, backend
    finally:
        cap.release()
