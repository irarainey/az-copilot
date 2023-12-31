import asyncio
import semantic_kernel
from azext_copilot.constants import (
    API_KEY_CONFIG_KEY,
    COGNITIVE_SEARCH_CONFIG_SECTION,
    COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY,
    COPILOT_CONFIG_SECTION,
    EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY,
    ENABLE_LOGGING_CONFIG_KEY,
    ENDPOINT_CONFIG_KEY,
    OPENAI_CONFIG_SECTION,
    SEARCH_INDEX_NAME_CONFIG_KEY,
    SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY,
    SEARCH_RESULT_COUNT_CONFIG_KEY,
    SEARCH_VECTOR_SIZE_CONFIG_KEY,
    SYSTEM_MESSAGE,
    USE_RAG_CONFIG_KEY,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
)
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)


# This class is used to interact with the OpenAI API
class OpenAIService:
    def __init__(self, config):
        # Set variables
        self.openai_api_key = config[OPENAI_CONFIG_SECTION][API_KEY_CONFIG_KEY]
        self.openai_api_endpoint = config[OPENAI_CONFIG_SECTION][ENDPOINT_CONFIG_KEY]
        self.completion_deployment_name = config[OPENAI_CONFIG_SECTION][
            COMPLETION_DEPLOYMENT_NAME_CONFIG_KEY
        ]
        self.embedding_deployment_name = config[OPENAI_CONFIG_SECTION][
            EMBEDDING_DEPLOYMENT_NAME_CONFIG_KEY
        ]
        self.search_api_key = config[COGNITIVE_SEARCH_CONFIG_SECTION][
            API_KEY_CONFIG_KEY
        ]
        self.search_endpoint = config[COGNITIVE_SEARCH_CONFIG_SECTION][
            ENDPOINT_CONFIG_KEY
        ]
        self.search_vector_size = config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_VECTOR_SIZE_CONFIG_KEY
        ]
        self.search_index = config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_INDEX_NAME_CONFIG_KEY
        ]
        self.search_result_count = config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_RESULT_COUNT_CONFIG_KEY
        ]
        self.search_relevance_threshold = config[COGNITIVE_SEARCH_CONFIG_SECTION][
            SEARCH_RELEVANCE_THRESHOLD_CONFIG_KEY
        ]
        self.use_rag = config[COPILOT_CONFIG_SECTION][USE_RAG_CONFIG_KEY]
        self.enable_logging = config[COPILOT_CONFIG_SECTION][ENABLE_LOGGING_CONFIG_KEY]

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

        if self.use_rag:
            # Register the text embedding generation service with the kernel
            self.kernel.add_text_embedding_generation_service(
                "text-embedding-ada-002",
                AzureTextEmbedding(
                    deployment_name=self.embedding_deployment_name,
                    endpoint=self.openai_api_endpoint,
                    api_key=self.openai_api_key,
                ),
            )

            # Register Cognitive Search as a memory store
            self.kernel.register_memory_store(
                memory_store=AzureCognitiveSearchMemoryStore(
                    self.search_vector_size,
                    self.search_endpoint,
                    self.search_api_key,
                )
            )

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
            Azure CLI Documentation: {{$az_documentation}}
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

        # Set the RAG data to empty
        documentation = ""

        # If RAG is enabled search the memory store for relevant documentation
        if self.use_rag:
            # Search the memory store for any relevant documentation
            search_results = await context.memory.search_async(
                collection=self.search_index,
                query=prompt,
                limit=self.search_result_count,
                min_relevance_score=self.search_relevance_threshold,
            )

            # Build the result of the search
            for result in search_results:
                documentation += f"\n{result.description}\n{result.text}\n"

            if self.enable_logging:
                print(f"[OPENAI|SEND PROMPT] RAG Search Result: {documentation}")

        # Define the context variables
        context["az_documentation"] = documentation
        context["chat_history"] = history_message
        context["user_input"] = prompt

        if self.enable_logging:
            print(f"[OPENAI|SEND PROMPT] History: {history_message}")

        if self.enable_logging:
            print(f"[OPENAI|SEND PROMPT] Prompt: {prompt}")

        # Invoke the semantic function
        return await chat_function.invoke_async(context=context)
