from azext_copilot.copilot import copilot
from azure.cli.core import AzCommandsLoader


def call_cli(cmd_prompt):
    copilot(cmd_prompt)


class CopilotCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_copilot#{}')
        super(CopilotCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                    custom_command_type=custom_type)

    def load_command_table(self, _):
        with self.command_group('') as g:
            g.custom_command('copilot', 'call_cli')

        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('copilot') as c:
            c.argument('cmd_prompt', options_list=['--command', '-c'], help='The plain English command you wish to execute.')


COMMAND_LOADER_CLS = CopilotCommandsLoader
