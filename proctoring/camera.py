import threading
import time
import cv2
import logging


logger = logging.getLogger(__name__)


class CameraManager:
    """
    Centralized webcam manager.

    Only ONE OpenCV VideoCapture instance is created.

    A background thread continuously captures frames.
    Other parts of the application use the latest frame
    instead of opening/reading the webcam independently.
    """

    def __init__(self, camera_index=0):
        self.camera_index = camera_index

        self.capture = None

        self.latest_frame = None

        self.lock = threading.Lock()

        self.running = False
        self.thread = None

    # =========================================================
    # START CAMERA
    # =========================================================

    def start(self):
        """
        Start the webcam capture thread.
        """

        if self.running and self.thread and self.thread.is_alive():
            return True

        logger.info("[CAMERA] Starting camera...")

        self.capture = cv2.VideoCapture(self.camera_index)

        if not self.capture.isOpened():
            logger.error(
                "[CAMERA] Unable to open webcam."
            )

            self.capture.release()
            self.capture = None

            return False

        # Optional camera settings.
        # These help some webcams initialize more reliably.

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            640
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            480
        )

        self.capture.set(
            cv2.CAP_PROP_FPS,
            30
        )

        self.running = True

        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )

        self.thread.start()

        logger.info(
            "[CAMERA] Camera opened successfully."
        )

        return True

    # =========================================================
    # CAPTURE LOOP
    # =========================================================

    def _capture_loop(self):
        """
        Continuously capture frames in the background.
        """

        logger.info(
            "[CAMERA] Capture thread started."
        )

        while self.running:

            if self.capture is None:
                time.sleep(0.2)
                continue

            success, frame = self.capture.read()

            if not success:

                logger.warning(
                    "[CAMERA] Failed to capture frame."
                )

                time.sleep(0.1)

                continue

            with self.lock:

                self.latest_frame = frame

    # =========================================================
    # GET LATEST FRAME
    # =========================================================

    def get_frame(self):
        """
        Return the most recently captured frame.
        """

        if not self.running:

            if not self.start():

                return None

        with self.lock:

            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

    # =========================================================
    # CAMERA STATUS
    # =========================================================

    def is_available(self):

        if not self.running:
            return False

        if self.capture is None:
            return False

        return self.capture.isOpened()

    # =========================================================
    # MJPEG VIDEO STREAM
    # =========================================================

    def frames(self):
        """
        Stream the latest camera frames as MJPEG.
        """

        if not self.start():

            logger.error(
                "[CAMERA] Cannot start video stream."
            )

            return

        logger.info(
            "[CAMERA] Video stream connected."
        )

        while self.running:

            frame = self.get_frame()

            if frame is None:

                time.sleep(0.05)

                continue

            success, buffer = cv2.imencode(
                ".jpg",
                frame
            )

            if not success:

                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )

            # Prevent unnecessary CPU usage.

            time.sleep(0.03)

    # =========================================================
    # STOP CAMERA
    # =========================================================

    def stop(self):

        logger.info(
            "[CAMERA] Stopping camera..."
        )

        self.running = False

        if self.thread and self.thread.is_alive():

            self.thread.join(
                timeout=1
            )

        self.thread = None

        if self.capture is not None:

            self.capture.release()

            self.capture = None

        with self.lock:

            self.latest_frame = None

        logger.info(
            "[CAMERA] Camera stopped."
        )


# =============================================================
# GLOBAL CAMERA MANAGER
# =============================================================

camera_manager = CameraManager()