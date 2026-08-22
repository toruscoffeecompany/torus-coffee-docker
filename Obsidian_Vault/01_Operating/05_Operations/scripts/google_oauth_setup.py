#!/usr/bin/env python3
"""Google OAuth setup for Torus Coffee Company - re-authenticate and verify access."""
import os
import sys
import json
from pathlib import Path

# Add venv to path
venv_path = Path(__file__).parent.parent / "venv" / "Lib" / "site-packages"
sys.path.insert(0, str(venv_path))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Config
TOKEN_PATH = Path(r"C:\Users\torus\AppData\Local\hermes\google_token.json")
CLIENT_SECRET_PATH = Path(r"C:\Users\torus\AppData\Local\hermes\google_client_secret.json")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/calendar",
]

def main():
    print("=== Google OAuth Setup ===\n")
    
    # Load existing token
    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            print(f"✓ Loaded existing token")
            print(f"  Valid: {creds.valid}")
            print(f"  Expired: {creds.expired}")
        except Exception as e:
            print(f"⚠ Could not load token: {e}")
            creds = None
    
    # Refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("\nRefreshing token...")
            try:
                creds.refresh(Request())
                print("✓ Token refreshed")
            except Exception as e:
                print(f"⚠ Refresh failed: {e}")
                print("Need to re-authenticate via browser...")
                creds = None
        
        if not creds:
            print("\nLaunching browser for OAuth consent...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
            print("✓ OAuth consent completed")
        
        # Save token
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"✓ Token saved to {TOKEN_PATH}")
    else:
        print("✓ Token is already valid")
    
    # Test Gmail
    print("\n=== Testing Gmail Access ===")
    try:
        gmail = build("gmail", "v1", credentials=creds)
        profile = gmail.users().getProfile(userId="me").execute()
        print(f"✓ Gmail connected: {profile.get('emailAddress')}")
    except Exception as e:
        print(f"✗ Gmail failed: {e}")
    
    # Test Drive
    print("\n=== Testing Drive Access ===")
    try:
        drive = build("drive", "v3", credentials=creds)
        about = drive.about().get(fields="user").execute()
        print(f"✓ Drive connected: {about.get('user', {}).get('emailAddress')}")
    except Exception as e:
        print(f"✗ Drive failed: {e}")
    
    print("\n=== Setup Complete ===")

if __name__ == "__main__":
    main()
