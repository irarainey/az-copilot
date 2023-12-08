from azext_copilot.configuration import show_config, update_config
from azext_copilot.copilot import copilot
from azext_copilot.version import get_version


# This is the entry point for the AZ CLI extension to call the Copilot
def copilot_cmd(prompt, autorun=False):
    copilot(prompt, autorun)


# This is the entry point for the AZ CLI extension to set the config
def set_config_cmd(
    openai_api_key,
    openai_endpoint,
    completion_deployment_name,
    embedding_deployment_name,
    search_api_key,
    search_endpoint,
    search_index,
    search_vector_size,
    search_result_count,
    search_relevance_threshold,
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
        search_index,
        search_vector_size,
        search_result_count,
        search_relevance_threshold,
        autorun,
        show_command,
        use_rag,
        enable_logging,
    )


# This is the entry point for the AZ CLI extension to show the config
def show_config_cmd():
    print(show_config())


def get_version_cmd():
    print(get_version())
