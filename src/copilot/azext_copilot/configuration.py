import os
import yaml
from pathlib import Path
from .constants import CONFIG_FILENAME


def create_configuration():
    # Define the name and path of the configuration file
    user_profile = os.path.expanduser("~")
    config_file = f"{user_profile}/.az-copilot/{CONFIG_FILENAME}"

    # Define the default configuration values
    default_config = {
        "AzureOpenAI": {
            "ApiKey": None,
            "Endpoint": None,
            "GptDeploymentName": None,
            "EmbeddingDeploymentName": None,
        },
        "AzureCognitiveSearch": {
            "ApiKey": None,
            "Endpoint": None,
        },
        "Copilot": {
            "AutoRun": False,
            "ShowCommand": True,
        },
    }

    # Create the directory if it doesn't exist
    path = Path(f"{user_profile}/.az-copilot")
    path.mkdir(parents=True, exist_ok=True)

    # Create the configuration file
    write_config_file(config_file, default_config)


def get_configuration():
    # Define the name and path of the configuration file
    user_profile = os.path.expanduser("~")
    config_file = f"{user_profile}/.az-copilot/{CONFIG_FILENAME}"

    # Check if the configuration file exists
    if os.path.exists(config_file):
        # If it exists, read the configuration values
        config = read_config_file(config_file)
        openai_api_key = config["AzureOpenAI"]["ApiKey"]
        openai_endpoint = config["AzureOpenAI"]["Endpoint"]
        openai_gpt_deployment = config["AzureOpenAI"]["GptDeploymentName"]
        openai_embedding_deployment = config["AzureOpenAI"][
            "EmbeddingDeploymentName"
        ]
        cognitive_search_api_key = config["AzureCognitiveSearch"]["ApiKey"]
        cognitive_search_endpoint = config["AzureCognitiveSearch"]["Endpoint"]
        autorun = config["Copilot"]["AutoRun"]
        show_command = config["Copilot"]["ShowCommand"]

        return (
            openai_api_key,
            openai_endpoint,
            openai_gpt_deployment,
            openai_embedding_deployment,
            cognitive_search_api_key,
            cognitive_search_endpoint,
            autorun,
            show_command,
        )
    else:
        # If it doesn't exist, create a new configuration file with default values
        create_configuration()

        # Display a message to the user
        print(
            f"Configuration file was not found so an empty one has been created at '{config_file}'. Run 'az copilot config set' to set the configuration values."
        )

        # Exit the application
        exit(0)


def update_configuration(
    openai_gpt_deployment,
    openai_api_key,
    openai_endpoint,
    openai_embedding_deployment,
    cognitive_search_api_key,
    cognitive_search_endpoint,
    autorun,
    show_command,
):
    # Define the name and path of the configuration file
    user_profile = os.path.expanduser("~")
    config_file = f"{user_profile}/.az-copilot/{CONFIG_FILENAME}"

    config = read_config_file(config_file)
    update_config_values(
        config,
        openai_gpt_deployment,
        openai_api_key,
        openai_endpoint,
        openai_embedding_deployment,
        cognitive_search_api_key,
        cognitive_search_endpoint,
        autorun,
        show_command,
    )
    write_config_file(config_file, config)


def read_config_file(config_file):
    with open(config_file, "r") as configfile:
        config = yaml.safe_load(configfile)
    return config


def write_config_file(config_file, config):
    with open(config_file, "w") as configfile:
        yaml.dump(config, configfile, default_flow_style=False)


def update_config_values(
    config,
    openai_gpt_deployment,
    openai_api_key,
    openai_endpoint,
    openai_embedding_deployment,
    cognitive_search_api_key,
    cognitive_search_endpoint,
    autorun,
    show_command,
):
    # Update the values in the config dictionary
    if openai_api_key is not None:
        config["AzureOpenAI"]["ApiKey"] = openai_api_key

    if openai_endpoint is not None:
        config["AzureOpenAI"]["Endpoint"] = openai_endpoint

    if openai_gpt_deployment is not None:
        config["AzureOpenAI"]["GptDeploymentName"] = openai_gpt_deployment

    if openai_embedding_deployment is not None:
        config["AzureOpenAI"]["EmbeddingDeploymentName"] = openai_embedding_deployment

    if cognitive_search_api_key is not None:
        config["AzureCognitiveSearch"]["ApiKey"] = cognitive_search_api_key

    if cognitive_search_endpoint is not None:
        config["AzureCognitiveSearch"]["Endpoint"] = cognitive_search_endpoint

    if autorun is not None:
        config["Copilot"]["AutoRun"] = (autorun == "True" or autorun == "true" or autorun is True)

    if show_command is not None:
        config["Copilot"]["ShowCommand"] = (show_command == "True" or show_command == "true" or show_command is True)

    return config
