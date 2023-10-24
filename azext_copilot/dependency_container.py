from dependency_injector import containers, providers
from azext_copilot.infrastructure import AzureAuthenticationService, AzureOpenAIClient
from azext_copilot.infrastructure.services.azure_cli_command_execution_service import (
    AzureCliCommandExecution,
)
from azext_copilot.services import EnvironmentContextService
from azext_copilot.services import ConversationEngine


def setup_dependency_container(modules=None, packages=None):
    container = DependencyContainer()
    container.wire(modules=modules, packages=packages)
    environment_context_service = EnvironmentContextService()
    environment_context_service.load_environment()

    if not environment_context_service.environment_valid():
        raise Exception("Missing environment variables")

    container.config.azure_open_ai_key.from_value(
        environment_context_service.azure_open_ai_key
    )
    container.config.azure_open_ai_url.from_value(
        environment_context_service.azure_open_ai_url
    )
    container.config.azure_cognitive_search_key.from_value(
        environment_context_service.azure_cognitive_search_key
    )
    container.config.azure_cognitive_search_url.from_value(
        environment_context_service.azure_cognitive_search_url
    )
    container.config.azure_cognitive_search_index_name.from_value(
        environment_context_service.azure_cognitive_search_index_name
    )
    container.config.azure_open_ai_embedding_deployment_name.from_value(
        environment_context_service.azure_open_ai_embedding_deployment_name
    )
    container.config.azure_open_ai_gpt_deployment_name.from_value(
        environment_context_service.azure_open_ai_gpt_deployment_name
    )
    return container


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration()
    azure_authentication_service = providers.ThreadSafeSingleton(
        AzureAuthenticationService
    )
    azure_open_ai_client_service = providers.Factory(
        AzureOpenAIClient,
        api_key=config.azure_open_ai_key,
        api_base=config.azure_open_ai_url,
        search_endpoint=config.azure_cognitive_search_url,
        search_key=config.azure_cognitive_search_key,
        open_ai_text_embedding_deployment_name=config.azure_open_ai_embedding_deployment_name,
        open_ai_gpt_deployment_name=config.azure_open_ai_gpt_deployment_name,
    )
    conversation_engine = providers.Factory(
        ConversationEngine, open_ai_service=azure_open_ai_client_service
    )
    execution_service = providers.Factory(AzureCliCommandExecution)
