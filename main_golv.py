from golv import GoLVSetup, VMType, CommandSecurityLevel

# ----------------------------------------
# ⚡ CONFIGURATION : pour l'auth sécuriser 
# ----------------------------------------
API_KEY = "eyJhbGciOiJIUzI1NiIsInVzZXJfaWQiOjUsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzY2NzE0NTM0fQ.C8doXu3PsSnzxrD65hcONwTF2Idh9-gV_zYdPXjINUw"

def main():
    print("🚀 Initialisation du SDK GoLV...")
    setup = GoLVSetup(api_key=API_KEY)
    print(f"SDK Setup: {setup}")

    # Création d'une VM de test
    vm_config = setup.create_default_vm("test-vm")
    print(f"VMConfig: {vm_config}")

    client = setup.get_client()

    try:
        vm_data = client.create_vm(vm_config)
        print(f"✅ VM créée: {vm_data}")
    except Exception as e:
        print(f"❌ Erreur création VM: {e}")
        return

    # Création d'un agent sécurisé
    agent = setup.create_agent(
        vm_config=vm_config,
        allowed_commands=["echo", "python", "git"]
    )
    print(f"Agent initialisé: {agent}")

    # Test commande echo
    print("\n💬 Test commande echo")
    result = agent.execute("echo 'Hello GoLV'")
    print(result.output)

    # Test exécution Python
    print("\n💻 Test commande Python")
    python_code = 'print("Hello from Python in VM")'
    result_py = agent.execute_python(python_code)
    print(result_py.output)

    # Test exécution Git (si autorisé)
    if "git" in agent.config.allowed_commands:
        print("\n🌿 Test commande Git")
        result_git = agent.execute_git("status")
        print(result_git.output)
    else:
        print("\n⚠️ Commandes Git non autorisées")

    # Récupérer le statut de la VM
    print("\n📊 Statut VM")
    status = agent.get_status()
    print(status)

if __name__ == "__main__":
    main()
