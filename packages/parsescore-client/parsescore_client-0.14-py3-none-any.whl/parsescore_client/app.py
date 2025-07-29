import tkinter as tk
from threading import Thread
from tkinter import filedialog

from nicegui import native, ui

from .config import load_path, save_path
from .control import update_background

# region UI Components


def open_file_window():
    """Opens a file dialog to select the WoW retail folder."""
    root = tk.Tk()
    root.withdraw()

    wow_path = filedialog.askdirectory() + "/"
    save_path(wow_path)
    ui_wow_path.refresh()
    return wow_path


@ui.refreshable
def ui_wow_path():
    wow_path = load_path()
    if wow_path:
        ui.input(placeholder=wow_path, value=wow_path).classes("w-full")
    else:
        ui.input(placeholder="WoW _retail_ Folder path", value="").classes("w-full")


with ui.row().classes("w-full items-center"):
    with ui.column().classes("w-full items-center"):
        ui.label("ParseScore Client").classes("text-2xl font-bold mb-4")
        ui_wow_path()
        ui.button("Choose WoW Folder path", on_click=open_file_window).classes("w-full")

# endregion


def setup_background_threads():
    update_thread = Thread(target=update_background)
    update_thread.daemon = True  # Ensure the thread exits when the main program does
    update_thread.start()


def main():
    setup_background_threads()
    ui.run(native=True, title="ParseScore", dark=True, reload=False, port=native.find_open_port())


if __name__ in {"__main__", "__mp_main__"}:
    main()
