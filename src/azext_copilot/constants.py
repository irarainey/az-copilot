# The JSON return keys for the OpenAI response
COMMAND_KEY = "COMMAND"
PROBLEM_KEY = "PROBLEM"
EXPLANATION_KEY = "EXPLANATION"

# The scope for the Azure CLI token
AZURE_TOKEN_SCOPE = "https://management.azure.com/.default"

# The configuration file path
CONFIG_PATH = ".az-copilot"

# The configuration file name
CONFIG_FILENAME = "config.json"

# The Azure CLI documentation URL on GitHub
CLI_DOCUMENTATION_URL = "https://github.com/MicrosoftDocs/azure-docs-cli/tree/main/latest/docs-ref-autogen"  # noqa: E501

# The raw Azure CLI documentation URL on GitHub
RAW_CLI_DOCUMENTATION_URL = (
    "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs-cli/main"  # noqa: E501
)

# The directory where the extracted documentation is stored
EXTRACTON_DOCS_FOLDER = "extract/docs"

# The directory where the extracted YAML files are stored
EXTRACTON_YML_FOLDER = "extract/yml"

# Define the configuration keys
OPENAI_CONFIG_SECTION = "AzureOpenAI"
COGNITIVE_SEARCH_CONFIG_SECTION = "AzureCognitiveSearch"
COPILOT_CONFIG_SECTION = "Copilot"
API_KEY_CONFIG_KEY = "ApiKey"
ENDPOINT_CONFIG_KEY = "Endpoint"
COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY = "CompletionDeploymentName"
EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY = "EmbeddingDeploymentName"
SEARCH_INDEX_NAME_CONFIG_KEY = "SearchIndexName"
SEARCH_VECTOR_SIZE_CONFIG_KEY = "SearchVectorSize"
SEARCH_RESULT_COUNT_CONFIG_KEY = "SearchResultCount"
SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY = "SearchRelevanceThreshold"
AUTO_RUN_CONFIG_KEY = "AutoRun"
SHOW_COMMAND_CONFIG_KEY = "ShowCommand"
USE_RAG_CONFIG_KEY = "UseRAG"
ENABLE_LOGGING_CONFIG_KEY = "EnableLogging"

# The default configuration values
DEFAULT_CONFIG = {
    f"{OPENAI_CONFIG_SECTION}": {
        f"{API_KEY_CONFIG_KEY}": None,
        f"{ENDPOINT_CONFIG_KEY}": None,
        f"{COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY}": None,
        f"{EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY}": None,
    },
    f"{COGNITIVE_SEARCH_CONFIG_SECTION}": {
        f"{API_KEY_CONFIG_KEY}": None,
        f"{ENDPOINT_CONFIG_KEY}": None,
        f"{SEARCH_INDEX_NAME_CONFIG_KEY}": "az-cli-docs",
        f"{SEARCH_VECTOR_SIZE_CONFIG_KEY}": 1536,
        f"{SEARCH_RESULT_COUNT_CONFIG_KEY}": 3,
        f"{SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY}": 0.8,
    },
    f"{COPILOT_CONFIG_SECTION}": {
        f"{AUTO_RUN_CONFIG_KEY}": False,
        f"{SHOW_COMMAND_CONFIG_KEY}": True,
        f"{USE_RAG_CONFIG_KEY}": False,
        f"{ENABLE_LOGGING_CONFIG_KEY}": False,
    },
}

# This is the system message that is sent to the OpenAI API
SYSTEM_MESSAGE = f"""
            You are an assistant that manages and creates Microsoft Azure resources.
            Your task is to create Azure CLI commands.
            You should respond in JSON format with three keys: {COMMAND_KEY}, {PROBLEM_KEY} and {EXPLANATION_KEY}.
            You should ensure all JSON property names should be enclosed with double quotes
            You should not auto-populate command arguments.
            If you miss information such as parameters that are needed for the command, you should use the {PROBLEM_KEY} key.
            If no information is missing the {PROBLEM_KEY} value should be empty.
            In the {EXPLANATION_KEY} key you should provide a short description what the command does.
            You should only use the {COMMAND_KEY} key if you have all the information and can form a complete and valid Azure CLI command.
            The results should be in JSON format in the structure of:
            'json-start-bracket' "{COMMAND_KEY}": "the Azure CLI commands", "{PROBLEM_KEY}": "asking the user for input", "{EXPLANATION_KEY}": "explaining what the command does"  'json-end-bracket'.
            """  # noqa: E501
