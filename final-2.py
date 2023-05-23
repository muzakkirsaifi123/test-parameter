#!/usr/bin/env python3
import requests
import base64
import os
import shutil
import yaml
import urllib3
import platform
from zipfile import ZipFile
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential
import shutil

# import automationassets
# from automationassets import AutomationAssetNotFound

def fetch_key_vault_secret(tenant_id:str, client_id:str, client_secret:str, secret_name:str) -> str:

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
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
# def extract_zip_file(file: str) -> int:
#     with ZipFile(file, 'r') as zObject:
#         # Extracting all the members of the zip into a specific location.
#         zObject.extractall(path="repo")
#     return 0

def extract_zip_file(file: str) -> int:
    shutil.unpack_archive(file, "repo")
    return 0

# Get the subfolders name
# def get_subfolders_name(dirname: str) -> list:
#     subdirs_list = [os.path.join(dirname, o) for o in os.listdir(
#         dirname) if os.path.isdir(os.path.join(dirname, o))]
#     return subdirs_list

def get_subfolders_name(dirname: str) -> list:
    subdirs_list = [f.path for f in os.scandir(dirname) if f.is_dir()]
    return subdirs_list

# Get File Content from the file present on given file path
# def get_file_content(file: str) -> dict:
#     with open(file, "r") as yaml_file:
#         # print(type(yaml.safe_load(naas_yaml)))
#         return yaml.safe_load(yaml_file)

