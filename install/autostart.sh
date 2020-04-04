#!/bin/bash

echo "starting redis Docker container"
docker run --name redis -p 6379:6379 -v redis-data:/data -d redis redis-server --appendonly yes

echo "entering BadgeHub environment"
cd /usr/local/cfsj-login-system/src/
source /usr/local/cfsj-login-system/src/venv/bin/activate
echo "starting BadgeHub"
python /usr/local/cfsj-login-system/src/run.py
chromium-browser --kiosk http://localhost:5000