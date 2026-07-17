#!/usr/bin/env python3
"""refresh_google_token.py — refresh Google OAuth token in place, no re-auth needed.

The PAT/refresh_token at ~/.hermes/profiles/ezy_portal_expert/google_token.json
expires every ~30 min for the access token, every ~7 days for the refresh token.
When lumos/sheets scripts fail with `invalid_grant: Token has been expired or revoked`,
just run this — DON'T bother the user for re-auth.

Usage:
    python3 refresh_google_token.py
    # OR from another script:
    from refresh_google_token import get_valid_credentials
"""
import os, json, urllib.request, urllib.parse, datetime

TOKEN_PATH = os.path.expanduser("~/.hermes/profiles/ezy_portal_expert/google_token.json")


def refresh_now():
    """POST refresh_token to Google's token_uri, save new access token in place.
    Returns the updated token dict."""
    t = json.load(open(TOKEN_PATH))
    data = urllib.parse.urlencode({
        "client_id": t["client_id"],
        "client_secret": t["client_secret"],
        "refresh_token": t["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        t["token_uri"],
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    r = urllib.request.urlopen(req, timeout=15)
    new = json.loads(r.read())
    t["token"] = new["access_token"]
    if "expires_in" in new:
        t["expiry"] = (
            datetime.datetime.utcnow()
            + datetime.timedelta(seconds=new["expires_in"])
        ).isoformat() + "Z"
    json.dump(t, open(TOKEN_PATH, "w"), indent=2)
    return t


def get_valid_credentials():
    """Returns google.oauth2 Credentials object with refreshed token. Used by scripts:
        from google.oauth2.credentials import Credentials
        creds = get_valid_credentials()
        svc = build('sheets','v4', credentials=creds, cache_discovery=False)
    """
    from google.oauth2.credentials import Credentials
    t = json.load(open(TOKEN_PATH))
    creds = Credentials.from_authorized_user_info(t)
    if creds.expired:
        refresh_now()
        t = json.load(open(TOKEN_PATH))
        creds = Credentials.from_authorized_user_info(t)
    return creds


if __name__ == "__main__":
    t = refresh_now()
    print(f"OK refreshed, expires: {t.get('expiry')}")
