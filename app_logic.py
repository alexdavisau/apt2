# app_logic.py
import json
import alation_api  # Import the new api module

CONFIG_FILE = "config.json"
app_settings = {}


def save_settings(url, token, user_id):
    """Saves the provided settings to the config file."""
    settings_to_save = {"alation_url": url, "refresh_token": token, "user_id": user_id}
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings_to_save, f, indent=4)
        print(f"LOG: Settings successfully saved to {CONFIG_FILE}")
        global app_settings
        app_settings = settings_to_save
        return True
    except Exception as e:
        print(f"ERROR: Could not save settings to {CONFIG_FILE}. Error: {e}")
        return False


def load_settings():
    """Loads settings from the config file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f)
            print(f"LOG: Settings loaded from {CONFIG_FILE}")
            return settings
    except FileNotFoundError:
        print(f"LOG: {CONFIG_FILE} not found. No settings loaded.")
        return None
    except Exception as e:
        print(f"ERROR: Could not load settings from {CONFIG_FILE}. Error: {e}")
        return None


def initialize_app(main_window_ref):
    """
    The main logic that runs on startup. Takes a reference to the main window
    to allow UI changes (e.g., enabling buttons).
    """
    print("LOG: Application starting...")
    global app_settings
    app_settings = load_settings()

    if not app_settings:
        print("LOG: No saved credentials found. Please configure via File -> Settings.")
        print("LOG: Initialization complete.")
        return

    print("LOG: Credentials loaded. Attempting to authenticate...")

    url = app_settings.get("alation_url")
    user_id = app_settings.get("user_id")
    refresh_token = app_settings.get("refresh_token")

    if not all([url, user_id, refresh_token]):
        print("ERROR: Incomplete settings in config.json. Please save settings again.")
        print("LOG: Initialization complete.")
        return

    auth_success = alation_api.refresh_api_token(url, user_id, refresh_token)

    if auth_success:
        print("LOG: Authentication successful. Application is ready.")
        # Enable the UI button
        main_window_ref.btn_refetch_cache.config(state="normal")
    else:
        print("LOG: Authentication failed. Please check credentials in Settings or network connection.")
        # Keep button disabled
        main_window_ref.btn_refetch_cache.config(state="disabled")

    print("LOG: Initialization complete.")


# --- MODIFIED FUNCTION ---
# In app_logic.py

# --- MODIFIED FUNCTION ---
# --- MODIFIED FUNCTION ---
# --- MODIFIED FUNCTION ---
def refetch_cache(main_window_ref):
    """
    Fetches all folder data and populates the first dropdown.
    """
    print("LOG: User clicked 'Re-fetch Cache'.")
    url = app_settings.get("alation_url")
    if not url:
        print("ERROR: Alation URL not configured.")
        return

    # --- Reset UI and data ---
    main_window_ref.hub_combobox['values'] = []
    main_window_ref.folder_combobox['values'] = []
    main_window_ref.folder_combobox.set('')
    main_window_ref.folder_combobox.config(state="disabled")
    main_window_ref.template_combobox['values'] = []
    main_window_ref.template_combobox.set('')
    main_window_ref.template_combobox.config(state="disabled")
    global app_data
    app_data = AppData()

    app_data.all_folders = alation_api.get_folders(url, params=None)

    if not app_data.all_folders:
        print("LOG: Could not fetch any folders or none were found.")
        return

    # --- NEW, SIMPLIFIED LOGIC ---
    # 1. Get a unique, sorted list of all Document Hub IDs from the data
    all_hub_ids = set()
    for folder in app_data.all_folders:
        hub_id = folder.get('document_hub_id')
        if hub_id:
            all_hub_ids.add(hub_id)

    sorted_hub_ids = sorted(list(all_hub_ids))

    # 2. Populate the first dropdown with the discovered Hub IDs
    if sorted_hub_ids:
        main_window_ref.hub_combobox['values'] = sorted_hub_ids
        main_window_ref.hub_combobox.config(state="readonly")
        print(f"LOG: Found and populated {len(sorted_hub_ids)} Document Hubs.")
    else:
        print("LOG: No Document Hubs could be identified from the folder list.")
