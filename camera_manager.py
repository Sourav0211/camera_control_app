# camera_manager.py
import cv2
import threading

class CameraManager:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.cap = None
        self.is_active = False
        self.lock = threading.Lock()
        
    def initialize(self):
        """Initialize camera connection"""
        try:
            # Try V4L2 for Linux, fall back to default for macOS
            import platform
            if platform.system() == 'Linux':
                self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2)
            else:
                # macOS and other systems use default backend
                self.cap = cv2.VideoCapture(self.camera_id)
            
            if self.cap.isOpened():
                self.is_active = True
                return True
            return False
        except Exception as e:
            print(f"Error initializing camera {self.camera_id}: {e}")
            return False
    
    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
            self.is_active = False
    
    def get_frame(self):
        """Capture a single frame"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def get_settings(self):
        """Get current camera settings"""
        if not self.cap or not self.cap.isOpened():
            return {}
        
        settings = {
            'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
            'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST),
            'saturation': self.cap.get(cv2.CAP_PROP_SATURATION),
            'hue': self.cap.get(cv2.CAP_PROP_HUE),
            'exposure': self.cap.get(cv2.CAP_PROP_EXPOSURE),
            'gain': self.cap.get(cv2.CAP_PROP_GAIN),
            'width': self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),
            'height': self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
            'fps': self.cap.get(cv2.CAP_PROP_FPS)
        }
        return settings
    
    def set_setting(self, setting_name, value):
        """Set a specific camera setting"""
        if not self.cap or not self.cap.isOpened():
            return False
        
        setting_map = {
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION,
            'hue': cv2.CAP_PROP_HUE,
            'exposure': cv2.CAP_PROP_EXPOSURE,
            'gain': cv2.CAP_PROP_GAIN,
            'width': cv2.CAP_PROP_FRAME_WIDTH,
            'height': cv2.CAP_PROP_FRAME_HEIGHT,
            'fps': cv2.CAP_PROP_FPS
        }
        
        if setting_name in setting_map:
            return self.cap.set(setting_map[setting_name], float(value))
        return False


def detect_cameras(max_cameras=10):
    """Detect available cameras on the system"""
    import platform
    available_cameras = []
    
    for i in range(max_cameras):
        if platform.system() == 'Linux':
            cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
        else:
            cap = cv2.VideoCapture(i)
            
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
        else:
            # On macOS, cameras might not be sequential, so check a few more
            if platform.system() != 'Linux' and i < 3:
                continue
            break
    return available_cameras