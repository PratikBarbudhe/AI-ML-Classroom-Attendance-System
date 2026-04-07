import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
from PIL import Image, ImageTk
import threading
import pickle
import time
import logging
import csv
from camera_utils import open_camera, test_camera_frame
from attendance_utils import AttendanceStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOGGER = logging.getLogger("face_recognition_app_simplified")

class FaceRecognitionAppSimplified:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Classroom Attendance System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for better appearance
        self.BG_COLOR = "#f0f0f0"
        self.PRIMARY_COLOR = "#2196F3"
        self.SUCCESS_COLOR = "#4CAF50"
        self.WARNING_COLOR = "#FF9800"
        self.DANGER_COLOR = "#F44336"
        self.INFO_COLOR = "#9C27B0"
        
        self.root.configure(bg=self.BG_COLOR)
        
        # Variables
        self.thread = None
        self.stop_threads = False
        self.is_processing = False
        self.camera_index = 0
        self.sample_count = 0
        self.max_samples = 30  # Increased for better accuracy
        self.current_person = ""
        self.model_trained = False
        self.name_dict = {}
        self.auto_capture = False
        self.auto_capture_interval = 0.5  # Faster capture
        self.last_capture_time = 0
        self.last_attendance_text = "No attendance marked yet"
        
        # Data paths
        self.data_dir = "data"
        self.faces_dir = os.path.join(self.data_dir, "faces")
        self.model_path = os.path.join(self.data_dir, "models", "face_model.pkl")
        self.students_csv = os.path.join(self.data_dir, "students.csv")
        self.attendance_store = AttendanceStore()
        
        # Create directories if they don't exist
        os.makedirs(self.faces_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "models"), exist_ok=True)
        os.makedirs(os.path.dirname(self.students_csv), exist_ok=True)
        
        # Face detection with better parameters
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Face recognition with improved LBPH parameters
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create(
                radius=2, neighbors=8, grid_x=8, grid_y=8, threshold=80
            )
            self.load_model()
            self.create_widgets()
        except AttributeError:
            messagebox.showerror("Error", "OpenCV contrib modules not installed. Please run: pip install opencv-contrib-python")
            root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            root.destroy()
        
    def create_widgets(self):
        """Create all GUI widgets with improved styling"""
        # Create main frames with colors
        self.top_frame = tk.Frame(self.root, height=150, bg=self.BG_COLOR)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.control_frame = tk.Frame(self.root, height=280, bg=self.BG_COLOR)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        self.control_frame.pack_propagate(False)
        
        # Title with modern styling
        title_label = tk.Label(self.top_frame, text="🎓 AI Classroom Attendance System", 
                              font=("Arial", 22, "bold"), bg=self.BG_COLOR, fg="#1565C0")
        title_label.pack(pady=10)
        
        # Status frame - improved styling
        status_frame = tk.LabelFrame(self.top_frame, text="📊 Model Status", 
                                    font=("Arial", 11, "bold"), bg=self.BG_COLOR, 
                                    fg=self.PRIMARY_COLOR, padx=10, pady=5)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Checking model status...", 
                                    font=("Arial", 10), fg="blue", bg=self.BG_COLOR)
        self.status_label.pack(pady=5)

        # Attendance dashboard - improved styling
        attendance_frame = tk.LabelFrame(self.top_frame, text="📈 Attendance Dashboard", 
                                        font=("Arial", 11, "bold"), bg=self.BG_COLOR, 
                                        fg=self.PRIMARY_COLOR, padx=10, pady=5)
        attendance_frame.pack(fill=tk.X, pady=5)
        
        # Dashboard info in grid
        dashboard_info_frame = tk.Frame(attendance_frame, bg=self.BG_COLOR)
        dashboard_info_frame.pack(fill=tk.X, pady=3)
        
        self.total_events_label = tk.Label(dashboard_info_frame, text="📅 Today's events: 0", 
                                          font=("Arial", 10, "bold"), bg=self.BG_COLOR, fg="#1976D2")
        self.total_events_label.grid(row=0, column=0, padx=10, pady=2, sticky=tk.W)
        
        self.unique_people_label = tk.Label(dashboard_info_frame, text="👥 Unique people: 0", 
                                           font=("Arial", 10, "bold"), bg=self.BG_COLOR, fg="#7B1FA2")
        self.unique_people_label.grid(row=0, column=1, padx=10, pady=2, sticky=tk.W)
        
        self.last_event_label = tk.Label(dashboard_info_frame, text="⏱️ Last: No attendance marked yet", 
                                        font=("Arial", 9), bg=self.BG_COLOR, fg="#555555")
        self.last_event_label.grid(row=1, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)
        
        # Dashboard buttons frame
        dashboard_btn_frame = tk.Frame(attendance_frame, bg=self.BG_COLOR)
        dashboard_btn_frame.pack(fill=tk.X, pady=3)
        
        self.export_button = tk.Button(dashboard_btn_frame, text="📥 Export CSV", 
                                      command=self.export_today_attendance, 
                                      bg=self.SUCCESS_COLOR, fg="white", 
                                      font=("Arial", 9, "bold"), relief=tk.RAISED, padx=10)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        self.view_log_button = tk.Button(dashboard_btn_frame, text="📋 View Log", 
                                        command=self.view_today_log, 
                                        bg=self.PRIMARY_COLOR, fg="white", 
                                        font=("Arial", 9, "bold"), relief=tk.RAISED, padx=10)
        self.view_log_button.pack(side=tk.LEFT, padx=5)
        
        # Image display with border
        image_border = tk.Frame(self.main_frame, bg="#333", relief=tk.SUNKEN, bd=2)
        image_border.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.image_label = tk.Label(image_border, bg="black", text="📹 Camera Feed", 
                                   fg="white", font=("Arial", 14, "bold"))
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Control frames with better layout
        control_top = tk.Frame(self.control_frame, bg=self.BG_COLOR)
        control_top.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        left_control = tk.Frame(control_top, bg=self.BG_COLOR)
        left_control.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        middle_control = tk.Frame(control_top, bg=self.BG_COLOR)
        middle_control.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        right_control = tk.Frame(control_top, bg=self.BG_COLOR)
        right_control.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # LEFT: Camera settings - improved styling
        camera_frame = tk.LabelFrame(left_control, text="🎥 Camera Settings", 
                                    font=("Arial", 10, "bold"), bg=self.BG_COLOR, 
                                    fg=self.PRIMARY_COLOR, padx=8, pady=8)
        camera_frame.pack(fill=tk.X, pady=3)
        
        camera_label = tk.Label(camera_frame, text="Camera Index:", font=("Arial", 9), bg=self.BG_COLOR)
        camera_label.grid(row=0, column=0, padx=5, pady=4, sticky=tk.W)
        
        self.camera_var = tk.StringVar(value="0")
        camera_combobox = ttk.Combobox(camera_frame, textvariable=self.camera_var, width=8, 
                                      font=("Arial", 9), state="readonly")
        camera_combobox['values'] = ('0', '1', '2', '3')
        camera_combobox.grid(row=0, column=1, padx=5, pady=4, sticky=tk.W)
        
        self.test_camera_button = tk.Button(camera_frame, text="🔍 Test", 
                                           command=self.test_camera, 
                                           bg=self.WARNING_COLOR, fg="white", 
                                           font=("Arial", 9, "bold"), relief=tk.RAISED)
        self.test_camera_button.grid(row=0, column=2, padx=5, pady=4)
        
        # MIDDLE: Person capture frame - improved styling
        person_frame = tk.LabelFrame(middle_control, text="📸 Capture & Import", 
                                    font=("Arial", 10, "bold"), bg=self.BG_COLOR, 
                                    fg=self.PRIMARY_COLOR, padx=8, pady=8)
        person_frame.pack(fill=tk.X, pady=3)
        
        person_label = tk.Label(person_frame, text="Student ID:", font=("Arial", 9), bg=self.BG_COLOR)
        person_label.grid(row=0, column=0, padx=5, pady=4, sticky=tk.W)
        
        self.person_id_entry = tk.Entry(person_frame, width=12, font=("Arial", 9), relief=tk.SUNKEN, bd=1)
        self.person_id_entry.grid(row=0, column=1, padx=5, pady=4, sticky=tk.EW)
        
        person_name_label = tk.Label(person_frame, text="Name:", font=("Arial", 9), bg=self.BG_COLOR)
        person_name_label.grid(row=1, column=0, padx=5, pady=4, sticky=tk.W)
        
        self.person_entry = tk.Entry(person_frame, width=12, font=("Arial", 9), relief=tk.SUNKEN, bd=1)
        self.person_entry.grid(row=1, column=1, padx=5, pady=4, sticky=tk.EW)
        
        # Buttons in person frame
        buttons_frame = tk.Frame(person_frame, bg=self.BG_COLOR)
        buttons_frame.grid(row=0, column=2, rowspan=2, padx=5, pady=4, sticky=tk.NSEW)
        
        self.capture_button = tk.Button(buttons_frame, text="📷\nCapture", 
                                       command=self.start_capture, 
                                       bg=self.SUCCESS_COLOR, fg="white", 
                                       font=("Arial", 8, "bold"), relief=tk.RAISED, 
                                       width=8, height=2)
        self.capture_button.pack(pady=2)
        
        self.import_button = tk.Button(buttons_frame, text="📱\nImport", 
                                      command=self.open_import_tool, 
                                      bg=self.INFO_COLOR, fg="white", 
                                      font=("Arial", 8, "bold"), relief=tk.RAISED, 
                                      width=8, height=2)
        self.import_button.pack(pady=2)
        
        # Auto capture option
        self.auto_capture_var = tk.BooleanVar(value=True)
        auto_capture_check = tk.Checkbutton(person_frame, text="Auto Capture", 
                                           variable=self.auto_capture_var, 
                                           font=("Arial", 9), bg=self.BG_COLOR,
                                           activebackground=self.BG_COLOR)
        auto_capture_check.grid(row=2, column=0, columnspan=2, padx=5, pady=4, sticky=tk.W)
        
        # Configure column widths
        person_frame.columnconfigure(1, weight=1)
        
        # Students list frame
        students_frame = tk.LabelFrame(middle_control, text="👥 Registered Students", 
                                      font=("Arial", 10, "bold"), bg=self.BG_COLOR, 
                                      fg=self.PRIMARY_COLOR, padx=5, pady=5)
        students_frame.pack(fill=tk.BOTH, expand=True, pady=3)
        
        # Treeview for students with custom style
        tree_scroll = ttk.Scrollbar(students_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.students_tree = ttk.Treeview(students_frame, columns=("ID", "Name"), 
                                         show="headings", height=6, 
                                         yscrollcommand=tree_scroll.set)
        self.students_tree.heading("ID", text="ID")
        self.students_tree.heading("Name", text="Name")
        self.students_tree.column("ID", width=50)
        self.students_tree.column("Name", width=120)
        
        tree_scroll.config(command=self.students_tree.yview)
        self.students_tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.refresh_students_list()
        
        # Delete student button
        self.delete_student_btn = tk.Button(students_frame, text="🗑️ Delete Selected", 
                                           command=self.delete_selected_student, 
                                           bg=self.DANGER_COLOR, fg="white", 
                                           font=("Arial", 9, "bold"), relief=tk.RAISED)
        self.delete_student_btn.pack(fill=tk.X, padx=2, pady=3)
        
        # RIGHT: Training and Recognition
        train_frame = tk.LabelFrame(right_control, text="🧠 Train Model", 
                                   font=("Arial", 10, "bold"), bg=self.BG_COLOR, 
                                   fg=self.PRIMARY_COLOR, padx=8, pady=8)
        train_frame.pack(fill=tk.X, pady=3)
        
        self.train_button = tk.Button(train_frame, text="Train Recognition Model", 
                                     command=self.train_model, 
                                     bg=self.PRIMARY_COLOR, fg="white", 
                                     font=("Arial", 9, "bold"), relief=tk.RAISED)
        self.train_button.pack(fill=tk.X, padx=2, pady=3)
        
        # Training progress
        self.train_progress_var = tk.IntVar()
        self.train_progress_bar = ttk.Progressbar(train_frame, variable=self.train_progress_var, 
                                                 maximum=100, mode='determinate')
        self.train_progress_bar.pack(fill=tk.X, padx=2, pady=3)
        
        self.train_status_label = tk.Label(train_frame, text="Ready", 
                                          font=("Arial", 8), bg=self.BG_COLOR, fg="#666666")
        self.train_status_label.pack(pady=2)
        
        # Recognition settings
        recog_frame = tk.LabelFrame(right_control, text="🎯 Face Recognition", 
                                   font=("Arial", 10, "bold"), bg=self.BG_COLOR, 
                                   fg=self.PRIMARY_COLOR, padx=8, pady=8)
        recog_frame.pack(fill=tk.X, pady=3)
        
        self.recognize_button = tk.Button(recog_frame, text="Start Recognition", 
                                         command=self.start_recognition, 
                                         bg=self.SUCCESS_COLOR, fg="white", 
                                         font=("Arial", 9, "bold"), relief=tk.RAISED)
        self.recognize_button.pack(fill=tk.X, padx=2, pady=3)
        
        # Recognition status
        self.recog_status_label = tk.Label(recog_frame, text="Stopped", 
                                          font=("Arial", 8), bg=self.BG_COLOR, fg="#666666")
        self.recog_status_label.pack(pady=2)
        
        # Stop button at bottom
        stop_frame = tk.Frame(self.control_frame, bg=self.BG_COLOR)
        stop_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.stop_button = tk.Button(stop_frame, text="⏹️  STOP ALL", 
                                    command=self.stop_processing, 
                                    state=tk.DISABLED, 
                                    bg=self.DANGER_COLOR, fg="white", 
                                    font=("Arial", 11, "bold"), relief=tk.RAISED)
        self.stop_button.pack(fill=tk.X, padx=0, pady=3)
        
        # Keyboard shortcuts
        self.root.bind('<Escape>', lambda e: self.stop_processing())
        self.root.bind('<Control-s>', lambda e: self.start_capture())
        self.root.bind('<Control-t>', lambda e: self.train_model())
        self.root.bind('<Control-r>', lambda e: self.start_recognition())
        
        # Check model status
        self.check_model_status()
        self.update_attendance_dashboard()
    
    def refresh_students_list(self):
        """Refresh the students list in the GUI"""
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        if os.path.exists(self.students_csv):
            try:
                with open(self.students_csv, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            self.students_tree.insert("", "end", values=row)
            except Exception as e:
                LOGGER.error(f"Error reading students CSV: {e}")
    
    def save_student_to_csv(self, student_id, student_name):
        """Save student to CSV"""
        try:
            os.makedirs(os.path.dirname(self.students_csv), exist_ok=True)
            rows = []
            
            if os.path.exists(self.students_csv):
                with open(self.students_csv, 'r', encoding='utf-8') as f:
                    rows = list(csv.reader(f))
            
            # Check if student already exists
            if any(row and row[0] == str(student_id) for row in rows):
                messagebox.showwarning("Duplicate", f"Student ID {student_id} already exists!")
                return False
            
            # Add new student
            rows.append([str(student_id), student_name])
            
            with open(self.students_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save student: {e}")
            LOGGER.exception("Error saving student")
            return False
    
    def delete_selected_student(self):
        """Delete selected student and all their face data"""
        selected_item = self.students_tree.focus()
        if not selected_item:
            messagebox.showwarning("Delete", "Select a student first!")
            return
        
        values = self.students_tree.item(selected_item)['values']
        if not values:
            return
        
        student_id = values[0]
        student_name = values[1] if len(values) > 1 else "Unknown"
        
        # Confirmation dialog
        if not messagebox.askyesno("Confirm Delete", 
                                   f"Delete {student_name} (ID: {student_id}) and all face data?\nThis cannot be undone!"):
            return
        
        try:
            # Remove from CSV
            if os.path.exists(self.students_csv):
                rows = []
                with open(self.students_csv, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = [row for row in reader if not (row and row[0] == str(student_id))]
                
                with open(self.students_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
            
            # Remove face images
            student_dir = os.path.join(self.faces_dir, str(student_id))
            if os.path.exists(student_dir):
                import shutil
                shutil.rmtree(student_dir)
            
            # Remove trained model to force retraining
            model_file = os.path.join(self.data_dir, "models", "face_recognizer.xml")
            if os.path.exists(model_file):
                os.remove(model_file)
            if os.path.exists(self.model_path):
                os.remove(self.model_path)
            
            self.model_trained = False
            
            # Refresh UI
            self.refresh_students_list()
            self.check_model_status()
            
            messagebox.showinfo("Success", f"Student {student_name} deleted successfully!\nPlease retrain the model.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete student: {e}")
            LOGGER.exception("Error deleting student")
    
    def check_model_status(self):
        """Check if a trained model exists and update status"""
        if self.model_trained:
            self.status_label.config(text="✅ Model loaded successfully. Ready for recognition.", fg="green")
        else:
            self.status_label.config(text="❌ No trained model found. Capture samples and train the model.", fg="red")

    def update_attendance_dashboard(self):
        """Refresh attendance statistics"""
        try:
            summary = self.attendance_store.get_today_summary()
            self.total_events_label.config(text=f"Today's events: {summary['total_events']}")
            self.unique_people_label.config(text=f"Unique people: {summary['unique_people']}")
            last_event = summary["last_event"]
            if last_event:
                self.last_event_label.config(
                    text=(
                        f"Last marked: {last_event['person_name']} at "
                        f"{last_event['recognized_at']} (conf: {last_event['confidence']:.1f})"
                    )
                )
            else:
                self.last_event_label.config(text="No attendance marked yet")
        except Exception:
            LOGGER.exception("Failed to update attendance dashboard")

        self.root.after(5000, self.update_attendance_dashboard)

    def mark_attendance_event(self, person_name, confidence):
        """Mark attendance with cooldown"""
        try:
            marked, message = self.attendance_store.mark_attendance(
                person_name=person_name,
                confidence=confidence,
                source="webcam",
                min_interval_seconds=60,
            )
            if marked:
                LOGGER.info(message)
        except Exception:
            LOGGER.exception("Failed to mark attendance")

    def export_today_attendance(self):
        """Export today's attendance to CSV"""
        try:
            output_path, row_count = self.attendance_store.export_today_csv()
            messagebox.showinfo("Export Complete", f"Exported {row_count} rows to:\n{output_path}")
        except Exception as exc:
            messagebox.showerror("Export Error", f"Could not export attendance: {exc}")

    def view_today_log(self):
        """Show recent attendance records"""
        try:
            records = self.attendance_store.get_today_records()
            if not records:
                messagebox.showinfo("Today Log", "No attendance records found for today.")
                return
            preview = "\n".join(
                [
                    f"{item['recognized_at']} | {item['person_name']} | conf={item['confidence']:.1f}"
                    for item in records[:20]
                ]
            )
            if len(records) > 20:
                preview += f"\n... and {len(records) - 20} more"
            messagebox.showinfo("Today Log", preview)
        except Exception as exc:
            messagebox.showerror("Log Error", f"Could not load attendance log: {exc}")
    
    def load_model(self):
        """Load a previously trained face recognition model"""
        if not os.path.exists(self.model_path):
            return
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            model_file = model_data['model_file']
            if os.path.exists(model_file):
                self.recognizer.read(model_file)
                self.name_dict = model_data['name_dict']
                self.model_trained = True
            
        except Exception as e:
            LOGGER.error(f"Error loading model: {str(e)}")
    
    def test_camera(self):
        """Test if camera can be accessed"""
        try:
            camera_idx = int(self.camera_var.get())
            success, frame, backend = test_camera_frame(camera_idx)
            if success and frame is not None:
                messagebox.showinfo(
                    "Success",
                    f"Camera {camera_idx} is working correctly (backend: {backend})"
                )
                cv2.imshow('Camera Test', frame)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
                return
            messagebox.showerror("Error", f"Could not open camera with index {camera_idx}")
            
        except Exception as e:
            LOGGER.exception("Camera test failed")
            messagebox.showerror("Error", f"Camera test failed: {str(e)}")
    
    def preprocess_face(self, gray_frame, face_coords):
        """Preprocess face with histogram equalization for better recognition"""
        try:
            x, y, w, h = face_coords
            face_roi = gray_frame[y:y+h, x:x+w]
            
            if face_roi.size == 0:
                return None
            
            # Histogram equalization for better contrast
            face_roi = cv2.equalizeHist(face_roi)
            
            # Resize to standard size
            face_roi = cv2.resize(face_roi, (200, 200))
            
            return face_roi
        except Exception:
            return None
    
    def open_import_tool(self):
        """Open the Image Import Tool for importing phone photos"""
        try:
            # Import the image import tool
            from image_import_tool import ImageImportTool
            
            # Create a new window for the import tool
            import_window = tk.Toplevel(self.root)
            app = ImageImportTool(import_window)
            
            # Make it modal-like
            import_window.transient(self.root)
            import_window.grab_set()
            
            LOGGER.info("Image Import Tool opened")
        except Exception as e:
            LOGGER.error(f"Error opening import tool: {e}")
            messagebox.showerror("Error", f"Failed to open import tool:\n{str(e)}\n\nMake sure image_import_tool.py exists")
    
    def start_capture(self):
        """Start face sample capture process"""
        student_id = self.person_id_entry.get().strip()
        student_name = self.person_entry.get().strip()
        
        if not student_id or not student_name:
            messagebox.showerror("Error", "Please enter Student ID and Name")
            return
        
        try:
            self.camera_index = int(self.camera_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid camera index")
            return
        
        self.auto_capture = self.auto_capture_var.get()
        
        # Save student to CSV
        if not self.save_student_to_csv(student_id, student_name):
            return
        
        # Create directory for this student
        student_dir = os.path.join(self.faces_dir, student_id)
        os.makedirs(student_dir, exist_ok=True)
        
        self.current_person = student_id
        self.sample_count = 0
        self.is_processing = True
        self.stop_threads = False
        
        # Update UI
        self.capture_button.config(state=tk.DISABLED)
        self.train_button.config(state=tk.DISABLED)
        self.recognize_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start capture in a thread
        self.thread = threading.Thread(target=self.capture_samples_thread, args=(student_id, student_name))
        self.thread.daemon = True
        self.thread.start()
    
    def capture_samples_thread(self, student_id, student_name):
        """Thread function for capturing face samples with improved preprocessing"""
        student_dir = os.path.join(self.faces_dir, student_id)
        
        cap, _ = open_camera(self.camera_index)
        
        if cap is None or not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("Error", 
                            f"Could not open camera with index {self.camera_index}"))
            self.root.after(0, self.reset_ui)
            return
        
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.last_capture_time = time.time()
            
            while self.sample_count < self.max_samples and not self.stop_threads:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Better face detection with improved parameters
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(100, 100)
                )
                
                face_found = len(faces) > 0
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Display instructions
                cv2.putText(frame, f"Student: {student_name} ({student_id})", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Samples: {self.sample_count}/{self.max_samples}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if self.auto_capture:
                    cv2.putText(frame, "Auto Capture: ON (Press 'a' to toggle)", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                else:
                    cv2.putText(frame, "Press 'c' to capture, 'a' for auto, 'q' to quit", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                
                cv2.imshow('Capture Face Samples', frame)
                
                # Auto capture logic
                current_time = time.time()
                if self.auto_capture and face_found and (current_time - self.last_capture_time) >= self.auto_capture_interval:
                    if len(faces) > 0:
                        face_preprocessed = self.preprocess_face(gray, faces[0])
                        if face_preprocessed is not None:
                            sample_file = os.path.join(student_dir, f"{student_id}_{self.sample_count}.jpg")
                            cv2.imwrite(sample_file, face_preprocessed)
                            self.sample_count += 1
                            self.last_capture_time = current_time
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c') and face_found:
                    if len(faces) > 0:
                        face_preprocessed = self.preprocess_face(gray, faces[0])
                        if face_preprocessed is not None:
                            sample_file = os.path.join(student_dir, f"{student_id}_{self.sample_count}.jpg")
                            cv2.imwrite(sample_file, face_preprocessed)
                            self.sample_count += 1
                elif key == ord('q'):
                    break
                elif key == ord('a'):
                    self.auto_capture = not self.auto_capture
                    self.last_capture_time = current_time
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Refresh students list
            self.root.after(0, self.refresh_students_list)
            
            if self.sample_count == self.max_samples:
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                f"Successfully captured {self.sample_count} samples for {student_name}"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Partial", 
                                f"Captured {self.sample_count}/{self.max_samples} samples"))
            
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            LOGGER.exception("Capture thread failed")
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self.reset_ui)
    
    def train_model(self):
        """Train face recognition model with captured samples"""
        if not os.path.exists(self.faces_dir) or not os.listdir(self.faces_dir):
            messagebox.showerror("Error", "No face samples found. Capture samples first.")
            return
        
        # Progress dialog
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
        
        self.train_button.config(state=tk.DISABLED)
        self.capture_button.config(state=tk.DISABLED)
        self.recognize_button.config(state=tk.DISABLED)
        
        def training_thread():
            try:
                faces = []
                labels = []
                name_dict = {}
                label_counter = 0
                
                # Process each student directory
                for student_id in os.listdir(self.faces_dir):
                    student_dir = os.path.join(self.faces_dir, student_id)
                    
                    if not os.path.isdir(student_dir):
                        continue
                    
                    # Find student name from CSV
                    student_name = student_id
                    if os.path.exists(self.students_csv):
                        with open(self.students_csv, 'r', encoding='utf-8') as f:
                            for row in csv.reader(f):
                                if row and row[0] == student_id:
                                    student_name = row[1] if len(row) > 1 else student_id
                                    break
                    
                    name_dict[label_counter] = student_name
                    
                    # Process images
                    for img_name in os.listdir(student_dir):
                        if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                            continue
                        
                        img_path = os.path.join(student_dir, img_name)
                        face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                        
                        if face_img is None:
                            continue
                        
                        face_img = cv2.resize(face_img, (200, 200))
                        faces.append(face_img)
                        labels.append(label_counter)
                    
                    label_counter += 1
                
                if len(faces) == 0:
                    self.root.after(0, lambda: messagebox.showerror("Error", 
                                    "Not enough face samples. Capture more samples."))
                    self.root.after(0, lambda: progress_window.destroy())
                    self.root.after(0, self.reset_ui)
                    return
                
                # Train with improved LBPH
                self.recognizer = cv2.face.LBPHFaceRecognizer_create(
                    radius=2, neighbors=8, grid_x=8, grid_y=8, threshold=80
                )
                self.recognizer.train(faces, np.array(labels))
                
                # Save model
                model_file = os.path.join(self.data_dir, "models", "face_recognizer.xml")
                self.recognizer.write(model_file)
                
                model_data = {
                    'model_file': model_file,
                    'name_dict': name_dict
                }
                
                with open(self.model_path, 'wb') as f:
                    pickle.dump(model_data, f)
                
                self.name_dict = name_dict
                self.model_trained = True
                
                self.root.after(0, lambda: progress_window.destroy())
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                f"Model trained with {len(faces)} samples from {label_counter} students."))
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
            messagebox.showerror("Error", "No trained model. Please train the model first.")
            return
        
        try:
            self.camera_index = int(self.camera_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid camera index")
            return
        
        self.is_processing = True
        self.stop_threads = False
        
        self.capture_button.config(state=tk.DISABLED)
        self.train_button.config(state=tk.DISABLED)
        self.recognize_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.thread = threading.Thread(target=self.recognition_thread)
        self.thread.daemon = True
        self.thread.start()
    
    def recognition_thread(self):
        """Thread function for face recognition with improved accuracy"""
        cap, _ = open_camera(self.camera_index)
        
        if cap is None or not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror("Error", 
                            f"Could not open camera with index {self.camera_index}"))
            self.root.after(0, self.reset_ui)
            return
            
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            while not self.stop_threads:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Improved face detection
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(100, 100)
                )
                
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (200, 200))
                    face_roi = cv2.equalizeHist(face_roi)
                    
                    try:
                        label, confidence = self.recognizer.predict(face_roi)
                        
                        if confidence < 75:  # Lower is better
                            name = self.name_dict.get(label, "Unknown")
                            if name != "Unknown":
                                self.mark_attendance_event(name, confidence)
                        else:
                            name = "Unknown"
                        
                        conf_text = f"{confidence:.1f}"
                        
                        color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        cv2.rectangle(frame, (x, y-30), (x+w, y), color, -1)
                        cv2.putText(frame, f"{name} ({conf_text})", (x+6, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    except Exception:
                        LOGGER.exception("Prediction failed")
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                cv2.putText(frame, "Face Recognition Running - Press 'Q' to quit", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Face Recognition', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            self.root.after(0, self.reset_ui)
            
        except Exception as e:
            LOGGER.exception("Recognition thread failed")
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