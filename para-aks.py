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
def extract_zip_file(file: str) -> int:
    with ZipFile(file, 'r') as zObject:
        # Extracting all the members of the zip into a specific location.
        zObject.extractall(path="repo")
    return 0


# Get the subfolders name
def get_subfolders_name(dirname: str) -> list:
    subdirs_list = [os.path.join(dirname, o) for o in os.listdir(
        dirname) if os.path.isdir(os.path.join(dirname, o))]
    # print('From Function: ')
    # print(subdirs_list)
    return subdirs_list


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

    if component_dict:

        template_parameters = {}
        template_parameters['acr_name']=component_dict['name']
        template_parameters['resource_group_name']=component_dict['resource-group-name']
        template_parameters['location']=component_dict['config']['resourceLocation']
        template_parameters['service_tier']=component_dict['config']['service_tiers']
    
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

    if component_dict:

        template_parameters = {}
        template_parameters['name']=component_dict['name']
        template_parameters['sku']=component_dict['sku']
        template_parameters['private-endpoint']=component_dict['private-endpoint']
        
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




def flatten_yaml(yaml_obj, parent_key='', sep='-'):
    items = []

    for k, v in yaml_obj.items():
        new_key = f"{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_yaml(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def yaml_to_flat_str(data, prefix=''):
    result = ''
    for key, value in data.items():
        if isinstance(value, dict):
            result += yaml_to_flat_str(value, prefix=f"{prefix}{key}")
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                result += yaml_to_flat_str(item, prefix=f"{prefix}{key}[{idx}]")
        else:
            result += f"{key}: {value}\n"
    return result


# trigger pipeline
def trigger_pipeline(pipeline_id: str, organization_name: str, project_name: str, token: str, template_params: dict = None, branch_name: str = None, component_dict: dict = None) -> int:
    api_url = f"https://dev.azure.com/{organization_name}/{project_name}/_apis/pipelines/{pipeline_id}/runs?api-version=6.1-preview.1"
    # print(api_url)
    ado_pat = token

    body_json = {
        # 'templateParameters': template_params,
        "definition": {
            "id": pipeline_id
        }
    }

    if template_params is not None:
        body_json['templateParameters'] = template_params

    if branch_name is not None:
        resources_body_json = {
            "repositories": {
                "self": {
                    "refName": f"refs/heads/{branch_name}"
                }
            }
        }

        body_json['resources'] = resources_body_json


    print(body_json)

    response = requests.post(api_url, headers=build_headers_for_ado_with_authorization(
        ado_pat_token=ado_pat), json=body_json)
    

    if response.status_code == 200:
        print("triggered successfully!")
        return 0
    else:
        print(f"failed{response.status_code}")
        return response.status_code


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

def fetch_resource_types(compute_yaml_file_path):
    # define a Empty string
    types = []

    with open(compute_yaml_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
        # print(yaml_data)

        if "shared-resources" in yaml_data:

            shared_resources = yaml_data["shared-resources"]
            # print(shared_resources)
            if isinstance(shared_resources, list):
                for resource in shared_resources:
                    if isinstance(resource, dict) and "type" in resource:
                        types.append(resource["type"])

    return types

# file_path = 'sample.yaml'
# types_list = fetch_resource_types(file_path)
# print(types_list)

def traverse_shared_resources(compute_yaml_file_content, pipeline_id_mapping, organization_name, project_name, ado_pat, branch_name):
    for component in compute_yaml_file_content['shared-resources']:
        resource_type = component['type']

        # Check if the resource type exists in the mapping dictionary
        if resource_type in pipeline_id_mapping:
            pipeline_id = pipeline_id_mapping[resource_type]
            print(f'resource type: {resource_type}')
            flattened_data = flatten_yaml(component)
            parameters_tf = yaml_to_flat_str(flattened_data, prefix='')
            # print(parameters_tf)
            print()

            # trigger the pipeline
            print("resource----------------")
            trigger_pipeline(pipeline_id=pipeline_id,
                             organization_name=organization_name,
                             project_name=project_name,
                             token=ado_pat,
                             template_params=parameters_tf,
                             branch_name=branch_name)

def main():
    # fetch github pat token and ado pat token from key vault
    print(ado_pat)
    # download the Github Repository as a zip file
    zipfile_name = get_github_repo(owner="duck-creek", repo="DCOD.Next.EMS",
                                   ref="POC-Naas-Component", token=github_pat)

    # extract the zip file (github repository)
    extract_zip_file(file=zipfile_name)

    subdir_list = get_subfolders_name(dirname='repo')


    print(subdir_list)

    organization_name = 'devopsmuzakkir'
    project_name = 'branch-DCT'
    branch_name = 'main'


    try:
        if len(subdir_list) == 1:
            if platform.system() == 'Windows':  # if os == 'Windows'
                subdir = subdir_list[0].split('\\')
            elif platform.system() == 'Linux':  # if os == 'Linux'
                subdir = subdir_list[0].split('/')

        compute_yaml_file_path = os.path.abspath(
            f"repo/{subdir[-1]}/environments/us/dev/central-us/compute.yml"
        )
        compute_yaml_file_content = get_file_content(file=compute_yaml_file_path)

        # print(compute_yaml_file_path)
        types_list = fetch_resource_types(compute_yaml_file_path)
        print(types_list)


        pipeline_ids = ["6", "118"]
        # Define a dictionary to map resource types to pipeline IDs
        pipeline_id_mapping = {resource_type: pipeline_id for resource_type, pipeline_id in zip(types_list, pipeline_ids)}
        print(pipeline_id_mapping)
        print()
        
        traverse_shared_resources(compute_yaml_file_content, pipeline_id_mapping, organization_name, project_name, ado_pat, branch_name)

    finally:
        # clean up the workspace
        remove_directory(dirname='repo', recursive=True)
        remove_file(filename='repo.zip')

if __name__ == '__main__':
    main()
