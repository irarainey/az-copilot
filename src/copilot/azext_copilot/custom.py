from .configuration import update_configuration
from .copilot import copilot


# This is the entry point for the AZ CLI extension to call the Copilot
def call_openai(prompt):
    copilot(prompt)


# This is the entry point for the AZ CLI extension to set the configuration
def set_configuration(
    api_key,
    endpoint,
    completion_deployment_name,
    embedding_deployment_name,
    autorun,
    show_command,
):
    update_configuration(
        api_key,
        endpoint,
        completion_deployment_name,
        embedding_deployment_name,
        autorun,
        show_command,
    )


# This is the entry point for the AZ CLI extension to create the embedding
def create_embedding():
    print("Create embedding")


# This is the entry point for the AZ CLI extension to update the embedding
def update_embedding():
    print("Update embedding")
