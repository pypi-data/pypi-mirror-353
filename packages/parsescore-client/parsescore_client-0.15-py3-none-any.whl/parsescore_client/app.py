import tkinter as tk
from threading import Thread
from tkinter import filedialog

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


def main():
    setup_background_threads()


if __name__ in {"__main__", "__mp_main__"}:
    main()
