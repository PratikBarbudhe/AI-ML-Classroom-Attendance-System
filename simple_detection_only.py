import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

class SimpleDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Face Detection")
        self.root.geometry("600x400")
        
        # Variables
        self.thread = None
        self.stop_threads = False
        self.is_detecting = False
        self.camera_index = 0  # Default camera index
        
        # Create GUI
        self.create_widgets()
        
        # Load face detector
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load face detector: {str(e)}")
            root.destroy()
    
    def create_widgets(self):
        # Control frame
        control_frame = tk.Frame(self.root, height=100)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(control_frame, text="Face Detection", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Camera settings
        camera_frame = tk.LabelFrame(self.root, text="Camera Settings")
        camera_frame.pack(fill=tk.X, padx=10, pady=10)
        
        camera_label = tk.Label(camera_frame, text="Camera Index:")
        camera_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.camera_var = tk.StringVar(value="0")
        camera_combobox = ttk.Combobox(camera_frame, textvariable=self.camera_var, width=5)
        camera_combobox['values'] = ('0', '1', '2', '3')
        camera_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.test_camera_button = tk.Button(camera_frame, text="Test Camera", command=self.test_camera)
        self.test_camera_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Detection buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.detect_button = tk.Button(button_frame, text="Start Detection", command=self.start_detection)
        self.detect_button.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=5, pady=5, expand=True, fill=tk.X)
    
    def test_camera(self):
        """Test if camera can be accessed"""
        try:
            camera_idx = int(self.camera_var.get())
            cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)  # Use DirectShow on Windows
            
            if not cap.isOpened():
                messagebox.showerror("Error", f"Could not open camera with index {camera_idx}")
                cap.release()
                return
            
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Error", f"Could not read frame from camera {camera_idx}")
            else:
                messagebox.showinfo("Success", f"Camera {camera_idx} is working correctly")
                
                # Show a single frame
                cv2.imshow('Camera Test', frame)
                cv2.waitKey(2000)  # Wait for 2 seconds
                cv2.destroyAllWindows()
            
            cap.release()
            
        except Exception as e:
            messagebox.showerror("Error", f"Camera test failed: {str(e)}")
    
    def start_detection(self):
        """Start face detection"""
        try:
            self.camera_index = int(self.camera_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid camera index. Please enter a number.")
            return
        
        self.is_detecting = True
        self.stop_threads = False
        
        # Update UI
        self.detect_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start detection in a thread
        self.thread = threading.Thread(target=self.detection_thread)
        self.thread.daemon = True
        self.thread.start()
    
    def detection_thread(self):
        """Thread function for face detection"""
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("Error", 
                            f"Could not open camera with index {self.camera_index}"))
            self.root.after(0, self.reset_ui)
            return
        
        try:
            while not self.stop_threads:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Draw rectangle around the detected faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, "Face", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Display info
                cv2.putText(frame, f"Found {len(faces)} faces", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Display the frame
                cv2.imshow('Face Detection', frame)
                
                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q') or self.stop_threads:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def stop_detection(self):
        """Stop face detection"""
        self.stop_threads = True
        cv2.destroyAllWindows()
        self.reset_ui()
    
    def reset_ui(self):
        """Reset the UI after processing"""
        self.is_detecting = False
        self.detect_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleDetectionApp(root)
    root.mainloop() 