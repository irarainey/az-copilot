import ast
import json

COMMANDS_KEY = "command"
PROBLEM_KEY = "problem"


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
