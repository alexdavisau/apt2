# gui.py
import tkinter as tk
from tkinter import scrolledtext, Toplevel, Frame, Button, Label, Entry, messagebox
import app_logic


class MainWindow(Frame):
    """
    The main window for the application.
    """

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("APT - Alation Power Tools")
        self.parent.geometry("700x500")

        # --- Menu Bar ---
        self.menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Settings", command=self.open_settings_window)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.parent.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # --- Main Frames ---
        top_frame = Frame(self.parent, borderwidth=2, relief="groove")
        top_frame.pack(side="top", fill="x", padx=10, pady=10)

        middle_frame = Frame(self.parent, borderwidth=2, relief="groove")
        middle_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        # --- Top Frame Widgets (Buttons) ---
        self.btn_refetch_cache = Button(top_frame, text="Re-fetch Cache", command=app_logic.refetch_cache)
        self.btn_refetch_cache.pack(side="left", padx=5, pady=5)
        # Initially disabled until credentials are loaded and valid
        self.btn_refetch_cache.config(state="disabled")

        # --- Middle Frame Widgets (Logging) ---
        log_label = Label(middle_frame, text="Activity Log:")
        log_label.pack(side="top", anchor="w", padx=5)
        self.log_text = scrolledtext.ScrolledText(middle_frame, wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def open_settings_window(self):
        """Opens the settings window."""
        # Check if a settings window already exists
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.lift()  # Bring to front if already open
        else:
            self.settings_window = Toplevel(self.parent)
            self.settings_frame = SettingsWindow(self.settings_window)
            self.settings_frame.pack(fill="both", expand=True)


class SettingsWindow(Frame):
    """
    The settings window for entering credentials.
    """

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Settings")
        self.parent.geometry("400x200")

        # --- Widgets ---
        Label(self, text="Alation URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = Entry(self, width=40)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(self, text="Refresh Token:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.token_entry = Entry(self, width=40, show="*")
        self.token_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(self, text="User ID:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.user_id_entry = Entry(self, width=40)
        self.user_id_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- Buttons ---
        button_frame = Frame(self)
        button_frame.grid(row=3, columnspan=2, pady=10)
        Button(button_frame, text="Save Settings", command=self.save_and_close).pack(side="left", padx=5)
        Button(button_frame, text="Cancel", command=self.parent.destroy).pack(side="left", padx=5)

        # --- NEW: Load existing settings when window opens ---
        self.load_existing_settings()

    def load_existing_settings(self):
        """Pre-populates the fields with saved settings."""
        settings = app_logic.load_settings()
        if settings:
            self.url_entry.insert(0, settings.get("alation_url", ""))
            self.token_entry.insert(0, settings.get("refresh_token", ""))
            self.user_id_entry.insert(0, settings.get("user_id", ""))

    def save_and_close(self):
        """Saves the settings and closes the window."""
        # --- MODIFIED: Call save_settings from app_logic ---
        url = self.url_entry.get()
        token = self.token_entry.get()
        user_id = self.user_id_entry.get()

        if app_logic.save_settings(url, token, user_id):
            messagebox.showinfo("Success", "Settings saved successfully.")
            self.parent.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings. Check logs for details.")