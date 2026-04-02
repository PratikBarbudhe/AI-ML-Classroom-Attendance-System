"""
Batch Image Import Script
Allows importing images for multiple people from a folder structure.
Useful when you have photos organized by person name.
"""

import os
import shutil
import cv2
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s"
)
LOGGER = logging.getLogger("batch_import")


class BatchImageImporter:
    def __init__(self, faces_dir="data/faces"):
        self.faces_dir = faces_dir
        os.makedirs(faces_dir, exist_ok=True)
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
    def import_from_directory_structure(self, source_dir):
        """
        Import images from a directory structure like:
        source_dir/
        ├── Person1/
        │   ├── photo1.jpg
        │   └── photo2.jpg
        ├── Person2/
        │   ├── photo1.jpg
        │   └── photo2.jpg
        """
        if not os.path.isdir(source_dir):
            LOGGER.error(f"Source directory not found: {source_dir}")
            return
        
        print("\n" + "="*70)
        print("🔄 BATCH IMAGE IMPORT")
        print("="*70)
        print(f"Source directory: {source_dir}\n")
        
        # Get all subdirectories (each represents a person)
        people_folders = [d for d in os.listdir(source_dir) 
                         if os.path.isdir(os.path.join(source_dir, d))]
        
        if not people_folders:
            print("❌ No person folders found in source directory")
            return
        
        print(f"Found {len(people_folders)} person folders:\n")
        for person in sorted(people_folders):
            print(f"  📁 {person}")
        
        print("\n" + "-"*70)
        
        total_imported = 0
        total_skipped = 0
        
        for person_folder in sorted(people_folders):
            person_name = person_folder
            source_person_dir = os.path.join(source_dir, person_folder)
            dest_person_dir = os.path.join(self.faces_dir, person_name)
            
            # Get all image files
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.JPG', '.JPEG', '.PNG', '.BMP')
            image_files = [f for f in os.listdir(source_person_dir) 
                          if os.path.isfile(os.path.join(source_person_dir, f)) and 
                          f.lower().endswith(image_extensions)]
            
            if not image_files:
                LOGGER.warning(f"No images found for {person_name}")
                continue
            
            os.makedirs(dest_person_dir, exist_ok=True)
            
            successful = 0
            skipped = 0
            
            print(f"\n📸 Importing images for: {person_name}")
            print(f"   Found {len(image_files)} image files")
            
            for idx, filename in enumerate(image_files, 1):
                filepath = os.path.join(source_person_dir, filename)
                
                try:
                    # Read and validate image
                    img = cv2.imread(filepath)
                    if img is None:
                        LOGGER.warning(f"   ❌ Skipped (cannot read): {filename}")
                        skipped += 1
                        continue
                    
                    # Detect faces
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    if len(faces) == 0:
                        LOGGER.warning(f"   ⚠️  Skipped (no faces): {filename}")
                        skipped += 1
                        continue
                    
                    # Copy file with timestamp
                    name, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    new_filename = f"{name}_{timestamp}{ext}"
                    
                    dest_path = os.path.join(dest_person_dir, new_filename)
                    shutil.copy2(filepath, dest_path)
                    
                    print(f"   ✅ {idx}/{len(image_files)}: {filename} [{len(faces)} face(s)]")
                    successful += 1
                
                except Exception as e:
                    LOGGER.error(f"Error importing {filename}: {e}")
                    skipped += 1
            
            print(f"   Result: {successful} imported, {skipped} skipped")
            
            total_imported += successful
            total_skipped += skipped
        
        print("\n" + "="*70)
        print("✅ BATCH IMPORT COMPLETE")
        print("="*70)
        print(f"Total Imported: {total_imported} images")
        print(f"Total Skipped:  {total_skipped} images")
        print(f"Total People:   {len(people_folders)}")
        print("="*70 + "\n")
        
        return total_imported, total_skipped
    
    def list_existing_people(self):
        """List existing people in faces directory"""
        people = [d for d in os.listdir(self.faces_dir) 
                 if os.path.isdir(os.path.join(self.faces_dir, d))]
        
        print("\n📋 Existing People in System:")
        print("-" * 50)
        
        for person in sorted(people):
            person_dir = os.path.join(self.faces_dir, person)
            num_images = len([f for f in os.listdir(person_dir) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
            print(f"  👤 {person}: {num_images} images")
        
        print("-" * 50 + "\n")
        return people
    
    def verify_imports(self):
        """Verify that imports were successful"""
        print("\n🔍 VERIFICATION REPORT")
        print("-" * 50)
        
        people = self.list_existing_people()
        
        total_images = 0
        for person in people:
            person_dir = os.path.join(self.faces_dir, person)
            num_images = len([f for f in os.listdir(person_dir) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
            total_images += num_images
        
        print(f"Total People:   {len(people)}")
        print(f"Total Images:   {total_images}")
        
        if total_images < 5:
            print("\n⚠️  WARNING: Very few images for training!")
            print("   Recommended minimum: 15-20 images per person")
        elif total_images < 50:
            print("\n⚠️  INFO: Consider importing more images for better accuracy")
        else:
            print("\n✅ Good number of images for training!")
        
        print("-" * 50 + "\n")


def main():
    import sys
    
    print("\n" + "="*70)
    print("📱 BATCH IMAGE IMPORT TOOL")
    print("="*70 + "\n")
    
    importer = BatchImageImporter()
    
    print("This tool imports images organized by person folder structure.")
    print("\nExample directory structure:")
    print("""
    C:/Phone_Images/
    ├── Pratiksha/
    │   ├── photo1.jpg
    │   ├── photo2.jpg
    │   └── photo3.jpg
    ├── John Smith/
    │   ├── image1.jpg
    │   └── image2.jpg
    └── Rupali Mam/
        ├── 1.jpg
        └── 2.jpg
    """)
    
    print("-" * 70)
    
    # Show existing people
    importer.list_existing_people()
    
    # Get source directory
    print("Enter the source directory path containing person folders:")
    print("(Example: C:\\Phone_Images or /home/user/phone_images)")
    
    source_dir = input("\n📁 Source directory: ").strip()
    
    if not source_dir or source_dir.lower() in ['q', 'quit', 'cancel']:
        print("\n✖️  Cancelled")
        return
    
    # Expand path
    source_dir = os.path.expanduser(source_dir)
    
    if not os.path.isdir(source_dir):
        print(f"\n❌ Error: Directory not found: {source_dir}")
        return
    
    # Confirm
    print(f"\n✓ Source directory: {source_dir}")
    confirm = input("Proceed with batch import? (yes/no): ").strip().lower()
    
    if confirm not in ['y', 'yes', 'ok']:
        print("\n✖️  Cancelled")
        return
    
    # Import
    importer.import_from_directory_structure(source_dir)
    
    # Verify
    importer.verify_imports()
    
    print("📝 Next steps:")
    print("   1. Run face_recognition_app_simplified.py")
    print("   2. Click 'Train Model' to train with imported images")
    print("   3. Use 'Start Attendance' to recognize people\n")


if __name__ == "__main__":
    main()
