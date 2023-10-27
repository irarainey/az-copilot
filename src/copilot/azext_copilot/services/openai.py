from azext_copilot.constants import SYSTEM_MESSAGE
import semantic_kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextEmbedding,
)


# This class is used to interact with the OpenAI API
class OpenAIService:
    def __init__(
        self,
        api_key,
        api_base,
        open_ai_gpt_deployment_name,
        open_ai_text_embedding_deployment_name,
        search_key,
        search_endpoint,
    ):
        # Define the key variables for the OpenAI API
        self.api_base = api_base
        self.api_key = api_key
        self.open_ai_gpt_deployment_name = open_ai_gpt_deployment_name
        self.open_ai_text_embedding_deployment_name = (
            open_ai_text_embedding_deployment_name
        )
        self.search_endpoint = search_endpoint
        self.search_key = search_key
        self.vector_size = 1536

        # Create a new instance of the semantic kernel
        self.kernel = semantic_kernel.Kernel()

        # Create a memory store using Azure Cognitive Search
        connector = AzureCognitiveSearchMemoryStore(
            self.vector_size,
            self.search_endpoint,
            self.search_key,
        )

        # Register the text embedding generation service with the kernel
        self.kernel.add_text_embedding_generation_service(
            "ada",
            AzureTextEmbedding(
                deployment_name=self.open_ai_text_embedding_deployment_name,
                endpoint=self.api_base,
                api_key=self.api_key,
            ),
        )

        # Register the chat service with the kernel
        self.kernel.add_chat_service(
            "dv",
            AzureChatCompletion(
                self.open_ai_gpt_deployment_name, self.api_base, self.api_key
            ),
        )

        # Register the memory store with the kernel
        self.kernel.register_memory_store(memory_store=connector)

    # This method is used to send a message to the OpenAI API
    async def send_message(self, input, history=None):
        # Define the prompt configuration
        prompt_config = semantic_kernel.PromptTemplateConfig.from_completion_parameters(
            temperature=0, max_tokens=2000, top_p=0.5
        )

        # Define the prompt template
        sk_prompt = """
            History: {{$chat_history}}
            Prompt: {{$user_input}}
            """

        # Create a new prompt template
        prompt_template = semantic_kernel.ChatPromptTemplate(
            sk_prompt, self.kernel.prompt_template_engine, prompt_config
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
        context["chat_history"] = history_message
        context["user_input"] = input

        # Invoke the semantic function
        return await chat_function.invoke_async(context=context)
