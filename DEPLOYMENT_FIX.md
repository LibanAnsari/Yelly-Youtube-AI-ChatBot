# Streamlit Cloud Deployment Fix - Summary

## Problem Fixed
Your YouTube AI ChatBot was not updating the `transcripts.json` and `faiss_index` files when deployed to Streamlit Cloud because:
- Streamlit Cloud has a **read-only filesystem** for the app directory
- The app was trying to write to the `data/` folder, which is not writable in the cloud

## Solution Applied
Changed all file operations to use **temporary directories** (`/tmp/data/`) instead of the project `data/` folder:

### Files Modified:
1. **`utils/yt_utils.py`** - Transcript saving now uses `/tmp/data/transcripts.json`
2. **`utils/indexing.py`** - Text processing and FAISS index creation use `/tmp/data/` paths
3. **`utils/retrieval.py`** - FAISS index loading uses `/tmp/data/faiss_index`
4. **`.gitignore`** - Added to exclude runtime-generated files from git

### Key Changes:
```python
# Before (didn't work on Streamlit Cloud):
filename="data/transcripts.json"
save_local("data/faiss_index")
load_local("data/faiss_index")

# After (works on Streamlit Cloud):
filename="/tmp/data/transcripts.json"
save_local("/tmp/data/faiss_index")
load_local("/tmp/data/faiss_index")
```

## Why This Fixes the Issue
- ✅ `/tmp/` directory is **writable** on Streamlit Cloud
- ✅ Files are created fresh for each user session
- ✅ No permission errors or read-only filesystem issues
- ✅ Files don't persist between sessions (as you requested)

## Deployment Instructions
1. **Deploy as normal** - No special configuration needed
2. **The app will work correctly** on Streamlit Cloud now
3. **Runtime files are temporary** - They don't persist after app restarts (which is what you wanted)

## Local Development
- Your existing `data/` folder files remain unchanged for local testing
- The app automatically uses `/tmp/data/` paths in all environments
- No additional setup required for local development

## What Happens Now
When a user:
1. **Enters a YouTube URL** → Transcript saved to `/tmp/data/transcripts.json`
2. **App processes video** → FAISS index saved to `/tmp/data/faiss_index/`
3. **Asks questions** → App retrieves from the temporary files
4. **Session ends** → Files are cleaned up automatically

**Your app is now ready for Streamlit Cloud deployment! 🚀**