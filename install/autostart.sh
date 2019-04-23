#!/bin/bash
cd /usr/local/cfsj-login-system/src/
source /usr/local/cfsj-login-system/src/venv/bin/activate
/usr/local/cfsj-login-system/src/main.py
chromium-browser --kiosk http://localhost:5000