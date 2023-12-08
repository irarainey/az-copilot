from azure.cli.core import AzCommandsLoader


# This class is used to load the commands for the Az CLI extension
class CopilotCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        # The custom command type is used to load the custom commands
        custom_type = CliCommandType(operations_tmpl="azext_copilot.commands#{}")

        # The super method is used to initialize the base class
        super(CopilotCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=custom_type
        )

    # The load_command_table method is used to load the commands
    def load_command_table(self, _):
        # The command_group method is used to create a new command group
        with self.command_group("") as g:
            g.custom_command("copilot", "copilot_cmd")
            g.custom_command("copilot config set", "set_config_cmd")
            g.custom_command("copilot config show", "show_config_cmd")
            g.custom_command("copilot version", "get_version_cmd")

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
                help="The plain English prompt for the AZ CLI command you would like "
                "to execute.",
                required=True,
            )
            # Define a single autorun argument
            c.argument(
                "autorun",
                options_list=["--autorun", "-a"],
                help="Boolean value to autorun the individual command when ready.",
                required=False,
            )

        # Create a new argument context for the copilot config set command
        with self.argument_context("copilot config set") as c:
            # Define the OpenAI api key argument
            c.argument(
                "openai_api_key",
                options_list=["--openai-api-key", "-ok"],
                help="The Azure OpenAI API key.",
                required=False,
            )
            # Define the OpenAI endpoint argument
            c.argument(
                "openai_endpoint",
                options_list=["--openai-endpoint", "-oe"],
                help="The Azure OpenAI endpoint.",
                required=False,
            )
            # Define the OpenAI completion deployment name argument
            c.argument(
                "completion_deployment_name",
                options_list=["--completion-name", "-cn"],
                help="The Azure OpenAI completion model deployment name.",
                required=False,
            )
            # Define the OpenAI embedding deployment name argument
            c.argument(
                "embedding_deployment_name",
                options_list=["--embedding-name", "-en"],
                help="The Azure OpenAI embedding model deployment name.",
                required=False,
            )
            # Define the Cognitive Search api key argument
            c.argument(
                "search_api_key",
                options_list=["--search-api-key", "-sk"],
                help="The Azure Cognitive Search API key.",
                required=False,
            )
            # Define the Cognitive Search endpoint argument
            c.argument(
                "search_endpoint",
                options_list=["--search-endpoint", "-se"],
                help="The Azure Cognitive Search endpoint.",
                required=False,
            )
            # Define the Cognitive Search index name argument
            c.argument(
                "search_index",
                options_list=["--search-index-name", "-si"],
                help="The Azure Cognitive Search index name.",
                required=False,
            )
            # Define the Cognitive Search vector size argument
            c.argument(
                "search_vector_size",
                options_list=["--search-vector-size", "-sv"],
                help="The Azure Cognitive Search vector size.",
                required=False,
            )
            # Define the Cognitive Search result count argument
            c.argument(
                "search_result_count",
                options_list=["--search-result-count", "-sc"],
                help="The Azure Cognitive Search result count.",
                required=False,
            )
            # Define the Cognitive Search relevance threshold argument
            c.argument(
                "search_relevance_threshold",
                options_list=["--search-relevance-threshold", "-st"],
                help="The Azure Cognitive Search relevance threshold.",
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
            # Define the use RAG command argument
            c.argument(
                "use_rag",
                options_list=["--use-rag", "-r"],
                help="Boolean value to enable or disable RAG.",
                required=False,
            )
            # Define the use logging command argument
            c.argument(
                "enable_logging",
                options_list=["--enable-logging", "-l"],
                help="Boolean value to enable or disable logging.",
                required=False,
            )


COMMAND_LOADER_CLS = CopilotCommandsLoader
