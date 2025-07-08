import xml.etree.ElementTree as ET
from nornir.core.task import Result
from pathlib import Path
import requests
from jinja2 import Environment, FileSystemLoader

"""The script renders the provided configuration templates and sends the configuration to the target devices"""


def send_config(task, configs):
    """Render the templates and send configuration"""

    api_url = f"https://{task.host.hostname}/rest/v1.2/configuration/configElements"
    token = task.host["token"]
    headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}

    current_file = Path(__file__).resolve()
    main_dir = current_file.parent.parent
    templates_dir = main_dir / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))

    rendered_configs = []
    for config in configs:

        template = env.get_template(f"{config}.j2")

        config_element = config.replace("-", "_")
        parameters = task.host.data.get(config_element, [])
        if isinstance(parameters, dict):
            rendered = template.render(param=parameters)
            rendered_configs.append(dict({config: rendered}))
        else:
            for param in parameters:
                rendered = template.render(param=param)
                rendered_configs.append(dict({config: rendered}))

    task.host["config"] = rendered_configs
    data = task.host["config"]
    result = []
    for element in data:
        for element_name, element_config in element.items():
            response = requests.post(
                url=api_url,
                headers=headers,
                timeout=10,
                data=element_config,
                verify=False,
            )
            if response.status_code == 200:
                result.append(f"Configuration applied: {element_name}")
                changed = True
            else:
                root = ET.fromstring(response.text)
                error_message = root.find(".//errorMessage")
                result.append(
                    f"Configuration failed: {element_name}. Status code: {response.status_code}. {error_message.text}"
                )
                changed = False

    return Result(host=task.host, result=result, changed=changed)
