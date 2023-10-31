import os
import json
from pathlib import Path
from azext_copilot.constants import CONFIG_FILENAME, CONFIG_PATH, DEFAULT_CONFIG


# Create a new configuration file
def create_configuration():
    # Define the name and path of the configuration file
    config_file = Path.home() / CONFIG_PATH / CONFIG_FILENAME

    # Create the directory if it doesn't exist
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Create the configuration file
    write_config_file(config_file, DEFAULT_CONFIG)


# Get the configuration values
def get_configuration():
    # Define the name and path of the configuration file
    config_file = Path.home() / CONFIG_PATH / CONFIG_FILENAME

    # Check if the configuration file exists
    if os.path.exists(config_file):
        # If it exists, read the configuration values
        config = read_config_file(config_file)
        openai_api_key = config["AzureOpenAI"]["ApiKey"]
        openai_endpoint = config["AzureOpenAI"]["Endpoint"]
        completion_deployment_name = config["AzureOpenAI"]["CompletionDeploymentName"]
        embedding_deployment_name = config["AzureOpenAI"]["EmbeddingDeploymentName"]
        search_api_key = config["AzureCognitiveSearch"]["ApiKey"]
        search_endpoint = config["AzureCognitiveSearch"]["Endpoint"]
        autorun = config["Copilot"]["AutoRun"]
        show_command = config["Copilot"]["ShowCommand"]
        use_rag = config["Copilot"]["UseRAG"]

        return (
            openai_api_key,
            openai_endpoint,
            completion_deployment_name,
            embedding_deployment_name,
            search_api_key,
            search_endpoint,
            autorun,
            show_command,
            use_rag,
        )
    else:
        # If it doesn't exist, create a new configuration file with default values
        create_configuration()

        # Display a message to the user
        print(
            f"Configuration file was not found so an empty one has been created at '{config_file}'. Run 'az copilot config set' to set the configuration values."  # noqa: E501
        )

        # Exit the application
        exit(0)


# Update the configuration values
def update_configuration(
    openai_api_key,
    openai_endpoint,
    completion_deployment_name,
    embedding_deployment_name,
    search_api_key,
    search_endpoint,
    autorun,
    show_command,
    use_rag,
):
    # Define the name and path of the configuration file
    config_file = Path.home() / CONFIG_PATH / CONFIG_FILENAME

    config = read_config_file(config_file)
    update_config_values(
        config,
        openai_api_key,
        openai_endpoint,
        completion_deployment_name,
        embedding_deployment_name,
        search_api_key,
        search_endpoint,
        autorun,
        show_command,
        use_rag,
    )
    write_config_file(config_file, config)


# Read the configuration file
def read_config_file(config_file):
    with open(config_file, "r") as configfile:
        config = json.load(configfile)
    return config


# Write the configuration file
def write_config_file(config_file, config):
    with open(config_file, "w") as configfile:
        json.dump(config, configfile, indent=4)


# Update the configuration values
def update_config_values(
    config,
    openai_api_key,
    openai_endpoint,
    completion_deployment_name,
    embedding_deployment_name,
    search_api_key,
    search_endpoint,
    autorun,
    show_command,
    use_rag,
):
    # Update the values in the config object
    if openai_api_key is not None:
        config["AzureOpenAI"]["ApiKey"] = openai_api_key

    if openai_endpoint is not None:
        config["AzureOpenAI"]["Endpoint"] = openai_endpoint

    if completion_deployment_name is not None:
        config["AzureOpenAI"]["CompletionDeploymentName"] = completion_deployment_name

    if embedding_deployment_name is not None:
        config["AzureOpenAI"]["EmbeddingDeploymentName"] = embedding_deployment_name

    if search_api_key is not None:
        config["AzureCognitiveSearch"]["ApiKey"] = search_api_key

    if search_endpoint is not None:
        config["AzureCognitiveSearch"]["Endpoint"] = search_endpoint

    if autorun is not None:
        config["Copilot"]["AutoRun"] = (
            autorun == "True" or autorun == "true" or autorun is True
        )

    if show_command is not None:
        config["Copilot"]["ShowCommand"] = (
            show_command == "True" or show_command == "true" or show_command is True
        )

    if use_rag is not None:
        config["Copilot"]["UseRAG"] = (
            use_rag == "True" or use_rag == "true" or use_rag is True
        )

    return config
