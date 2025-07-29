# 🏷️ upicvision

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/upicvision)](https://pypi.org/project/upicvision/)
[![PyPI Version](https://img.shields.io/pypi/v/upicvision)](https://pypi.org/project/upicvision/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Kazu-Kusa/upicvision)
[![PyPI Downloads](https://static.pepy.tech/badge/upicvision/week)](https://pepy.tech/projects/upicvision)
[![PyPI Downloads](https://static.pepy.tech/badge/upicvision)](https://pepy.tech/projects/upicvision)

---

## 📸 Overview

The `TagDetector` class is a powerful 🚀 real-time AprilTag detection system that transforms your camera into a smart tag recognition device! 

🎯 **Key Features:**
- 📷 **Real-time Detection**: Lightning-fast AprilTag identification using OpenCV and AprilTag libraries
- 🎮 **Easy Control**: Simple start, stop, pause, and resume operations
- ⚙️ **Flexible Configuration**: Customizable camera settings and resolution scaling
- 🔧 **Resource Management**: Smart camera initialization and cleanup
- 🎪 **Thread-Safe**: Built-in threading support for smooth performance

Perfect for robotics 🤖, augmented reality 🥽, and computer vision applications! 

## 🚀 Quick Start Guide

### 🔧 Initialization
```python
from upic import TagDetector

# 🎬 Create your detector with custom settings
detector = TagDetector(cam_id=0, resolution_multiplier=0.75)
```

### 📹 Camera Operations
```python
# 🟢 Start the magic - open camera and begin detection
detector.open_camera().apriltag_detect_start()

# ⏸️ Pause detection temporarily (camera stays active)
detector.halt_detection()

# ▶️ Resume detection when ready
detector.resume_detection()

# 🔴 Clean shutdown - release camera resources
detector.release_camera()
```

### 🏷️ Getting the Detected Tag
```python
# 🔍 Check what tag is currently detected
current_tag_id = detector.tag_id
print(f"🎯 Current Tag ID: {current_tag_id}")
```

### 💡 Complete Working Example
```python
from upic import TagDetector

# 🚀 Initialize the detector
detector = TagDetector(cam_id=0, resolution_multiplier=0.75)

# 🎬 Start detection
detector.open_camera().apriltag_detect_start()

# 🎮 Control detection as needed
detector.halt_detection()  # ⏸️ Pause
detector.resume_detection()  # ▶️ Resume

# 🔍 Get the detected tag
current_tag_id = detector.tag_id
print(f"🎯 Detected Tag ID: {current_tag_id}")

# 🧹 Clean up when finished
detector.release_camera()
```