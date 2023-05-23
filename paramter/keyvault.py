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

