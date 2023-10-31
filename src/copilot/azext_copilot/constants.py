# The JSON return keys for the OpenAI response
COMMAND_KEY = "COMMAND"
PROBLEM_KEY = "PROBLEM"
EXPLANATION_KEY = "EXPLANATION"

# The configuration file path
CONFIG_PATH = ".az-copilot"

# The configuration file name
CONFIG_FILENAME = "config.json"

# The Coginitive Search index name
SEARCH_INDEX_NAME = "az-cli-docs"

# The Cognitive Search vector size
SEARCH_VECTOR_SIZE = 1536

# The Cognitive Search result count
SEARCH_RESULT_COUNT = 5

# The Cognitive Search relevance threshold
SEARCH_RELEVANCE_THRESHOLD = 0.8

# The Azure CLI documentation URL on GitHub
CLI_DOCUMENTATION_URL = "https://github.com/MicrosoftDocs/azure-docs-cli/tree/main/latest/docs-ref-autogen"  # noqa: E501

# The raw Azure CLI documentation URL on GitHub
RAW_CLI_DOCUMENTATION_URL = "https://raw.githubusercontent.com/MicrosoftDocs/azure-docs-cli/main"  # noqa: E501

# The directory where the extracted documentation is stored
EXTRACTON_DOCS_FOLDER = "extract/docs"

# The directory where the extracted YAML files are stored
EXTRACTON_YML_FOLDER = "extract/yml"

# The default configuration values
DEFAULT_CONFIG = {
    "AzureOpenAI": {
        "ApiKey": None,
        "Endpoint": None,
        "CompletionDeploymentName": None,
        "EmbeddingDeploymentName": None,
    },
    "AzureCognitiveSearch": {
        "ApiKey": None,
        "Endpoint": None,
    },
    "Copilot": {
        "AutoRun": False,
        "ShowCommand": True,
        "UseRAG": False,
        "EnableLogging": False,
    },
}

# This is the system message that is sent to the OpenAI API
SYSTEM_MESSAGE = """
            You are an assistant that manages and creates Microsoft Azure resources.
            Your task is to create Azure CLI commands.
            You should respond in JSON format with three keys: COMMAND, PROBLEM and EXPLANATION.
            You should ensure all JSON property names should be enclosed with double quotes
            You should not auto-populate command arguments.
            If you miss information such as parameters that are needed for the command, you should use the PROBLEM key.
            If no information is missing the PROBLEM value should be empty.
            In the EXPLANATION key you should provide a short description what the command does.
            You should only use the COMMAND key if you have all the information and can form a complete and valid Azure CLI command.
            The results should be in JSON format in the structure of:
            'json-start-bracket' "COMMAND": "the Azure CLI commands", "PROBLEM": "asking the user for input", "EXPLANATION": "explaining what the command does"  'json-end-bracket'.
            """  # noqa: E501
