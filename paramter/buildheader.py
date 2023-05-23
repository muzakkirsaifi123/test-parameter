import base64

# build headers for pipeline api call
def build_headers_for_ado_with_authorization(ado_pat_token: str, content_type: str = 'application/json') -> dict:
    headers = {
        "Authorization": "Basic " + base64.b64encode(f":{ado_pat_token}".encode("ascii")).decode("ascii"),
        "Content-Type": content_type
    }
    return headers