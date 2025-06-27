import requests
import os
import time
import json
import webbrowser
import logging
from urllib.parse import urlparse, parse_qs

try:
    from dotenv import load_dotenv

    load_dotenv()
    CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
except ImportError:
    logging.info(
        "dotenv library not found. Please install it with 'pip install python-dotenv'"
    )
    # Or set your credentials manually for a quick test:
    CLIENT_ID = "YOUR_CLIENT_ID"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"


AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
API_URL = "https://www.strava.com/api/v3"
TOKEN_FILE = "credentials/strava_tokens.json"

# Check if credentials are set
if not CLIENT_ID or not CLIENT_SECRET or CLIENT_ID == "YOUR_CLIENT_ID":
    logging.info("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set.")
    logging.info("Please create a .env file or set them in the script.")
    exit()


def save_tokens(tokens, token_file=TOKEN_FILE):
    """Saves the tokens to a file."""
    with open(token_file, "w") as f:
        json.dump(tokens, f)
    logging.info("Tokens saved to strava_tokens.json")


def load_tokens():
    """Loads the tokens from a file."""
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def refresh_access_token(tokens):
    """Refreshes the access token using the refresh token."""
    logging.info("Access token expired, refreshing...")
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token",
    }

    response = requests.post(TOKEN_URL, data=payload)
    response.raise_for_status()  # Raise an exception for bad status codes

    new_tokens = response.json()
    save_tokens(new_tokens)
    return new_tokens


def get_access_token():
    """
    Gets a valid access token.
    - Loads from file if available.
    - Refreshes if expired.
    - Guides through initial auth if no tokens exist.
    """
    tokens = load_tokens()

    if tokens:
        # Check if the token is expired or will expire in the next minute
        if time.time() > tokens["expires_at"] - 60:
            tokens = refresh_access_token(tokens)
        else:
            logging.info("Access token is valid.")
        return tokens["access_token"]

    # --- Initial Authentication Flow ---
    else:
        logging.info("No tokens found. Starting initial authentication.")
        # Step 1: Get authorization from the user
        auth_params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": "http://localhost/exchange_token",
            "approval_prompt": "force",
            "scope": "read,activity:read_all",  # Request read access to all activities
        }

        auth_full_url = (
            requests.Request("GET", AUTH_URL, params=auth_params).prepare().url
        )
        logging.info(
            "\n1. A browser window will open for you to authorize this script."
        )
        logging.info(
            "2. After authorizing, Strava will redirect you to a URL that looks like 'http://localhost/exchange_token?state=&code=...&scope=...'"
        )
        logging.info(
            "3. Please copy that entire URL from your browser's address bar and paste it here."
        )

        webbrowser.open(auth_full_url)

        auth_response_url = input("\nPaste the full redirect URL here: ")

        # Step 2: Extract the authorization code from the URL
        try:
            parsed_url = urlparse(auth_response_url)
            query_params = parse_qs(parsed_url.query)
            auth_code = query_params["code"][0]
            logging.info(f"Successfully extracted authorization code: {auth_code}")
        except (KeyError, IndexError):
            logging.info("Error: Could not find 'code' in the provided URL.")
            return None

        # Step 3: Exchange the authorization code for an access token
        token_payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code,
            "grant_type": "authorization_code",
        }

        logging.info("Exchanging authorization code for access token...")
        response = requests.post(TOKEN_URL, data=token_payload)
        response.raise_for_status()

        new_tokens = response.json()
        save_tokens(new_tokens)

        return new_tokens["access_token"]


def get_athlete_activities(access_token):
    """Fetches the last 20 activities for the authenticated athlete."""
    if not access_token:
        logging.info("Cannot fetch activities without a valid access token.")
        return None

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": 5, "page": 4}

    logging.info("\nFetching recent activities from Strava...")
    response = requests.get(
        f"{API_URL}/athlete/activities", headers=headers, params=params
    )

    try:
        response.raise_for_status()
        activities = response.json()

        if not activities:
            logging.info("No activities found.")
        else:
            logging.info("--- Recent Activities ---")
            for activity in activities:
                activity_name = activity["name"]
                distance_km = activity["distance"] / 1000
                logging.info(f"- {activity_name} ({distance_km:.2f} km)")

        return activities

    except requests.exceptions.HTTPError as err:
        logging.info(f"HTTP Error: {err}")
        logging.info(f"Response Body: {response.text}")
        return None


if __name__ == "__main__":
    logging.info("--- Strava API Script ---")
    access_token = get_access_token()
    if access_token:
        activities = get_athlete_activities(access_token)
    else:
        logging.info("\nCould not obtain access token. Exiting.")
