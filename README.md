# Azure CLI Copilot

This project is an experimental extension for the Azure CLI that allows you to use plain English commands to run Azure CLI commands. It uses Azure OpenAI to determine the most likely Azure CLI command to run based on the plain English command you provide.

The Azure CLI documentation is used to create embeddings for each Azure CLI command. These embeddings are then stored in Azure Cognitive Search and used for [Retrieval Augmented Generation (RAG)](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) to determine the most up to date syntax for the command you wish to execute.

This project is built using Microsoft Semantic Kernel SDK, which allows for easy integration with a range of services. For more information on the open source project, see the [GitHub repository](https://github.com/microsoft/semantic-kernel)

## Usage

To use the Copilot simply use the command `az copilot --prompt "your command prompt here"`. This will invoke the call to determine the most likely Azure CLI command to run based on the prompt you provide.

The Azure CLI command will then be presented to you and you can choose to run it or not.

![List Resource Groups](https://raw.githubusercontent.com/irarainey/az-copilot/main/images/list_resource_groups.png)

If the Copilot deteremines that more information is required, such as missing parameters, it will prompt you for the additional information.

![Create Resource Groups](https://raw.githubusercontent.com/irarainey/az-copilot/main/images/create_without_params.png)

## Prerequisites

To use the Copilot extension you will need the following:
- An Azure subscription
- The Azure CLI installed
- Python 3.9 or later installed

## Deployment Steps

To get up and running with the Copilot extension, you will need to complete several steps. In order these are:

- Deploy required Azure OpenAI and Azure Cognitive Services resources
- Install the Azure CLI Copilot extension
- Set the configuration ouput by the infrastructure deployment
- Run the extraction script to create up to date embeddings from the Azure CLI documentation

### Deploy Required Azure Resources


### Install the Azure CLI Copilot Extension

The Copilot extension is available as a Python wheel file and can be installed using the `az extension add` command directly from the [releases page](https://github.com/irarainey/az-copilot/releases)

To install the latest version of the extension, run the following command:

```bash
az extension add --source https://github.com/irarainey/az-copilot/releases/download/latest/copilot.whl --yes
```

You can check the version of the extension you have installed by running the following command:

```bash
az extension list --query "[?name == 'copilot'].version" -o tsv
```

To unstall the extension, simply run the remove command:

```bash
az extension remove --name copilot
```

### Set Configuration Options

The Copilot extension requires several configuration options to be set. All configuration options are stored in a local configuration file stored in the root of your user profile directory, in a directory named `.az-copilot`. The configuration file is named `config.json`.

If the configuration file does not exist, it will be created when you run the `az copilot config set` command.

You can edit this file directly, or use the `az copilot config set` command to set the configuration options. All options are optional. You can set a single, or all options at once.

For information on the options available, run the command `az copilot config set --help`

This will display the following table of options:

```bash
Command
    az copilot config set

Arguments
    --autorun -a                     : Boolean value to autorun the command when ready.
    --completion-name -cn            : The Azure OpenAI completion model deployment name.
    --embedding-name -en             : The Azure OpenAI embedding model deployment name.
    --enable-logging -l              : Boolean value to enable or disable logging.
    --openai-api-key -ok             : The Azure OpenAI API key.
    --openai-endpoint -oe            : The Azure OpenAI endpoint.
    --search-api-key -sk             : The Azure Cognitive Search API key.
    --search-endpoint -se            : The Azure Cognitive Search endpoint.
    --search-index-name -si          : The Azure Cognitive Search index name.
    --search-relevance-threshold -st : The Azure Cognitive Search relevance threshold.
    --search-result-count -sc        : The Azure Cognitive Search result count.
    --search-vector-size -sv         : The Azure Cognitive Search vector size.
    --show-command -s                : Boolean value to show or hide commands.
    --use-rag -r                     : Boolean value to enable or disable RAG.
```

Additionally you can use the command `az copilot config show` to display the current configuration options.

![Configuration Options](https://raw.githubusercontent.com/irarainey/az-copilot/main/images/show_configuration.png)

For security API keys are not displayed in the output.

### Run the Extraction Script
