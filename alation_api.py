# alation_api.py
import requests

# This variable will hold the short-lived API Access Token after a successful refresh.
# It is stored in memory and not written to the config file.
current_api_access_token = None


def validate_api_token(alation_url, user_id, access_token):
    """
    Validates the current API access token.
    NOTE: Alation's validateAPIAccessToken endpoint is sometimes not enabled.
    A more reliable check is to simply try making a real API call (like fetching user details).
    For now, we will just attempt to get the user's own profile.
    """
    if not access_token:
        print("LOG: No API Access Token present to validate.")
        return False

    headers = {'Token': access_token}
    api_url = f"{alation_url}/integration/v2/user/{user_id}/"  # API call to get own user

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            print("LOG: API Access Token is valid.")
            return True
        else:
            print(f"LOG: API Access Token is invalid or expired. Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error during token validation: {e}")
        return False


def refresh_api_token(alation_url, user_id, refresh_token):
    """
    Refreshes the API access token using the refresh token.
    """
    global current_api_access_token
    api_url = f"{alation_url}/integration/v1/createAPIAccessToken/"
    body = {
        "refresh_token": refresh_token,
        "user_id": int(user_id)  # Ensure user_id is an integer
    }

    try:
        print("LOG: Attempting to refresh API Access Token...")
        response = requests.post(api_url, json=body)

        if response.status_code == 201:
            new_token_data = response.json()
            current_api_access_token = new_token_data['api_access_token']
            print("LOG: Successfully refreshed API Access Token.")
            return True
        else:
            print(f"ERROR: Failed to refresh access token. Status: {response.status_code}, Response: {response.text}")
            current_api_access_token = None
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error during token refresh: {e}")
        return False


# --- NEW FUNCTION ---
def get_folders(alation_url, params=None):
    """
    Generic function to fetch folders from the Alation API.
    Can be used to get top-level doc hubs or child folders.
    """
    if not current_api_access_token:
        print("ERROR: No valid API Access Token. Cannot fetch folders.")
        return None

    headers = {'Token': current_api_access_token}
    api_url = f"{alation_url}/integration/v2/folder/"

    try:
        print(f"LOG: Fetching folders with params: {params}")
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"ERROR: Failed to fetch folders. Status: {response.status_code}, Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error while fetching folders: {e}")
        return None