from azext_copilot.configuration import update_configuration
from azext_copilot.copilot import copilot


# This is the entry point for the AZ CLI extension to call the Copilot
def call_openai(prompt):
    copilot(prompt)


# This is the entry point for the AZ CLI extension to set the configuration
def set_configuration(
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
    update_configuration(
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
