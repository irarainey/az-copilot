import ast
import json
from azext_copilot.constants import COMMAND_KEY, PROBLEM_KEY


# The conversation engine class
class ConversationEngine:
    def __init__(self, openai_service, enable_logging):
        self.chat_history = []
        self._commands = None
        self._problems = None

        # Setup services
        self.openai_client_service = openai_service
        self.enable_logging = enable_logging

    def send_prompt(self, prompt):
        self.chat_history.append(("q", prompt))

        # create history message
        history = [x[1] for x in self.chat_history]

        # get openAI response
        response = self.openai_client_service.send_prompt(prompt, history)

        r = ast.literal_eval(response.result)
        response = json.loads(json.dumps(r))

        if self.enable_logging:
            print(
                f"[CONVERSATION ENGINE|SEND PROMPT] Conversation Response: {response}"
            )

        if COMMAND_KEY in response:
            self._commands = response[COMMAND_KEY]

        if PROBLEM_KEY in response:
            self._problems = response[PROBLEM_KEY]
        else:
            self._problems = None

        self.chat_history.append(("a", response))
        return response

    def is_finished(self):
        return self._commands is not None and not self.has_problem()

    def has_problem(self):
        return self._problems and self._problems.strip() != ""
