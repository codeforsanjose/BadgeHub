ps -face | grep zbar | awk '{print $2}' | xargs kill -s KILL
