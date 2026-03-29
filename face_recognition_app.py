import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
from face_utils import FaceUtils
import threading
import time

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize face utils
        self.face_utils = FaceUtils()
        
        # Variables
        self.capture_thread = None
        self.recognition_thread = None
        self.stop_threads = False
        self.is_capturing = False
        self.is_recognizing = False
        
        # Create GUI
        self.create_widgets()
        
        # Load model status
        self.check_model_status()
    
    def create_widgets(self):
        # Create main frames
        self.top_frame = tk.Frame(self.root, height=100)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.control_frame = tk.Frame(self.root, height=150)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(self.top_frame, text="Face Recognition System", font=("Arial", 24, "bold"))
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = tk.LabelFrame(self.top_frame, text="Model Status")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Checking model status...", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Image display
        self.image_label = tk.Label(self.main_frame, bg="black")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        self.capture_frame = tk.LabelFrame(self.control_frame, text="Capture Samples")
        self.capture_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.person_label = tk.Label(self.capture_frame, text="Person Name:")
        self.person_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.person_entry = tk.Entry(self.capture_frame, width=20)
        self.person_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.source_label = tk.Label(self.capture_frame, text="Source:")
        self.source_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.source_var = tk.StringVar(value="webcam")
        self.webcam_radio = tk.Radiobutton(self.capture_frame, text="Webcam", variable=self.source_var, value="webcam")
        self.webcam_radio.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.image_radio = tk.Radiobutton(self.capture_frame, text="Image", variable=self.source_var, value="image")
        self.image_radio.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.browse_button = tk.Button(self.capture_frame, text="Browse Image", command=self.browse_image)
        self.browse_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        self.image_path = None
        
        self.capture_button = tk.Button(self.capture_frame, text="Capture Samples", command=self.start_capture)
        self.capture_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Training and recognition
        self.train_frame = tk.LabelFrame(self.control_frame, text="Model Training & Recognition")
        self.train_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.train_button = tk.Button(self.train_frame, text="Train Model", command=self.train_model)
        self.train_button.pack(fill=tk.X, padx=5, pady=5)
        
        self.recognition_frame = tk.Frame(self.train_frame)
        self.recognition_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.recog_source_label = tk.Label(self.recognition_frame, text="Source:")
        self.recog_source_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.recog_source_var = tk.StringVar(value="webcam")
        self.recog_webcam_radio = tk.Radiobutton(self.recognition_frame, text="Webcam", 
                                                variable=self.recog_source_var, value="webcam")
        self.recog_webcam_radio.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.recog_image_radio = tk.Radiobutton(self.recognition_frame, text="Image", 
                                               variable=self.recog_source_var, value="image")
        self.recog_image_radio.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.recog_browse_button = tk.Button(self.recognition_frame, text="Browse Image", 
                                            command=self.browse_recognition_image)
        self.recog_browse_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        self.recognition_image_path = None
        
        self.recognition_button = tk.Button(self.train_frame, text="Start Recognition", 
                                           command=self.start_recognition)
        self.recognition_button.pack(fill=tk.X, padx=5, pady=5)
        
        self.stop_button = tk.Button(self.train_frame, text="Stop", command=self.stop_processing,
                                    state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, padx=5, pady=5)
    
    def check_model_status(self):
        """Check if a trained model exists and update status"""
        success, message = self.face_utils.load_model()
        if success:
            self.status_label.config(text=message)
        else:
            self.status_label.config(text="No trained model found. Please capture samples and train the model.")
    
    def browse_image(self):
        """Browse for an image file for face sample capture"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.image_path = file_path
            messagebox.showinfo("Image Selected", f"Selected image: {os.path.basename(file_path)}")
    
    def browse_recognition_image(self):
        """Browse for an image file for face recognition"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.recognition_image_path = file_path
            messagebox.showinfo("Image Selected", f"Selected image: {os.path.basename(file_path)}")
    
    def start_capture(self):
        """Start face sample capture process"""
        person_name = self.person_entry.get().strip()
        source = self.source_var.get()
        
        if not person_name:
            messagebox.showerror("Error", "Please enter a person name")
            return
        
        if source == "image" and not self.image_path:
            messagebox.showerror("Error", "Please select an image file")
            return
        
        self.is_capturing = True
        self.stop_threads = False
        self.capture_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start capture in a thread
        self.capture_thread = threading.Thread(
            target=self.capture_samples_thread,
            args=(person_name, source)
        )
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def capture_samples_thread(self, person_name, source):
        """Thread function for face sample capture"""
        try:
            if source == "webcam":
                success, message = self.face_utils.capture_face_samples(person_name, source)
            else:
                success, message = self.face_utils.capture_face_samples(person_name, source, image_path=self.image_path)
            
            # Update UI from main thread
            self.root.after(0, lambda: self.handle_capture_result(success, message))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_capture_ui)
    
    def handle_capture_result(self, success, message):
        """Handle the result of face sample capture"""
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
        
        self.reset_capture_ui()
    
    def reset_capture_ui(self):
        """Reset the UI after face sample capture"""
        self.is_capturing = False
        self.capture_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED if not self.is_recognizing else tk.NORMAL)
    
    def train_model(self):
        """Train face recognition model"""
        # Disable buttons during training
        self.train_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.DISABLED)
        self.recognition_button.config(state=tk.DISABLED)
        
        # Show progress
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Training Model")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(progress_window, text="Training model, please wait...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()
        
        # Start training in a thread
        def training_thread():
            try:
                success, message = self.face_utils.train_model()
                
                # Update UI from main thread
                self.root.after(0, lambda: self.handle_training_result(success, message, progress_window))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
                self.root.after(0, lambda: progress_window.destroy())
                self.root.after(0, self.reset_training_ui)
        
        threading.Thread(target=training_thread, daemon=True).start()
    
    def handle_training_result(self, success, message, progress_window):
        """Handle the result of model training"""
        progress_window.destroy()
        
        if success:
            messagebox.showinfo("Success", message)
            self.check_model_status()
        else:
            messagebox.showerror("Error", message)
        
        self.reset_training_ui()
    
    def reset_training_ui(self):
        """Reset the UI after model training"""
        self.train_button.config(state=tk.NORMAL)
        self.capture_button.config(state=tk.NORMAL)
        self.recognition_button.config(state=tk.NORMAL)
    
    def start_recognition(self):
        """Start face recognition process"""
        source = self.recog_source_var.get()
        
        if source == "image" and not self.recognition_image_path:
            messagebox.showerror("Error", "Please select an image file")
            return
        
        if not self.face_utils.model_trained:
            messagebox.showerror("Error", "No trained model available. Please train the model first.")
            return
        
        self.is_recognizing = True
        self.stop_threads = False
        self.recognition_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.DISABLED)
        self.train_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start recognition in a thread
        self.recognition_thread = threading.Thread(
            target=self.recognition_thread_func,
            args=(source,)
        )
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
    
    def recognition_thread_func(self, source):
        """Thread function for face recognition"""
        try:
            if source == "webcam":
                success, message = self.face_utils.recognize_faces(source)
            else:
                success, message = self.face_utils.recognize_faces(source, image_path=self.recognition_image_path)
            
            # Update UI from main thread
            self.root.after(0, lambda: self.handle_recognition_result(success, message))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_recognition_ui)
    
    def handle_recognition_result(self, success, message):
        """Handle the result of face recognition"""
        if not success:
            messagebox.showerror("Error", message)
        
        self.reset_recognition_ui()
    
    def reset_recognition_ui(self):
        """Reset the UI after face recognition"""
        self.is_recognizing = False
        self.recognition_button.config(state=tk.NORMAL)
        self.capture_button.config(state=tk.NORMAL)
        self.train_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED if not self.is_capturing else tk.NORMAL)
    
    def stop_processing(self):
        """Stop any ongoing capture or recognition process"""
        self.stop_threads = True
        
        # Force stop OpenCV windows
        cv2.destroyAllWindows()
        
        messagebox.showinfo("Stopped", "Processing has been stopped")
        
        self.reset_capture_ui()
        self.reset_recognition_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop() 