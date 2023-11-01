import json
from azext_copilot.configuration import read_config, update_config
from azext_copilot.copilot import copilot


# This is the entry point for the AZ CLI extension to call the Copilot
def call_copilot(prompt):
    copilot(prompt)


# This is the entry point for the AZ CLI extension to set the config
def set_config(
    openai_api_key,
    openai_endpoint,
    completion_deployment_name,
    embedding_deployment_name,
    search_api_key,
    search_endpoint,
    autorun,
    show_command,
    use_rag,
    enable_logging,
):
    update_config(
        openai_api_key,
        openai_endpoint,
        completion_deployment_name,
        embedding_deployment_name,
        search_api_key,
        search_endpoint,
        autorun,
        show_command,
        use_rag,
        enable_logging,
    )


# This is the entry point for the AZ CLI extension to show the config
def show_config():
    print(json.dumps(read_config(), indent=4))
