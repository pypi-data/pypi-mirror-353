# 📼 midia-compress - Python Video Compression Tool

A Python 🐍 library for smart video compression using FFmpeg, with a user-friendly CLI ✨


## 🚀 Installation

```bash
pip install midia-compress
```

### 🔧 Prerequisites

- Python 3.7+

- FFmpeg installed on your system


### 🛠️ How to Install FFmpeg:

- Windows:
  ```bash
  winget install Gyan.FFmpeg
  ```

- Linux (Debian/Ubuntu):
  ```bash
  sudo apt install ffmpeg
  ```
- MacOS:
  ```bash
  brew install ffmpeg
  ```



## 💻 How to Use the CLI

```bash
midia-compress
```

This will:

- 🔍 Search for MP4 files in the current directory

- 📉 Compress all with CRF 28 (good quality/size ratio)

-  💾 Save as "compressed_original_name.mp4"



# 📊 Quality Comparison
| CRF | Quality       | File Size      |
|-----|--------------|---------------|
| 18  | 🏆 Best      | ⚠️ Very Large |
| 23  | 💎 Excellent | 📏 Balanced   |
| 28  | 👍 Good      | 🐜 Small      |


# 🤝 Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository

2. Create a branch (git checkout -b feature/amazing)

3. Commit your changes (git commit -m 'Add amazing feature')

4. Push (git push origin feature/amazing)

5. Open a Pull Request


# 📜 License

MIT
