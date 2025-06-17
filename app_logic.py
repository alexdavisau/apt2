# app_logic.py
import json
import alation_api

CONFIG_FILE = "config.json"
app_settings = {}


# --- CORRECTED CLASS DEFINITION ---
class AppData:
    def __init__(self):
        self.all_folders = []
        self.id_to_title_map = {}
        self.doc_hubs = {}
        self.template_title_to_id_map = {}  # This attribute is now correctly included


app_data = AppData()


def save_settings(url, token, user_id):
    settings_to_save = {"alation_url": url, "refresh_token": token, "user_id": user_id}
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings_to_save, f, indent=4)
        print(f"LOG: Settings successfully saved to {CONFIG_FILE}");
        global app_settings;
        app_settings = settings_to_save
        return True
    except Exception as e:
        print(f"ERROR: Could not save settings to {CONFIG_FILE}. Error: {e}"); return False


def load_settings():
    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f); print(f"LOG: Settings loaded from {CONFIG_FILE}"); return settings
    except FileNotFoundError:
        print(f"LOG: {CONFIG_FILE} not found. No settings loaded."); return None
    except Exception as e:
        print(f"ERROR: Could not load settings from {CONFIG_FILE}. Error: {e}"); return None


def initialize_app(main_window_ref):
    print("LOG: Application starting...");
    global app_settings;
    app_settings = load_settings()
    if not app_settings: print("LOG: No saved credentials found. Please configure via File -> Settings."); print(
        "LOG: Initialization complete."); return
    print("LOG: Credentials loaded. Attempting to authenticate...")
    url, user_id, refresh_token = app_settings.get("alation_url"), app_settings.get("user_id"), app_settings.get(
        "refresh_token")
    if not all([url, user_id, refresh_token]): print(
        "ERROR: Incomplete settings in config.json. Please save settings again."); print(
        "LOG: Initialization complete."); return
    auth_success = alation_api.refresh_api_token(url, user_id, refresh_token)
    if auth_success:
        print("LOG: Authentication successful. Application is ready.");
        main_window_ref.btn_refetch_cache.config(state="normal")
        print("LOG: Automatically fetching initial data...");
        refetch_cache(main_window_ref)
    else:
        print("LOG: Authentication failed. Please check credentials in Settings or network connection.");
        main_window_ref.btn_refetch_cache.config(state="disabled")
    print("LOG: Initialization complete.")


def refetch_cache(main_window_ref):
    print("LOG: User clicked 'Re-fetch Cache'.")
    url = app_settings.get("alation_url")
    if not url: print("ERROR: Alation URL not configured."); return
    main_window_ref.hub_combobox['values'] = [];
    main_window_ref.folder_tree.delete(*main_window_ref.folder_tree.get_children())
    main_window_ref.template_combobox['values'] = [];
    global app_data;
    app_data = AppData()
    app_data.all_folders = alation_api.get_folders(url, params=None)
    if not app_data.all_folders: print("LOG: Could not fetch folder data. Aborting."); return
    app_data.id_to_title_map = {folder['id']: folder.get('title') or 'Untitled Folder' for folder in
                                app_data.all_folders}
    hub_ids = sorted(list(set(f['document_hub_id'] for f in app_data.all_folders if f.get('document_hub_id'))))
    app_data.doc_hubs = {hub_id: f"Hub ID: {hub_id}" for hub_id in hub_ids}
    if hub_ids:
        main_window_ref.hub_combobox['values'] = hub_ids;
        main_window_ref.hub_combobox.config(state="readonly")
        print(f"LOG: Found and populated {len(hub_ids)} Document Hubs.")
    else:
        print("LOG: No Document Hubs could be identified.")


def on_hub_selected(main_window_ref, event):
    selected_hub_id = int(main_window_ref.hub_combobox.get());
    print(f"LOG: User selected Hub ID: {selected_hub_id}")
    tree = main_window_ref.folder_tree;
    tree.delete(*tree.get_children())
    main_window_ref.template_combobox['values'] = [];
    main_window_ref.template_combobox.set('')
    folders_in_hub = [f for f in app_data.all_folders if f.get('document_hub_id') == selected_hub_id]
    folders_by_parent = {};
    for folder in folders_in_hub:
        parent_id = folder.get('parent_folder_id')
        if parent_id not in folders_by_parent: folders_by_parent[parent_id] = []
        folders_by_parent[parent_id].append(folder)
    build_folder_tree(tree, '', folders_by_parent, None)
    main_window_ref.template_combobox.config(state="disabled");
    print(f"LOG: Built folder tree for Hub ID {selected_hub_id}.")


def build_folder_tree(tree, parent_item, folders_by_parent, parent_id):
    children = folders_by_parent.get(parent_id, [])
    for folder in children:
        folder_id = folder['id'];
        display_text = f"{(folder.get('title') or 'Untitled Folder')} (ID: {folder_id})"
        item_id = tree.insert(parent_item, 'end', iid=folder_id, text=display_text)
        if folder_id in folders_by_parent:
            build_folder_tree(tree, item_id, folders_by_parent, folder_id)


def on_folder_selected(main_window_ref, event):
    selected_items = main_window_ref.folder_tree.selection()
    if not selected_items: return
    selected_folder_id = int(selected_items[0]);
    selected_title = app_data.id_to_title_map.get(selected_folder_id, "Unknown")
    print(f"LOG: User selected Folder: '{selected_title}'")

    main_window_ref.template_combobox['values'] = [];
    main_window_ref.template_combobox.set('')
    global app_data;
    app_data.template_title_to_id_map = {}

    url = app_settings.get("alation_url");
    hub_id = int(main_window_ref.hub_combobox.get())
    documents = alation_api.get_documents(url, hub_id, selected_folder_id)

    if documents:
        template_ids = set(doc.get('template_id') for doc in documents if doc.get('template_id'))
        if template_ids:
            print(f"LOG: Found {len(template_ids)} unique template IDs from documents.")
            template_names = []
            for t_id in template_ids:
                name = alation_api.get_template_name(url, t_id)
                app_data.template_title_to_id_map[name] = t_id
                template_names.append(name)

            main_window_ref.template_combobox['values'] = sorted(template_names)
            main_window_ref.template_combobox.config(state="readonly")
        else:
            main_window_ref.template_combobox.config(state="disabled");
            print("LOG: Documents in this folder do not have any associated templates.")
    else:
        main_window_ref.template_combobox.config(state="disabled");
        print("LOG: No documents found in this folder.")


def on_template_selected(main_window_ref, event):
    selected_template = main_window_ref.template_combobox.get()
    print(f"LOG: User selected Template: '{selected_template}'")
    if main_window_ref.folder_tree.selection():
        main_window_ref.btn_generate.config(state="normal")


def generate_template(main_window_ref):
    print("LOG: User clicked 'Generate Template'.")
    url = app_settings.get("alation_url")
    selected_template_name = main_window_ref.template_combobox.get()
    selected_template_id = app_data.template_title_to_id_map.get(selected_template_name)
    if not url or not selected_template_id:
        print("ERROR: URL or Template not selected correctly.");
        return
    template_details = alation_api.get_template_details(url, selected_template_id)
    if template_details and 'fields' in template_details:
        all_fields = [{'name_singular': 'Title', 'field_type': 'TEXT'}]
        all_fields.extend(template_details['fields'])
        print(f"--- Fields for Template ID: {selected_template_id} ('{selected_template_name}') ---")
        for field in all_fields:
            print(f"  - Field Name: {field.get('name_singular')}, Type: {field.get('field_type')}")
        print("---------------------------------------")
    else:
        print("LOG: Could not fetch template details or template has no fields.")