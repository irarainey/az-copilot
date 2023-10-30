import asyncio
import semantic_kernel
from azext_copilot.constants import SEARCH_INDEX_NAME, SYSTEM_MESSAGE
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
)
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)


# This class is used to interact with the OpenAI API
class OpenAIService:
    def __init__(
        self,
        openai_api_key,
        openai_api_endpoint,
        completion_deployment_name,
        embedding_deployment_name,
        search_api_key,
        search_endpoint,
    ):
        # Define the key variables for the OpenAI API
        self.openai_api_key = openai_api_key
        self.openai_api_endpoint = openai_api_endpoint
        self.completion_deployment_name = completion_deployment_name
        self.embedding_deployment_name = embedding_deployment_name
        self.vector_size = 1536
        self.search_api_key = search_api_key
        self.search_endpoint = search_endpoint

        # Create a new instance of the semantic kernel
        self.kernel = semantic_kernel.Kernel()

        # Register the chat service with the kernel
        self.kernel.add_chat_service(
            "gpt-35-turbo-16k",
            AzureChatCompletion(
                self.completion_deployment_name,
                self.openai_api_endpoint,
                self.openai_api_key,
            ),
        )

        # Register the text embedding generation service with the kernel
        self.kernel.add_text_embedding_generation_service(
            "text-embedding-ada-002",
            AzureTextEmbedding(
                deployment_name=self.embedding_deployment_name,
                endpoint=self.openai_api_endpoint,
                api_key=self.openai_api_key,
            ),
        )

        self.kernel.register_memory_store(
            memory_store=AzureCognitiveSearchMemoryStore(
                self.vector_size,
                self.search_endpoint,
                self.search_api_key,
            )
        )

        self.kernel.import_skill(semantic_kernel.core_skills.TextMemorySkill())

    def send_prompt(self, input, history=None):
        return asyncio.run(self.send(input, history))

    # This method is used to send a message to the OpenAI API
    async def send(self, prompt, history=None):
        # Define the prompt configuration
        prompt_config = semantic_kernel.PromptTemplateConfig.from_completion_parameters(
            temperature=0, max_tokens=2000, top_p=0.5
        )

        # Create a new prompt template
        prompt_template = semantic_kernel.ChatPromptTemplate(
            """
            History: {{$chat_history}}
            Prompt: {{$user_input}}
            """,
            self.kernel.prompt_template_engine,
            prompt_config,
        )

        # Add a system message to the prompt template
        prompt_template.add_system_message(SYSTEM_MESSAGE)

        # Define the semantic function configuration
        func_config = semantic_kernel.SemanticFunctionConfig(
            prompt_config, prompt_template
        )

        # Register the semantic function
        chat_function = self.kernel.register_semantic_function(
            "ChatBot", "Chat", func_config
        )

        # Define the history message
        history_message = ""
        if history:
            for i in range(len(history[:-1])):
                if i % 2 == 0:
                    q = history[i]
                    a = history[i + 1]
                    history_message += f"\n{q}\n{a}\n"

        # Create a new context
        context = self.kernel.create_new_context()

        # Define the context variables
        context[
            semantic_kernel.core_skills.TextMemorySkill.COLLECTION_PARAM
        ] = SEARCH_INDEX_NAME
        context[semantic_kernel.core_skills.TextMemorySkill.RELEVANCE_PARAM] = 0.5
        context["chat_history"] = history_message
        context["user_input"] = prompt

        # Invoke the semantic function
        return await chat_function.invoke_async(context=context)
