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
import glob
# from triggerfunctionaks import trigger_pipeline
# from keyvault import fetch_key_vault_secret
# # from git import get_github_repo, extract_zip_file
# from getfunction import get_pipeline_id, get_file_content,get_subfolders_name
# from removefunction import remove_directory, remove_file
# import automationassets
# from automationassets import AutomationAssetNotFound


#############
# FUNCTIONS #
#############

# fetch secret value from the key vault
def fetch_key_vault_secret(tenant_id:str, client_id:str, client_secret:str, secret_name:str) -> str:
    # Retrieve the IDs and secret to use with ServicePrincipalCredentials
    # subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    # tenant_id = os.environ["AZURE_TENANT_ID"]
    # client_id = os.environ["AZURE_CLIENT_ID"]
    # client_secret = os.environ["AZURE_CLIENT_SECRET"]

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

    client = SecretClient(
        vault_url="https://PATVault06.vault.azure.net/",
        credential=credential
    )
    
    secret = client.get_secret(secret_name)
    print(f"Secret value is {secret.value}")
    return secret.value


# Get GitHub Repo as Zip
def get_github_repo(owner: str, repo: str, ref: str, token: str, outfile: str = 'repo.zip') -> str:
    http = urllib3.PoolManager()

    url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{ref}"

    r = http.request(
        'GET',
        url=url,
        preload_content=False,
        headers={'Authorization': "Bearer " + token}
    )

    with open(outfile, 'wb') as out:
        while True:
            data = r.read(64)
            if not data:
                break
            out.write(data)
    r.release_conn()

    return outfile


# Extract zip file
def extract_zip_file(file: str) -> int:
    with ZipFile(file, 'r') as zObject:
        # Extracting all the members of the zip into a specific location.
        zObject.extractall(path="repo")
    return 0


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



# build headers for pipeline api call
def build_headers_for_ado_with_authorization(ado_pat_token: str, content_type: str = 'application/json') -> dict:
    headers = {
        "Authorization": "Basic " + base64.b64encode(f":{ado_pat_token}".encode("ascii")).decode("ascii"),
        "Content-Type": content_type
    }
    return headers





# trigger pipeline
def trigger_pipeline_aks(pipeline_id: str, organization_name: str, project_name: str, token:str, component_dict:dict={}, branch_name:str='') -> int:
    api_url = f"https://dev.azure.com/{organization_name}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
    ado_pat = token

    # print(component_dict)
    # if component_dict:
    #     template_parameters = {}
    # for key, value in component_dict.items():
    #     template_parameters[key] = value
    # print(template_parameters)

    # def build_template_parameters(component_dict, prefix='', template_parameters=None):
    #     if template_parameters is None:
    #         template_parameters = {}

    #     for key, value in component_dict.items():
    #         new_key = f'{prefix}_{key}' if prefix else key

    #         if isinstance(value, dict):
    #             build_template_parameters(value, prefix=new_key, template_parameters=template_parameters)
    #         else:
    #             template_parameters[new_key] = value

    #     return template_parameters

    # if component_dict:
    #     template_parameters = build_template_parameters(component_dict)
    #     print(template_parameters)




    if component_dict:

        template_parameters = {}
        template_parameters['cluster_name']=component_dict['name']
        template_parameters['private_cluster']=component_dict['config']['private_cluster_enabled']
        template_parameters['network_plugin']=component_dict['config']['network_profile']['network_plugin']
        # template_parameters['network_policy']=component_dict['config']['network-policy']
        template_parameters['loadbalancer_sku']= component_dict['config']['network_profile']['load_balancer_sku']
        template_parameters['node_pool_vm_size']=component_dict['config']['node-pool']['vm_size']
        template_parameters['node_pool_name']=component_dict['config']['node-pool']['name']
        template_parameters['enable_auto_scaling'] = component_dict['config']['enable_auto_scaling']
        # template_parameters['node_pool_type']=component_dict['config']['node-pool']['type']
        template_parameters['node_pool_vm_disk_size']=component_dict['config']['node-pool']['os-disk-size-gb']
        template_parameters['node_count']=component_dict['config']['node-pool']['node-count']
        template_parameters['vnet_name']=component_dict['config']['vnet_name']
        template_parameters['resource_group_name']=component_dict['resource-group-name']
        template_parameters['location']=component_dict['config']['location']
        template_parameters['kubernetes_version']=component_dict['config']['kubernetes-version']
    
    
    body_data = {
        'templateParameters': template_parameters,
        "definition": {
            "id": pipeline_id
        },
        "resources": {
            "repositories": {
                "self": {
                    "refName": "refs/heads/POC-Naas-Component"
                }
            }
        }
    }
    
    
    # print(body_data)
    print(template_parameters)

    # response = requests.post(api_url, headers=build_headers_for_ado_with_authorization(
    #     ado_pat_token=ado_pat), json=body_data)

    # if response.status_code == 200:
    #     print("triggered successfully!")
    #     return 0
    # else:
    #     print(f"failed{response.status_code}")
    #     return response.status_code

