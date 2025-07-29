# 🎉 filehandler6027

[![PyPI version](https://img.shields.io/pypi/v/filehandler6027.svg)](https://pypi.org/project/filehandler6027/)
[![License](https://img.shields.io/pypi/l/filehandler6027)](https://github.com/charlie6027/filehandler6027/blob/main/LICENSE)

A lightweight Python package to handle file operations (traditional and modern) in a platform-independent way.

---

## 📖 Table of Contents

- [✅ Features](#-features)
- [🚀 Demo](#-demo)
- [📦 Installation](#-installation)
- [🛠️ Optional Enhancements](#-optional-enhancements-if-you-like)

---

## ✅ Features

- Clean file path builder using `~`
- JSON-style data handling
- Traditional and modern mode support

---

## 🚀 Demo

```bash
python examples/demo_celebration_output.py

## 📸 Example Output

Here’s what it looks like when running `FileHandler` in both modes:

![Terminal demo output](docs/img/docs/img/fh_screenshot_dmo.png)


## ➕ Append Example

```python
from filehandler import FileHandler, FileHandleMode

fh = FileHandler(FileHandleMode.Modern)

fh.append('~/Documents/logfile.txt', {'event': 'login', 'user': 'charlie'})
fh.append('~/Documents/logfile.txt', "raw string log entry")

