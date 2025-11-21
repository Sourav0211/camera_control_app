# app.py

from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
from camera_manager import CameraManager, detect_cameras

app = Flask(__name__)

# Store camera objects
cameras = {}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/cameras')
def list_cameras():
    """List all available cameras"""
    available = detect_cameras()
    connected = list(cameras.keys())
    return jsonify({
        'available': available,
        'connected': connected
    })

@app.route('/api/camera/<int:camera_id>/connect', methods=['POST'])
def connect_camera(camera_id):
    """Connect to a specific camera"""
    if camera_id in cameras:
        return jsonify({'status': 'already_connected', 'camera_id': camera_id})
    
    cam = CameraManager(camera_id)
    if cam.initialize():
        cameras[camera_id] = cam
        return jsonify({'status': 'success', 'camera_id': camera_id})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to connect'}), 400

@app.route('/api/camera/<int:camera_id>/disconnect', methods=['POST'])
def disconnect_camera(camera_id):
    """Disconnect from a specific camera"""
    if camera_id in cameras:
        cameras[camera_id].release()
        del cameras[camera_id]
        return jsonify({'status': 'success', 'camera_id': camera_id})
    return jsonify({'status': 'error', 'message': 'Camera not connected'}), 400

@app.route('/api/camera/<int:camera_id>/settings')
def get_camera_settings(camera_id):
    """Get settings for a specific camera"""
    if camera_id not in cameras:
        return jsonify({'error': 'Camera not connected'}), 400
    
    settings = cameras[camera_id].get_settings()
    return jsonify(settings)

@app.route('/api/camera/<int:camera_id>/settings', methods=['POST'])
def update_camera_settings(camera_id):
    """Update settings for a specific camera"""
    if camera_id not in cameras:
        return jsonify({'error': 'Camera not connected'}), 400
    
    data = request.json
    setting_name = data.get('setting')
    value = data.get('value')
    
    if not setting_name or value is None:
        return jsonify({'error': 'Invalid parameters'}), 400
    
    success = cameras[camera_id].set_setting(setting_name, value)
    if success:
        return jsonify({'status': 'success', 'setting': setting_name, 'value': value})
    else:
        return jsonify({'error': 'Failed to set setting'}), 400

@app.route('/api/camera/<int:camera_id>/stream')
def video_feed(camera_id):
    """Video streaming route"""
    if camera_id not in cameras:
        return "Camera not connected", 400
    
    def generate():
        camera = cameras[camera_id]
        while camera_id in cameras:
            with camera.lock:
                frame = camera.get_frame()
                if frame is not None:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)