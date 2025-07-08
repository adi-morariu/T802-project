import xml.etree.ElementTree as ET
from nornir.core.task import Result
import requests
import time

"""The script saves the configuration of an Acme SBC"""


def save_config(task):
    """Save the configuration after it is applied to the device"""

    token = task.host["token"]
    api_url = f"https://{task.host.hostname}/rest/v1.2/configuration/management?action=save"
    headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}
    response = requests.put(url=api_url, headers=headers, timeout=10, verify=False)

    if response.status_code == 202:
        root = ET.fromstring(response.text)
        link_url = root.find(".//link")
        max_time = 10
        start_time = time.time()
        while True:
            response = requests.get(
                url=link_url.text, headers=headers, timeout=10, verify=False
            )
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                status = root.find(".//status")
                if status.text in ("success", "fail"):
                    break
                elif time.time() - start_time > max_time:
                    raise TimeoutError("Operation timed out while waiting for status.")
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
