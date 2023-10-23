import os
from dotenv import load_dotenv
from src.domain import constants


class EnvironmentContextService:

    def load_environment(self):
        load_dotenv()

        if not self.environment_valid():
            raise Exception("You have not provided all environment variables")

        os.environ["OPENAI_API_KEY"] = self.azure_open_ai_key
        os.environ["OPENAI_API_TYPE"] = "azure"
        os.environ["OPENAI_API_BASE"] = self.azure_open_ai_url
        os.environ["OPENAI_API_VERSION"] = "2023-05-15"
        os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = self.azure_open_ai_gpt_deployment_name

    def environment_valid(self) -> bool:

        if not os.environ.get(constants.AZURE_COGNITIVE_SEARCH_KEY):
            return False

        if not os.environ.get(constants.AZURE_COGNITIVE_SEARCH_URL):
            return False

        if not os.environ.get(constants.AZURE_COGNITIVE_SEARCH_INDEX_NAME):
            return False

        if not os.environ.get(constants.AZURE_OPEN_AI_KEY):
            return False

        if not os.environ.get(constants.AZURE_OPEN_AI_URL):
            return False

        if not os.environ.get(constants.AZURE_OPEN_AI_EMBEDDING_DEPLOYMENT_NAME):
            return False

        return True

    @property
    def azure_cognitive_search_key(self):
        return os.environ.get(constants.AZURE_COGNITIVE_SEARCH_KEY)

    @property
    def azure_cognitive_search_url(self):
        return os.environ.get(constants.AZURE_COGNITIVE_SEARCH_URL)

    @property
    def azure_cognitive_search_index_name(self):
        return os.environ.get(constants.AZURE_COGNITIVE_SEARCH_INDEX_NAME)

    @property
    def azure_open_ai_key(self):
        return os.environ.get(constants.AZURE_OPEN_AI_KEY)

    @property
    def azure_open_ai_url(self):
        return os.environ.get(constants.AZURE_OPEN_AI_URL)

    @property
    def azure_open_ai_gpt_deployment_name(self):
        return os.environ.get(constants.AZURE_OPEN_AI_GPT_DEPLOYMENT_NAME)

    @property
    def azure_open_ai_embedding_deployment_name(self):
        return os.environ.get(constants.AZURE_OPEN_AI_EMBEDDING_DEPLOYMENT_NAME)
