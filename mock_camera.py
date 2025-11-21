import cv2
import numpy as np
import time
import sys

def generate_test_frame(frame_count, width=640, height=480):
    """Generate a test frame with moving elements"""
    # Create a black background
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Add gradient background
    for i in range(height):
        color_value = int((i / height) * 255)
        frame[i, :] = [color_value // 3, color_value // 2, color_value]
    
    # Add moving circle
    center_x = int(width // 2 + 150 * np.sin(frame_count * 0.05))
    center_y = int(height // 2 + 100 * np.cos(frame_count * 0.05))
    cv2.circle(frame, (center_x, center_y), 40, (0, 255, 0), -1)
    
    # Add text with frame counter
    cv2.putText(frame, f'Virtual Camera - Frame: {frame_count}', 
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Add timestamp
    timestamp = time.strftime('%H:%M:%S')
    cv2.putText(frame, timestamp, 
                (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    return frame

def main():
    device = '/dev/video0'
    width, height = 640, 480
    fps = 30
    
    print(f"Starting mock camera feed to {device}")
    print("Press Ctrl+C to stop")
    
    try:
        # Open video writer directly
        fourcc = cv2.VideoWriter_fourcc(*'YUY2')  # Use YUY2 format
        out = cv2.VideoWriter(device, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print(f"Error: Could not write to {device}")
            print("Make sure v4l2loopback is loaded with: sudo modprobe v4l2loopback")
            sys.exit(1)
        
        print("Mock camera started successfully!")
        frame_count = 0
        
        while True:
            frame = generate_test_frame(frame_count, width, height)
            out.write(frame)
            
            frame_count += 1
            
            if frame_count % 100 == 0:
                print(f"Frames sent: {frame_count}")
            
            time.sleep(1.0 / fps)
    
    except KeyboardInterrupt:
        print("\nStopping mock camera feed...")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'out' in locals():
            out.release()
        print("Mock camera feed stopped")

if __name__ == '__main__':
    main()