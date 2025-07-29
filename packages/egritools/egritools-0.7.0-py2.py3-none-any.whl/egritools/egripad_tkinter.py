"""
EgriPad: File Processor GUI [Tkinter Version]

A lightweight, dependency-free file editor designed for simplicity and portability.
Supports batch editing, custom extensions, file management, and live search — 
perfect for desktop and mobile environments via Tkinter or Kivy. 

Created by Christopher (Egrigor86)
Part of the Egritools suite.

Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "Christopher (Egrigor86)"
__appname__ = "EgriPad"
__license__ = "MIT"
__description__ = "Minimalist file processor GUI for Tkinter environments."
__url__ = ""  

import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog


class FileEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tk File Editor")
        self.directory = os.getcwd()
        self.current_file = None
        self.modified = False
        self.allowed_extensions = [".txt", ".md", ".json"]

        self.build_ui()
        self.refresh_file_list()

    def build_ui(self):
        # Sidebar
        self.sidebar_frame = tk.Frame(self.root)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.ext_filter = tk.Entry(self.sidebar_frame)
        self.ext_filter.insert(0, ",".join(self.allowed_extensions))
        self.ext_filter.bind("<Return>", lambda e: self.update_extensions())
        self.ext_filter.pack(fill=tk.X)

        self.file_listbox = tk.Listbox(self.sidebar_frame, width=30)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        scrollbar = tk.Scrollbar(self.sidebar_frame, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Editor area
        self.editor_frame = tk.Frame(self.root)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(self.editor_frame, text="No file loaded")
        self.status_label.pack(fill=tk.X)

        self.text_area = tk.Text(self.editor_frame, wrap=tk.WORD, undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<<Modified>>", self.on_text_change)

        # Search bar
        search_frame = tk.Frame(self.editor_frame)
        search_frame.pack(fill=tk.X)

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Find", command=self.search_text).pack(side=tk.LEFT)

        # Buttons
        button_frame = tk.Frame(self.editor_frame)
        button_frame.pack(fill=tk.X)

        tk.Button(button_frame, text="Open", command=self.open_file).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Save", command=self.save_file).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Rename", command=self.rename_file).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Delete", command=self.delete_file).pack(side=tk.LEFT)
        tk.Button(button_frame, text="New File", command=self.create_new_file).pack(side=tk.LEFT)

    def update_extensions(self):
        raw = self.ext_filter.get()
        self.allowed_extensions = [e.strip() for e in raw.split(",") if e.strip().startswith(".")]
        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for filename in sorted(os.listdir(self.directory)):
            if any(filename.endswith(ext) for ext in self.allowed_extensions):
                self.file_listbox.insert(tk.END, filename)

    def on_file_select(self, event):
        if self.modified:
            messagebox.showwarning("Unsaved changes", "Please save or discard changes first.")
            return
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0])
            self.load_file(filename)

    def load_file(self, filename):
        path = os.path.join(self.directory, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, content)
            self.current_file = filename
            self.status_label.config(text=f"Editing: {filename}")
            self.modified = False
            self.text_area.edit_modified(False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def on_text_change(self, event):
        if self.text_area.edit_modified():
            self.modified = True
            self.text_area.edit_modified(False)

    def open_file(self):
        if not self.current_file:
            messagebox.showinfo("No file", "Select a file first.")
            return
        self.load_file(self.current_file)

    def save_file(self):
        if not self.current_file:
            messagebox.showinfo("No file", "Nothing to save.")
            return
        try:
            with open(os.path.join(self.directory, self.current_file), "w", encoding="utf-8") as f:
                f.write(self.text_area.get("1.0", tk.END).strip())
            self.modified = False
            messagebox.showinfo("Saved", f"{self.current_file} saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save:\n{e}")

    def delete_file(self):
        if not self.current_file:
            messagebox.showinfo("No file", "No file to delete.")
            return
        confirm = messagebox.askyesno("Confirm", f"Delete '{self.current_file}'?")
        if confirm:
            try:
                os.remove(os.path.join(self.directory, self.current_file))
                self.text_area.delete("1.0", tk.END)
                self.current_file = None
                self.status_label.config(text="No file loaded")
                self.modified = False
                self.refresh_file_list()
                messagebox.showinfo("Deleted", "File deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete:\n{e}")

    def rename_file(self):
        if not self.current_file:
            messagebox.showinfo("No file", "Nothing to rename.")
            return
        new_name = simpledialog.askstring("Rename File", "Enter new filename:", initialvalue=self.current_file)
        if not new_name:
            return
        old_path = os.path.join(self.directory, self.current_file)
        new_path = os.path.join(self.directory, new_name)
        if os.path.exists(new_path):
            messagebox.showerror("Exists", "A file with that name already exists.")
            return
        try:
            os.rename(old_path, new_path)
            self.current_file = new_name
            self.status_label.config(text=f"Editing: {new_name}")
            self.refresh_file_list()
            messagebox.showinfo("Renamed", f"Renamed to {new_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Rename failed:\n{e}")

    def create_new_file(self):
        name = simpledialog.askstring("New File", "Enter filename (e.g., note.txt):")
        if not name:
            return
        if not any(name.endswith(ext) for ext in self.allowed_extensions):
            messagebox.showwarning("Invalid", "Must use allowed extension.")
            return
        path = os.path.join(self.directory, name)
        if os.path.exists(path):
            messagebox.showwarning("Exists", "File already exists.")
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            self.current_file = name
            self.text_area.delete("1.0", tk.END)
            self.status_label.config(text=f"Editing: {name}")
            self.modified = False
            self.refresh_file_list()
            messagebox.showinfo("Created", f"New file '{name}' created.")
        except Exception as e:
            messagebox.showerror("Error", f"Creation failed:\n{e}")

    def search_text(self):
        query = self.search_entry.get()
        if not query:
            return
        start = self.text_area.search(query, "1.0", tk.END)
        if not start:
            messagebox.showinfo("Not found", f"'{query}' not found.")
            return
        end = f"{start}+{len(query)}c"
        self.text_area.tag_remove("highlight", "1.0", tk.END)
        self.text_area.tag_add("highlight", start, end)
        self.text_area.tag_config("highlight", background="yellow")
        self.text_area.see(start)


def main():
    root = tk.Tk()
    root.geometry("900x600")
    app = FileEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()