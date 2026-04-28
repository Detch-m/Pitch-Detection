"""Check availability of required media processing packages."""

import importlib.util

for pkg in ["cv2", "imageio-ffmpeg", "numpy", "sounddevice", "soundfile", "PyQt5", "librosa", "matplotlib"]:
    print(pkg, bool(importlib.util.find_spec(pkg)))
