# The JSON return keys for the OpenAI response
COMMAND_KEY = "COMMAND"
PROBLEM_KEY = "PROBLEM"
EXPLANATION_KEY = "EXPLANATION"

# The configuration file path
CONFIG_PATH = ".az-copilot"

# The configuration file name
CONFIG_FILENAME = "config.json"

# The default configuration values
DEFAULT_CONFIG = {
    "AzureOpenAI": {
        "ApiKey": None,
        "Endpoint": None,
        "CompletionDeploymentName": None,
        "EmbeddingDeploymentName": None,
    },
    "Copilot": {
        "AutoRun": False,
        "ShowCommand": True,
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
