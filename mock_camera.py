
import cv2
import numpy as np
import time
import sys

def generate_test_frame(frame_count, width=1280, height=720):
    """Generate a test frame with moving elements"""
    # Create a black background
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradient background
    for i in range(height):
        color_value = int((i / height) * 255)
        frame[i, :] = [color_value // 3, color_value // 2, color_value]
    
    # Add moving circle
    center_x = int(width // 2 + 200 * np.sin(frame_count * 0.05))
    center_y = int(height // 2 + 150 * np.cos(frame_count * 0.05))
    cv2.circle(frame, (center_x, center_y), 50, (0, 255, 0), -1)
    
    # Add text with frame counter
    cv2.putText(frame, f'Virtual Camera - Frame: {frame_count}', 
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Add timestamp
    timestamp = time.strftime('%H:%M:%S')
    cv2.putText(frame, timestamp, 
                (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    # Add some random noise for realism
    noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    frame = cv2.add(frame, noise)
    
    return frame

def main():
    # Virtual camera device (created by v4l2loopback)
    device = '/dev/video0'
    
    print(f"Starting mock camera feed to {device}")
    print("Press Ctrl+C to stop")
    
    try:
        # Open the virtual camera device
        cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
        
        # Set properties
        width, height = 1280, 720
        fps = 30
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        if not cap.isOpened():
            print(f"Error: Could not open {device}")
            print("Make sure v4l2loopback is loaded and you have permissions")
            sys.exit(1)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(device, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print(f"Error: Could not write to {device}")
            sys.exit(1)
        
        frame_count = 0
        
        while True:
            frame = generate_test_frame(frame_count, width, height)
            out.write(frame)
            
            frame_count += 1
            
            # Control frame rate
            time.sleep(1.0 / fps)
            
            if frame_count % 100 == 0:
                print(f"Frames sent: {frame_count}")
    
    except KeyboardInterrupt:
        print("\nStopping mock camera feed...")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if 'out' in locals():
            out.release()
        if 'cap' in locals():
            cap.release()
        print("Mock camera feed stopped")

if __name__ == '__main__':
    main()