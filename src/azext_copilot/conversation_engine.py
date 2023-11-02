import ast
import json
import re
from azext_copilot.constants import (
    COMMAND_KEY,
    COPILOT_CONFIG_SECTION,
    ENABLE_LOGGING_CONFIG_KEY,
    PROBLEM_KEY,
)


# The conversation engine class
class ConversationEngine:
    def __init__(self, openai_service, config):
        self.chat_history = []
        self._commands = None
        self._problems = None

        # Setup services
        self.openai_service = openai_service
        self.enable_logging = config[COPILOT_CONFIG_SECTION][ENABLE_LOGGING_CONFIG_KEY]

    def send_prompt(self, prompt):
        self.chat_history.append(("q", prompt))

        # create history message
        history = [x[1] for x in self.chat_history]

        # get openAI response
        openai_response = self.openai_service.send_prompt(prompt, history)

        if openai_response.error_occurred:
            if self.enable_logging:
                print(
                    "[CONVERSATION ENGINE|SEND PROMPT] Error Response: "
                    f"{openai_response.last_error_description}"
                )
            matches = re.findall(
                r"\(<(.*?)>, '(.*?)', (.*?)\)", openai_response.last_error_description
            )
            if matches:
                error_code, error_message, _ = matches[0]
                print(f"An error has occured. {error_message} ({error_code}).")
            else:
                print(openai_response.last_error_description)
            exit(0)

        if self.enable_logging:
            print(
                "[CONVERSATION ENGINE|SEND PROMPT] Conversation Response: "
                f"{openai_response.result}"
            )

        json_response = ast.literal_eval(openai_response.result)
        response = json.loads(json.dumps(json_response))

        if COMMAND_KEY in response:
            self._commands = response[COMMAND_KEY]
            if self._commands is None or self._commands.strip() == "":
                self._commands = "UNKNOWN"

        if PROBLEM_KEY in response:
            if self._commands == "UNKNOWN":
                self._problems = (
                    "A command couldn't be determined from your input. "
                    "Try rephrasing you prompt."
                )
            else:
                self._problems = response[PROBLEM_KEY]
        else:
            self._problems = None

        response[COMMAND_KEY] = self._commands
        response[PROBLEM_KEY] = self._problems

        self.chat_history.append(("a", response))
        return response

    def is_finished(self):
        return self._commands is not None and not self.has_problem()

    def has_problem(self):
        return self._problems and self._problems.strip() != ""
