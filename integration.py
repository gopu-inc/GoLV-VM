import golv
from golv import GoLVAgent, AgentConfig, VMConfig, CommandSecurityLevel

# Configuration comme vous l'avez décrit
config = AgentConfig(
    api_key="YOUR-API-KEY",
    vm_config=VMConfig(
        vm_id="YOUR-ID-VMS",  # Optionnel, créera une nouvelle si None
        vm_type="ubuntu",
        version="22.04 LTS"
    ),
    timeout=100,
    use_command=True,
    security_level=CommandSecurityLevel.AI,
    max_command_length=500
)

# Créer l'agent
agent = GoLVAgent(config)

# Utilisation par une IA
result = agent.execute("git clone https://github.com/example/repo.git")
print(result.output)

# Exécuter du code Python
code = """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Mean: {np.mean(arr)}")
print(f"Std: {np.std(arr)}")
"""
result = agent.execute_python(code)
print(result.stdout)

# Commande Git
result = agent.execute_git("status")
print(result.stdout)

# Session interactive pour débogage
agent.interactive_session()
