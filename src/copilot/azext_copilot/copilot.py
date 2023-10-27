import click
import asyncio
from functools import wraps
from .conversation_engine import ConversationEngine
from .services.authentication import AuthenticationService
from .services.openai import OpenAIService
from .helpers import execute
from .configuration import get_configuration


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
        autorun,
        show_command,
    ) = get_configuration()

    # Determine if configuration has been set
    if (
        openai_api_key is None
        or openai_endpoint is None
        or openai_gpt_deployment is None
        or openai_embedding_deployment is None
        or cognitive_search_api_key is None
        or cognitive_search_endpoint is None
        or autorun is None
        or show_command is None
    ):
        print(
            "Configuration was found with empty values. "
            "Run 'az copilot config set' to set the configuration values."
        )
        return

    # Convert prompt to a single string (which isn't needed when called from the AZ CLI)
    prompt = " ".join(prompt)

    # check authentication
    authentication_service = AuthenticationService()

    if not authentication_service.is_authenticated():
        click.echo(
            "You are currently not authenticated. "
            "Login with 'az login' before continuing."
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
        click.echo(f"=> Command: {response['command']}")
        click.echo(f"=> Explanation: {response['explanation']}")
        click.echo(f"=> Problem: {response['problem']}")
        prompt = click.prompt(f"\n{response['problem']}")

        if prompt == "quit":
            click.echo("Quitting conversation.")
            return

        response = await engine.send_prompt(prompt)

    if autorun is True:
        if show_command is True:
            click.echo(f"\nCommand: {response['command']}")
            click.echo(f"Explanation: {response['explanation']}")
        click.echo(f"\n{execute(response['command'])}")
    else:
        click.echo(f"\nCommand: {response['command']}")
        click.echo(f"Explanation: {response['explanation']}")
        run_command = click.confirm("\nDo you want to execute this command?")
        if run_command:
            click.echo(f"\n{execute(response['command'])}")
        else:
            click.echo("Command not executed.")
