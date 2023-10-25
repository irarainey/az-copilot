import click
import asyncio
from functools import wraps
from azext_copilot.conversation_engine import ConversationEngine
from azext_copilot.services.authentication import AuthenticationService
from azext_copilot.services.openai import OpenAIService
from azext_copilot._helpers import execute, configuration


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.argument("prompt", nargs=-1, required=True)
@coro
async def copilot(prompt):

    # Get configuration values
    (
        openai_api_key,
        openai_endpoint,
        openai_gpt_deployment,
        openai_embedding_deployment,
        cognitive_search_api_key,
        cognitive_search_endpoint,
    ) = configuration()

    # Determine if configuration is default
    if openai_api_key == "your_api_key_here":
        print(
            "[ERROR] Configuration was found with default values. Please edit the configuration file."
        )
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
