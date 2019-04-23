import os
import sys
import socket


def get_server_ip_address():
    """
    https://stackoverflow.com/a/166589/940217
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    our_ip = s.getsockname()[0]
    s.close()
    return our_ip


def get_script_path():
    """
    http://stackoverflow.com/a/4943474/940217
    """
    return os.path.dirname(os.path.realpath(sys.argv[0]))
