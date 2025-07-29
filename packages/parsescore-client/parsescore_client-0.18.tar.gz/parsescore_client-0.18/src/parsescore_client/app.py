import tkinter as tk
from threading import Thread
from tkinter import filedialog

import flet as ft

from .config import load_path, save_path
from .control import update_background

# region UI Components


def open_file_window():
    """Opens a file dialog to select the WoW retail folder."""
    root = tk.Tk()
    root.withdraw()

    wow_path = filedialog.askdirectory() + "/"
    save_path(wow_path)
    return wow_path


def ui_wow_path():
    wow_path = load_path()
    if not wow_path:
        wow_path = open_file_window()
        save_path(wow_path)


# endregion


def setup_background_threads():
    update_thread = Thread(target=update_background)
    update_thread.daemon = True  # Ensure the thread exits when the main program does
    update_thread.start()


def main(page: ft.Page):
    setup_background_threads()

    page.window.width = 400
    page.window.height = 150
    page.window.minimizable = True
    page.window.minimized = True

    def wow_path_result(e: ft.FilePickerResultEvent):
        wow_path.value = e.path if e.path else "Cancelled!"
        wow_path.update()
        save_path(wow_path.value)

    pick_wow_path_dialog = ft.FilePicker(on_result=wow_path_result)
    wow_path = ft.TextField(label="WoW _retail_ folder path", value=load_path())

    page.overlay.append(pick_wow_path_dialog)

    page.add(
        ft.Column(
            [
                wow_path,
                ft.ElevatedButton(
                    "Pick files",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda _: pick_wow_path_dialog.get_directory_path(),
                    width=300,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.app(main)
