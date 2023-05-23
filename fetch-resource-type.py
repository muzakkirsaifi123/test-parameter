import yaml

def fetch_resource_types(file_path):
    # define a Empty string
    types = []

    with open(file_path, 'r') as file:
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

file_path = 'sample.yaml'
types_list = fetch_resource_types(file_path)
print(types_list)
