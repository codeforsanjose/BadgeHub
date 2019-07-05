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


def convert_to_dict(obj):
    """
    A function takes in a custom object and returns a dictionary representation of the object.
    This dict representation includes meta data such as the object's module and class names.

    see https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041
    """

    #  Populate the dictionary with object properties
    obj_dict = {}
    obj_dict.update(obj.__dict__)
    return obj_dict
