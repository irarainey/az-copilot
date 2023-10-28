import semantic_kernel
import semantic_kernel as sk
from azext_copilot.constants import SYSTEM_MESSAGE
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextEmbedding,
)
import chromadb
from semantic_kernel.connectors.memory.chroma.chroma_memory_store import (
    ChromaMemoryStore,
)


# This class is used to interact with the OpenAI API
class OpenAIService:
    def __init__(
        self,
        api_key,
        api_endpoint,
        completion_deployment_name,
        embedding_deployment_name,
    ):
        # Define the key variables for the OpenAI API
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.completion_deployment_name = completion_deployment_name
        self.embedding_deployment_name = embedding_deployment_name

        # Create a new instance of the semantic kernel
        self.kernel = semantic_kernel.Kernel()

        # Register the chat service with the kernel
        self.kernel.add_chat_service(
            "gpt-35-turbo-16k",
            AzureChatCompletion(
                self.completion_deployment_name, self.api_endpoint, self.api_key
            ),
        )

        # Register the text embedding generation service with the kernel
        self.kernel.add_text_embedding_generation_service(
            "text-embedding-ada-002",
            AzureTextEmbedding(
                deployment_name=self.embedding_deployment_name,
                endpoint=self.api_endpoint,
                api_key=self.api_key,
            ),
        )

        chroma = ChromaMemoryStore(persist_directory="/home/ira/.az-copilot")
        self.kernel.register_memory_store(memory_store=chroma)

        # chroma_client = chromadb.PersistentClient(path="/home/ira/.az-copilot")
        # collection = chroma_client.get_or_create_collection(name="az-cli-documentation")
        # self.kernel.import_skill(sk.core_skills.TextMemorySkill())

    # This method is used to send a message to the OpenAI API
    async def send_message(self, input, history=None):
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
        context["chat_history"] = history_message
        context["user_input"] = input

        # Invoke the semantic function
        return await chat_function.invoke_async(context=context)
