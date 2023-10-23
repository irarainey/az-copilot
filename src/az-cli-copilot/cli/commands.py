import click
import asyncio
from functools import wraps
from src.dependency_container import setup_dependency_container

container = setup_dependency_container()


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper

@click.command()
@click.argument("prompt", nargs=-1, required=True)
@coro
async def cli(prompt):
    """Simple program that displays a response to a prompt."""
    prompt = " ".join(prompt)
    # check authentication
    authentication_service = container.azure_authentication_service()

    if not authentication_service.is_authenticated():
        click.echo("You are currently not authenticated with Azure. "
                   "Please login by running the following command: az login")
        return

    # setup conversation engine
    engine = container.conversation_engine()
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

    click.echo("\nNo problems detected with your prompt:")
    click.echo(f"\tCommand: {response['command']}")
    click.echo(f"\tExplanation: {response['explanation']}")

    # final prompt
    execute = click.confirm("\nDo you want to execute this command?")
    if execute:
        click.echo(f"\nExecuting command: {response['command']}")
        executor = container.execution_service()
        print(f"\n{executor.execute(response['command'])}")
    else:
        click.echo("Ending conversation.")
