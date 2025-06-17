# main.py
import tkinter as tk
import gui
import app_logic
import sys
from tkinter import scrolledtext


class TextRedirector:
    """A class to redirect stdout to a tkinter Text widget."""

    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.config(state='normal')
        self.widget.insert('end', str, (self.tag,))
        self.widget.see('end')  # Scroll to the end
        self.widget.config(state='disabled')

    def flush(self):
        pass  # Required for file-like object


def main():
    """Main function to create and run the application."""
    root = tk.Tk()
    main_window = gui.MainWindow(root)
    main_window.pack(side="top", fill="both", expand=True)

    # --- Setup Logging to UI ---
    # Redirect the standard output to the log text widget
    sys.stdout = TextRedirector(main_window.log_text, "stdout")

    # --- Run App Initialization Logic ---
    app_logic.initialize_app()

    # --- Start the GUI Main Loop ---
    root.mainloop()


if __name__ == "__main__":
    main()