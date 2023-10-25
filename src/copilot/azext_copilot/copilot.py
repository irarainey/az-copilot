import os
import subprocess
import click
import asyncio
import json
import ast
from functools import wraps
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
import semantic_kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextEmbedding,
)

AZURE_OPENAI_API_KEY = "AZURE_OPENAI_API_KEY"
AZURE_OPENAI_ENDPOINT = "AZURE_OPENAI_ENDPOINT"
AZURE_OPENAI_DEPLOYMENT_NAME = "AZURE_OPENAI_DEPLOYMENT_NAME"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
AZURE_COGNITIVE_SEARCH_URL = "AZURE_COGNITIVE_SEARCH_URL"
AZURE_COGNITIVE_SEARCH_KEY = "AZURE_COGNITIVE_SEARCH_KEY"
COMMANDS_KEY = "command"
PROBLEM_KEY = "problem"


load_dotenv()


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
    authentication_service = AuthenticationService()

    if not authentication_service.is_authenticated():
        click.echo(
            "You are currently not authenticated with Azure. "
            "Please login by running the following command: az login"
        )
        return

    # setup conversation engine
    openai = OpenAIService(
        api_base=os.environ[AZURE_OPENAI_ENDPOINT],
        api_key=os.environ[AZURE_OPENAI_API_KEY],
        open_ai_gpt_deployment_name=os.environ[AZURE_OPENAI_DEPLOYMENT_NAME],
        open_ai_text_embedding_deployment_name=os.environ[
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
        ],
        search_endpoint=os.environ["AZURE_COGNITIVE_SEARCH_URL"],
        search_key=os.environ["AZURE_COGNITIVE_SEARCH_KEY"],
    )
    engine = ConversationEngine(openai)
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

    # click.echo("\nNo problems detected with your prompt:")
    # click.echo(f"\tCommand: {response['command']}")
    # click.echo(f"\tExplanation: {response['explanation']}")

    # final prompt
    # execute = click.confirm("\nDo you want to execute this command?")
    # if execute:
    # click.echo(f"\nExecuting command: {response['command']}")
    print(f"\n{execute(response['command'])}")
    # else:
    #    click.echo("Ending conversation.")


def execute(command):
    try:
        completed_process = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return completed_process.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr


class AuthenticationService:
    def __init__(self):
        self._credential = AzureCliCredential()

    def is_authenticated(self):
        try:
            token = self._credential.get_token("https://management.azure.com/.default")
            return token is not None
        except Exception as e:
            print(e)
            return False

    @property
    def credential(self):
        return self._credential


class ConversationEngine:
    def __init__(self, open_ai_service):
        self.chat_history = []
        self._commands = None
        self._problems = None
        # setup services
        self.azure_open_ai_client_service = open_ai_service

    async def generate_response(self, prompt):
        self.chat_history = [("q", prompt)]

        # get openAI response
        response = await self.azure_open_ai_client_service.send_message(prompt)
        response = json.loads(response.result.strip(""))
        self.chat_history.append(("a", response))
        return response

    async def send_prompt(self, prompt):
        # Replace this with your own conversational engine logic
        self.chat_history.append(("q", prompt))

        # create history message
        history = [x[1] for x in self.chat_history]

        # get openAI response
        response = await self.azure_open_ai_client_service.send_message(prompt, history)

        r = ast.literal_eval(response.result)
        # awful piece of code
        response = json.loads(json.dumps(r))

        if COMMANDS_KEY in response:
            self._commands = response[COMMANDS_KEY]

        if PROBLEM_KEY in response:
            self._problems = response[PROBLEM_KEY]
        else:
            self._problems = None

        self.chat_history.append(("a", response))
        return response

    async def continue_conversation(self, prompt):
        # Replace this with your own conversational engine logic
        self.chat_history.append(("q", prompt))

        # create history message
        history = [x[1] for x in self.chat_history]

        # get openAI response
        response = await self.azure_open_ai_client_service.send_message(prompt, history)

        r = ast.literal_eval(response.result)
        # awful piece of code
        response = json.loads(json.dumps(r))

        if COMMANDS_KEY in response:
            self._commands = response[COMMANDS_KEY]

        if PROBLEM_KEY in response:
            self._problems = response[PROBLEM_KEY]

        self.chat_history.append(("a", response))
        return response

    def is_finished(self):
        return self._commands is not None and not self.has_problem()

    def has_problem(self):
        return self._problems and self._problems.strip() != ""


