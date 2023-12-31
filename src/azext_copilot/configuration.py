import os
import json
from pathlib import Path
from azext_copilot.constants import (
    API_KEY_CONFIG_KEY,
    AUTO_RUN_CONFIG_KEY,
    COGNITIVE_SEARCH_CONFIG_SECTION,
    COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY,
    CONFIG_FILENAME,
    CONFIG_PATH,
    COPILOT_CONFIG_SECTION,
    DEFAULT_CONFIG,
    EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY,
    ENABLE_LOGGING_CONFIG_KEY,
    ENDPOINT_CONFIG_KEY,
    OPENAI_CONFIG_SECTION,
    SEARCH_INDEX_NAME_CONFIG_KEY,
    SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY,
    SEARCH_RESULT_COUNT_CONFIG_KEY,
    SEARCH_VECTOR_SIZE_CONFIG_KEY,
    SHOW_COMMAND_CONFIG_KEY,
    USE_RAG_CONFIG_KEY,
)


# Show the config values
def show_config():
    config = read_config()
    openai_key = config[OPENAI_CONFIG_SECTION][API_KEY_CONFIG_KEY]
    cognitive_key = config[COGNITIVE_SEARCH_CONFIG_SECTION][API_KEY_CONFIG_KEY]

    # Mask the API key if present
    if openai_key is not None and openai_key != "":
        config[OPENAI_CONFIG_SECTION][API_KEY_CONFIG_KEY] = "********"

    # Mask the API key if present
    if cognitive_key is not None and cognitive_key != "":
        config[COGNITIVE_SEARCH_CONFIG_SECTION][API_KEY_CONFIG_KEY] = "********"

    # Return the config as JSON
    return json.dumps(config, indent=4)


# Read the config file
def read_config():
    # Get the path of the config file
    config_path = Path.home() / CONFIG_PATH / CONFIG_FILENAME
    # Check if the configuration file exists
    if os.path.exists(config_path):
        # Read the configuration file
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        # Return the config
        return config
    else:
        # Create the configuration file and return the default config
        return write_config(DEFAULT_CONFIG)


# Write the config file
def write_config(config):
    # Define the name and path of the configuration file
    config_path = Path.home() / CONFIG_PATH / CONFIG_FILENAME

    # Create the directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Create the configuration file
    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)

    # Return the config
    return config


# Update the config values
def update_config(
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
    # Read the config file
    config = read_config()

    # Update the values in the config object
    if openai_api_key is not None:
        config[OPENAI_CONFIG_SECTION][API_KEY_CONFIG_KEY] = openai_api_key

    if openai_endpoint is not None:
        config[OPENAI_CONFIG_SECTION][ENDPOINT_CONFIG_KEY] = openai_endpoint

    if completion_deployment_name is not None:
        config[OPENAI_CONFIG_SECTION][
            COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY
        ] = completion_deployment_name

    if embedding_deployment_name is not None:
        config[OPENAI_CONFIG_SECTION][
            EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY
        ] = embedding_deployment_name

    if search_api_key is not None:
        config[COGNITIVE_SEARCH_CONFIG_SECTION][API_KEY_CONFIG_KEY] = search_api_key

    if search_endpoint is not None:
        config[COGNITIVE_SEARCH_CONFIG_SECTION][ENDPOINT_CONFIG_KEY] = search_endpoint

    if search_index is not None:
        config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_INDEX_NAME_CONFIG_KEY
        ] = search_index

    if search_vector_size is not None:
        config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_VECTOR_SIZE_CONFIG_KEY
        ] = search_vector_size

    if search_result_count is not None:
        config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_RESULT_COUNT_CONFIG_KEY
        ] = search_result_count

    if search_relevance_threshold is not None:
        config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY
        ] = search_relevance_threshold

    if autorun is not None:
        config[COPILOT_CONFIG_SECTION][AUTO_RUN_CONFIG_KEY] = (
            autorun == "True" or autorun == "true" or autorun is True
        )

    if show_command is not None:
        config[COPILOT_CONFIG_SECTION][SHOW_COMMAND_CONFIG_KEY] = (
            show_command == "True" or show_command == "true" or show_command is True
        )

    if use_rag is not None:
        config[COPILOT_CONFIG_SECTION][USE_RAG_CONFIG_KEY] = (
            use_rag == "True" or use_rag == "true" or use_rag is True
        )

    if enable_logging is not None:
        config[COPILOT_CONFIG_SECTION][ENABLE_LOGGING_CONFIG_KEY] = (
            enable_logging == "True"
            or enable_logging == "true"
            or enable_logging is True
        )

    # Write the config file
    write_config(config)


