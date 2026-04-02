# 📱 Image Import Tool - User Guide

## Overview
The **Image Import Tool** allows you to easily import high-quality face images from your phone, camera, or any other source. This significantly improves the accuracy of the face recognition system compared to laptop camera captures.

## Why Import Images Instead of Capturing from Laptop?
✅ **Better Quality** - Phone cameras often have better resolution and lighting  
✅ **Better Angles** - Capture faces from different angles for improved recognition  
✅ **Better Conditions** - Take photos in optimal lighting conditions  
✅ **Batch Import** - Add multiple images at once  
✅ **Flexibility** - Use existing photos or take new ones with your phone  

## Getting Started

### Step 1: Run the Import Tool
```bash
python image_import_tool.py
```

A new window will open with the Image Import Tool interface.

### Step 2: Select or Create a Person

#### Option A: Select Existing Person
1. Look at the **left panel** under "📁 Existing Faces"
2. Click on any person's name in the list
3. Their info will appear above

#### Option B: Create New Person
1. Type the person's name in the "Create New Person" field
2. Click the **Create** button
3. The person will appear in the existing faces list

**Examples of good person names:**
- `John Smith`
- `Pratiksha`
- `Rupali Mam`
- `Student ID: 12345`

### Step 3: Select Images to Import

#### Option A: Select Individual Images
1. Click **📂 Browse Images** button
2. Navigate to folder with your phone photos
3. Select one or more images (hold Ctrl to select multiple)
4. Click Open
5. Selected images will appear in the file list

#### Option B: Import Entire Folder
1. Click **📁 Browse Folder** button
2. Navigate to the folder containing all your phone photos
3. Click "Select Folder"
4. All images in that folder will be selected

### Step 4: Preview Images

- **Preview Panel** on the right shows each image
- Use **⬅️ Prev** and **Next ➡️** buttons to navigate
- Preview shows:
  - File name
  - File size and dimensions
  - Number of faces detected in the image
- ❌ Images with **0 faces detected** will be skipped during import

### Step 5: Review and Adjust Selection

**To remove an image:**
1. Click it in the file list
2. Click **❌ Remove Selected**

**To clear all selected images:**
- Click **🗑️ Clear List**

### Step 6: Import Images

1. Make sure person is selected
2. Make sure images are selected
3. Click **✅ Import Selected Images**
4. Wait for import to complete - progress bar shows status
5. Success message will show:
   - How many images were imported
   - How many were skipped (no faces detected)

## Understanding the Import Process

### What Happens During Import:
1. ✅ Each image is read from your phone folder
2. ✅ Face detection runs - images without faces are skipped
3. ✅ Valid images are copied to the person's face folder
4. ✅ Files are renamed with timestamps to avoid conflicts
5. ✅ Images are ready for the face recognition model

### Example Import Result:
```
Before Import:
data/faces/John Smith/  (empty)

After Importing 5 Photos:
data/faces/John Smith/
├── photo1_20260402_143022.jpg
├── photo2_20260402_143035.jpg
├── photo3_20260402_143048.jpg
├── photo4_20260402_143101.jpg
└── photo5_20260402_143114.jpg
```

## Tips for Best Results

### 1. Image Quality
- Use at least **640x480** resolution
- Ensure face is **as large and clear** as possible
- **Avoid blurry** images

### 2. Variety
- Capture **multiple angles**: front, left 30°, right 30°
- Different **lighting conditions**: natural light, indoor, low light
- Different **expressions**: neutral, slight smile
- Different **distances**: close and far
- **Different clothing** if possible

### 3. Batch Import
- Organize phone photos into folders by person:
  ```
  Phone/Downloads/
  ├── John_Smith/  (10+ photos)
  ├── Pratiksha/   (8 photos)
  └── Rupali_Mam/  (6 photos)
  ```
- Use "Browse Folder" to import all at once

### 4. Recommended Minimum
- At least **15-20 images** per person for best accuracy
- Higher quality > higher quantity
- If accuracy is low, import more images

## Workflow Example

Here's a typical workflow:

1. **On Your Phone:**
   - Transfer photos from phone to laptop
   - Organize into folders: `C:\Phone_Images\Students\`

2. **In Import Tool:**
   - Open Image Import Tool
   - Create person: "Student - Pratiksha"
   - Browse folder: `C:\Phone_Images\Students\Pratiksha`
   - See 12 images selected
   - Use arrow buttons to preview and verify
   - Click Import
   - See "12 images imported successfully"

3. **Back in Main App:**
   - Train the face recognition model with new images
   - Run attendance system with improved accuracy

## Troubleshooting

### Issue: "No images found in folder"
- ✅ Make sure you selected a folder (not a file)
- ✅ Ensure folder contains `.jpg`, `.jpeg`, `.png`, or `.bmp` files
- ✅ Check file extensions are correct

### Issue: "Images skipped - no faces detected"
- ✅ Image quality is too low - try clearer photos
- ✅ Face is too small - take closer photos
- ✅ Photo is blurry - use steady hands or tripod
- ✅ Wrong file format - verify files are valid images

### Issue: "Permission denied when copying"
- ✅ Close the file in other applications
- ✅ Make sure the person folder exists
- ✅ Run with administrator privileges if needed

### Issue: Images not appearing after import
- ✅ Refresh the person list - click **🔄 Refresh**
- ✅ Check person name spelling matches exactly
- ✅ Look directly in `data/faces/<PersonName>/` folder

## Integration with Main App

Once you've imported images:

1. **Train the Model:**
   - Open `face_recognition_app_simplified.py`
   - Click "Train Model" button
   - Model learns from all imported images

2. **Run Attendance:**
   - Click "Start Attendance" or camera button
   - System will recognize people with high accuracy

## File Organization

Your imported images are stored in:
```
data/
└── faces/
    ├── Pratiksha/
    │   ├── photo_20260402_143022.jpg
    │   ├── photo_20260402_143035.jpg
    │   └── ... (all your imported images)
    ├── Student - John/
    └── Rupali Mam/
        └── ... (images for this person)
```

## Batch Processing (Advanced)

If you have many people to import, use the batch script:

```bash
python batch_import.py
```

This will guide you through importing images for multiple people at once.

## Support

For issues or improvements, check:
- `docs/IMPROVEMENTS.md` - planned features
- `README.md` - general project info
- `logs/` folder - check for error messages
