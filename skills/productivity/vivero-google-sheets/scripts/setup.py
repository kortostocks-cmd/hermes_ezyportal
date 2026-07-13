#!/usr/bin/env python3
"""Google Workspace OAuth2 setup for vivero-google-sheets skill (profile-scoped)."""

import os
import sys
import subprocess
from pathlib import Path

# Profile-specific Hermes home
HERMES_PROFILE_HOME = Path(__file__).resolve().parents[4]  # ~/.hermes/profiles/ezy_portal_expert
os.environ["HERMES_HOME"] = str(HERMES_PROFILE_HOME)

# Delegate to the google-workspace skill's setup.py
GW_SETUP = HERMES_PROFILE_HOME / "skills/productivity/google-workspace/scripts/setup.py"

if __name__ == "__main__":
    # Pass all args to the actual setup script
    subprocess.run([sys.executable, str(GW_SETUP)] + sys.argv[1:], check=False)