import semantic_kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextEmbedding,
)


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
        self.api_base = api_base
        self.api_key = api_key
        self.open_ai_gpt_deployment_name = open_ai_gpt_deployment_name
        self.open_ai_text_embedding_deployment_name = (
            open_ai_text_embedding_deployment_name
        )
        self.search_endpoint = search_endpoint
        self.search_key = search_key
        self.vector_size = 1536
        self.kernel = semantic_kernel.Kernel()

        connector = AzureCognitiveSearchMemoryStore(
            self.vector_size,
            self.search_endpoint,
            self.search_key,
        )

        self.kernel.add_text_embedding_generation_service(
            "ada",
            AzureTextEmbedding(
                deployment_name=self.open_ai_text_embedding_deployment_name,
                endpoint=self.api_base,
                api_key=self.api_key,
            ),
        )

        self.kernel.register_memory_store(memory_store=connector)

        self.kernel.add_chat_service(
            "dv",
            AzureChatCompletion(
                self.open_ai_gpt_deployment_name, self.api_base, self.api_key
            ),
        )

    async def send_message(self, input, history=None):
        prompt_config = semantic_kernel.PromptTemplateConfig.from_completion_parameters(
            temperature=0, max_tokens=2000, top_p=0.5
        )

        sk_prompt = """
            History: {{$chat_history}}
            Prompt: {{$user_input}}
            """

        prompt_template = semantic_kernel.ChatPromptTemplate(
            sk_prompt, self.kernel.prompt_template_engine, prompt_config
        )

        prompt_template.add_system_message(
            """
            You are an assistant that manages and creates Microsoft Azure resources.
            Your task is to create Azure CLI commands.
            You respond in JSON format with three keys: COMMAND, PROBLEM and EXPLANATION.
            You should ensure all JSON property names should be enclosed with double quotes
            You should not auto-populate command arguments. If you miss information such as parameters that are needed for the command, you should use the PROBLEM key.
            In the EXPLANATION key you should provide a short description what the command does.
            You should only use the COMMAND key if you have all the information and can form a complete and valid Azure CLI command.
            The results should be in JSON format in the structure of:
            'json-start-bracket' "COMMAND": "the Azure CLI commands", "PROBLEM": "asking the user for input", "EXPLANATION": "explaining what the command does"  'json-end-bracket'.
            """  # noqa: E501
        )

        func_config = semantic_kernel.SemanticFunctionConfig(
            prompt_config, prompt_template
        )

        chat_function = self.kernel.register_semantic_function(
            "ChatBot", "Chat", func_config
        )

        history_message = ""
        if history:
            for i in range(len(history[:-1])):
                if i % 2 == 0:
                    q = history[i]
                    a = history[i + 1]
                    history_message += f"\n{q}\n{a}\n"

        context = self.kernel.create_new_context()
        context["chat_history"] = history_message
        context["user_input"] = input

        return await chat_function.invoke_async(context=context)
