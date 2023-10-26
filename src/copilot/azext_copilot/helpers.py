import os
import yaml
import subprocess
from pathlib import Path
from azext_copilot.constants import CONFIG_FILENAME


def execute(command):
    try:
        completed_process = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return completed_process.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr


def configuration():
    # Define the name and path of the configuration file
    user_profile = os.path.expanduser("~")
    config_file = f"{user_profile}/.az-copilot/{CONFIG_FILENAME}"

    # Check if the configuration file exists
    if os.path.exists(config_file):
        # If it exists, read the configuration values
        with open(config_file, "r") as configfile:
            config = yaml.safe_load(configfile)
            openai_api_key = config["AzureOpenAI"]["ApiKey"]
            openai_endpoint = config["AzureOpenAI"]["Endpoint"]
            openai_gpt_deployment = config["AzureOpenAI"]["GptDeploymentName"]
            openai_embedding_deployment = config["AzureOpenAI"][
                "EmbeddingDeploymentName"
            ]
            cognitive_search_api_key = config["AzureCognitiveSearch"]["ApiKey"]
            cognitive_search_endpoint = config["AzureCognitiveSearch"]["Endpoint"]
            autorun = config["Copilot"]["AutoRun"]

            return (
                openai_api_key,
                openai_endpoint,
                openai_gpt_deployment,
                openai_embedding_deployment,
                cognitive_search_api_key,
                cognitive_search_endpoint,
                autorun,
            )
    else:
        # If it doesn't exist, create a new configuration file with default values
        default_config = {
            "AzureOpenAI": {
                "ApiKey": "your_api_key_here",
                "Endpoint": "your_endpoint_here",
                "GptDeploymentName": "your_gpt_deployment_name_here",
                "EmbeddingDeploymentName": "your_embedding_deployment_name_here",
            },
            "AzureCognitiveSearch": {
                "ApiKey": "your_api_key_here",
                "Endpoint": "your_endpoint_here",
            },
            "Copilot": {"AutoRun": False},
        }

        path = Path(f"{user_profile}/.az-copilot")
        path.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as configfile:
            yaml.dump(default_config, configfile, default_flow_style=False)

        print(
            f"Configuration file was not found so one has been created at '{config_file}' with default values."
        )

        exit(0)
