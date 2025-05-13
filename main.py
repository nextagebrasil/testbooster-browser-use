import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import Agent

load_dotenv()


async def main():
    llm = ChatOpenAI(model='gpt-4o')
    planner_llm = ChatOpenAI(model='o3-mini')
    agent = Agent(
        task="",
        llm=llm,
        planner_llm=planner_llm,  # Separate model for planning
        use_vision_for_planner=False,  # Disable vision for planner
        planner_interval=4,  # Plan every 4 steps
        # message_context="Additional information about the task",
        use_vision=True,
        # Quando ativado, o modelo processa informações visuais de páginas da web; Para GPT-4o, o processamento de imagem custa aproximadamente 800-1000 tokens (~US$ 0,002) por imagem (mas isso depende do tamanho de tela definido)
        # save_conversation_path="" #Caminho para salvar o histórico completo da conversa. Útil para depuração.
        # override_system_message="" #Substituir completamente o prompt padrão do sistema por um personalizado.
        # extend_system_message="" #Adicione instruções adicionais ao prompt do sistema padrão.
        enable_memory=False,
        # memory_config=MemoryConfig(
        #     agent_id="my_agent",
        #     memory_interval=15,
        #     embedder_provider="openai",
        #     embedder_model="text-embedding-3-large",
        #     embedder_dims=1536,
        # )

    )

    await agent.run()
    agent.browser()
    # Acess Histórico do agente
    # agent.urls()              # List of visited URLs
    # agent.screenshots()       # List of screenshot paths
    # agent.action_names()      # Names of executed actions
    # agent.extracted_content() # Content extracted during execution
    # agent.errors()           # Any errors that occurred
    # agent.model_actions()     # All actions with their parameters


asyncio.run(main())
