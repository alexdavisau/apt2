# gui.py
import tkinter as tk
from tkinter import scrolledtext, Toplevel, Frame, Button, Label, Entry, messagebox
from tkinter.ttk import Combobox, Treeview
import app_logic


class MainWindow(Frame):
    """
    The main window for the application.
    """

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("APT - Alation Power Tools")
        self.parent.geometry("700x600")

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

        selection_frame = Frame(self.parent, borderwidth=2, relief="groove")
        selection_frame.pack(side="top", fill="x", padx=10, pady=5)
        selection_frame.columnconfigure(1, weight=1)

        log_frame = Frame(self.parent, borderwidth=2, relief="groove")
        log_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        # --- Top Frame Widgets (Buttons) ---
        self.btn_refetch_cache = Button(top_frame, text="Re-fetch Cache", command=lambda: app_logic.refetch_cache(self))
        self.btn_refetch_cache.pack(side="left", padx=5, pady=5)
        self.btn_refetch_cache.config(state="disabled")

        # --- Selection Frame Widgets ---
        Label(selection_frame, text="Document Hub ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hub_combobox = Combobox(selection_frame, state="readonly")
        self.hub_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.hub_combobox.bind("<<ComboboxSelected>>", lambda event: app_logic.on_hub_selected(self, event))

        Label(selection_frame, text="Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.folder_tree = Treeview(selection_frame, selectmode="browse", height=5)
        self.folder_tree.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.folder_tree.bind("<<TreeviewSelect>>", lambda event: app_logic.on_folder_selected(self, event))

        Label(selection_frame, text="Template:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.template_combobox = Combobox(selection_frame, state="disabled")
        self.template_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        # --- NEW: Bind event to template selection ---
        self.template_combobox.bind("<<ComboboxSelected>>", lambda event: app_logic.on_template_selected(self, event))

        # --- NEW: Link command to the generate button ---
        self.btn_generate = Button(selection_frame, text="Generate Template", state="disabled",
                                   command=lambda: app_logic.generate_template(self))
        self.btn_generate.grid(row=3, column=1, padx=5, pady=10, sticky="e")

        # --- Log Frame Widgets ---
        log_label = Label(log_frame, text="Activity Log:")
        log_label.pack(side="top", anchor="w", padx=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def open_settings_window(self):
        # This method remains unchanged
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.lift()
        else:
            self.settings_window = Toplevel(self.parent)
            self.settings_frame = SettingsWindow(self.settings_window)
            self.settings_frame.pack(fill="both", expand=True)


class SettingsWindow(Frame):
    # This class remains unchanged
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent;
        self.parent.title("Settings");
        self.parent.geometry("400x200")
        Label(self, text="Alation URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = Entry(self, width=40);
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)
        Label(self, text="Refresh Token:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.token_entry = Entry(self, width=40, show="*");
        self.token_entry.grid(row=1, column=1, padx=5, pady=5)
        Label(self, text="User ID:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.user_id_entry = Entry(self, width=40);
        self.user_id_entry.grid(row=2, column=1, padx=5, pady=5)
        button_frame = Frame(self);
        button_frame.grid(row=3, columnspan=2, pady=10)
        Button(button_frame, text="Save Settings", command=self.save_and_close).pack(side="left", padx=5)
        Button(button_frame, text="Cancel", command=self.parent.destroy).pack(side="left", padx=5)
        self.load_existing_settings()

    def load_existing_settings(self):
        settings = app_logic.load_settings()
        if settings:
            self.url_entry.insert(0, settings.get("alation_url", ""));
            self.token_entry.insert(0, settings.get("refresh_token", ""));
            self.user_id_entry.insert(0, settings.get("user_id", ""))

    def save_and_close(self):
        url, token, user_id = self.url_entry.get(), self.token_entry.get(), self.user_id_entry.get()
        if app_logic.save_settings(url, token, user_id):
            messagebox.showinfo("Success", "Settings saved successfully.");
            self.parent.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings. Check logs for details.")