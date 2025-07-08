import xml.etree.ElementTree as ET
from nornir.core.task import Result
import requests

"""The script gets the access token needed for the REST API interaction with Acme SBCs"""


def get_access_token(task):
    """Get the access token needed for the REST API interaction"""

    api_url = f"https://{task.host.hostname}/rest/v1.2/auth/token"
    username = task.host.username
    password = task.host.password
    headers = {"Accept": "application/xml"}
    response = requests.post(
        url=api_url,
        headers=headers,
        auth=(username, password),
        timeout=10,
        verify=False,
    )

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        token = root.find(".//accessToken")
        task.host["token"] = token.text
        return Result(host=task.host, result="Token aquired")
    else:
        root = ET.fromstring(response.text)
        error_message = root.find(".//errorMessage")
        return Result(
            host=task.host,
            result=f"Status code: {response.status_code}. {error_message.text}",
        )
