import cv2
import numpy as np
import threading
import time
from datetime import datetime

class MockCameraController:
    def __init__(self, device_index=0):
        self.device_index = device_index
        self.frame = None
        self.lock = threading.Lock()
        self.is_running = False
        self.thread = None
        self.width = 640
        self.height = 480

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._generate_frames, daemon=True)
        self.thread.start()

    def _generate_frames(self):
        while self.is_running:
            # Create a fake RGB image
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # Fill with a color (blue-ish)
            frame[:] = (60, 60, 180)

            # Add timestamp text
            text = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            cv2.putText(frame, f"Mock Camera {self.device_index}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, text, (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            with self.lock:
                self.frame = frame

            time.sleep(1 / 30)  # simulate 30 FPS

    def get_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def set_property(self, prop, value):
        # For mock: update resolution if needed
        if prop == "width":
            self.width = int(value)
        elif prop == "height":
            self.height = int(value)

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
        self.frame = None
