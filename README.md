# 🎯 AI Classroom Attendance System

A Python face recognition system that automatically tracks student attendance in classrooms using OpenCV and deep learning.

## ✨ Production Ready - v2.0

**Status**: ✅ Clean, Organized, Production-Ready

---

## 🚀 Quick Start (5 Minutes)

### One-Line Setup (Windows)
```bash
python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python face_recognition_app_simplified.py
```

### One-Line Setup (Mac/Linux)
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python3 face_recognition_app_simplified.py
```

### Step-by-Step Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python face_recognition_app_simplified.py
```

👉 **[START_HERE.md](START_HERE.md)** has more options and detailed instructions.

---

## 📁 Project Structure

```
├── face_recognition_app_simplified.py    ← RUN THIS
├── config.py                             ← Settings
├── utils.py                              ← Utilities
├── face_utils.py                         ← Face operations
├── camera_utils.py                       ← Camera access
├── attendance_utils.py                   ← Database
├── requirements.txt                      ← Dependencies
├── README.md                             ← This file
├── START_HERE.md                         ← Quick start guide
├── docs/
│   └── SETUP.md                          ← Detailed setup
└── data/                                 ← Auto-created
    ├── faces/                            ← Face samples
    ├── models/                           ← Trained models
    └── attendance/                       ← Database
```

---

## ✨ Features

✅ **Face Detection** - Real-time face detection  
✅ **Face Recognition** - High-accuracy identification  
✅ **Attendance Tracking** - Automatic recording  
✅ **Database** - SQLite storage  
✅ **Data Export** - CSV exports  
✅ **Configuration** - Centralized settings  
✅ **Validation** - Input validation  
✅ **Logging** - Error management  

---

## 💻 How to Use

1. **Add Person** → Enter name → Click "Capture Samples"
2. **Capture** → Press 'c' 30 times (good lighting)
3. **Train** → Click "Train Recognition Model" (1-5 min)
4. **Test** → Click "Start Recognition"
5. **Export** → Click "Export Today CSV"

---

## ⚙️ Configuration

Edit `config.py`:

```python
FACE_SAMPLES_REQUIRED = 30          # Samples per person
FACE_MATCH_TOLERANCE = 0.6          # Recognition sensitivity (lower = stricter)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
DEFAULT_CAMERA_INDEX = 0            # Which camera to use
```

---

## 📋 Requirements

- Python 3.7+
- Webcam/camera
- 1 GB free space
- Dependencies auto-installed via `pip install -r requirements.txt`

---

## 🆘 Troubleshooting

**Camera not found?**
- Verify camera is connected
- Try changing `DEFAULT_CAMERA_INDEX` in `config.py`

**Poor recognition?**
- Use better lighting
- Add more samples (50+)
- Reduce `FACE_MATCH_TOLERANCE` for stricter matching

**Installation issues?**
- Use Python 3.7+
- Use virtual environment
- Run: `pip install --upgrade pip`

📖 **For detailed help**: See `docs/SETUP.md`

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| [START_HERE.md](START_HERE.md) | Quick start guide |
| [docs/SETUP.md](docs/SETUP.md) | Detailed step-by-step |
| [README.md](README.md) | This file |

---

## 🎯 Summary

Your project is clean, organized, and ready to use!

**Next Step**: Run the quick start command above or open [START_HERE.md](START_HERE.md) for detailed instructions. 🚀
