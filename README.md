# Face Detection and Recognition System

A Python application for face detection and recognition using OpenCV.

## Quick Start Guide

### 1. Run the installer

```
python install_dependencies.py
```

This will open a GUI installer that helps install the needed packages.

### 2. Choose the right version for your system

- **Simple Detection** - Just detects faces (works on all systems)
- **Full Recognition** - Detects AND recognizes faces with names (requires additional dependencies)

## Usage - Full Recognition System

1. Run the recognition app:
   ```
   python face_recognition_app_simplified.py
   ```

2. Capture face samples:
   - Enter a person's name
   - Click "Capture Samples"
   - Press 'c' key when the face is correctly framed (10 samples needed)
   - Press 'q' key to exit capture mode

3. Train the model:
   - Click "Train Recognition Model"
   - Wait for training to complete

4. Start recognition:
   - Click "Start Recognition"
   - Detected faces will show with recognized names

## Usage - Simple Detection

If the full system doesn't work, use the simplified detection:

```
python simple_detection_only.py
```

This just detects faces (no recognition or names) and works without opencv-contrib.

## Troubleshooting

### Camera Issues

- Try different camera indexes (0, 1, 2, 3) in the dropdown
- Use the "Test Camera" button to verify your camera works
- Check Windows privacy settings to ensure camera access is allowed

### Installation Problems

If automatic installation doesn't work:

1. Manually install dependencies:
   ```
   pip install opencv-python numpy pillow
   ```

2. For full recognition features:
   ```
   pip install opencv-contrib-python
   ```

3. If that fails, try installing an older version:
   ```
   pip install opencv-contrib-python==4.5.5.64
   ```

### Runtime Errors

- **AttributeError with face recognition**: Your OpenCV doesn't have contrib modules installed
- **Could not open camera**: Try a different camera index or check if another app is using the camera
- **Application crashes**: Try the simple detection version which has fewer dependencies 