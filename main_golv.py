# Fichier : main_golv.py
"""
Exemple complet d'utilisation du SDK GoLV
"""
import golv
import sys
from pathlib import Path

# Configuration automatique
try:
    from golv import GoLVSetup
    from golv import GoLVAgent
    
    def get_golv_agent():
        """Récupérer l'agent GoLV configuré automatiquement"""
        setup = GoLVSetup()
        
        try:
            config = setup.get_agent_config()
            agent = GoLVAgent(config)
            print(f"✅ Agent GoLV chargé - VM: {agent.vm_id[:12]}...")
            return agent
        except FileNotFoundError:
            print("""
❌ Configuration GoLV non trouvée.
   
   Veuillez d'abord exécuter :
   
   python setup_golv.py --register --username VOTRE_NOM --password VOTRE_MOT_DE_PASSE
   
   ou
   
   python setup_golv.py --login --username VOTRE_NOM --password VOTRE_MOT_DE_PASSE
            """)
            sys.exit(1)
    
    # Exemple d'utilisation
    if __name__ == "__main__":
        print("🚀 Initialisation GoLV Agent...")
        
        # Récupérer l'agent configuré
        agent = get_golv_agent()
        
        # Test des commandes
        print("\n🧪 Test des commandes de base...")
        
        # 1. Commande simple
        result = agent.execute("echo 'Hello GoLV!' && pwd")
        print(f"Test 1: {result.stdout}")
        
        # 2. Python
        result = agent.execute_python("print('Python working!'); import sys; print(f'Version: {sys.version}')")
        print(f"Test 2: {result.stdout}")
        
        # 3. Git (si autorisé)
        try:
            result = agent.execute_git("--version")
            print(f"Test 3: Git {result.stdout}")
        except:
            print("Test 3: Git non disponible ou non autorisé")
        
        # 4. Statut de la VM
        status = agent.get_status()
        print(f"\n📊 Statut VM: {status.get('status', {}).get('status', 'unknown')}")
        
        print("\n✅ GoLV est prêt à être utilisé par votre IA!")
        
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    print("Installez d'abord le SDK: pip install -e .")
