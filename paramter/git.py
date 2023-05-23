# #!/usr/bin/env python3
# import requests
# import base64
# import requests
# import os
# import shutil
# import yaml
# import urllib3
# from zipfile import ZipFile
# from azure.keyvault.secrets import SecretClient
# from azure.identity import ClientSecretCredential
# from triggerfunctionaks import trigger_pipeline

# # Get GitHub Repo as Zip
# def get_github_repo(owner: str, repo: str, ref: str, token: str, outfile: str = 'repo.zip') -> str:
#     http = urllib3.PoolManager()

#     url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{ref}"

#     r = http.request(
#         'GET',
#         url=url,
#         preload_content=False,
#         headers={'Authorization': "Bearer " + token}
#     )

#     with open(outfile, 'wb') as out:
#         while True:
#             data = r.read(64)
#             if not data:
#                 break
#             out.write(data)
#     r.release_conn()

#     return outfile


# # Extract zip file
# def extract_zip_file(file: str) -> int:
#     with ZipFile(file, 'r') as zObject:
#         # Extracting all the members of the zip into a specific location.
#         zObject.extractall(path="repo")
#     return 0
