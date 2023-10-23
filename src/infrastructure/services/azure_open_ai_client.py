import semantic_kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.memory.azure_cognitive_search import (
    AzureCognitiveSearchMemoryStore,
)
from semantic_kernel.connectors.ai.open_ai import (
    AzureTextEmbedding,
)


class AzureOpenAIClient:
    def __init__(
            self,
            api_key,
            api_base,
            open_ai_text_embedding_deployment_name,
            open_ai_gpt_deployment_name,
            search_endpoint,
            search_key
    ):
        self.vector_size = 1536
        self.open_ai_text_embedding_deployment_name = \
            open_ai_text_embedding_deployment_name
        self.open_ai_gpt_deployment_name = open_ai_gpt_deployment_name
        self.kernel = semantic_kernel.Kernel()

        # Configure AI service used by the kernel
        _, api_key, endpoint = semantic_kernel.azure_openai_settings_from_dot_env()

        connector = AzureCognitiveSearchMemoryStore(
            self.vector_size,
            search_endpoint,
            search_key,
        )

        self.kernel.add_text_embedding_generation_service(
            "ada",
            AzureTextEmbedding(
                deployment_name=self.open_ai_text_embedding_deployment_name,
                endpoint=api_base,
                api_key=api_key,
            ),
        )

        self.kernel.register_memory_store(memory_store=connector)

        self.kernel.add_chat_service(
            "dv", AzureChatCompletion(self.open_ai_gpt_deployment_name, endpoint, api_key)
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
            """You are an azure assistant that manages and creates azure resources. \
            Your task is to create azure cli commands. \
            You respond in json format that has three keys: command, problem and explanation. \
            You should not auto-populate command arguments. If you miss information such as parameters that are needed for the command, you should use the problem key. \
            In the explanation key you should provide a small description what the command does. \
            You should only use the command key if you have all the information and can form a complete azure cli command. \
            The results should be in json format in the structure of: \
            'json-start-bracket' "command": "the azure cli commands", "problem": "asking the user for input", "explanation": "explaining what the command does"  'json-end-bracket'.
            Json property names should be enclosed with double quotes"""
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
                    a = history[i+1]
                    history_message += f"\n{q}\n{a}\n"

        context = self.kernel.create_new_context()
        context["chat_history"] = history_message
        context["user_input"] = input
        return await chat_function.invoke_async(context=context)
