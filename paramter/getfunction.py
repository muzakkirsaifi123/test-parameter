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

# Get File Content from the file present on given file path
def get_file_content(file: str) -> dict:
    with open(file, "r") as yaml_file:
        # print(type(yaml.safe_load(naas_yaml)))
        return yaml.safe_load(yaml_file)


# Get the pipeline id for the resource
def get_pipeline_id(resource: str, subdir: str) -> str:
    pipeline_id_yaml_file_content = get_file_content(
        file=f"repo/{subdir}/Code/yml/Pipeline_id.yml")

    for pipeline_data in pipeline_id_yaml_file_content["resources"]:
        if pipeline_data["resourceType"] == resource:
            # print(pipeline_data["pipelineID"])
            return pipeline_data['pipelineID']
# Get the subfolders name
def get_subfolders_name(dirname: str) -> list:
    subdirs_list = [os.path.join(dirname, o) for o in os.listdir(
        dirname) if os.path.isdir(os.path.join(dirname, o))]
    # print('From Function: ')
    # print(subdirs_list)
    return subdirs_list