# trigger function for the ACR
def trigger_pipeline_acr(pipeline_id: str, organization_name: str, project_name: str, token:str, component_dict:dict={}, branch_name:str='') -> int:
    api_url = f"https://dev.azure.com/{organization_name}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
    ado_pat = token

    # print(component_dict)
    # if component_dict:
    #     template_parameters = {}
    # for key, value in component_dict.items():
    #     template_parameters[key] = value
    # print(template_parameters)

    # def build_template_parameters(component_dict, prefix='', template_parameters=None):
    #     if template_parameters is None:
    #         template_parameters = {}

    #     for key, value in component_dict.items():
    #         new_key = f'{prefix}_{key}' if prefix else key

    #         if isinstance(value, dict):
    #             build_template_parameters(value, prefix=new_key, template_parameters=template_parameters)
    #         else:
    #             template_parameters[new_key] = value

    #     return template_parameters

    # if component_dict:
    #     template_parameters = build_template_parameters(component_dict)
    #     print(template_parameters)




    if component_dict:

        template_parameters = {}
        template_parameters['acr_name']=component_dict['name']
        # template_parameters['private_cluster']=component_dict['config']['private_cluster_enabled']
        # template_parameters['network_plugin']=component_dict['config']['network_profile']['network_plugin']
        # template_parameters['network_policy']=component_dict['config']['network-policy']
        # template_parameters['loadbalancer_sku']= component_dict['config']['network_profile']['load_balancer_sku']
        # template_parameters['node_pool_vm_size']=component_dict['config']['node-pool']['vm_size']
        # template_parameters['node_pool_name']=component_dict['config']['node-pool']['name']
        # template_parameters['enable_auto_scaling'] = component_dict['config']['enable_auto_scaling']
        # template_parameters['node_pool_type']=component_dict['config']['node-pool']['type']
        # template_parameters['node_pool_vm_disk_size']=component_dict['config']['node-pool']['os-disk-size-gb']
        # template_parameters['node_count']=component_dict['config']['node-pool']['node-count']
        # template_parameters['vnet_name']=component_dict['config']['vnet_name']
        template_parameters['resource_group_name']=component_dict['resource-group-name']
        template_parameters['location']=component_dict['config']['resourceLocation']
        template_parameters['service_tier']=component_dict['config']['service_tiers']

        # template_parameters['kubernetes_version']=component_dict['config']['kubernetes-version']
    
    
    body_data = {
        'templateParameters': template_parameters,
        "definition": {
            "id": pipeline_id
        },
        "resources": {
            "repositories": {
                "self": {
                    "refName": "refs/heads/POC-Naas-Component"
                }
            }
        }
    }
    
    
    # print(body_data)
    print(template_parameters)

    # response = requests.post(api_url, headers=build_headers_for_ado_with_authorization(
    #     ado_pat_token=ado_pat), json=body_data)

    # if response.status_code == 200:
    #     print("triggered successfully!")
    #     return 0
    # else:
    #     print(f"failed{response.status_code}")
    #     return response.status_code






#trigger function for the storage-account

def trigger_pipeline_storage_account(pipeline_id: str, organization_name: str, project_name: str, token:str, component_dict:dict={}, branch_name:str='') -> int:
    api_url = f"https://dev.azure.com/{organization_name}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
    ado_pat = token

    # print(component_dict)
    # if component_dict:
    #     template_parameters = {}
    # for key, value in component_dict.items():
    #     template_parameters[key] = value
    # print(template_parameters)

    # def build_template_parameters(component_dict, prefix='', template_parameters=None):
    #     if template_parameters is None:
    #         template_parameters = {}

    #     for key, value in component_dict.items():
    #         new_key = f'{prefix}_{key}' if prefix else key

    #         if isinstance(value, dict):
    #             build_template_parameters(value, prefix=new_key, template_parameters=template_parameters)
    #         else:
    #             template_parameters[new_key] = value

    #     return template_parameters

    # if component_dict:
    #     template_parameters = build_template_parameters(component_dict)
    #     print(template_parameters)




    if component_dict:

        template_parameters = {}
        template_parameters['name']=component_dict['name']
        template_parameters['sku']=component_dict['sku']
        template_parameters['private-endpoint']=component_dict['private-endpoint']

        # template_parameters['private_cluster']=component_dict['config']['private_cluster_enabled']
        # template_parameters['network_plugin']=component_dict['config']['network_profile']['network_plugin']
        # # template_parameters['network_policy']=component_dict['config']['network-policy']
        # template_parameters['loadbalancer_sku']= component_dict['config']['network_profile']['load_balancer_sku']
        # template_parameters['node_pool_vm_size']=component_dict['config']['node-pool']['vm_size']
        # template_parameters['node_pool_name']=component_dict['config']['node-pool']['name']
        # template_parameters['enable_auto_scaling'] = component_dict['config']['enable_auto_scaling']
        # # template_parameters['node_pool_type']=component_dict['config']['node-pool']['type']
        # template_parameters['node_pool_vm_disk_size']=component_dict['config']['node-pool']['os-disk-size-gb']
        # template_parameters['node_count']=component_dict['config']['node-pool']['node-count']
        # template_parameters['vnet_name']=component_dict['config']['vnet_name']
        # template_parameters['resource_group_name']=component_dict['resource-group-name']
        # template_parameters['location']=component_dict['config']['location']
        # template_parameters['kubernetes_version']=component_dict['config']['kubernetes-version']
    
    
    body_data = {
        'templateParameters': template_parameters,
        "definition": {
            "id": pipeline_id
        },
        "resources": {
            "repositories": {
                "self": {
                    "refName": "refs/heads/POC-Naas-Component"
                }
            }
        }
    }
    
    
    # print(body_data)
    print(template_parameters)

    # response = requests.post(api_url, headers=build_headers_for_ado_with_authorization(
    #     ado_pat_token=ado_pat), json=body_data)

    # if response.status_code == 200:
    #     print("triggered successfully!")
    #     return 0
    # else:
    #     print(f"failed{response.status_code}")
    #     return response.status_code




