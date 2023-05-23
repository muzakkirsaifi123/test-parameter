import yaml
import requests, json
from  buildheader import build_headers_for_ado_with_authorization
# trigger pipeline
def trigger_pipeline(pipeline_id: str, organization_name: str, project_name: str, token:str, component_dict:dict={}, branch_name:str='') -> int:
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

    response = requests.post(api_url, headers=build_headers_for_ado_with_authorization(
        ado_pat_token=ado_pat), json=body_data)

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
