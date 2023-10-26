from azure.cli.core import AzCommandsLoader


class CopilotCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_copilot.custom#{}')
        super(CopilotCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    custom_command_type=custom_type)

    def load_command_table(self, _):
        with self.command_group('') as g:
            g.custom_command('copilot', 'call_openai')
            g.custom_command('copilot config', 'reset_configuration')

        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('copilot') as c:
            c.argument('prompt', options_list=['--prompt', '-p'], help='The plain English prompt for the Az CLI command you would like to execute.')


COMMAND_LOADER_CLS = CopilotCommandsLoader
