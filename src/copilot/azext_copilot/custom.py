
from .copilot import copilot


def call_openai(prompt):
    copilot(prompt)


def reset_configuration():
    print("reset_configuration")
