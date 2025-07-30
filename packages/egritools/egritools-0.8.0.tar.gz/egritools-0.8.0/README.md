# Egritools

A powerful and extensible utility suite developed by **Christopher (Egrigor86)**.

**Egritools** combines a collection of personal automation tools for file handling, model training, dataset prep, and local workflow management — all under a unified command-line launcher.

---

## 🧰 Included Tools

### 🗃️ File & Data Tools
- **Change File Extensions** — Bulk rename file extensions in any folder.
- **Combine TXT** — Concatenate multiple `.txt` files into one.
- **Preclean JSON Arrays** — Quickly clean malformed JSON lists.
- **Chunking File Processor** — Split large files into uniform parts.
- **File Processor (Standard / API)** — Lightweight GUI and API file editing tools.
- **Instant Backup** — One-click directory backup to another location.

### 🧪 AI & Model Tools
- **GPT2 Trainer** — Local fine-tuning utility for GPT2-based models.
- **GPT2 Tokenizer Creator** — Build custom tokenizers for GPT2 training.
- **Paraphrase Tool [Streamlit]** — Local paraphrasing GUI using LLM inference.

### 🧱 Environment & Package Tools
- **Create Python Venv** — Simple virtual environment creator.
- **Offline Wheel Manager** — Browse and install `.whl` packages offline.

### ☁️ Deployment
- **Upload to HuggingFace** — Push datasets/models to the HuggingFace Hub.

### 📝 File Editors
- **EgriPad [Tkinter]** — Minimalist cross-platform text editor with file management.
- **EgriPad [Kivy]** — Touch-optimized version for Android and mobile devices.

---

## 🚀 Launcher

To start the toolkit, run:

```bash
python -m egritools
```

You'll see an interactive menu like:

```
🧰 EGRIGOR'S TOOLKIT
=======================
1. Change File Extensions
...
15 EgriPad [Tkinter]
16 EgriPad [Kivy]
0. Exit
```

Each option launches the corresponding tool from a shared interface.

---

## 🔧 Installation (Manual)

Ensure Python 3.8+ is installed.

Clone the repo:
```bash
git clone https://github.com/egrigor86/egritools.git
cd egritools
```

Optional (for global command):
```bash
pip install .
```

---

## 📎 Notes

- No internet required for most tools (designed for local use).
- EgriPad is fully offline and supports basic editing, rename, delete, filtering, and file search.
- More tools will be added over time. Suggestions are welcome.

---

**Created and maintained by Christopher (Egrigor86)**  
For contributors, license, or future plans — stay tuned.
