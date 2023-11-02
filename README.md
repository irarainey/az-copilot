# Azure CLI Copilot

This project is an experimental extension for the Azure CLI that allows you to use plain English commands to run Azure CLI commands. It uses Azure OpenAI to determine the most likely Azure CLI command to run based on the plain English command you provide.

The Azure CLI documentation is used to create embeddings for each Azure CLI command. These embeddings are then stored in Azure Cognitive Search and used to determine the most up to date syntax for the command you wish to execute.

![List Resource Groups](https://raw.githubusercontent.com/irarainey/az-copilot/main/resources/images/list_resource_group.png)

## Deployment Steps

To get up and running with the Copilot extension, you will need to complete several steps. In order these are:

- Deploy required Azure OpenAI and Azure Cognitive Services resources
- Install the Azure CLI Copilot extension
- Set the configuration ouput by the infrastructure deployment
- Run the extraction script to create up to date embeddings from the Azure CLI documentation

To install 

```bash
az extension add --source https://github.com/irarainey/az-copilot/releases/download/<VERSION>/copilot-<VERSION>-py3-none-any.whl --yes
```

For example:

```bash
az extension add --source https://github.com/irarainey/az-copilot/releases/download/0.1.14/copilot-0.1.14-py3-none-any.whl --yes
```