class OpenAIService:
    def __init__(
        self,
        api_key,
        api_base,
        open_ai_text_embedding_deployment_name,
        open_ai_gpt_deployment_name,
        search_endpoint,
        search_key,
    ):
        self.vector_size = 1536
        self.open_ai_text_embedding_deployment_name = (
            open_ai_text_embedding_deployment_name
        )
        self.open_ai_gpt_deployment_name = open_ai_gpt_deployment_name
        self.kernel = semantic_kernel.Kernel()

        # Configure AI service used by the kernel
        _, api_key, endpoint = semantic_kernel.azure_openai_settings_from_dot_env()

        connector = AzureCognitiveSearchMemoryStore(
            self.vector_size,
            search_endpoint,
            search_key,
        )

        self.kernel.add_text_embedding_generation_service(
            "ada",
            AzureTextEmbedding(
                deployment_name=self.open_ai_text_embedding_deployment_name,
                endpoint=api_base,
                api_key=api_key,
            ),
        )

        self.kernel.register_memory_store(memory_store=connector)

        self.kernel.add_chat_service(
            "dv",
            AzureChatCompletion(self.open_ai_gpt_deployment_name, endpoint, api_key),
        )

    async def send_message(self, input, history=None):
        prompt_config = semantic_kernel.PromptTemplateConfig.from_completion_parameters(
            temperature=0, max_tokens=2000, top_p=0.5
        )

        sk_prompt = """
            History: {{$chat_history}}
            Prompt: {{$user_input}}
            """

        prompt_template = semantic_kernel.ChatPromptTemplate(
            sk_prompt, self.kernel.prompt_template_engine, prompt_config
        )

        prompt_template.add_system_message(
            """You are an azure assistant that manages and creates azure resources. \
            Your task is to create azure cli commands. \
            You respond in json format that has three keys: command, problem and explanation. \
            You should not auto-populate command arguments. If you miss information such as parameters that are needed for the command, you should use the problem key. \
            In the explanation key you should provide a small description what the command does. \
            You should only use the command key if you have all the information and can form a complete azure cli command. \
            The results should be in json format in the structure of: \
            'json-start-bracket' "command": "the azure cli commands", "problem": "asking the user for input", "explanation": "explaining what the command does"  'json-end-bracket'.
            Json property names should be enclosed with double quotes"""
        )

        func_config = semantic_kernel.SemanticFunctionConfig(
            prompt_config, prompt_template
        )

        chat_function = self.kernel.register_semantic_function(
            "ChatBot", "Chat", func_config
        )

        history_message = ""
        if history:
            for i in range(len(history[:-1])):
                if i % 2 == 0:
                    q = history[i]
                    a = history[i + 1]
                    history_message += f"\n{q}\n{a}\n"

        context = self.kernel.create_new_context()
        context["chat_history"] = history_message
        context["user_input"] = input
        return await chat_function.invoke_async(context=context)


class Message:
    def __init__(self, role, message=None, message_type=None):
        self._role = role
        self._message = message
        self._message_type = message_type

    @property
    def length(self):
        return len(self._message)

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, message_type):
        self._message_type = message_type

    def to_dict(self):
        return {
            "role": self._role.value,
            "content": self._message,
        }


class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            # Convert the Message object to a dictionary
            return obj.__repr__()

        # Call the base class implementation which handles other types
        return super().default(obj)


class Conversation:
    def __init__(self, messages: list[Message] = None):
        self._messages = []

        if messages is not None:
            for message in messages:
                self.add_message(message)

    def add_message(self, message: Message):
        if self._messages is None:
            self._messages = []

        self._messages.append(message)

    @property
    def messages(self):
        return [message.to_dict() for message in self._messages]
