import subprocess

def main():
    print("""
🧰 EGRIGOR'S TOOLKIT
=======================
1. Change File Extensions
2. Create Python Venv
3. Upload to HuggingFace
4. Preclean JSON Files
5. Offline Wheel Manager
6. GPT2 Trainer
7. Combine TXT
8. Launcher
9. File Processor
10. Create GPT2 Tokenizer
11. Instant Backup
12. Chunking File Processor
13. Paraphrase [Streamlit]
14 File Processor[Api Version]
15 EgriPad [Tkinter]
16 EgriPad [Kivy]
0. Exit
""")
    choice = input("Pick a tool (1-14): ").strip()

    commands = {
        "1": "change-extension",
        "2": "create-venv",
        "3": "hf-upload",
        "4": "preclean-gui",
        "5": "wheel-manager",
        "6": "gpt2-trainer",
        "7": "combine-txt",
        "8": "launcher-gui",
        "9": "file_processor",
        "10": "gpt2token",
        "11": "instantbackup",
        "12": "chunkprocessor",
        "13": "paraphrase",
        "14": "fileapi",
        "15": "egripad",
        "16": "egripadkv"
    }

    if choice in commands:
        subprocess.run(commands[choice], shell=True)
    elif choice == "0":
        print("Goodbye.")
    else:
        print("Invalid selection.")
