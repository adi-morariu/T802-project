import xml.etree.ElementTree as ET
from nornir.core.task import Result
import requests

"""The script activates a previously saved configuration of an Acme SBC"""


def activate_config(task):
    """Activate the configuration after it is saved"""

    token = task.host["token"]
    api_url = f"https://{task.host.hostname}/rest/v1.2/configuration/management?action=activate"
    headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}
    response = requests.post(url=api_url, headers=headers, timeout=10, verify=False)

    if response.status_code == 202:
        root = ET.fromstring(response.text)
        link_url = root.find(".//link")
        response = requests.get(
            url=link_url.text, headers=headers, timeout=10, verify=False
        )
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            status = root.find(".//status")
            if status.text == "success":
                message = status.text
            else:
                error_message = root.find(".//errorMessage")
                message = f"{status.text}, {error_message.text}"
            return Result(host=task.host, result=message)
    else:
        root = ET.fromstring(response.text)
        error_message = root.find(".//errorMessage")
        return Result(
            host=task.host,
            result=f"Status code: {response.status_code}. {error_message.text}",
        )
