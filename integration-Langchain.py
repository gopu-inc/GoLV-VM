import golv
from golv import GoLVAgent, AgentConfig, VMConfig
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.llms import OpenAI

# Créer l'outil GoLV pour LangChain
class GoLVTool:
    def __init__(self, agent: GoLVAgent):
        self.agent = agent
    
    def run(self, command: str) -> str:
        """Exécuter une commande sécurisée"""
        try:
            result = self.agent.execute(command)
            return result.output
        except Exception as e:
            return f"Error: {str(e)}"

# Configuration
golv_config = AgentConfig(
    api_key="your-api-key",
    vm_config=VMConfig(vm_type="python-dev", version="3.11")
)

# Créer l'agent GoLV
golv_agent = GoLVAgent(golv_config)
golv_tool = GoLVTool(golv_agent)

# Intégration avec LangChain
tools = [
    Tool(
        name="Terminal",
        func=golv_tool.run,
        description="Exécuter des commandes terminal sécurisées"
    )
]

llm = OpenAI(temperature=0)
agent = create_react_agent(llm, tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# L'IA peut maintenant utiliser le terminal
response = agent_executor.invoke({
    "input": "Clone le dépôt https://github.com/example/test, "
             "puis liste les fichiers dans le répertoire"
})
print(response["output"])
