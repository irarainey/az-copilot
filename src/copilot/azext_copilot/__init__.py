from azure.cli.core import AzCommandsLoader


def show_message():
    print('Simple prompt command')


class CopilotCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(operations_tmpl='azext_copilot#{}')
        super(CopilotCommandsLoader, self).__init__(cli_ctx=cli_ctx, custom_command_type=custom_type)

    def load_command_table(self, args):
        
        with self.command_group('copilot') as g:
            g.custom_command('tips', 'show_message')
            
        return self.command_table
    
    def load_arguments(self, _):
        pass


COMMAND_LOADER_CLS = CopilotCommandsLoader
