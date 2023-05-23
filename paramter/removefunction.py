#!/usr/bin/env python3
import requests
import base64
import requests
import os
import shutil
import yaml
import urllib3
from zipfile import ZipFile
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential
from triggerfunctionaks import trigger_pipeline


# Remove the directory (recursive or non recursive)
def remove_directory(dirname: str, recursive: bool) -> int:
    if recursive:
        shutil.rmtree(dirname)
        return 0
    else:
        os.rmdir(dirname)
        return 0


# Remove the file
def remove_file(filename: str) -> int:
    os.remove(filename)
    return 0

