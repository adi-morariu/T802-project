import xml.etree.ElementTree as ET
from nornir.core.task import Result
import requests

"""The script locks the configuration when configuring Acme SBCs to avoid concurent access"""


def get_config_lock(task):
    """Get the configuration lock to avoid concurent access"""

    token = task.host["token"]
    api_url = f"https://{task.host.hostname}/rest/v1.2/configuration/lock"
    headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}
    response = requests.post(url=api_url, headers=headers, timeout=10, verify=False)

    if response.status_code == 204:
        return Result(host=task.host, result="Configuration lock aquired")
    else:
        root = ET.fromstring(response.text)
        error_message = root.find(".//errorMessage")
        return Result(
            host=task.host,
            result=f"Status code: {response.status_code}. {error_message.text}",
        )
