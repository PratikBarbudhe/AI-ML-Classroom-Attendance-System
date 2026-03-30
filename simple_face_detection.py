import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageTk
import threading
import logging
from camera_utils import open_camera, test_camera_frame

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOGGER = logging.getLogger("simple_face_detection")

class SimpleFaceDetection:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Face Detection System")
        self.root.geometry("800x600")
        
        # Variables
        self.detection_thread = None
        self.stop_threads = False
        self.is_detecting = False
        self.camera_index = 0  # Default camera index
        
        # Create GUI
        self.create_widgets()
        
        # Load the pre-trained face detector from OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def create_widgets(self):
        # Create main frames
        self.top_frame = tk.Frame(self.root, height=100)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.control_frame = tk.Frame(self.root, height=150)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(self.top_frame, text="Simple Face Detection", font=("Arial", 24, "bold"))
        title_label.pack(pady=10)
        
        # Image display
        self.image_label = tk.Label(self.main_frame, bg="black")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        self.source_var = tk.StringVar(value="webcam")
        self.webcam_radio = tk.Radiobutton(self.control_frame, text="Webcam", variable=self.source_var, value="webcam")
        self.webcam_radio.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Camera index selection
        camera_frame = tk.Frame(self.control_frame)
        camera_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        camera_label = tk.Label(camera_frame, text="Camera:")
        camera_label.pack(side=tk.LEFT)
        
        self.camera_var = tk.StringVar(value="0")
        camera_combobox = ttk.Combobox(camera_frame, textvariable=self.camera_var, width=5)
        camera_combobox['values'] = ('0', '1', '2', '3')
        camera_combobox.pack(side=tk.LEFT, padx=5)
        
        self.image_radio = tk.Radiobutton(self.control_frame, text="Image", variable=self.source_var, value="image")
        self.image_radio.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.browse_button = tk.Button(self.control_frame, text="Browse Image", command=self.browse_image)
        self.browse_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.image_path = None
        
        self.detect_button = tk.Button(self.control_frame, text="Start Detection", command=self.start_detection)
        self.detect_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Test Camera button
        self.test_camera_button = tk.Button(self.control_frame, text="Test Camera", command=self.test_camera)
        self.test_camera_button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def browse_image(self):
        """Browse for an image file for face detection"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            messagebox.showinfo("Image Selected", f"Selected image: {os.path.basename(file_path)}")
    
    def test_camera(self):
        """Test if camera can be accessed"""
        try:
            camera_idx = int(self.camera_var.get())
            success, frame, backend = test_camera_frame(camera_idx)
            if not success or frame is None:
                messagebox.showerror("Error", f"Could not open camera with index {camera_idx}")
                return
            messagebox.showinfo("Success", f"Camera {camera_idx} is working correctly (backend: {backend})")
            cv2.imshow('Camera Test', frame)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()
            
        except Exception as e:
            LOGGER.exception("Camera test failed")
            messagebox.showerror("Error", f"Camera test failed: {str(e)}")
    
    def start_detection(self):
        """Start face detection process"""
        source = self.source_var.get()
        
        if source == "image" and not self.image_path:
            messagebox.showerror("Error", "Please select an image file")
            return
        
        if source == "webcam":
            try:
                self.camera_index = int(self.camera_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid camera index. Please enter a number.")
                return
        
        self.is_detecting = True
        self.stop_threads = False
        self.detect_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start detection in a thread
        self.detection_thread = threading.Thread(
            target=self.detection_thread_func,
            args=(source,)
        )
        self.detection_thread.daemon = True
        self.detection_thread.start()
    
    def detection_thread_func(self, source):
        """Thread function for face detection"""
        try:
            if source == "webcam":
                self.detect_faces_webcam()
            else:
                self.detect_faces_image(self.image_path)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def detect_faces_webcam(self):
        """Detect faces from webcam feed"""
        cap, _ = open_camera(self.camera_index)
        
        if not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("Error", f"Could not open camera with index {self.camera_index}"))
            self.root.after(0, self.reset_ui)
            return
        
        try:
            while not self.stop_threads:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Draw rectangle around the faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Display info
                cv2.putText(frame, f"Detected: {len(faces)} faces", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Display the resulting frame
                cv2.imshow('Face Detection', frame)
                
                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q') or self.stop_threads:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            LOGGER.exception("Webcam detection failed")
            cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def detect_faces_image(self, image_path):
        """Detect faces in a static image"""
        try:
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                self.root.after(0, lambda: messagebox.showerror("Error", "Could not read image"))
                self.root.after(0, self.reset_ui)
                return
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            # Draw rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add text with info
            cv2.putText(image, f"Detected: {len(faces)} faces", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display the resulting image
            cv2.imshow('Face Detection', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            cv2.destroyAllWindows()
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        """Reset the UI after processing"""
        self.is_detecting = False
        self.detect_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def stop_processing(self):
        """Stop any ongoing detection process"""
        self.stop_threads = True
        
        # Force stop OpenCV windows
        cv2.destroyAllWindows()
        
        messagebox.showinfo("Stopped", "Detection has been stopped")
        self.reset_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleFaceDetection(root)
    root.mainloop() 