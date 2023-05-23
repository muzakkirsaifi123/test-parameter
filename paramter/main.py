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
from keyvault import fetch_key_vault_secret
# from git import get_github_repo, extract_zip_file
from getfunction import get_pipeline_id, get_file_content,get_subfolders_name
from removefunction import remove_directory, remove_file
# import automationassets
# from automationassets import AutomationAssetNotFound


#############
# FUNCTIONS #
#############
def main():
    # fetch github pat token and ado pat token from key vault
    # Here

    github_pat = fetch_key_vault_secret(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret, secret_name="GitHub-PAT")
    ado_pat = fetch_key_vault_secret(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret, secret_name="ADO-PAT")
    # download the Github Repository as a zip file
    zipfile_name = get_github_repo(owner="duck-creek", repo="DCOD.Next.EMS",
                                   ref="POC-Naas-Component", token=github_pat)
    #  # extract the zip file (github repository)
    extract_zip_file(file=zipfile_name)

    # subdir_list = get_subfolders_name(dirname='repo')
    # print(subdir_list)
    # if len(subdir_list) == 1:
    subdir_list = get_subfolders_name(dirname='repo')

    # print(subdir_list)

    # try:
        # pass
    if len(subdir_list) == 1:
        subdir = subdir_list[0].split('/')
        # print(subdir)
    # print(subdir)

    # get compute.yml file content
    compute_yaml_file_content = get_file_content(
        file=f"repo/{subdir[-1]}/environments/us/dev/central-us/compute.yml")
    # print(compute_yaml_file_content)
    resource_yaml_file_content = get_file_content(
        file=f"repo/{subdir[-1]}/environments/us/dev/central-us/resource-list.yaml")
    # print(resource_yaml_file_content)
    component_list = resource_yaml_file_content['my_resource']
    print(component_list)
    # print(compute_yaml_file_content['components'])

    # for component in compute_yaml_file_content['components']:
    #     if component['type'] == 'aks':
    #         aks_component = component    
    #         print(aks_component)



    # for component in compute_yaml_file_content['components']:
    #     if component['type'] in component_list:
    #         if component['type'] == 'aks':
    #             aks_component = component
    #             print("This is the AKS componnets:-\n",aks_component)
    #         elif component['type'] == 'ecr':
    #             acr_component = component
    #             print("This is the ACR componnets:-\n",acr_component)
    #         elif component['type'] == 'vnet':
    #             vnet_component = component
    #             print("This is the vnet componnets:-\n",vnet_component)
    #         elif component['type'] == 'subnet':
    #             subnet_component = component
    #             print("This is the subnet componnets:-\n",subnet_component)
    organization_name = "DCT"
    project_name = "test"
    pipeline_id = "2"


    for component_type in component_list:
        for component in compute_yaml_file_content['components']:
            if component['type'] == component_type:
                print(f"This is the {component_type} component:\n{component}\n")
                
                
                
                
                
                # trigger_pipeline(pipeline_id=pipeline_id,
                #         organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict = component)
    # def trigger_pipeline_{component_type}_test():
    #     print("hello-World")

    trigger_pipeline(pipeline_id=pipeline_id,
                        organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict = component)

    # finally:
        #  remove_directory(dirname='repo', recursive=True)
        #  remove_file(filename='repo.zip')

if __name__ == '__main__':
    main()