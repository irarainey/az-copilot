from .configuration import update_configuration
from .copilot import copilot


def call_openai(prompt):
    copilot(prompt)


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
