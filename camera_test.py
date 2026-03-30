import cv2
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from camera_utils import open_camera, test_camera_frame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOGGER = logging.getLogger("camera_test")

def test_camera(camera_index=0):
    """Test camera and display feed"""
    try:
        cap, backend = open_camera(camera_index)
        if cap is None or not cap.isOpened():
            print(f"Error: Could not open camera with index {camera_index}")
            return False

        print(f"Camera {camera_index} opened successfully (backend: {backend})")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Could not read frame")
                break
                
            # Display frame info
            height, width = frame.shape[:2]
            cv2.putText(frame, f"Camera {camera_index} ({width}x{height})", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show frame
            cv2.imshow(f"Camera Test - Index {camera_index}", frame)
            
            # Exit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return True
        
    except Exception as e:
        LOGGER.exception("Camera stream test failed")
        print(f"Error: {str(e)}")
        return False

# GUI to test multiple cameras
def camera_tester_app():
    root = tk.Tk()
    root.title("Camera Tester")
    root.geometry("400x300")
    
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    tk.Label(frame, text="Camera Tester", font=("Arial", 16, "bold")).pack(pady=10)
    
    # Camera index selection
    selection_frame = tk.Frame(frame)
    selection_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(selection_frame, text="Camera Index:").pack(side=tk.LEFT, padx=5)
    
    camera_var = tk.StringVar(value="0")
    camera_combo = ttk.Combobox(selection_frame, textvariable=camera_var, width=5)
    camera_combo['values'] = ('0', '1', '2', '3')
    camera_combo.pack(side=tk.LEFT, padx=5)
    
    # Test button
    def start_test():
        try:
            camera_idx = int(camera_var.get())
            status_label.config(text=f"Testing camera {camera_idx}...")
            root.update()
            
            success = test_camera(camera_idx)
            
            if success:
                status_label.config(text=f"Camera {camera_idx} tested successfully")
            else:
                status_label.config(text=f"Failed to access camera {camera_idx}")
                
        except ValueError:
            status_label.config(text="Invalid camera index")
    
    tk.Button(frame, text="Test Camera", command=start_test).pack(pady=10)
    
    # Test all cameras button
    def test_all_cameras():
        found_cameras = []
        status_label.config(text="Testing all cameras...")
        root.update()
        
        for idx in range(4):  # Test camera indexes 0-3
            try:
                success, _, _ = test_camera_frame(idx)
                if success:
                    found_cameras.append(idx)
            except Exception:
                LOGGER.exception("Failed while probing camera index %s", idx)
        
        if found_cameras:
            status_label.config(text=f"Found working cameras at indexes: {found_cameras}")
        else:
            status_label.config(text="No working cameras found")
    
    tk.Button(frame, text="Find All Cameras", command=test_all_cameras).pack(pady=10)
    
    # Status
    status_frame = tk.LabelFrame(frame, text="Status")
    status_frame.pack(fill=tk.X, pady=10)
    
    status_label = tk.Label(status_frame, text="Ready to test cameras")
    status_label.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    camera_tester_app() 