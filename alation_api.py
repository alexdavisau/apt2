# alation_api.py
import requests

current_api_access_token = None


# The refresh_api_token and get_folders functions remain unchanged.
def refresh_api_token(alation_url, user_id, refresh_token):
    global current_api_access_token
    api_url = f"{alation_url}/integration/v1/createAPIAccessToken/";
    body = {"refresh_token": refresh_token, "user_id": int(user_id)}
    try:
        print("LOG: Attempting to refresh API Access Token...")
        response = requests.post(api_url, json=body)
        if response.status_code == 201:
            new_token_data = response.json();
            current_api_access_token = new_token_data['api_access_token']
            print("LOG: Successfully refreshed API Access Token.");
            return True
        else:
            print(f"ERROR: Failed to refresh access token. Status: {response.status_code}, Response: {response.text}")
            current_api_access_token = None;
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error during token refresh: {e}");
        return False


def get_folders(alation_url, params=None):
    if not current_api_access_token: print("ERROR: No valid API Access Token. Cannot fetch folders."); return None
    headers = {'Token': current_api_access_token};
    api_url = f"{alation_url}/integration/v2/folder/"
    try:
        print(f"LOG: Fetching folders with params: {params}");
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"ERROR: Failed to fetch folders. Status: {response.status_code}, Response: {response.text}"); return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error while fetching folders: {e}");
        return None


# get_all_templates and get_template_details are kept for future use if needed, but are not currently called.
def get_all_templates(alation_url):
    if not current_api_access_token: print("ERROR: No valid API Access Token. Cannot fetch templates."); return None
    headers = {'Token': current_api_access_token};
    api_url = f"{alation_url}/integration/v1/custom_template/"
    try:
        print("LOG: Fetching global list of all custom templates...")
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            print("LOG: Successfully fetched global template list."); return response.json()
        else:
            print(
                f"ERROR: Failed to fetch templates. Status: {response.status_code}, Response: {response.text}"); return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error while fetching templates: {e}"); return None


def get_template_details(alation_url, template_id):
    if not current_api_access_token: print(
        "ERROR: No valid API Access Token. Cannot fetch template details."); return None
    headers = {'Token': current_api_access_token};
    api_url = f"{alation_url}/integration/v1/custom_template/{template_id}/"
    try:
        print(f"LOG: Fetching details for template ID: {template_id}");
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"ERROR: Failed to fetch template details. Status: {response.status_code}, Response: {response.text}"); return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error while fetching template details: {e}"); return None


# --- NEW FUNCTION ---
def get_documents(alation_url, hub_id, folder_id):
    """
    Fetches documents from a specific folder within a specific hub.
    """
    if not current_api_access_token:
        print("ERROR: No valid API Access Token. Cannot fetch documents.")
        return None

    headers = {'Token': current_api_access_token}
    api_url = f"{alation_url}/integration/v2/document/"
    params = {
        'document_hub_id': hub_id,
        'parent_folder_id': folder_id
    }

    try:
        print(f"LOG: Fetching documents with params: {params}")
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"ERROR: Failed to fetch documents. Status: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error while fetching documents: {e}")
        return None