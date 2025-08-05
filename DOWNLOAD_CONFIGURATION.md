# Download Configuration Guide

## 🎯 How Downloads Work

The MCP server's `download_video` tool uses **yt-dlp** under the hood, which means you get all of yt-dlp's powerful download configuration options through the MCP interface.

## 📁 Download Locations

### **Default Behavior**
```json
{
  "url": "https://example.com/video"
}
```
- **Downloads to**: Current working directory of the MCP server process
- **Filename**: yt-dlp's default naming (usually includes video title + format ID)
- **Example**: `Video Title [abc123].mp4`

### **Configured Output Path**
```json
{
  "url": "https://example.com/video", 
  "output_path": "/Users/username/Downloads/%(title)s.%(ext)s"
}
```
- **Downloads to**: Specified directory
- **Filename**: Uses yt-dlp template variables
- **Example**: `/Users/username/Downloads/Video Title.mp4`

## 🎨 Template Variables

yt-dlp supports many template variables for dynamic filenames:

| Variable | Description | Example |
|----------|-------------|---------|
| `%(title)s` | Video title | "Amazing Video" |
| `%(uploader)s` | Channel/uploader name | "TechChannel" |
| `%(ext)s` | File extension | "mp4" |
| `%(upload_date)s` | Upload date | "20250804" |
| `%(duration)s` | Video duration | "180" |
| `%(resolution)s` | Video resolution | "1080p" |
| `%(format_id)s` | Format identifier | "137" |
| `%(id)s` | Video ID | "abc123xyz" |

## 📂 Common Configuration Patterns

### **1. Downloads Folder**
```json
{
  "output_path": "~/Downloads/%(title)s.%(ext)s"
}
```
Result: `~/Downloads/Video Title.mp4`

### **2. Organized by Channel**
```json
{
  "output_path": "~/Videos/%(uploader)s/%(title)s.%(ext)s"
}
```
Result: `~/Videos/TechChannel/Video Title.mp4`

### **3. Organized by Date**
```json
{
  "output_path": "~/Videos/%(upload_date)s/%(title)s.%(ext)s"
}
```
Result: `~/Videos/20250804/Video Title.mp4`

### **4. Quality-based Organization**
```json
{
  "output_path": "~/Videos/%(resolution)s/%(title)s.%(ext)s"
}
```
Result: `~/Videos/1080p/Video Title.mp4`

### **5. Fixed Filename**
```json
{
  "output_path": "/tmp/my_video.mp4"
}
```
Result: `/tmp/my_video.mp4` (exact name)

## 🔧 Advanced Configuration

### **Format Selection + Output Path**
```json
{
  "url": "https://example.com/video",
  "format_id": "137+140",
  "output_path": "~/Downloads/HQ/%(title)s.%(ext)s"
}
```
- Downloads specific format (1080p video + best audio)
- Saves to organized directory structure

### **Safe Filenames**
yt-dlp automatically:
- Removes invalid filename characters
- Handles Unicode characters appropriately  
- Truncates overly long names
- Avoids filename conflicts

## 🛡️ Security & Best Practices

### **Path Safety**
- Use absolute paths for predictable results
- Avoid user input directly in paths without validation
- Consider sandboxing downloads to specific directories

### **Example Safe Configuration**
```python
# In a production MCP server, you might restrict paths:
ALLOWED_DOWNLOAD_DIRS = [
    "/tmp/downloads",
    os.path.expanduser("~/Downloads"),
    "/var/downloads"
]

def validate_output_path(path):
    abs_path = os.path.abspath(path)
    return any(abs_path.startswith(allowed) for allowed in ALLOWED_DOWNLOAD_DIRS)
```

## 🎮 Real-World Examples

### **Facebook Reel**
Our test showed:
```json
{
  "url": "https://www.facebook.com/reel/721818657509109",
  "output_path": "/tmp/organized_videos/%(uploader)s/%(title)s.%(ext)s"
}
```

Downloaded to:
```
/tmp/organized_videos/
└── 901K views &#xb7; 17K reactions ｜ Unlimited？ ｜ bryguyferreira/
    └── 901K views · 17K reactions ｜ Unlimited？ ｜ bryguyferreira.mp4
```

### **YouTube Video** 
```json
{
  "url": "https://www.youtube.com/watch?v=abc123",
  "output_path": "~/Downloads/YouTube/%(uploader)s - %(title)s.%(ext)s"
}
```

Would create:
```
~/Downloads/YouTube/
└── TechChannel - How to Build a Computer.mp4
```

## 🔄 Dynamic Configuration

In a real MCP integration, the LLM can make intelligent decisions:

### **LLM-Driven Path Selection**
```python
# LLM analyzes video and chooses appropriate organization
if video_info['uploader'] == 'Educational Channel':
    output_path = f"~/Education/{video_info['subject']}/%(title)s.%(ext)s"
elif video_info['duration'] < 60:
    output_path = "~/Shorts/%(title)s.%(ext)s"  
else:
    output_path = "~/Videos/%(uploader)s/%(title)s.%(ext)s"
```

### **Quality-Based Paths**
```python
# LLM selects quality and appropriate storage location
if format_info['resolution'] >= '1080p':
    output_path = "~/Videos/HQ/%(title)s.%(ext)s"
else:
    output_path = "~/Videos/Standard/%(title)s.%(ext)s"
```

## 📊 Summary

| Configuration | Use Case | Result |
|---------------|----------|---------|
| No `output_path` | Quick downloads | Current directory |
| `~/Downloads/%(title)s.%(ext)s` | Simple organization | Downloads folder |
| `~/Videos/%(uploader)s/%(title)s.%(ext)s` | Channel organization | Organized by creator |
| `/tmp/video.mp4` | Temporary/testing | Fixed location |
| `~/Archive/%(upload_date)s/%(title)s.%(ext)s` | Date-based archive | Time-organized storage |

The MCP server provides **complete flexibility** in download location and naming, allowing LLM clients to make intelligent decisions about file organization based on video content, user preferences, and storage strategies.