# Function logic for AKS component
# def trigger_pipeline_aks(component):
    
# # Function logic for ACR component

# def trigger_pipeline_acr(component):
#     print("From ACR")



# # Function logic for VNet component

# def trigger_pipeline_vnet(component):


# # Function logic for Subnet component
# def trigger_pipeline_subnet(component):




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


# def trigger_pipeline_acr(pipeline_id: str, organization_name: str, project_name: str, token:str, component_dict:dict={}, branch_name:str='') -> int:
#     print("I am from ACR")

# def trigger_pipeline_storage_account(pipeline_id: str, organization_name: str, project_name: str, token:str, component_dict:dict={}, branch_name:str='') -> int:
#     print("I am from storage-account")

def main():
    # fetch github pat token and ado pat token from key vault


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

    try:
            # pass
        if len(subdir_list) == 1:
            subdir = subdir_list[0].split('/')
            # print(subdir)
        # print(subdir)

        # get compute.yml file content
        # compute_yaml_file_content = get_file_content(
        #     file=f"repo/{subdir[-1]}/components/aks.yml")
        

        # Define the pattern for file names
        file_pattern = f"repo/{subdir[-1]}/components/*.yml"

        # Get a list of file paths that match the pattern
        file_paths = glob.glob(file_pattern)

        # Iterate over the file paths and process each file
        # for file_path in file_paths:
        #     compute_yaml_file_content = get_file_content(file=file_path)

        #     # Process the file as needed
        #     for component in compute_yaml_file_content['components']:
        #         if component['type'] == 'akse':
        #             aks_component = component
        #             print("This is the AKS component:\n", aks_component)
        #             # Call the trigger_pipeline function for AKS component
        #             # trigger_pipeline(pipeline_id=pipeline_id, organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict=aks_component)
        #         elif component['type'] == 'ecr':
        #             ecr_component = component
        #             print("This is the ECR component:\n", ecr_component)
        # Iterate over the file paths and process each file
        organization_name = "DCT"
        project_name = "test"
        pipeline_id = "2"

        for file_path in file_paths:
            compute_yaml_file_content = get_file_content(file=file_path)

            # Process the file as needed
            for component in compute_yaml_file_content['components']:
                component_type = component['type']
                # print("Component:", component)

                # Call the corresponding trigger function based on the component type
                if component_type == 'aks':
                    trigger_pipeline_aks(pipeline_id=pipeline_id,
                            organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict = component)
                elif component_type == 'acr':
                    trigger_pipeline_acr(pipeline_id=pipeline_id,
                            organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict = component)
                elif component_type == 'storage-account':
                    # print("I am from storage-account")
                    trigger_pipeline_storage_account(pipeline_id=pipeline_id,
                            organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict = component)
        # Add more conditions for othe
                    # Call the trigger_pipeline function for ECR component
                    # trigger_pipeline(pipeline_id=pipeline_id, organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict=ecr_component)
        # Add more conditions for other component types as needed




    # for component_type in component_list:
    #     for component in compute_yaml_file_content['components']:
    #         if component['type'] == component_type:
    #             print(f"This is the {component_type} component:\n{component}\n")
                
                
                
                
                
                # trigger_pipeline(pipeline_id=pipeline_id,
                #         organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict = component)
    # def trigger_pipeline_{component_type}_test():
    #     print("hello-World")

        # trigger_pipeline(pipeline_id=pipeline_id,
        #                     organization_name=organization_name, project_name=project_name, token=ado_pat, component_dict = aks_component)

    finally:
        #  remove_directory(dirname='repo', recursive=True)
         remove_file(filename='repo.zip')

if __name__ == '__main__':
    main()