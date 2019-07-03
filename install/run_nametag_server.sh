#!/bin/bash

source /usr/local/cfsj-login-system/src/venv/bin/activate
echo "starting the server"
python -u nametag_server.py
deactivate