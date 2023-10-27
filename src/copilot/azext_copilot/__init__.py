from azure.cli.core import AzCommandsLoader


class CopilotCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        custom_type = CliCommandType(operations_tmpl="azext_copilot.custom#{}")
        super(CopilotCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=custom_type
        )

    def load_command_table(self, _):
        with self.command_group("") as g:
            g.custom_command("copilot", "call_openai")
            g.custom_command("copilot config set", "set_configuration")

        return self.command_table

    def load_arguments(self, _):
        with self.argument_context("copilot") as c:
            c.argument(
                "prompt",
                options_list=["--prompt", "-p"],
                help="The plain English prompt for the Az CLI command you would like "
                "to execute.",
                required=True,
            )

        with self.argument_context("copilot config set") as c:
            c.argument(
                "openai_gpt_deployment",
                options_list=["--deployment-name", "-dn"],
                help="The Azure OpenAI deployment name.",
                required=False,
            )
            c.argument(
                "openai_api_key",
                options_list=["--api-key", "-ak"],
                help="The Azure OpenAI API key.",
                required=False,
            )
            c.argument(
                "openai_endpoint",
                options_list=["--openai-endpoint", "-oe"],
                help="The Azure OpenAI endpoint.",
                required=False,
            )
            c.argument(
                "openai_embedding_deployment",
                options_list=["--embedding-name", "-en"],
                help="The Azure OpenAI embedding model deployment name.",
                required=False,
            )
            c.argument(
                "cognitive_search_api_key",
                options_list=["--search-key", "-sk"],
                help="The Azure Cognitive Search API key.",
                required=False,
            )
            c.argument(
                "cognitive_search_endpoint",
                options_list=["--cognitive-search-endpoint", "-ce"],
                help="The Azure Cognitive Search endpoint.",
                required=False,
            )
            c.argument(
                "autorun",
                options_list=["--autorun", "-ar"],
                help="Boolean value to autorun the command when ready.",
                required=False,
            )
            c.argument(
                "show_command",
                options_list=["--show-command", "-sc"],
                help="Boolean value to show or hide commands.",
                required=False,
            )


COMMAND_LOADER_CLS = CopilotCommandsLoader
