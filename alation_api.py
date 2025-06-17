# alation_api.py
import requests

current_api_access_token = None


# The validate_api_token and refresh_api_token functions remain unchanged
def validate_api_token(alation_url, user_id, access_token):
    if not access_token: print("LOG: No API Access Token present to validate."); return False
    headers = {'Token': access_token};
    api_url = f"{alation_url}/integration/v2/user/{user_id}/"
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            print("LOG: API Access Token is valid."); return True
        else:
            print(f"LOG: API Access Token is invalid or expired. Status: {response.status_code}"); return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error during token validation: {e}");
        return False


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


# --- NEW FUNCTION ---
def get_template_details(alation_url, template_id):
    """
    Fetches the details and fields for a specific custom template.
    """
    if not current_api_access_token:
        print("ERROR: No valid API Access Token. Cannot fetch template details.")
        return None

    headers = {'Token': current_api_access_token}
    api_url = f"{alation_url}/integration/v1/custom_template/{template_id}/"

    try:
        print(f"LOG: Fetching details for template ID: {template_id}")
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"ERROR: Failed to fetch template details. Status: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error while fetching template details: {e}")
        return None