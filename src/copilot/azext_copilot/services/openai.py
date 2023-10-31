import asyncio
import semantic_kernel
from azext_copilot.constants import (
    SEARCH_INDEX_NAME,
    SEARCH_RELEVANCE_THRESHOLD,
    SEARCH_RESULT_COUNT,
    SEARCH_VECTOR_SIZE,
    SYSTEM_MESSAGE,
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
    def __init__(
        self,
        openai_api_key,
        openai_api_endpoint,
        completion_deployment_name,
        embedding_deployment_name,
        search_api_key,
        search_endpoint,
        use_rag,
        enable_logging,
    ):
        # Define the key variables for the OpenAI API
        self.openai_api_key = openai_api_key
        self.openai_api_endpoint = openai_api_endpoint
        self.completion_deployment_name = completion_deployment_name
        self.embedding_deployment_name = embedding_deployment_name
        self.search_api_key = search_api_key
        self.search_endpoint = search_endpoint
        self.use_rag = use_rag
        self.enable_logging = enable_logging

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

        # Register Cognitive Search as a memory store
        self.kernel.register_memory_store(
            memory_store=AzureCognitiveSearchMemoryStore(
                SEARCH_VECTOR_SIZE,
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
                collection=SEARCH_INDEX_NAME,
                query=prompt,
                limit=SEARCH_RESULT_COUNT,
                min_relevance_score=SEARCH_RELEVANCE_THRESHOLD,
            )

            # Build the result of the search
            for result in search_results:
                documentation += f"\n{result.description}\n{result.text}\n"

            if self.enable_logging:
                print(f"[OPENAI|SEND PROMPT] Search Result: {documentation}")

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
