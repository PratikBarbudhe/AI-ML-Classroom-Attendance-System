import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageTk
import threading
import pickle
import time

class FaceRecognitionAppSimplified:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition System")
        self.root.geometry("800x600")
        
        # Variables
        self.thread = None
        self.stop_threads = False
        self.is_processing = False
        self.camera_index = 0  # Default camera index
        self.sample_count = 0
        self.max_samples = 10
        self.current_person = ""
        self.model_trained = False  # Initialize this before loading model
        self.name_dict = {}
        self.auto_capture = False   # For auto capture mode
        self.auto_capture_interval = 1.0  # Seconds between auto captures
        self.last_capture_time = 0
        
        # Data paths
        self.data_dir = "data"
        self.faces_dir = os.path.join(self.data_dir, "faces")
        self.model_path = os.path.join(self.data_dir, "models", "face_model.pkl")
        
        # Create directories if they don't exist
        os.makedirs(self.faces_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "models"), exist_ok=True)
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Face recognition
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.load_model()
            # Create GUI
            self.create_widgets()
        except AttributeError:
            messagebox.showerror("Error", "OpenCV contrib modules not installed. Please run: pip install opencv-contrib-python")
            root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            root.destroy()
        
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
        
        # Control frames
        left_control = tk.Frame(self.control_frame)
        left_control.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=5)
        
        right_control = tk.Frame(self.control_frame)
        right_control.pack(side=tk.RIGHT, fill=tk.Y, expand=True, padx=5)
        
        # Left side - Camera settings
        camera_frame = tk.LabelFrame(left_control, text="Camera Settings")
        camera_frame.pack(fill=tk.X, pady=5)
        
        camera_label = tk.Label(camera_frame, text="Camera Index:")
        camera_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.camera_var = tk.StringVar(value="0")
        camera_combobox = ttk.Combobox(camera_frame, textvariable=self.camera_var, width=5)
        camera_combobox['values'] = ('0', '1', '2', '3')
        camera_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.test_camera_button = tk.Button(camera_frame, text="Test Camera", command=self.test_camera)
        self.test_camera_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Person frame - for capturing samples
        person_frame = tk.LabelFrame(left_control, text="Capture Face Samples")
        person_frame.pack(fill=tk.X, pady=5)
        
        person_label = tk.Label(person_frame, text="Person Name:")
        person_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.person_entry = tk.Entry(person_frame, width=15)
        self.person_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.capture_button = tk.Button(person_frame, text="Capture Samples", command=self.start_capture)
        self.capture_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Auto capture option
        self.auto_capture_var = tk.BooleanVar(value=False)
        auto_capture_check = tk.Checkbutton(person_frame, text="Auto Capture", 
                                          variable=self.auto_capture_var)
        auto_capture_check.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Right side - Training and Recognition
        train_frame = tk.LabelFrame(right_control, text="Train Model")
        train_frame.pack(fill=tk.X, pady=5)
        
        self.train_button = tk.Button(train_frame, text="Train Recognition Model", command=self.train_model)
        self.train_button.pack(fill=tk.X, padx=5, pady=5)
        
        recog_frame = tk.LabelFrame(right_control, text="Face Recognition")
        recog_frame.pack(fill=tk.X, pady=5)
        
        self.recognize_button = tk.Button(recog_frame, text="Start Recognition", command=self.start_recognition)
        self.recognize_button.pack(fill=tk.X, padx=5, pady=5)
        
        # Stop button
        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Check model status
        self.check_model_status()
    
    def check_model_status(self):
        """Check if a trained model exists and update status"""
        if self.model_trained:
            self.status_label.config(text="Model loaded successfully. Ready for recognition.")
        else:
            self.status_label.config(text="No trained model found. Please capture samples and train the model.")
    
    def load_model(self):
        """Load a previously trained face recognition model"""
        if not os.path.exists(self.model_path):
            return
        
        try:
            # Load the model data
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Load the recognizer with the saved model
            self.recognizer.read(model_data['model_file'])
            self.name_dict = model_data['name_dict']
            self.model_trained = True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
    
    def test_camera(self):
        """Test if camera can be accessed"""
        try:
            camera_idx = int(self.camera_var.get())
            
            # Try different backends
            for backend in [cv2.CAP_DSHOW, cv2.CAP_ANY]:
                try:
                    cap = cv2.VideoCapture(camera_idx, backend)
                    
                    if not cap.isOpened():
                        continue
                    
                    ret, frame = cap.read()
                    if not ret:
                        cap.release()
                        continue
                    
                    # Success
                    messagebox.showinfo("Success", f"Camera {camera_idx} is working correctly")
                    
                    # Show a single frame
                    cv2.imshow('Camera Test', frame)
                    cv2.waitKey(2000)  # Wait for 2 seconds
                    cv2.destroyAllWindows()
                    
                    cap.release()
                    return
                except:
                    continue
            
            # If we get here, all backends failed
            messagebox.showerror("Error", f"Could not open camera with index {camera_idx}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Camera test failed: {str(e)}")
    
    def start_capture(self):
        """Start face sample capture process"""
        person_name = self.person_entry.get().strip()
        if not person_name:
            messagebox.showerror("Error", "Please enter a person name")
            return
        
        try:
            self.camera_index = int(self.camera_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid camera index. Please enter a number.")
            return
        
        # Check if auto capture is enabled
        self.auto_capture = self.auto_capture_var.get()
        
        # Create directory for this person
        person_dir = os.path.join(self.faces_dir, person_name)
        os.makedirs(person_dir, exist_ok=True)
        
        self.current_person = person_name
        self.sample_count = 0
        self.is_processing = True
        self.stop_threads = False
        
        # Update UI
        self.capture_button.config(state=tk.DISABLED)
        self.train_button.config(state=tk.DISABLED)
        self.recognize_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start capture in a thread
        self.thread = threading.Thread(target=self.capture_samples_thread)
        self.thread.daemon = True
        self.thread.start()
    
    def capture_samples_thread(self):
        """Thread function for capturing face samples"""
        person_dir = os.path.join(self.faces_dir, self.current_person)
        
        # Try different backends
        cap = None
        for backend in [cv2.CAP_DSHOW, cv2.CAP_ANY]:
            try:
                cap = cv2.VideoCapture(self.camera_index, backend)
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret:
                        break  # Found a working backend
                cap.release()
                cap = None
            except:
                continue
        
        if cap is None or not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("Error", 
                            f"Could not open camera with index {self.camera_index}"))
            self.root.after(0, self.reset_ui)
            return
        
        try:
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Initialize auto capture time
            self.last_capture_time = time.time()
            
            while self.sample_count < self.max_samples and not self.stop_threads:
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
                face_found = len(faces) > 0
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Display instructions and progress
                cv2.putText(frame, f"Person: {self.current_person}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Samples: {self.sample_count}/{self.max_samples}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                if self.auto_capture:
                    cv2.putText(frame, "Auto Capture Mode", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Press 'c' to capture, 'q' to quit", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Display the frame
                cv2.imshow('Capture Face Samples', frame)
                
                # Auto capture logic
                current_time = time.time()
                if self.auto_capture and face_found and (current_time - self.last_capture_time) >= self.auto_capture_interval:
                    if self.capture_face_sample(gray, faces[0]):
                        self.last_capture_time = current_time
                    
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c') and face_found:
                    self.capture_face_sample(gray, faces[0])
                elif key == ord('q'):
                    break
                elif key == ord('a'):  # Toggle auto capture
                    self.auto_capture = not self.auto_capture
                    self.last_capture_time = current_time  # Reset timer
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Show result message
            if self.sample_count == self.max_samples:
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                f"Successfully captured {self.sample_count} samples for {self.current_person}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Partial Completion", 
                                f"Captured {self.sample_count}/{self.max_samples} samples for {self.current_person}"))
            
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def capture_face_sample(self, gray_frame, face_coords):
        """Capture a single face sample"""
        try:
            # Extract face coordinates
            x, y, w, h = face_coords
            
            # Extract face region
            face_img = gray_frame[y:y+h, x:x+w]
            
            # Ensure the face region is valid
            if face_img.size == 0:
                return False
            
            # Save the face image
            sample_file = os.path.join(self.faces_dir, self.current_person, 
                                      f"{self.current_person}_{self.sample_count}.jpg")
            cv2.imwrite(sample_file, face_img)
            
            self.sample_count += 1
            return True
            
        except Exception as e:
            print(f"Error capturing face sample: {str(e)}")
            return False
    
    def train_model(self):
        """Train face recognition model with the captured samples"""
        # Check if there are any samples to train on
        if not os.path.exists(self.faces_dir) or not os.listdir(self.faces_dir):
            messagebox.showerror("Error", "No face samples found. Capture samples first.")
            return
        
        # Show progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Training Model")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(progress_window, text="Training model, please wait...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode="indeterminate")
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()
        
        # Disable buttons
        self.train_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.DISABLED)
        self.recognize_button.config(state=tk.DISABLED)
        
        # Start training in a thread
        def training_thread():
            try:
                # Prepare training data
                faces = []
                labels = []
                name_dict = {}  # Map numeric label to person name
                label_counter = 0
                
                # Process each person's directory
                for person_name in os.listdir(self.faces_dir):
                    person_dir = os.path.join(self.faces_dir, person_name)
                    
                    if not os.path.isdir(person_dir):
                        continue
                    
                    # Assign a numeric label to this person
                    name_dict[label_counter] = person_name
                    
                    # Process each image in the person's directory
                    for img_name in os.listdir(person_dir):
                        if not img_name.endswith(('.jpg', '.jpeg', '.png')):
                            continue
                            
                        img_path = os.path.join(person_dir, img_name)
                        
                        # Load and preprocess the image
                        face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                        if face_img is None:
                            continue
                            
                        # Add to training data
                        faces.append(face_img)
                        labels.append(label_counter)
                    
                    label_counter += 1
                
                # Check if we have enough data
                if len(faces) == 0 or label_counter == 0:
                    self.root.after(0, lambda: messagebox.showerror("Error", 
                                    "Not enough face samples found. Capture more samples."))
                    self.root.after(0, lambda: progress_window.destroy())
                    self.root.after(0, self.reset_ui)
                    return
                
                # Train the model
                self.recognizer.train(faces, np.array(labels))
                
                # Save the model temporarily
                model_file = os.path.join(self.data_dir, "models", "face_recognizer.xml")
                self.recognizer.write(model_file)
                
                # Save model info with name mappings
                model_data = {
                    'model_file': model_file,
                    'name_dict': name_dict
                }
                
                with open(self.model_path, 'wb') as f:
                    pickle.dump(model_data, f)
                
                self.name_dict = name_dict
                self.model_trained = True
                
                # Update UI
                self.root.after(0, lambda: progress_window.destroy())
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                f"Model trained successfully with {len(faces)} samples from {label_counter} people."))
                self.root.after(0, self.check_model_status)
                self.root.after(0, self.reset_ui)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Training error: {str(e)}"))
                self.root.after(0, lambda: progress_window.destroy())
                self.root.after(0, self.reset_ui)
        
        threading.Thread(target=training_thread, daemon=True).start()
    
    def start_recognition(self):
        """Start face recognition process"""
        if not self.model_trained:
            messagebox.showerror("Error", "No trained model available. Please train the model first.")
            return
        
        try:
            self.camera_index = int(self.camera_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid camera index. Please enter a number.")
            return
        
        self.is_processing = True
        self.stop_threads = False
        
        # Update UI
        self.capture_button.config(state=tk.DISABLED)
        self.train_button.config(state=tk.DISABLED)
        self.recognize_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start recognition in a thread
        self.thread = threading.Thread(target=self.recognition_thread)
        self.thread.daemon = True
        self.thread.start()
    
    def recognition_thread(self):
        """Thread function for face recognition"""
        # Try different backends
        cap = None
        for backend in [cv2.CAP_DSHOW, cv2.CAP_ANY]:
            try:
                cap = cv2.VideoCapture(self.camera_index, backend)
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret:
                        break  # Found a working backend
                cap.release()
                cap = None
            except:
                continue
        
        if cap is None or not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("Error", 
                            f"Could not open camera with index {self.camera_index}"))
            self.root.after(0, self.reset_ui)
            return
            
        try:
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            while not self.stop_threads:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert to grayscale for detection and recognition
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Process each detected face
                for (x, y, w, h) in faces:
                    # Extract the face region
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Perform recognition
                    try:
                        label, confidence = self.recognizer.predict(face_roi)
                        
                        # Get the name from the label
                        if confidence < 70:  # Lower confidence is better
                            name = self.name_dict.get(label, "Unknown")
                        else:
                            name = "Unknown"
                        
                        # Display confidence value
                        conf_text = f"{confidence:.1f}%"
                        
                        # Draw rectangle around the face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        # Draw name and confidence
                        cv2.rectangle(frame, (x, y-25), (x+w, y), (0, 255, 0), -1)
                        cv2.putText(frame, f"{name} ({conf_text})", (x+6, y-6),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    except:
                        # If recognition fails, just show the face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Display instructions
                cv2.putText(frame, "Face Recognition Running", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Display the frame
                cv2.imshow('Face Recognition', frame)
                
                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q') or self.stop_threads:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def stop_processing(self):
        """Stop any ongoing process"""
        self.stop_threads = True
        cv2.destroyAllWindows()
        self.reset_ui()
    
    def reset_ui(self):
        """Reset the UI after processing"""
        self.is_processing = False
        self.capture_button.config(state=tk.NORMAL)
        self.train_button.config(state=tk.NORMAL)
        self.recognize_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionAppSimplified(root)
    root.mainloop() 