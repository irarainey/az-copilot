import argparse
from azext_copilot.conversation_engine import ConversationEngine
from azext_copilot.services.authentication import AuthenticationService
from azext_copilot.services.openai import OpenAIService
from azext_copilot.helpers import execute
from azext_copilot.configuration import get_configuration
from azext_copilot.constants import COMMAND_KEY, PROBLEM_KEY, EXPLANATION_KEY


def invoke():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=str)
    args = parser.parse_args()
    copilot(args.prompt)


def copilot(prompt):
    # Get configuration values
    (
        openai_api_key,
        openai_endpoint,
        completion_deployment_name,
        embedding_deployment_name,
        search_api_key,
        search_endpoint,
        autorun,
        show_command,
        use_rag,
        enable_logging,
    ) = get_configuration()

    # Determine if configuration has been set
    if (
        openai_api_key is None
        or openai_endpoint is None
        or completion_deployment_name is None
        or embedding_deployment_name is None
        or search_api_key is None
        or search_endpoint is None
        or autorun is None
        or show_command is None
        or use_rag is None
        or enable_logging is None
    ):
        print(
            "Configuration was found with empty values. "
            "Run 'az copilot config set' to set the configuration values."
        )
        return

    # Check authentication
    authentication_service = AuthenticationService()

    # If the user is not authenticated, display a message and exit
    if not authentication_service.is_authenticated():
        print(
            "You are currently not authenticated. "
            "Login with 'az login' before continuing."
        )
        return

    # Setup OpenAI service
    openai = OpenAIService(
        openai_api_key,
        openai_endpoint,
        completion_deployment_name,
        embedding_deployment_name,
        search_api_key,
        search_endpoint,
        use_rag,
        enable_logging,
    )

    # Setup conversation engine
    engine = ConversationEngine(openai, enable_logging)

    # Send the prompt to the engine
    response = engine.send_prompt(prompt)

    # Run the feedback loop
    while not engine.is_finished():
        print("\nI need more information:")
        print(f"\nCommand: {response[COMMAND_KEY]}")
        print(f"Explanation: {response[EXPLANATION_KEY]}")
        print(f"Problem: {response[PROBLEM_KEY]}")
        prompt = input(f"\n{response[PROBLEM_KEY].rstrip('.')}: ")

        # Check if the user wants to quit
        if prompt == "quit":
            print("Quitting Copilot conversation.")
            return

        response = engine.send_prompt(prompt)

    # If autorun is True just execute the command
    if autorun is True:
        # Check if the user wants to see the command
        if show_command is True:
            print(f"\nCommand: {response[COMMAND_KEY]}")
            print(f"Explanation: {response[EXPLANATION_KEY]}")

        # Execute the command and show the output
        print(f"\n{execute(response[COMMAND_KEY], enable_logging)}")
    else:
        # Show Command setting is ignored here because you can't make
        # a choice if you don't see the command first
        print(f"\nCommand: {response[COMMAND_KEY]}")
        print(f"Explanation: {response[EXPLANATION_KEY]}")
        run_command = (
            input("\nDo you want to execute this command? (y/n) ").lower().strip()
            == "y"
        )

        # If the user wants to execute the command, do so
        if run_command:
            print(f"\n{execute(response[COMMAND_KEY], enable_logging)}")
        else:
            print("Command not executed.")
