from azure.cli.core import AzCommandsLoader


# This class is used to load the commands for the Az CLI extension
class CopilotCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        # The custom command type is used to load the custom commands
        custom_type = CliCommandType(operations_tmpl="azext_copilot.custom#{}")

        # The super method is used to initialize the base class
        super(CopilotCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=custom_type
        )

    # The load_command_table method is used to load the commands
    def load_command_table(self, _):
        # The command_group method is used to create a new command group
        with self.command_group("") as g:
            g.custom_command("copilot", "call_openai")
            g.custom_command("copilot config set", "set_configuration")
            g.custom_command("copilot embedding init", "initialise_embedding")
            g.custom_command("copilot embedding update", "update_embedding")

        # Return the command table
        return self.command_table

    # The load_arguments method is used to load the arguments
    def load_arguments(self, _):
        # Create a new argument context for the copilot command
        with self.argument_context("copilot") as c:
            # Define the prompt argument
            c.argument(
                "prompt",
                options_list=["--prompt", "-p"],
                help="The plain English prompt for the Az CLI command you would like "
                "to execute.",
                required=True,
            )

        # Create a new argument context for the copilot config set command
        with self.argument_context("copilot config set") as c:
            # Define the OpenAI api key argument
            c.argument(
                "api_key",
                options_list=["--api-key", "-k"],
                help="The Azure OpenAI API key.",
                required=False,
            )
            # Define the OpenAI endpoint argument
            c.argument(
                "endpoint",
                options_list=["--endpoint", "-e"],
                help="The Azure OpenAI endpoint.",
                required=False,
            )
            # Define the OpenAI completion name argument
            c.argument(
                "completion_deployment",
                options_list=["--completion-name", "-dn"],
                help="The Azure OpenAI completion model deployment name.",
                required=False,
            )
            # Define the OpenAI embedding name argument
            c.argument(
                "embedding_deployment",
                options_list=["--embedding-name", "-en"],
                help="The Azure OpenAI embedding model deployment name.",
                required=False,
            )
            # Define the autorun argument
            c.argument(
                "autorun",
                options_list=["--autorun", "-a"],
                help="Boolean value to autorun the command when ready.",
                required=False,
            )
            # Define the show command argument
            c.argument(
                "show_command",
                options_list=["--show-command", "-s"],
                help="Boolean value to show or hide commands.",
                required=False,
            )


COMMAND_LOADER_CLS = CopilotCommandsLoader
