"""
Image Import Tool for Face Recognition System
Allows importing images from phone or other sources and organizing them by person.
This tool helps improve face recognition accuracy by adding multiple quality images.
"""

import os
import shutil
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from PIL import Image, ImageTk
import threading
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOGGER = logging.getLogger("image_import_tool")


class ImageImportTool:
    def __init__(self, root):
        self.root = root
        self.root.title("📱 Face Image Import Tool")
        self.root.geometry("1100x850")
        self.root.minsize(900, 700)
        
        # Configure colors
        self.BG_COLOR = "#f0f0f0"
        self.PRIMARY_COLOR = "#2196F3"
        self.SUCCESS_COLOR = "#4CAF50"
        self.WARNING_COLOR = "#FF9800"
        self.DANGER_COLOR = "#F44336"
        self.INFO_COLOR = "#9C27B0"
        
        self.root.configure(bg=self.BG_COLOR)
        
        # Data paths
        self.data_dir = "data"
        self.faces_dir = os.path.join(self.data_dir, "faces")
        os.makedirs(self.faces_dir, exist_ok=True)
        
        # Variables
        self.selected_person = tk.StringVar()
        self.import_thread = None
        self.selected_files = []
        self.current_preview_index = 0
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.create_widgets()
        self.refresh_person_list()
        
    def create_widgets(self):
        """Create the GUI widgets with improved styling"""
        # Title with styling
        title_label = tk.Label(self.root, text="📱 Import Face Images from Phone/Camera", 
                              font=("Arial", 18, "bold"), bg=self.BG_COLOR, fg="#1565C0")
        title_label.pack(pady=15)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # LEFT PANEL - Person Selection
        left_panel = tk.LabelFrame(main_frame, text="👥 Select Person", 
                                  font=("Arial", 11, "bold"), bg=self.BG_COLOR, 
                                  fg=self.PRIMARY_COLOR, padx=10, pady=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5, ipadx=5)
        
        # Person selection dropdown
        person_label = tk.Label(left_panel, text="Select Existing:", font=("Arial", 10, "bold"), 
                               bg=self.BG_COLOR)
        person_label.pack(padx=10, pady=(5, 3), anchor=tk.W)
        
        self.person_dropdown = ttk.Combobox(left_panel, textvariable=self.selected_person, 
                                           width=22, font=("Arial", 9), state="readonly")
        self.person_dropdown.pack(padx=10, pady=5, fill=tk.X)
        self.person_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_person_selected())
        
        # New person entry
        new_person_label = tk.Label(left_panel, text="Create New Person:", 
                                   font=("Arial", 10, "bold"), bg=self.BG_COLOR)
        new_person_label.pack(padx=10, pady=(15, 3), anchor=tk.W)
        
        new_person_frame = tk.Frame(left_panel, bg=self.BG_COLOR)
        new_person_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.new_person_entry = tk.Entry(new_person_frame, font=("Arial", 10), 
                                        width=22, relief=tk.SUNKEN, bd=1)
        self.new_person_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        create_person_btn = tk.Button(new_person_frame, text="Create", 
                                     command=self.create_new_person, 
                                     bg=self.SUCCESS_COLOR, fg="white", 
                                     font=("Arial", 9, "bold"), relief=tk.RAISED)
        create_person_btn.pack(side=tk.LEFT)
        
        # Person info
        info_label = tk.Label(left_panel, text="📊 Person Info:", font=("Arial", 10, "bold"),
                             bg=self.BG_COLOR)
        info_label.pack(padx=10, pady=(15, 3), anchor=tk.W)
        
        self.person_info_label = tk.Label(left_panel, text="No person selected", 
                                         font=("Arial", 9), justify=tk.LEFT,
                                         bg=self.BG_COLOR, fg="#444444")
        self.person_info_label.pack(padx=10, pady=5, anchor=tk.W, fill=tk.X)
        
        # Display existing people
        existing_label = tk.Label(left_panel, text="📁 Existing Faces:", font=("Arial", 10, "bold"),
                                 bg=self.BG_COLOR)
        existing_label.pack(padx=10, pady=(15, 3), anchor=tk.W)
        
        self.person_listbox = tk.Listbox(left_panel, height=15, font=("Arial", 9),
                                        relief=tk.SUNKEN, bd=1, bg="white")
        self.person_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.person_listbox.bind('<<ListboxSelect>>', self.on_person_from_list)
        
        # Refresh button
        refresh_btn = tk.Button(left_panel, text="🔄 Refresh", command=self.refresh_person_list,
                               bg=self.PRIMARY_COLOR, fg="white",
                               font=("Arial", 9, "bold"), relief=tk.RAISED)
        refresh_btn.pack(padx=10, pady=5, fill=tk.X)
        
        # View Student Data button
        view_data_btn = tk.Button(left_panel, text="📊 View All Students", command=self.view_student_data,
                                 bg="#1976D2", fg="white",
                                 font=("Arial", 9, "bold"), relief=tk.RAISED)
        view_data_btn.pack(padx=10, pady=5, fill=tk.X)
        
        # CENTER PANEL - Image Import
        center_panel = tk.LabelFrame(main_frame, text="🖼️ Import Images", 
                                    font=("Arial", 11, "bold"), bg=self.BG_COLOR,
                                    fg=self.PRIMARY_COLOR, padx=10, pady=10)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5, ipadx=5)
        
        # Import buttons
        button_frame = tk.Frame(center_panel, bg=self.BG_COLOR)
        button_frame.pack(padx=(0, 0), pady=8, fill=tk.X)
        
        browse_btn = tk.Button(button_frame, text="📂 Browse\nImages", 
                              command=self.browse_images,
                              bg=self.WARNING_COLOR, fg="white", 
                              font=("Arial", 9, "bold"), relief=tk.RAISED,
                              height=2, width=15)
        browse_btn.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        folder_btn = tk.Button(button_frame, text="📁 Browse\nFolder", 
                              command=self.browse_folder,
                              bg=self.INFO_COLOR, fg="white", 
                              font=("Arial", 9, "bold"), relief=tk.RAISED,
                              height=2, width=15)
        folder_btn.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        # Selected files list
        files_label = tk.Label(center_panel, text="Selected Files:", 
                              font=("Arial", 10, "bold"), bg=self.BG_COLOR)
        files_label.pack(padx=0, pady=(10, 3), anchor=tk.W)
        
        # Files frame with scrollbar
        files_frame = tk.Frame(center_panel, bg=self.BG_COLOR)
        files_frame.pack(padx=0, pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(files_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(files_frame, yscrollcommand=scrollbar.set, 
                                       font=("Arial", 9), height=8,
                                       relief=tk.SUNKEN, bd=1, bg="white")
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Action buttons
        action_frame = tk.Frame(center_panel, bg=self.BG_COLOR)
        action_frame.pack(padx=0, pady=8, fill=tk.X)
        
        clear_btn = tk.Button(action_frame, text="🗑️ Clear", 
                             command=self.clear_selection,
                             bg=self.DANGER_COLOR, fg="white", 
                             font=("Arial", 9, "bold"), relief=tk.RAISED)
        clear_btn.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        remove_btn = tk.Button(action_frame, text="❌ Remove", 
                              command=self.remove_selected_file,
                              bg="#FF5252", fg="white", 
                              font=("Arial", 9, "bold"), relief=tk.RAISED)
        remove_btn.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        # Import progress
        progress_label = tk.Label(center_panel, text="Import Status:", 
                                 font=("Arial", 10, "bold"), bg=self.BG_COLOR)
        progress_label.pack(padx=0, pady=(10, 3), anchor=tk.W)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(center_panel, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(padx=0, pady=5, fill=tk.X)
        
        self.status_label = tk.Label(center_panel, text="✓ Ready to import images", 
                                    font=("Arial", 9), bg=self.BG_COLOR, fg="#2E7D32")
        self.status_label.pack(padx=0, pady=3, anchor=tk.W, fill=tk.X)
        
        # Import button
        import_btn = tk.Button(center_panel, text="✅ IMPORT SELECTED IMAGES", 
                              command=self.import_images_threaded,
                              bg=self.SUCCESS_COLOR, fg="white", 
                              font=("Arial", 10, "bold"), relief=tk.RAISED,
                              height=2)
        import_btn.pack(padx=0, pady=8, fill=tk.X)
        
        # RIGHT PANEL - Preview
        right_panel = tk.LabelFrame(main_frame, text="👁️ Preview", 
                                   font=("Arial", 11, "bold"), bg=self.BG_COLOR,
                                   fg=self.PRIMARY_COLOR, padx=10, pady=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5, ipadx=5)
        
        # Preview image
        preview_img_frame = tk.Frame(right_panel, bg="#333", relief=tk.SUNKEN, bd=2)
        preview_img_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=8)
        
        self.preview_label = tk.Label(preview_img_frame, bg="black", text="📸 No image", 
                                      fg="white", font=("Arial", 12))
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Preview info
        self.preview_info_label = tk.Label(right_panel, text="", font=("Arial", 9), 
                                          justify=tk.LEFT, bg=self.BG_COLOR, fg="#555555")
        self.preview_info_label.pack(padx=0, pady=5, anchor=tk.W, fill=tk.X)
        
        # Preview navigation
        nav_frame = tk.Frame(right_panel, bg=self.BG_COLOR)
        nav_frame.pack(padx=0, pady=8, fill=tk.X)
        
        prev_btn = tk.Button(nav_frame, text="⬅️ Prev", command=self.prev_preview, 
                            bg=self.PRIMARY_COLOR, fg="white",
                            font=("Arial", 9, "bold"), relief=tk.RAISED)
        prev_btn.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        next_btn = tk.Button(nav_frame, text="Next ➡️", command=self.next_preview, 
                            bg=self.PRIMARY_COLOR, fg="white",
                            font=("Arial", 9, "bold"), relief=tk.RAISED)
        next_btn.pack(side=tk.LEFT, padx=3, fill=tk.BOTH, expand=True)
        
        self.preview_counter = tk.Label(nav_frame, text="0/0", font=("Arial", 9, "bold"),
                                       bg=self.BG_COLOR, fg="#1976D2")
        self.preview_counter.pack(side=tk.LEFT, padx=8)
        
    def refresh_person_list(self):
        """Refresh the list of existing people"""
        self.person_listbox.delete(0, tk.END)
        people = []
        
        if os.path.exists(self.faces_dir):
            people = sorted([d for d in os.listdir(self.faces_dir) 
                           if os.path.isdir(os.path.join(self.faces_dir, d))])
        
        for person in people:
            self.person_listbox.insert(tk.END, person)
        
        # Update dropdown
        self.person_dropdown['values'] = people
        
    def on_person_from_list(self, event):
        """Handle selection from person listbox"""
        selection = self.person_listbox.curselection()
        if selection:
            person = self.person_listbox.get(selection[0])
            self.selected_person.set(person)
            self.on_person_selected()
    
    def on_person_selected(self):
        """Handle person selection"""
        person = self.selected_person.get()
        if not person:
            self.person_info_label.config(text="No person selected")
            return
        
        person_path = os.path.join(self.faces_dir, person)
        if os.path.exists(person_path):
            num_files = len([f for f in os.listdir(person_path) 
                           if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
            self.person_info_label.config(text=f"👤 {person}\n📸 Images: {num_files}")
        
    def view_student_data(self):
        """Open a window to view all student data"""
        # Create a new window
        data_window = tk.Toplevel(self.root)
        data_window.title("📊 All Student Data")
        data_window.geometry("600x500")
        data_window.minsize(500, 300)
        
        # Configure window
        data_window.configure(bg=self.BG_COLOR)
        
        # Title
        title_label = tk.Label(data_window, text="📊 All Currently Added Students", 
                              font=("Arial", 14, "bold"), bg=self.BG_COLOR, fg="#1565C0")
        title_label.pack(pady=10)
        
        # Get all students data
        students_data = []
        total_images = 0
        
        if os.path.exists(self.faces_dir):
            for person in sorted(os.listdir(self.faces_dir)):
                person_path = os.path.join(self.faces_dir, person)
                if os.path.isdir(person_path):
                    images = [f for f in os.listdir(person_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                    num_images = len(images)
                    students_data.append((person, num_images))
                    total_images += num_images
        
        # Create scrollable frame with Treeview
        frame = tk.Frame(data_window, bg=self.BG_COLOR)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for better table display
        columns = ("Name", "Images")
        tree = ttk.Treeview(frame, columns=columns, height=15, show='headings')
        
        # Define column headings and widths
        tree.heading('Name', text='Student Name')
        tree.heading('Images', text='Face Images')
        tree.column('Name', width=400, anchor=tk.W)
        tree.column('Images', width=100, anchor=tk.CENTER)
        
        # Add data to tree
        for idx, (name, count) in enumerate(students_data, 1):
            tree.insert('', tk.END, values=(name, count))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Summary frame
        summary_frame = tk.Frame(data_window, bg=self.BG_COLOR)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        summary_text = f"Total Students: {len(students_data)} | Total Images: {total_images}"
        summary_label = tk.Label(summary_frame, text=summary_text, 
                                font=("Arial", 10, "bold"), bg=self.BG_COLOR, 
                                fg=self.PRIMARY_COLOR)
        summary_label.pack(anchor=tk.W)
        
        # Close button
        close_btn = tk.Button(data_window, text="Close", command=data_window.destroy,
                             bg=self.PRIMARY_COLOR, fg="white",
                             font=("Arial", 9, "bold"), relief=tk.RAISED)
        close_btn.pack(pady=10, fill=tk.X, padx=10)
        
    def create_new_person(self):
        """Create a new person"""
        person_name = self.new_person_entry.get().strip()
        
        if not person_name:
            messagebox.showwarning("Warning", "Please enter a person name")
            return
        
        person_path = os.path.join(self.faces_dir, person_name)
        
        if os.path.exists(person_path):
            messagebox.showinfo("Info", f"'{person_name}' already exists")
            self.selected_person.set(person_name)
        else:
            os.makedirs(person_path, exist_ok=True)
            messagebox.showsuccess("Success", f"Created person: '{person_name}'")
            self.new_person_entry.delete(0, tk.END)
        
        self.refresh_person_list()
        self.on_person_selected()
    
    def browse_images(self):
        """Browse and select multiple image files"""
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_files_listbox()
            self.current_preview_index = 0
            self.show_preview()
    
    def browse_folder(self):
        """Browse and select all images from a folder"""
        folder = filedialog.askdirectory(title="Select Folder with Images")
        
        if folder:
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP')
            files = [os.path.join(folder, f) for f in os.listdir(folder) 
                    if f.lower().endswith(image_extensions)]
            
            if not files:
                messagebox.showwarning("Warning", "No images found in folder")
                return
            
            self.selected_files = sorted(files)
            self.update_files_listbox()
            self.current_preview_index = 0
            self.show_preview()
            messagebox.showinfo("Success", f"Found {len(files)} images")
    
    def update_files_listbox(self):
        """Update the files listbox"""
        self.files_listbox.delete(0, tk.END)
        for filepath in self.selected_files:
            filename = os.path.basename(filepath)
            self.files_listbox.insert(tk.END, filename)
    
    def clear_selection(self):
        """Clear all selected files"""
        self.selected_files = []
        self.update_files_listbox()
        self.current_preview_index = 0
        self.preview_label.config(text="No image selected", image='')
        self.preview_info_label.config(text="")
        self.preview_counter.config(text="0/0")
    
    def remove_selected_file(self):
        """Remove selected file from list"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_files.pop(index)
            self.update_files_listbox()
            self.current_preview_index = min(self.current_preview_index, len(self.selected_files) - 1)
            if self.selected_files:
                self.current_preview_index = max(0, self.current_preview_index)
            self.show_preview()
    
    def show_preview(self):
        """Show image preview"""
        if not self.selected_files:
            self.preview_label.config(text="No images selected", image='')
            self.preview_info_label.config(text="")
            self.preview_counter.config(text="0/0")
            return
        
        self.current_preview_index = min(self.current_preview_index, len(self.selected_files) - 1)
        filepath = self.selected_files[self.current_preview_index]
        
        try:
            # Load and display image
            img = Image.open(filepath)
            img.thumbnail((350, 400))
            photo = ImageTk.PhotoImage(img)
            
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
            
            # Get face detection info
            cv_img = cv2.imread(filepath)
            if cv_img is not None:
                gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                filesize = os.path.getsize(filepath) / 1024  # KB
                height, width = cv_img.shape[:2]
                
                info_text = f"File: {os.path.basename(filepath)}\n"
                info_text += f"Size: {filesize:.1f} KB | {width}x{height}px\n"
                info_text += f"Faces detected: {len(faces)}"
                
                self.preview_info_label.config(text=info_text)
            
            self.preview_counter.config(text=f"{self.current_preview_index + 1}/{len(self.selected_files)}")
        
        except Exception as e:
            self.preview_label.config(text=f"Error loading image: {str(e)}", image='')
            self.preview_counter.config(text=f"{self.current_preview_index + 1}/{len(self.selected_files)}")
    
    def next_preview(self):
        """Show next preview"""
        if self.selected_files:
            self.current_preview_index = (self.current_preview_index + 1) % len(self.selected_files)
            self.show_preview()
    
    def prev_preview(self):
        """Show previous preview"""
        if self.selected_files:
            self.current_preview_index = (self.current_preview_index - 1) % len(self.selected_files)
            self.show_preview()
    
    def import_images_threaded(self):
        """Import images in a separate thread"""
        person = self.selected_person.get()
        
        if not person:
            messagebox.showwarning("Warning", "Please select or create a person")
            return
        
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select images to import")
            return
        
        self.import_thread = threading.Thread(target=self.import_images, daemon=True)
        self.import_thread.start()
    
    def import_images(self):
        """Import selected images for the person"""
        person = self.selected_person.get()
        person_path = os.path.join(self.faces_dir, person)
        
        os.makedirs(person_path, exist_ok=True)
        
        total_files = len(self.selected_files)
        successful = 0
        skipped = 0
        
        self.status_label.config(text="Importing images...", fg="orange")
        
        for idx, filepath in enumerate(self.selected_files):
            try:
                # Update progress
                progress = int((idx / total_files) * 100)
                self.progress_var.set(progress)
                self.root.update()
                
                # Read and validate image
                img = cv2.imread(filepath)
                if img is None:
                    LOGGER.warning(f"Skipped (unable to read): {filepath}")
                    skipped += 1
                    continue
                
                # Detect faces
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 0:
                    LOGGER.warning(f"Skipped (no faces detected): {filepath}")
                    skipped += 1
                    continue
                
                # Copy file with timestamp
                filename = os.path.basename(filepath)
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"{name}_{timestamp}{ext}"
                
                dest_path = os.path.join(person_path, new_filename)
                shutil.copy2(filepath, dest_path)
                
                LOGGER.info(f"Imported: {new_filename}")
                successful += 1
            
            except Exception as e:
                LOGGER.error(f"Error importing {filepath}: {e}")
                skipped += 1
        
        # Final update
        self.progress_var.set(100)
        
        message = f"✅ Import Complete!\n\n"
        message += f"Successful: {successful}\n"
        message += f"Skipped: {skipped}\n"
        message += f"Total: {total_files}"
        
        if successful > 0:
            self.status_label.config(text=f"Import complete! {successful} images added", fg="green")
            messagebox.showinfo("Success", message)
            self.clear_selection()
            self.on_person_selected()
        else:
            self.status_label.config(text="Import failed - no valid images", fg="red")
            messagebox.showerror("Error", message)
        
        self.progress_var.set(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageImportTool(root)
    root.mainloop()
