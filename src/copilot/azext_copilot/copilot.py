import os
import yaml
import click
import asyncio
from functools import wraps
from azext_copilot.conversation_engine import ConversationEngine
from azext_copilot.services.authentication import AuthenticationService
from azext_copilot.services.openai import OpenAIService
from azext_copilot._helpers import execute


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument("prompt", nargs=-1, required=True)
@coro
async def copilot(prompt):
    (
        openai_api_key,
        openai_endpoint,
        openai_gpt_deployment,
        openai_embedding_deployment,
        cognitive_search_api_key,
        cognitive_search_endpoint,
    ) = configuration()

    if openai_api_key == "your_api_key_here":
        print(
            "[ERROR] Configuration was found with default values. Please edit the configuration file."
        )
        exit(0)

    if openai_api_key == "CREATED":
        exit(0)

    prompt = " ".join(prompt)

    # check authentication
    authentication_service = AuthenticationService()

    if not authentication_service.is_authenticated():
        click.echo(
            "You are currently not authenticated with Azure. "
            "Please login by running the following command: az login"
        )
        return

    # setup conversation engine
    openai = OpenAIService(
        openai_api_key,
        openai_endpoint,
        openai_gpt_deployment,
        openai_embedding_deployment,
        cognitive_search_api_key,
        cognitive_search_endpoint,
    )

    engine = ConversationEngine(openai)
    response = await engine.send_prompt(prompt)

    # feedback loop
    while not engine.is_finished():
        click.echo("\nI need some more information:")
        click.echo(f"\tCommand: {response['command']}")
        click.echo(f"\tExplanation: {response['explanation']}")
        click.echo(f"\tProblem: {response['problem']}")
        prompt = click.prompt(f"\n{response['problem']}")

        if prompt == "quit":
            click.echo("Quitting conversation.")
            exit(0)

        response = await engine.send_prompt(prompt)

    # click.echo("\nNo problems detected with your prompt:")
    # click.echo(f"\tCommand: {response['command']}")
    # click.echo(f"\tExplanation: {response['explanation']}")

    # final prompt
    # execute = click.confirm("\nDo you want to execute this command?")
    # if execute:
    # click.echo(f"\nExecuting command: {response['command']}")
    print(f"\n{execute(response['command'])}")
    # else:
    #    click.echo("Ending conversation.")


def configuration():
    # Define the name of the configuration file
    config_file = "config.yaml"

    # Check if the configuration file exists
    if os.path.exists(config_file):
        # If it exists, read the configuration values
        with open(config_file, "r") as configfile:
            config = yaml.safe_load(configfile)
            openai_api_key = config["AzureOpenAI"]["ApiKey"]
            openai_endpoint = config["AzureOpenAI"]["Endpoint"]
            openai_gpt_deployment = config["AzureOpenAI"]["GptDeploymentName"]
            openai_embedding_deployment = config["AzureOpenAI"][
                "EmbeddingDeploymentName"
            ]
            cognitive_search_api_key = config["AzureCognitiveSearch"]["ApiKey"]
            cognitive_search_endpoint = config["AzureCognitiveSearch"]["Endpoint"]

            return (
                openai_api_key,
                openai_endpoint,
                openai_gpt_deployment,
                openai_embedding_deployment,
                cognitive_search_api_key,
                cognitive_search_endpoint,
            )
    else:
        # If it doesn't exist, create a new configuration file with default values
        default_config = {
            "AzureOpenAI": {
                "ApiKey": "your_api_key_here",
                "Endpoint": "your_endpoint_here",
                "GptDeploymentName": "your_gpt_deployment_name_here",
                "EmbeddingDeploymentName": "your_embedding_deployment_name_here",
            },
            "AzureCognitiveSearch": {
                "ApiKey": "your_api_key_here",
                "Endpoint": "your_endpoint_here",
            },
        }

        with open(config_file, "w") as configfile:
            yaml.dump(default_config, configfile, default_flow_style=False)

        print(
            f"Configuration file was not found so one has been created at '{config_file}' with default values."
        )

        return (
            "CREATED",
            default_config["AzureOpenAI"]["Endpoint"],
            default_config["AzureOpenAI"]["GptDeploymentName"],
            default_config["AzureOpenAI"]["EmbeddingDeploymentName"],
            default_config["AzureCognitiveSearch"]["ApiKey"],
            default_config["AzureCognitiveSearch"]["Endpoint"],
        )
