# 🚀 Quick Start Guide

## ✨ Your Project is Now Clean & Ready!

### ✅ What Just Happened

**Cleaned Up**:
- ✓ Deleted 6 unused/obsolete files
- ✓ Organized documentation in `docs/` folder
- ✓ Project is now production-ready

### 📁 Current Clean Structure

```
AI-ML-Classroom-Attendance-System/
├── 🎯 APPLICATION
│   └── face_recognition_app_simplified.py    ← RUN THIS
│
├── ⚙️ CONFIG & CODE
│   ├── config.py
│   ├── utils.py
│   ├── face_utils.py
│   ├── camera_utils.py
│   ├── attendance_utils.py
│   └── requirements.txt
│
├── 📚 DOCS
│   ├── README.md                (Overview)
│   ├── START_HERE.md            (You are here)
│   └── docs/SETUP.md            (Detailed guide)
│
└── 📁 DATA (Auto-created)
    ├── faces/                   (Face samples)
    ├── models/                  (Trained models)
    └── attendance/              (Database)
```

---

## ⚡ RUN IMMEDIATELY

### Windows/PowerShell:
```bash
python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python face_recognition_app_simplified.py
```

### macOS/Linux:
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python3 face_recognition_app_simplified.py
```

---

## 📖 Step-by-Step (5 Minutes)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate it**
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python face_recognition_app_simplified.py
   ```

---

## 🎓 First Time Usage

Once the app launches:

1. **Add a person** - Enter name and click "Capture Samples"
2. **Capture** - Position face in camera, press 'c' 30 times
3. **Train** - Click "Train Recognition Model" (1-5 minutes)
4. **Test** - Click "Start Recognition" to test
5. **Export** - Click "Export Today CSV" for attendance report

---

## ⚙️ Configuration (Optional)

Edit `config.py` to customize:

```python
FACE_SAMPLES_REQUIRED = 30        # Samples per person
FACE_MATCH_TOLERANCE = 0.6        # Recognition strictness
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
DEFAULT_CAMERA_INDEX = 0
```

---

## ❓ FAQ

| Question | Answer |
|----------|--------|
| How long does setup take? | 5 minutes |
| Where are face samples? | `data/faces/` |
| Where is the database? | `data/attendance/` |
| Can I export data? | Yes, via "Export Today CSV" |
| Can I adjust settings? | Yes, edit `config.py` |
| Troubleshooting? | See `docs/SETUP.md` |

---

## 🎉 That's It!

Your project is ready to go. Run the quick command above and enjoy! ✨

**Need help?** All detailed instructions are in `docs/SETUP.md`
