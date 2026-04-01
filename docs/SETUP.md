# 🚀 Complete Project Setup & Installation Guide

## Project Overview

**AI Classroom Attendance System** - A Python application that uses face detection and recognition to automatically record student attendance.

### Key Features
- ✅ Face detection using deep learning
- ✅ Face recognition with trained models
- ✅ Automatic attendance recording with deduplication
- ✅ CSV export functionality
- ✅ SQLite database for record-keeping
- ✅ GUI application for easy management

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.7 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Storage**: 500 MB for dependencies + space for face samples
- **Webcam**: USB webcam or built-in camera

### Recommended Setup
- **Windows 10/11** with latest updates
- **Python 3.9+**
- **8+ GB RAM**
- **USB 3.0 camera or better**

---

## 🔧 Step-by-Step Installation

### Step 1: Verify Python Installation

Open command prompt/terminal and check Python version:

```bash
python --version
```

**Expected output**: `Python 3.7.0` or higher

If Python is not installed:
- **Windows**: Download from [python.org](https://www.python.org/downloads)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt-get install python3 python3-pip`

---

### Step 2: Clone/Download Project

**Option A: Using Git** (if you have git installed)
```bash
git clone <repository-url>
cd AI-ML-Classroom-Attendance-System
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to your desired location
3. Open terminal/command prompt in the extracted folder

---

### Step 3: Create Virtual Environment (Recommended)

Virtual environments isolate project dependencies from your system Python.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**After activation, your terminal should show `(venv)` prefix**

---

### Step 4: Install Dependencies

**Standard Installation** (Recommended)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**If you face issues with `face_recognition`:**

Windows users might need special setup. Try:
```bash
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

If still failing, try older version:
```bash
pip install face_recognition==1.3.0
```

**Check Installation:**
```bash
python -c "import face_recognition; import cv2; print('All dependencies installed successfully!')"
```

---

### Step 5: Verify Camera Access

**Windows:**
1. Settings → Privacy & Security → Camera
2. Ensure camera access is enabled
3. No other app should be using the camera

**macOS:**
1. System Preferences → Security & Privacy → Camera
2. Grant access to the application

**Linux:**
```bash
ls /dev/video*  # Check if camera device exists
```

**Test Camera with Python:**
```bash
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    cap.release()
    if ret:
        print('✓ Camera working!')
    else:
        print('✗ Camera found but cannot read frames')
else:
    print('✗ Camera not found')
"
```

---

### Step 6: Verify Project Structure

After setup, your project folder should look like:

```
AI-ML-Classroom-Attendance-System/
├── config.py                          ✓ Configuration
├── utils.py                           ✓ Utilities
├── face_utils.py                      ✓ Face functions
├── camera_utils.py                    ✓ Camera functions
├── attendance_utils.py                ✓ Attendance database
├── face_recognition_app_simplified.py ✓ Main application
├── requirements.txt                   ✓ Dependencies
├── README.md                          ✓ Original docs
├── SUMMARY.md                         ✓ Improvement summary
├── IMPROVEMENTS.md                    ✓ Detailed improvements
├── QUICK_START.md                     ✓ Quick start guide
├── BEST_PRACTICES.md                  ✓ Code standards
├── SETUP.md                           ✓ This file
└── data/
    ├── faces/                         (Empty, will be filled)
    ├── models/                        (Empty, will be filled)
    └── attendance/
        └── exports/                   (For CSV exports)
```

---

## 🎯 How to Start the Application

### Quick Start (First Time)

```bash
# 1. Activate virtual environment (if created)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 2. Run the application
python face_recognition_app_simplified.py
```

### What You'll See

The application will open with a GUI window showing:
- **Capture Samples** panel - for recording face samples
- **Train Recognition Model** section - for training
- **Start Recognition** area - for real-time face detection
- **Export Attendance** button - for CSV export

---

## 📸 First Time Usage Workflow

### Phase 1: Capture Face Samples

**For Each Person:**

1. **Enter Person's Name**
   - Example: "John Doe"
   - Must be 2-100 characters
   - Letters, numbers, spaces, hyphens, apostrophes only

2. **Click "Capture Samples"**
   - Camera window opens
   - Face detection draws rectangles around detected faces

3. **Position Your Face**
   - Look directly at camera
   - Good lighting is important (avoid backlight)
   - Keep face within the rectangle

4. **Capture Sample**
   - Press 'c' key when face is properly positioned
   - Repeat for 30 samples (system needs this for accuracy)
   - Progress shown: "Captured: X/30"

5. **Exit Capture**
   - Press 'q' key when done
   - Samples saved in `data/faces/PersonName/`

**Recommended Settings:**
- Lighting: Bright, indirect light (avoid shadows)
- Distance: 30-60 cm from camera
- Angles: Capture from multiple angles (front, slightly left, slightly right)
- Expressions: Mix of neutral and natural expressions
- Samples: Minimum 30, ideal 50+

### Phase 2: Train Recognition Model

1. **Click "Train Recognition Model"**
   - System processes all captured face samples
   - Creates face encodings for each person
   - Saves model to `data/models/face_model.pkl`
   - Shows progress: "Model trained: X encodings from Y people"

2. **Wait for Training**
   - First training might take 1-5 minutes (one-time)
   - Subsequent trainings are faster

3. **Verify Success**
   - Status shows successful training message
   - Model file created in data/models/

### Phase 3: Start Recognition & Attendance

1. **Click "Start Recognition"**
   - Webcam activates
   - Real-time face detection begins
   - Recognized faces show names

2. **How Recognition Works**
   - Detects faces in frame
   - Compares with trained faces
   - Marks attendance automatically
   - Deduplicates (won't record same person twice in 60 seconds)

3. **View Attendance**
   - Check "Today's Attendance" status
   - Shows: Name, Time, Confidence

### Phase 4: Export Attendance

1. **Click "Export Today CSV"**
   - Creates CSV file with all attendance records
   - Saved in `data/attendance/exports/`
   - Filename: `attendance_YYYYMMDD_HHMMSS.csv`

2. **CSV Contents**
   - Name - Student name
   - Time - Date and time recognized
   - Confidence - Recognition confidence (0-1)
   - Source - Device source

---

## 🔧 Configuration & Customization

All settings are in `config.py`:

```python
# Change number of samples required
FACE_SAMPLES_REQUIRED = 30  # Default 30

# Change face matching sensitivity
FACE_MATCH_TOLERANCE = 0.6  # Lower = stricter

# Change deduplication time window
ATTENDANCE_MIN_INTERVAL = 60  # seconds

# Change camera
DEFAULT_CAMERA_INDEX = 0  # Try 0, 1, 2, 3...

# Change camera resolution
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
```

After changing settings, restart the application.

---

## 🆘 Troubleshooting

### Camera Not Found

**Problem**: "Could not open camera"

**Solutions**:
1. Check if another app is using camera
2. Test different camera indices:
   ```python
   from camera_utils import get_available_cameras
   cameras = get_available_cameras()
   print(cameras)  # Shows available camera indices
   ```
3. Update camera driver
4. Check Windows Privacy Settings
5. Restart application

### No Faces Detected

**Problem**: Camera works but no faces in rectangles

**Solutions**:
1. Check lighting - needs to be bright
2. Move closer to camera (30-60 cm)
3. Face should be 20% of frame
4. Try different angle
5. Check webcam resolution

### Face Recognition Not Working

**Problem**: Faces detected but no names shown

**Solutions**:
1. Ensure model is trained (click "Train Model")
2. Need at least 10 samples per person
3. Use 30+ samples for better accuracy
4. Adjust `FACE_MATCH_TOLERANCE` lower (stricter)
5. Check that faces are clearly visible in samples

### "face_recognition not installed" Error

**Problem**: Module import error

**Solutions**:
```bash
# Option 1: Reinstall
pip uninstall face_recognition -y
pip install face_recognition==1.3.0

# Option 2: Try dlib separately
pip install dlib
pip install face_recognition

# Option 3: Check Python version
python --version  # Should be 3.7+
```

### Database Corrupted

**Problem**: Attendance records not showing

**Solutions**:
```bash
# Backup current database
copy data\attendance\attendance.db data\attendance\attendance.db.backup

# Delete corrupted database (will create new one)
del data\attendance\attendance.db

# Restart application
```

### Low Recognition Accuracy

**Problem**: System recognizes wrong person or "Unknown" for known faces

**Solutions**:
1. Capture more samples (50+)
2. Capture from different angles
3. Vary lighting conditions in samples
4. Adjust `FACE_MATCH_TOLERANCE` in config.py (try 0.5 or 0.55)
5. Retrain model
6. Make sure capture and recognition are in same lighting

---

## 📊 Project Structure Deep Dive

### Core Application Files

**`face_recognition_app_simplified.py`**
- Main GUI application
- Handles user interactions
- Manages camera display
- Controls application flow

**`config.py`**
- All configuration constants
- Settings for face recognition
- Database paths
- Camera settings

### Utility Modules

**`face_utils.py`**
- Face capture operations
- Model training
- Face recognition
- Sample management

**`camera_utils.py`**
- Camera initialization
- Camera testing
- Available camera detection

**`attendance_utils.py`**
- Database operations
- Attendance recording
- CSV export
- Data queries

**`utils.py`**
- Input validation
- File operations
- Data processing
- Utility functions

### Data Directories

**`data/faces/`**
- Stores face samples for each person
- Structure: `data/faces/PersonName/sample1.jpg`, etc.
- Can be backed up safely

**`data/models/`**
- Stores trained models
- `face_model.pkl` - trained face encodings
- Can be shared between systems

**`data/attendance/`**
- SQLite database (`attendance.db`)
- Stores all recorded attendance
- CSV exports saved in `exports/`

---

## 🚀 Command Reference

### Essential Commands

```bash
# Start application
python face_recognition_app_simplified.py

# Check camera availability
python -c "from camera_utils import get_available_cameras; print(get_available_cameras())"

# Validate installation
python -c "import face_recognition, cv2, numpy; print('✓ All modules loaded')"

# Check database
python -c "from attendance_utils import AttendanceStore; a = AttendanceStore(); print(a.get_today_summary())"
```

### Development Commands

```bash
# Run with logging to file
python face_recognition_app_simplified.py > app.log 2>&1

# Interactive console
python
>>> from face_utils import FaceUtils
>>> fu = FaceUtils()
>>> fu.get_trained_people()
```

---

## 📝 Important Files Reference

| File | Purpose | Modify? |
|------|---------|---------|
| `config.py` | Settings | ✅ Yes, for customization |
| `face_recognition_app_simplified.py` | Main app | ⚠️ Only if you know what you're doing |
| `face_utils.py` | Face operations | ❌ No |
| `attendance_utils.py` | Database ops | ❌ No |
| `camera_utils.py` | Camera ops | ❌ No |
| `utils.py` | Utilities | ❌ No |
| `requirements.txt` | Dependencies | ❌ No |

---

## 🔐 Security & Best Practices

1. **Backup Regularly**
   ```bash
   # Backup face data and databases
   xcopy data data_backup /E /I
   ```

2. **Database Security**
   - Attendance database contains personal data
   - Keep `data/attendance/` secure
   - Regular backups recommended

3. **Face Sample Storage**
   - Face samples in `data/faces/` can be shared/backed up
   - Encrypted storage recommended for security
   - Regular cleanup of old samples

4. **Camera Privacy**
   - Ensure camera is only used during class time
   - Disable when not in use
   - Inform students about face recognition

---

## 📚 Additional Resources

- **README.md** - Original project information
- **SUMMARY.md** - Improvement summary
- **IMPROVEMENTS.md** - Detailed changes made
- **QUICK_START.md** - Quick code examples
- **BEST_PRACTICES.md** - Development standards

---

## ✅ Verification Checklist

Before using in production:

- [ ] Python 3.7+ installed
- [ ] All dependencies installed (`pip show face_recognition`)
- [ ] Camera working (`python confirm_camera_works.py`)
- [ ] Face detection working (capture 1-2 samples)
- [ ] Model training works
- [ ] Recognition working (recognizes trained face)
- [ ] Attendance recording in database
- [ ] CSV export working
- [ ] Data backed up safely

---

## 🆘 Getting Help

If you encounter issues:

1. Check **Troubleshooting** section above
2. Review **IMPROVEMENTS.md** for API details
3. Check **BEST_PRACTICES.md** for code standards
4. Review application logs in terminal
5. Check database integrity

---

## 📞 Support & Contact

For issues with:
- **Face recognition**: Check lighting, sample quality, tolerance settings
- **Camera**: Verify permissions, drivers, cable connections
- **Database**: Backup and delete `attendance.db`, app will create new one
- **Dependencies**: Reinstall from `requirements.txt`

---

## 🎓 Learning Path

**Week 1: Basic Setup**
- Install and verify system
- Capture first person's samples
- Train model
- Test recognition

**Week 2: Operation**
- Add multiple users
- Test daily attendance
- Export records
- Verify accuracy

**Week 3: Optimization**
- Tune Face Match Tolerance
- Capture additional samples if needed
- Analyze recognition accuracy
- Set up automated backups

**Week 4: Production**
- Full deployment
- Train staff
- Establish procedures
- Monitor system performance

---

## 📊 System Performance Notes

- **First model training**: 1-5 minutes (varies by system)
- **Recognition per frame**: 100-500ms (depends on frame count)
- **Database operations**: < 100ms (SQLite is fast)
- **Camera FPS**: 30 FPS (configurable)

---

## 🎉 Success Indicators

System is working correctly when:
- ✅ Camera window shows face rectangles
- ✅ Training completes without errors
- ✅ Faces are recognized with names
- ✅ Attendance recorded in database
- ✅ CSV exports successfully
- ✅ Stats show attendees

---

**Last Updated**: April 2026  
**Version**: 2.0 (Improved)  
**Status**: Production Ready ✓

For the latest updates, check the project repository.
