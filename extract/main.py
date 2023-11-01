import os
import yaml
import json
import asyncio
import datetime
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextEmbedding,
)
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)
from azext_copilot.configuration import check_config, read_config
from azext_copilot.constants import (
    API_KEY_CONFIG_KEY,
    CLI_DOCUMENTATION_URL,
    COGNITIVE_SEARCH_CONFIG_SECTION,
    EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY,
    ENDPOINT_CONFIG_KEY,
    EXTRACTON_DOCS_FOLDER,
    OPENAI_CONFIG_SECTION,
    RAW_CLI_DOCUMENTATION_URL,
    SEARCH_INDEX_NAME_CONFIG_KEY,
    SEARCH_VECTOR_SIZE_CONFIG_KEY,
)


def soup_to_dict(element):
    if element.name:
        result = {"tag": element.name}
        if element.contents:
            result["contents"] = [soup_to_dict(e) for e in element.contents]
        if element.attrs:
            result["attributes"] = dict(element.attrs)
        return result
    else:
        return element.string


def extract_documentation_to_files(url):
    # Get the root page of the documentation
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, features="html.parser")

    # Extract the contents of the page
    soup_dict = soup_to_dict(soup)
    contents = soup_dict["contents"][0]

    # Convert it to JSON and extract the items collection
    json_contents = json.loads(contents)
    items = json_contents["payload"]["tree"]["items"]

    for item in items:
        if item["contentType"] == "directory":
            directory = f'{CLI_DOCUMENTATION_URL}/{item["path"].replace("latest/docs-ref-autogen", "")}'  # noqa: E501
            extract_documentation_to_files(directory)
        elif (
            item["contentType"] == "file" and item["path"].endswith("/TOC.yml") is False
        ):
            file = f'{RAW_CLI_DOCUMENTATION_URL}/{item["path"]}'
            response = requests.get(file)
            content = response.content.decode("utf-8")
            print(f"Found '{file}'")

            try:
                parsed_content = yaml.safe_load(content)
                if "directCommands" in parsed_content:
                    for command in parsed_content["directCommands"]:
                        print(f'=> Parsing \'{command["uid"]}\'')
                        copy = f'Command: {command["name"]}'
                        copy += f'\nDescription: {command["summary"] + "" if "summary" in command else ""} {command["description"] + "" if "description" in command else ""}'  # noqa: E501
                        copy += f'\nType: {command["sourceType"]}'

                        if "extensionSuffix" in command:
                            copy += f'\nType: {command["extensionSuffix"]}'

                        copy += f'\nSyntax:\n\t{command["syntax"] + "" if "syntax" in command else ""}'  # noqa: E501

                        if "examples" in command:
                            copy += "\nExamples:"
                            for example in command["examples"]:
                                cleaned_syntax = example["syntax"].replace(
                                    "\n", "\n\t\t"
                                )
                                copy += (
                                    f'\n\t{example["summary"] + "" if "summary" in example else ""}:\n\t\t{cleaned_syntax}'  # noqa: E501
                                )

                        if "requiredParameters" in command:
                            copy += "\nRequired Parameters:"
                            for req_param in command["requiredParameters"]:
                                copy += f'\n\t{req_param["name"]}'
                                copy += f'\n\t\t{req_param["summary"]}'

                        if "optionalParameters" in command:
                            copy += "\nOptional Parameters:"
                            for opt_param in command["optionalParameters"]:
                                copy += f'\n\t{opt_param["name"]}'

                                if "summary" in opt_param:
                                    copy += f'\n\t\t{opt_param["summary"]}'

                                if "defaultValue" in opt_param:
                                    copy += f'\n\t\tDefault Value: {opt_param["defaultValue"]}'  # noqa: E501

                                if "parameterValueGroup" in opt_param:
                                    copy += f'\n\t\tAccepted Values: {opt_param["parameterValueGroup"]}'  # noqa: E501

                        filename = (
                            command["uid"]
                            .replace("(", "_")
                            .replace(")", "_")
                            .replace("-", "_")
                        )
                        f = open(f"{EXTRACTON_DOCS_FOLDER}/{filename}.txt", "w")
                        f.write(copy)
                        f.close()

            except yaml.YAMLError as exc:
                print(f"Error parsing '{file}': {exc}")
                continue


async def index():
    docs_path_exists = os.path.exists(EXTRACTON_DOCS_FOLDER)

    if not docs_path_exists:
        os.makedirs(EXTRACTON_DOCS_FOLDER)

    extract_documentation_to_files(CLI_DOCUMENTATION_URL)

    # Get configuration values
    config = read_config()

    # Determine if configuration has been set
    check_state = check_config(config)
    if check_state != "":
        print(
            f"Configuration was found with empty values. [{check_state}]."
            "\nUse 'az copilot config set' to set the config values. "
            "Run 'az copilot config set --help' to see options "
            "or 'az copilot config show' to see current values."
        )
        return

    # Set variables from config
    openai_api_key = config[OPENAI_CONFIG_SECTION][API_KEY_CONFIG_KEY]
    openai_endpoint = config[OPENAI_CONFIG_SECTION][ENDPOINT_CONFIG_KEY]
    embedding_deployment_name = config[OPENAI_CONFIG_SECTION][
        EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY
    ]
    search_api_key = config[COGNITIVE_SEARCH_CONFIG_SECTION][API_KEY_CONFIG_KEY]
    search_endpoint = config[COGNITIVE_SEARCH_CONFIG_SECTION][ENDPOINT_CONFIG_KEY]
    search_index = config[COGNITIVE_SEARCH_CONFIG_SECTION][SEARCH_INDEX_NAME_CONFIG_KEY]
    search_vector_size = config[COGNITIVE_SEARCH_CONFIG_SECTION][
        SEARCH_VECTOR_SIZE_CONFIG_KEY
    ]

    kernel = Kernel()

    kernel.add_text_embedding_generation_service(
        "text-embedding-ada-002",
        AzureTextEmbedding(
            embedding_deployment_name,
            openai_endpoint,
            openai_api_key,
        ),
    )

    kernel.register_memory_store(
        memory_store=AzureCognitiveSearchMemoryStore(
            search_vector_size, search_endpoint, search_api_key, search_index
        )
    )

    now = datetime.date.today()
    counter = 0

    docs_path = Path(EXTRACTON_DOCS_FOLDER)
    for file_path in docs_path.iterdir():
        if file_path.is_file():
            counter += 1
            with file_path.open("r") as file:
                line1 = file.readline().strip()
                line2 = file.readline().strip().replace("Description: ", "")
                description = f"{line2} (Command: {line1})"
                file.seek(0)
                content = file.read()

            print(f"=> Indexing '{file_path.name}'")

            await kernel.memory.save_information_async(
                search_index,
                id=str(counter).zfill(6),
                text=content,
                description=description,
                additional_metadata=now,
            )

    print("\nIndexing complete\n")


if __name__ == "__main__":
    asyncio.run(index())
