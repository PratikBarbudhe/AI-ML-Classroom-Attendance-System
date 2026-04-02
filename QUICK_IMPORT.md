# 📱 Quick Start - Import Images from Phone

## 30-Second Setup

### Step 1: Run Import Tool
```bash
python image_import_tool.py
```

### Step 2: Create Person
- Type person's name in "Create New Person" field
- Click **Create**

### Step 3: Select Images
- Click **📂 Browse Images** (for individual photos)
- OR **📁 Browse Folder** (for entire folder)

### Step 4: Import
- Click **✅ Import Selected Images**
- Wait for completion

✅ **Done!** Images are now saved for that person.

---

## For Multiple People (Faster)

Use batch import instead:

```bash
python batch_import.py
```

Organize your phone photos like this first:
```
Phone_Images/
├── Pratiksha/  (put all her photos here)
├── John_Smith/ (put all his photos here)
└── Rupali_Mam/ (put all her photos here)
```

Then run `batch_import.py` and point to the `Phone_Images` folder.

---

## What to Import

✅ **Good quality photos:**
- Clear, well-lit images
- Face takes up at least 1/3 of frame
- Different angles and expressions
- 15-20 images per person for best results

❌ **Skip:**
- Blurry images
- Images with no face visible
- Very small faces
- Very dark/bright images

---

## Next Step

After importing, train the model:
1. Run `face_recognition_app_simplified.py`
2. Click **Train Model** button
3. Wait for training to complete
4. Use **Start Attendance** to recognize people

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No images found" | Make sure folder has .jpg/.png files |
| "No faces detected" | Use clearer, closer photos |
| Import is slow | Reduce image size or use fewer images |
| Images not appearing | Click 🔄 Refresh in the app |

**For detailed help:** See `IMPORT_GUIDE.md` in the project root.