def get_file_content(file: str) -> dict:
    try:
        with open(file, "r") as yaml_file:
            return yaml.load(yaml_file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        return {}  # Or raise an exception if desired
    

def get_resource_types_list(content:list) -> list:

    # initialize an empty resources list
    resources = []

    for component in content:
        resources.append(component['type'])

    return resources


# Get the pipeline id for the resource
def get_pipeline_id(resource: str, subdir: str) -> str:
    pipeline_id_yaml_file_content = get_file_content(
        file=f"repo/{subdir}/Code/yml/Pipeline_id.yml")

    for pipeline_data in pipeline_id_yaml_file_content["resources"]:
        if pipeline_data["resourceType"] == resource:
            # print(pipeline_data["pipelineID"])
            return pipeline_data['pipelineID']


# build headers for pipeline api call
def build_headers_for_ado_with_authorization(ado_pat_token: str, content_type: str = 'application/json') -> dict:
    headers = {
        "Authorization": "Basic " + base64.b64encode(f":{ado_pat_token}".encode("ascii")).decode("ascii"),
        "Content-Type": content_type
    }
    return headers



# flattern yaml content to dict
def flatten_yaml(yaml_obj, parent_key='', sep='_'):
    items = []
    for k, v in yaml_obj.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_yaml(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# flatten yaml to string
def yaml_to_flat_str(data):
    # Flatten the YAML
    flattened_data = flatten_yaml(data)

    # Convert to multiline string
    result = "\n".join(f'{k}="{v}"' for k, v in flattened_data.items())
    return result


# trigger pipeline


def trigger_pipeline(pipeline_id: str, organization_name: str, project_name: str, token: str, template_params: dict = None, branch_name: str = None, component_dict: dict = None) -> int:
# def trigger_pipeline(pipeline_id: str, organization_name: str, project_name: str, token: str, template_params: dict = None, branch_name: str = None, component_dict: dict = None) -> int:
    api_url = f"https://dev.azure.com/{organization_name}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
    ado_pat = token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "definition": {
            "id": pipeline_id
        }
    }

    if template_params is not None:
        body["templateParameters"] = template_params

    if branch_name is not None:
        body["resources"] = {
            "repositories": {
                "self": {
                    "refName": f"refs/heads/{branch_name}"
                }
            }
        }

        print(body)
    # response = requests.post(api_url, headers=build_headers_for_ado_with_authorization(
    # ado_pat_token=ado_pat), json=body)

    # if response.status_code == 200:
    #     print("triggered successfully!")
    #     return 0
    # else:
    #     print(f"failed{response.status_code}")
    #     return response.status_code


# def trigger_pipeline(pipeline_id: str, organization_name: str, project_name: str, token: str, template_params: dict = None, branch_name: str = None, component_dict: dict = None) -> int:
#     api_url = f"https://dev.azure.com/{organization_name}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=7.0"
#     ado_pat = token
#     body_json = {
#         "definition": {
#             "id": pipeline_id
#         }
#     }

#     if template_params is not None:
#         body_json['templateParameters'] = template_params

#     if branch_name is not None:
#         resources_body_json = {
#             "repositories": {
#                 "self": {
#                     "refName": f"refs/heads/{branch_name}"
#                 }
#             }
#         }

#         body_json['resources'] = resources_body_json

       

#         print(body_json)
#     response = requests.post(api_url, headers=build_headers_for_ado_with_authorization(
#         ado_pat_token=ado_pat), json=body)

#     if response.status_code == 200:
#         print("triggered successfully!")
#         return 0
#     else:
#         print(f"failed{response.status_code}")
#         return response.status_code


# create a dictionary from the lists
def create_dictionary(keys, values):
    dictionary = dict(zip(keys, values))
    return dictionary


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

def fetch_branches_starting_with(owner, repo, token, prefix):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        branches = [branch["name"] for branch in response.json()]
        filtered_branches = [branch for branch in branches if branch.lower().startswith(prefix.lower())]
        return filtered_branches
    else:
        print(f"Error: Failed to fetch branches (Status Code: {response.status_code})")
        return []
#################
# MAIN FUNCTION #
#################

def main():
    # fetch github pat token and ado pat token from key vault
    owner="duck-creek"
    repo="DCOD.Next.EMS"
    organization_name = 'DCTEng'
    project_name = 'Duck Creek'   
    prefix="poc"
    # github_pat = fetch_key_vault_secret(secret_name="GitHub-PAT")
    # ado_pat = fetch_key_vault_secret(secret_name="ADO-PAT")
    github_pat = fetch_key_vault_secret(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret, secret_name="GitHub-PAT")
    print("github token:-",github_pat)
    ado_pat = fetch_key_vault_secret(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret, secret_name="ADO-PAT")
    print("ado token:-",ado_pat)
    # download the Github Repository as a zip file
    zipfile_name = get_github_repo(owner="duck-creek", repo="DCOD.Next.EMS",
                                   ref="POC-Naas-Component", token=github_pat)

    # extract the zip file (github repository)
    extract_zip_file(file=zipfile_name)

    subdir_list = get_subfolders_name(dirname='repo')

    # print(subdir_list)
    # subdir = None

    # organization name and project name for azure devops api


    try:
        # pass
        # Get the name of the Duck Creek folder inside the repo directory
        # if len(subdir_list) == 1:
        #     if platform.system() == 'Windows':  # if os == 'Windows'
        #         subdir = subdir_list[0].split('\\')
        #     elif platform.system() == 'Linux':  # if os == 'Linux'
        #         subdir = subdir_list[0].split('/')
        if len(subdir_list) == 1:
              subdir = subdir_list[0].split(os.path.sep)
        # print(subdir)
        
        # map of the ado pipeline id of the resources
        # pipeline_id = {
        #     'aks': 1667,
        #     'acr': 1666
        # }
        
        # read the compute.yml file
        compute_yaml_file_content = get_file_content(
                file=f"repo/{subdir[-1]}/environments/us/dev/central-us/compute.yml")
        # print(compute_yaml_file_content)
            
        # get list of all the resource types from the comput.yml
        resource_type = get_resource_types_list(compute_yaml_file_content['shared-resources'])
        print(resource_type)

        resource_pipeline_id=[1667,1666]

        pipeline_id=create_dictionary(resource_type, resource_pipeline_id)
        print(pipeline_id)
        branch_to_trigger= fetch_branches_starting_with(owner, repo, github_pat, prefix)
        print(branch_to_trigger)

        for resource in resource_type: # loop through the resources list
            for component in compute_yaml_file_content['shared-resources']: # loop through the list of maps of the components in compute.yml
                if component['type'] == resource:
                    
                    print(f'Resource: {resource}')
                    print('--------------------------------')
                    
                    # template parameters (tfvars content) of the resource
                    aks_tfvars_content={
                        'tfvars_content': yaml_to_flat_str(component['config']) #
                    }
                    
                    print(aks_tfvars_content)
                    
                    # # trigger the pipeline
                    trigger_pipeline(pipeline_id=pipeline_id[resource],
                                    organization_name=organization_name,
                                    project_name=project_name,
                                    token=ado_pat,
                                    template_params=aks_tfvars_content,
                                    branch_name='POC-Naas-Component')
                    
                    print('')



    finally:
        # pass
        # clean up the workspace
        remove_directory(dirname='repo', recursive=True)
        remove_file(filename='repo.zip')


#########################
# calling main function #
#########################
if __name__ == '__main__':
    main()
