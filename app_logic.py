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
def refetch_cache():
    """
    Fetches the top-level Document Hubs from the Alation instance.
    """
    print("LOG: User clicked 'Re-fetch Cache'.")

    url = app_settings.get("alation_url")
    if not url:
        print("ERROR: Alation URL not configured.")
        return

    # Per Alation API docs, Doc Hubs are top-level folders in the default hub (ID 1).
    # We are looking for folders that are direct children of the root folder (ID 1)
    # within the default document hub (ID 1).
    params = {
        'document_hub_id': 1,
        'parent_folder_id': 1
    }

    doc_hubs = alation_api.get_folders(url, params=params)

    if doc_hubs:
        print("LOG: Successfully fetched top-level Document Hubs:")
        for hub in doc_hubs:
            # The API returns a list of folder objects. We print their titles.
            print(f"  - ID: {hub.get('id')}, Title: {hub.get('title')}")
    else:
        print("LOG: Could not fetch Document Hubs or none were found.")