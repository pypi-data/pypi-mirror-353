"""
EgriPad: File Processor GUI [Kivy Version]

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
__description__ = "Minimalist file processor GUI for Kivy environments."
__url__ = "" 


import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config

# Make it behave better on Android screens
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

class FileEditor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.directory = os.getcwd()
        self.current_file = None
        self.modified = False
        self.allowed_extensions = [".txt", ".md", ".json"]

        self.build_sidebar()
        self.build_editor_area()
        self.refresh_file_list()

    def build_sidebar(self):
        self.sidebar = BoxLayout(orientation='vertical', size_hint=(0.3, 1))

        # Extension filter input
        self.extension_input = TextInput(text=",".join(self.allowed_extensions), multiline=False, size_hint_y=0.08)
        self.extension_input.bind(on_text_validate=self.update_extensions)
        self.sidebar.add_widget(self.extension_input)

        # Scrollable file list
        self.file_scroll = ScrollView(size_hint=(1, 0.82))
        self.file_list = GridLayout(cols=1, size_hint_y=None)
        self.file_list.bind(minimum_height=self.file_list.setter('height'))
        self.file_scroll.add_widget(self.file_list)
        self.sidebar.add_widget(self.file_scroll)

        # New file button
        self.sidebar.add_widget(Button(text='New File', size_hint_y=0.1, on_press=self.create_new_file))
        self.add_widget(self.sidebar)

    def build_editor_area(self):
        self.editor_panel = BoxLayout(orientation='vertical', size_hint=(0.7, 1))

        # Current file label
        self.status_label = Label(text="No file loaded", size_hint_y=0.05)
        self.editor_panel.add_widget(self.status_label)

        # Text editor
        self.text_area = TextInput(multiline=True, font_size=16)
        self.text_area.bind(text=self.on_text_change)
        self.editor_panel.add_widget(self.text_area)

        # Search bar
        search_bar = BoxLayout(size_hint_y=0.05)
        self.search_input = TextInput(hint_text="Find text", multiline=False)
        self.search_input.bind(on_text_validate=self.search_text)
        search_bar.add_widget(self.search_input)
        search_bar.add_widget(Button(text="Find", size_hint_x=0.3, on_press=lambda x: self.search_text()))
        self.editor_panel.add_widget(search_bar)

        # Action buttons
        button_bar = BoxLayout(size_hint_y=0.1)
        button_bar.add_widget(Button(text='Open', on_press=self.open_file))
        button_bar.add_widget(Button(text='Save', on_press=self.save_file))
        button_bar.add_widget(Button(text='Rename', on_press=self.rename_file))
        button_bar.add_widget(Button(text='Delete', on_press=self.delete_file))
        self.editor_panel.add_widget(button_bar)

        self.add_widget(self.editor_panel)

    def update_extensions(self, *_):
        self.allowed_extensions = [e.strip() for e in self.extension_input.text.split(',') if e.strip().startswith('.')]
        self.refresh_file_list()

    def on_text_change(self, *_):
        self.modified = True

    def refresh_file_list(self):
        self.file_list.clear_widgets()
        for f in sorted(os.listdir(self.directory)):
            if any(f.endswith(ext) for ext in self.allowed_extensions):
                b = Button(text=f, size_hint_y=None, height=40)
                b.bind(on_press=self.select_file)
                self.file_list.add_widget(b)

    def select_file(self, instance):
        if self.modified:
            self.show_popup("Unsaved changes", "Please save or discard changes first.")
            return
        self.current_file = instance.text
        self.load_file(self.current_file)

    def load_file(self, filename):
        try:
            with open(os.path.join(self.directory, filename), 'r', encoding='utf-8') as f:
                self.text_area.text = f.read()
            self.modified = False
            self.status_label.text = f"Editing: {filename}"
        except Exception as e:
            self.show_popup("Load Error", str(e))

    def open_file(self, _):
        if not self.current_file:
            self.show_popup("No file selected", "Select a file to open.")
            return
        self.load_file(self.current_file)

    def save_file(self, _):
        if not self.current_file:
            self.show_popup("No file loaded", "Nothing to save.")
            return
        try:
            with open(os.path.join(self.directory, self.current_file), 'w', encoding='utf-8') as f:
                f.write(self.text_area.text.strip())
            self.modified = False
            self.show_popup("Saved", f"File '{self.current_file}' saved.")
        except Exception as e:
            self.show_popup("Save Error", str(e))

    def delete_file(self, _):
        if not self.current_file:
            self.show_popup("No file loaded", "Nothing to delete.")
            return
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=f"Delete '{self.current_file}'?"))
        confirm = BoxLayout(size_hint_y=0.3)
        confirm.add_widget(Button(text='Yes', on_press=lambda x: self._confirm_delete(True)))
        confirm.add_widget(Button(text='No', on_press=lambda x: self._confirm_delete(False)))
        content.add_widget(confirm)
        self.confirm_popup = Popup(title="Confirm Delete", content=content, size_hint=(0.6, 0.4))
        self.confirm_popup.open()

    def _confirm_delete(self, confirm):
        self.confirm_popup.dismiss()
        if confirm:
            try:
                os.remove(os.path.join(self.directory, self.current_file))
                self.text_area.text = ""
                self.status_label.text = "No file loaded"
                self.current_file = None
                self.modified = False
                self.refresh_file_list()
                self.show_popup("Deleted", "File deleted.")
            except Exception as e:
                self.show_popup("Delete Error", str(e))

    def rename_file(self, _):
        if not self.current_file:
            self.show_popup("No file selected", "Nothing to rename.")
            return

        def do_rename(instance):
            new_name = name_input.text.strip()
            popup.dismiss()
            if not new_name:
                return
            old_path = os.path.join(self.directory, self.current_file)
            new_path = os.path.join(self.directory, new_name)
            if os.path.exists(new_path):
                self.show_popup("Exists", "A file with that name already exists.")
                return
            try:
                os.rename(old_path, new_path)
                self.current_file = new_name
                self.status_label.text = f"Editing: {new_name}"
                self.refresh_file_list()
                self.show_popup("Renamed", f"Renamed to {new_name}")
            except Exception as e:
                self.show_popup("Rename Error", str(e))

        name_input = TextInput(text=self.current_file, multiline=False)
        confirm_btn = Button(text="Rename", size_hint_y=0.3)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(name_input)
        layout.add_widget(confirm_btn)
        popup = Popup(title="Rename File", content=layout, size_hint=(0.6, 0.4))
        confirm_btn.bind(on_press=do_rename)
        popup.open()

    def create_new_file(self, _):
        def make_file(instance):
            name = name_input.text.strip()
            popup.dismiss()
            if not name or not any(name.endswith(ext) for ext in self.allowed_extensions):
                self.show_popup("Invalid name", "Must have valid extension.")
                return
            path = os.path.join(self.directory, name)
            if os.path.exists(path):
                self.show_popup("Exists", "File already exists.")
                return
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.current_file = name
                self.status_label.text = f"Editing: {name}"
                self.text_area.text = ""
                self.modified = False
                self.refresh_file_list()
                self.show_popup("Created", f"Created {name}")
            except Exception as e:
                self.show_popup("Create Error", str(e))

        name_input = TextInput(hint_text="filename.txt", multiline=False)
        create_btn = Button(text="Create", size_hint_y=0.3)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(name_input)
        layout.add_widget(create_btn)
        popup = Popup(title="New File", content=layout, size_hint=(0.6, 0.4))
        create_btn.bind(on_press=make_file)
        popup.open()

    def search_text(self, *_):
        query = self.search_input.text.strip()
        if not query:
            return
        index = self.text_area.text.find(query)
        if index != -1:
            self.text_area.cursor = (len(query), index)
            self.text_area.scroll_y = 0  # force top
        else:
            self.show_popup("Not found", f"'{query}' not found in file.")

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.6, 0.4))
        popup.open()


class FileEditorApp(App):
    def build(self):
        return FileEditor()


# ✅ Importable via Egritools or CLI-launchable
def main():
    FileEditorApp().run()


if __name__ == "__main__":
    main()