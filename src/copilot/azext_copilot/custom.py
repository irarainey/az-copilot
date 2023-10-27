from .configuration import update_configuration
from .copilot import copilot


# This is the entry point for the AZ CLI extension to call the Copilot
def call_openai(prompt):
    copilot(prompt)


# This is the entry point for the AZ CLI extension to set the configuration
def set_configuration(
    openai_gpt_deployment,
    openai_api_key,
    openai_endpoint,
    openai_embedding_deployment,
    autorun,
    show_command,
):
    update_configuration(
        openai_gpt_deployment,
        openai_api_key,
        openai_endpoint,
        openai_embedding_deployment,
        autorun,
        show_command,
    )
