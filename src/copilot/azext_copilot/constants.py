CONFIG_PATH = ".az-copilot"
CONFIG_FILENAME = "config.json"
COMMANDS_KEY = "command"
PROBLEM_KEY = "problem"

DEFAULT_CONFIG = {
    "AzureOpenAI": {
        "ApiKey": None,
        "Endpoint": None,
        "GptDeploymentName": None,
        "EmbeddingDeploymentName": None,
    },
    "AzureCognitiveSearch": {
        "ApiKey": None,
        "Endpoint": None,
    },
    "Copilot": {
        "AutoRun": False,
        "ShowCommand": True,
    },
}
