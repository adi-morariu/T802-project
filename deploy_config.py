import argparse
from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
import urllib3
from tasks import activate_config
from tasks import get_access_token
from tasks import get_config_lock
from tasks import release_config_lock
from tasks import save_config
from tasks import send_config

# Disable certificate warnings
urllib3.disable_warnings()


"""The script renders configuration templates and sends configurations to Acme SBCs
   Usage: python deploy_config.py -d (or --device) -c (or --configs)
"""


def arg_parser():
    """Parse the arguments provided at script execution"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--device",
        help="Provide the host or group name from the hosts file",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--configs",
        nargs="+",
        help="Provide a list of configuration elements in the desired order",
        required=True,
    )
    return parser.parse_args()


def main():

    # Determine the hosts the script will run against
    args = arg_parser()
    target_sbc = args.device
    configs = args.configs

    # Initiate nornir
    nr = InitNornir(config_file="config.yaml")

    # Filter devices based on provided device input
    sbc = nr.filter(F(has_parent_group=target_sbc))

    # Get access token
    result_token = sbc.run(name="Get access token", task=get_access_token)
    print_result(result_token)

    # Get configuration lock
    result_lock = sbc.run(name="Get configuration lock", task=get_config_lock)
    print_result(result_lock)

    # Render and send configuration
    result_send = sbc.run(name="Send configuration", task=send_config, configs=configs)
    print_result(result_send)

    # Save configuration
    result_save = sbc.run(name="Save configuration", task=save_config)
    print_result(result_save)

    # Activate configuration
    result_activate = sbc.run(name="Activate configuration", task=activate_config)
    print_result(result_activate)

    # Release configuration lock
    result_unlock = sbc.run(name="Release configuration lock", task=release_config_lock)
    print_result(result_unlock)


if __name__ == "__main__":
    main()
