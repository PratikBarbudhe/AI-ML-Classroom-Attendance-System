import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

def install_package(package, progress_var=None, status_label=None):
    """Install a package using pip"""
    try:
        if status_label:
            status_label.config(text=f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        if status_label:
            status_label.config(text=f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        if status_label:
            status_label.config(text=f"Failed to install {package}")
        return False

def main():
    root = tk.Tk()
    root.title("Face Recognition - Install Dependencies")
    root.geometry("600x400")
    
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = tk.Label(main_frame, text="Install Dependencies", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)
    
    # Description
    description = tk.Label(main_frame, text="This will install the required packages for the face recognition system.")
    description.pack(pady=10)
    
    # Version selection
    version_frame = tk.LabelFrame(main_frame, text="Select Version")
    version_frame.pack(fill=tk.X, pady=10)
    
    version_var = tk.StringVar(value="simple")
    tk.Radiobutton(version_frame, text="Simple Detection Only (recommended)", 
                  variable=version_var, value="simple").pack(anchor=tk.W, padx=10, pady=5)
    tk.Radiobutton(version_frame, text="Full Recognition System (requires OpenCV contrib)", 
                  variable=version_var, value="full").pack(anchor=tk.W, padx=10, pady=5)
    
    # Progress frame
    progress_frame = tk.LabelFrame(main_frame, text="Installation Progress")
    progress_frame.pack(fill=tk.X, pady=10)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, padx=10, pady=10)
    
    status_label = tk.Label(progress_frame, text="Ready to install...")
    status_label.pack(padx=10, pady=5)
    
    # Install button
    def start_installation():
        version = version_var.get()
        install_button.config(state=tk.DISABLED)
        
        packages = ["numpy", "pillow", "opencv-python"]
        if version == "full":
            packages.append("opencv-contrib-python")
        
        total_packages = len(packages)
        
        for i, package in enumerate(packages):
            progress_var.set((i / total_packages) * 100)
            root.update()
            
            success = install_package(package, progress_var, status_label)
            if not success:
                messagebox.showerror("Installation Error", f"Failed to install {package}. Please try manually.")
                break
        
        progress_var.set(100)
        status_label.config(text="Installation completed!")
        messagebox.showinfo("Installation Complete", "Dependencies installed successfully.\n\n" + 
                          ("Run face_recognition_app_simplified.py for the full version\n" if version == "full" else "") +
                          "Run simple_detection_only.py for the simple version.")
        install_button.config(state=tk.NORMAL)
    
    install_button = tk.Button(main_frame, text="Install Dependencies", command=start_installation)
    install_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main() 