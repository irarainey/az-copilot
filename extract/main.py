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
from azext_copilot.configuration import get_configuration
from azext_copilot.constants import (
    CLI_DOCUMENTATION_URL,
    EXTRACTON_DOCS_FOLDER,
    EXTRACTON_YML_FOLDER,
    RAW_CLI_DOCUMENTATION_URL,
    SEARCH_INDEX_NAME,
    SEARCH_VECTOR_SIZE,
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


def extract_documentation_to_files():
    # Get the root page of the documentation
    response = requests.get(CLI_DOCUMENTATION_URL)
    content = response.content
    soup = BeautifulSoup(content, features="html.parser")

    # Extract the contents of the page
    soup_dict = soup_to_dict(soup)
    contents = soup_dict["contents"][0]

    # Convert it to JSON and extract the items collection
    json_contents = json.loads(contents)
    items = json_contents["payload"]["tree"]["items"]

    for item in items:
        if item["contentType"] == "file" and item["path"].endswith("/TOC.yml") is False:
            file = f'{RAW_CLI_DOCUMENTATION_URL}/{item["path"]}'
            response = requests.get(file)
            content = response.content.decode("utf-8")
            print(
                f'Found \'{file}\''
            )
            parts = item["path"].split("/")
            y = open(f"{EXTRACTON_YML_FOLDER}/{parts[-1]}", "w")
            y.write(content)
            y.close()

            parsed_content = yaml.safe_load(content)

            if "directCommands" in parsed_content:  
                for command in parsed_content["directCommands"]:
                    print(
                        f'=> Parsing \'{command["name"]}\''
                    )
                    copy = f'Command: {command["name"]}'
                    copy += f'\nDescription: {command["summary"]} {command["description"] + "" if "description" in command else ""}'
                    copy += f'\nSyntax:\n\t{command["syntax"]}'

                    if "examples" in command:
                        copy += "\nExamples:"
                        for example in command["examples"]:
                            cleaned_syntax = example["syntax"].replace("\n", "\n\t\t")
                            copy += f'\n\t{example["summary"]}:\n\t\t{cleaned_syntax}'

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
                                copy += (
                                    f'\n\t\tDefault Value: {opt_param["defaultValue"]}'
                                )

                            if "parameterValueGroup" in opt_param:
                                copy += f'\n\t\tAccepted Values: {opt_param["parameterValueGroup"]}'

                    f = open(f'{EXTRACTON_DOCS_FOLDER}/{command["uid"]}.txt', "w")
                    f.write(copy)
                    f.close()


async def index():
    docs_path_exists = os.path.exists(EXTRACTON_DOCS_FOLDER)
    yml_path_exists = os.path.exists(EXTRACTON_YML_FOLDER)

    if not docs_path_exists:
        os.makedirs(EXTRACTON_DOCS_FOLDER)

    if not yml_path_exists:
        os.makedirs(EXTRACTON_YML_FOLDER)

    extract_documentation_to_files()

    (
        openai_api_key,
        openai_endpoint,
        _,
        embedding_deployment_name,
        search_api_key,
        search_endpoint,
        _,
        _,
    ) = get_configuration()

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
            SEARCH_VECTOR_SIZE, search_endpoint, search_api_key, SEARCH_INDEX_NAME
        )
    )

    now = datetime.date.today()
    counter = 0

    docs_path = Path(EXTRACTON_DOCS_FOLDER)
    for file_path in docs_path.iterdir():
        if file_path.is_file():
            counter += 1
            with file_path.open('r') as file:
                description = ''.join(next(file) for _ in range(2)).replace('\n', '')
                file.seek(0)
                content = file.read()

            print(
                f'=> Indexing \'{file_path.name}\'')

            await kernel.memory.save_information_async(
                SEARCH_INDEX_NAME,
                id=str(counter).zfill(4),
                text=content,
                description=description,
                additional_metadata=now,
            )

    print("\nIndexing complete\n")


if __name__ == "__main__":
    asyncio.run(index())