def check_config(config):
    # Check if the OpenAI API key is set
    if (
        config[OPENAI_CONFIG_SECTION][API_KEY_CONFIG_KEY] is None
        or config[OPENAI_CONFIG_SECTION][API_KEY_CONFIG_KEY] == ""
    ):
        return "OpenAI API key"

    # Check if the OpenAI endpoint is set
    if (
        config[OPENAI_CONFIG_SECTION][ENDPOINT_CONFIG_KEY] is None
        or config[OPENAI_CONFIG_SECTION][ENDPOINT_CONFIG_KEY] == ""
    ):
        return "OpenAI Endpoint"

    # Check if the completion deployment name is set
    if (
        config[OPENAI_CONFIG_SECTION][COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY] is None
        or config[OPENAI_CONFIG_SECTION][COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY] == ""
    ):
        return "Completion Deployment Name"

    # Check if the auto run is set
    if config[COPILOT_CONFIG_SECTION][AUTO_RUN_CONFIG_KEY] is None:
        return "Auto Run"

    # Check if the show command is set
    if config[COPILOT_CONFIG_SECTION][SHOW_COMMAND_CONFIG_KEY] is None:
        return "Show Command"

    # Check if the enable logging is set
    if config[COPILOT_CONFIG_SECTION][ENABLE_LOGGING_CONFIG_KEY] is None:
        return "Enable Logging"

    # Check if the RAG is set
    if config[COPILOT_CONFIG_SECTION][USE_RAG_CONFIG_KEY] is None:
        return "Use RAG"
    else:
        # Check if RAG is enabled
        if config[COPILOT_CONFIG_SECTION][USE_RAG_CONFIG_KEY] is True:
            # Check if the embedding deployment name is set
            if (
                config[OPENAI_CONFIG_SECTION][EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY]
                is None
                or config[OPENAI_CONFIG_SECTION][EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY]
                == ""
            ):
                return "Embedding Deployment Name"

            # Check if the Cognitive Search API key is set
            if (
                config[COGNITIVE_SEARCH_CONFIG_SECTION][API_KEY_CONFIG_KEY] is None
                or config[COGNITIVE_SEARCH_CONFIG_SECTION][API_KEY_CONFIG_KEY] == ""
            ):
                return "Cognitive Search API Key"

            # Check if the Cognitive Search endpoint is set
            if (
                config[COGNITIVE_SEARCH_CONFIG_SECTION][ENDPOINT_CONFIG_KEY] is None
                or config[COGNITIVE_SEARCH_CONFIG_SECTION][ENDPOINT_CONFIG_KEY] == ""
            ):
                return "Cognitive Search Endpoint"

            # Check if the Cognitive Search index name is set
            if (
                config[COGNITIVE_SEARCH_CONFIG_SECTION][SEARCH_INDEX_NAME_CONFIG_KEY]
                is None
                or config[COGNITIVE_SEARCH_CONFIG_SECTION][SEARCH_INDEX_NAME_CONFIG_KEY]
                == ""
            ):
                return "Cognitive Search Index Name"

            # Check if the Cognitive Search vector size is set
            if (
                config[COGNITIVE_SEARCH_CONFIG_SECTION][SEARCH_VECTOR_SIZE_CONFIG_KEY]
                is None
                or config[COGNITIVE_SEARCH_CONFIG_SECTION][
                    SEARCH_VECTOR_SIZE_CONFIG_KEY
                ]
                == ""
            ):
                return "Cognitive Search Vector Size"

            # Check if the Cognitive Search result count is set
            if (
                config[COGNITIVE_SEARCH_CONFIG_SECTION][SEARCH_RESULT_COUNT_CONFIG_KEY]
                is None
                or config[COGNITIVE_SEARCH_CONFIG_SECTION][
                    SEARCH_RESULT_COUNT_CONFIG_KEY
                ]
                == ""
            ):
                return "Cognitive Search Result Count"

            # Check if the Cognitive Search relevance threshold is set
            if (
                config[COGNITIVE_SEARCH_CONFIG_SECTION][
                    SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY
                ]
                is None
                or config[COGNITIVE_SEARCH_CONFIG_SECTION][
                    SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY
                ]
                == ""
            ):
                return "Cognitive Search Relevance Threshold"

    return ""
