import click
import asyncio
from functools import wraps
from .conversation_engine import ConversationEngine
from .services.authentication import AuthenticationService
from .services.openai import OpenAIService
from .helpers import execute
from .configuration import get_configuration
from .constants import COMMAND_KEY, PROBLEM_KEY, EXPLANATION_KEY


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

    # Check authentication
    authentication_service = AuthenticationService()

    # If the user is not authenticated, display a message and exit
    if not authentication_service.is_authenticated():
        click.echo(
            "You are currently not authenticated. "
            "Login with 'az login' before continuing."
        )
        return

    # Setup OpenAI service
    openai = OpenAIService(
        openai_api_key,
        openai_endpoint,
        openai_gpt_deployment,
        openai_embedding_deployment,
        cognitive_search_api_key,
        cognitive_search_endpoint,
    )

    # Setup conversation engine
    engine = ConversationEngine(openai)

    # Send the prompt to the engine
    response = await engine.send_prompt(prompt)

    # Run the feedback loop
    while not engine.is_finished():
        click.echo("\nI need more information:")
        click.echo(f"\nCommand: {response[COMMAND_KEY]}")
        click.echo(f"Explanation: {response[EXPLANATION_KEY]}")
        click.echo(f"Problem: {response[PROBLEM_KEY]}")
        prompt = click.prompt(f"\n{response[PROBLEM_KEY].rstrip('.')}")

        # Check if the user wants to quit
        if prompt == "quit":
            click.echo("Quitting Copilot conversation.")
            return

        response = await engine.send_prompt(prompt)

    # If autorun is True just execute the command
    if autorun is True:
        # Check if the user wants to see the command
        if show_command is True:
            click.echo(f"\nCommand: {response[COMMAND_KEY]}")
            click.echo(f"Explanation: {response[EXPLANATION_KEY]}")

        # Execute the command and show the output
        click.echo(f"\n{execute(response[COMMAND_KEY])}")
    else:
        # Show Command setting is ignored here because you can't make
        # a choice if you don't see the command first
        click.echo(f"\nCommand: {response[COMMAND_KEY]}")
        click.echo(f"Explanation: {response[EXPLANATION_KEY]}")
        run_command = click.confirm("\nDo you want to execute this command?")

        # If the user wants to execute the command, do so
        if run_command:
            click.echo(f"\n{execute(response[COMMAND_KEY])}")
        else:
            click.echo("Command not executed.")
