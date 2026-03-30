# Face Detection and Recognition System

A Python application for classroom-oriented face detection and recognition using OpenCV.

## Quick Start Guide

### 1. Run the installer

```bash
python install_dependencies.py
```

This will open a GUI installer that helps install the needed packages.

### 2. Choose the right mode in installer

- **Simple Detection** - just detects faces (most compatible)
- **Recognition (LBPH/OpenCV contrib)** - detects and recognizes faces with names (recommended)
- **Advanced Recognition (face_recognition + dlib)** - highest accuracy path, requires dlib build support

## Usage - Recognition (LBPH) System

1. Run the recognition app:

   ```bash
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

## Usage - Advanced Recognition (face_recognition + dlib)

If you installed advanced dependencies:

```bash
python face_recognition_app.py
```

## Usage - Simple Detection

If recognition mode doesn't work, use detection-only mode:

```bash
python simple_detection_only.py
```

This only detects faces (no recognition or names) and works without OpenCV contrib.

## Troubleshooting

### Camera Issues

- Try different camera indexes (0, 1, 2, 3) in the dropdown
- Use the "Test Camera" button to verify your camera works
- Check Windows privacy settings to ensure camera access is allowed

### Installation Problems

If automatic installation doesn't work:

1. Manually install base dependencies:

   ```bash
   pip install opencv-python numpy pillow setuptools
   ```

2. For LBPH recognition features:

   ```bash
   pip install opencv-contrib-python
   ```

3. For advanced recognition features:

   ```bash
   pip install dlib face-recognition
   ```

4. If `opencv-contrib-python` fails, try an older version:

   ```bash
   pip install opencv-contrib-python==4.5.5.64
   ```

### Runtime Errors

- **AttributeError with face recognition**: OpenCV contrib modules are missing
- **dlib install fails**: use LBPH mode (`face_recognition_app_simplified.py`) instead
- **Could not open camera**: Try a different camera index or check if another app is using the camera
- **Application crashes**: Try the simple detection version which has fewer dependencies
