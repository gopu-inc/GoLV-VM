[![Vercel Deployment](https://img.shields.io/badge/deploy-vercel-blue?logo=vercel)](https://vercel.com/mauricio-100s-projects/golvcloud/HUH6zJsuxbyoxNbRkHLFTtjPf8an)
# 🔧 Configuration GoLV Python SDK

Ce guide explique comment configurer et utiliser le SDK GoLV pour Python.

## 📋 Prérequis

- Python 3.8+
- Un compte sur [GoLV Cloud](https://golv.onrender.com)
- Token d'API GoLV

## 🔐 **Étape 1 : Création de compte et récupération du token**

### Option A : Via l'API (recommandé pour l'automatisation)

```python
# Fichier : setup_golv.py
from golv import GoLVClient, VMConfig, AgentConfig, CommandSecurityLevel
import json
import os
from pathlib import Path

class GoLVSetup:
    def __init__(self, config_file="golv_config.json"):
        self.config_file = config_file
        self.config_path = Path.home() / ".golv" / config_file
        self.config_path.parent.mkdir(exist_ok=True)
        
    def register_new_user(self, username: str, password: str, email: str = ""):
        """Enregistrer un nouvel utilisateur"""
        client = GoLVClient()
        
        try:
            # 1. Enregistrement
            response = client.session.post(
                f"{client.base_url}/api/auth/register",
                json={
                    "username": username,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                
                # 2. Sauvegarder la configuration
                config = {
                    "username": username,
                    "api_key": token,
                    "created_at": "datetime.now().isoformat()",
                    "vms": [],
                    "settings": {
                        "default_timeout": 100,
                        "security_level": "ai",
                        "auto_create_vm": True
                    }
                }
                
                self._save_config(config)
                print(f"✅ Compte créé : {username}")
                print(f"🔑 Token API : {token[:20]}...")
                return token
            else:
                print(f"❌ Erreur : {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur d'enregistrement : {e}")
            return None
    
    def login_existing_user(self, username: str, password: str):
        """Connexion avec un compte existant"""
        client = GoLVClient()
        
        try:
            response = client.session.post(
                f"{client.base_url}/api/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                
                # Charger ou créer la config
                if self.config_path.exists():
                    with open(self.config_path, 'r') as f:
                        config = json.load(f)
                else:
                    config = {}
                
                config.update({
                    "username": username,
                    "api_key": token,
                    "last_login": "datetime.now().isoformat()"
                })
                
                self._save_config(config)
                print(f"✅ Connecté : {username}")
                return token
            else:
                print(f"❌ Erreur de connexion : {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur : {e}")
            return None
    
    def create_default_vm(self, token: str, vm_type: str = "python-dev"):
        """Créer une VM par défaut pour l'utilisateur"""
        client = GoLVClient(api_key=token)
        
        try:
            config = VMConfig(
                name=f"{self.get_username()}-default-vm",
                vm_type=vm_type,
                version="3.11" if vm_type == "python-dev" else "22.04 LTS",
                is_public=False,
                tags=["default", "auto-created", vm_type]
            )
            
            vm_data = client.create_vm(config)
            vm_id = vm_data.get("vm_id")
            
            if vm_id:
                # Sauvegarder dans la config
                self._add_vm_to_config(vm_id, {
                    "name": config.name,
                    "type": vm_type,
                    "created_at": "datetime.now().isoformat()",
                    "is_default": True
                })
                
                print(f"✅ VM créée : {vm_id}")
                return vm_id
            else:
                print("❌ Erreur création VM")
                return None
                
        except Exception as e:
            print(f"❌ Erreur : {e}")
            return None
    
    def get_agent_config(self) -> AgentConfig:
        """Récupérer la configuration de l'agent depuis le fichier"""
        if not self.config_path.exists():
            raise FileNotFoundError("Configuration GoLV non trouvée. Exécutez setup_golv.py d'abord.")
        
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Trouver la VM par défaut
        default_vm = next((vm for vm in config.get("vms", []) 
                          if vm.get("is_default", False)), None)
        
        if not default_vm and config.get("vms"):
            default_vm = config["vms"][0]
        
        if not default_vm:
            # Créer une VM si aucune n'existe
            vm_id = self.create_default_vm(config["api_key"])
            default_vm = {"id": vm_id, "name": "default-vm"}
        
        return AgentConfig(
            api_key=config["api_key"],
            vm_config=VMConfig(
                vm_id=default_vm["id"],
                vm_type=default_vm.get("type", "python-dev"),
                version=default_vm.get("version", "3.11"),
                name=default_vm["name"]
            ),
            timeout=config.get("settings", {}).get("default_timeout", 100),
            security_level=CommandSecurityLevel(
                config.get("settings", {}).get("security_level", "ai")
            )
        )
    
    def _save_config(self, config):
        """Sauvegarder la configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _add_vm_to_config(self, vm_id, vm_info):
        """Ajouter une VM à la configuration"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {"vms": []}
        
        vm_info["id"] = vm_id
        config.setdefault("vms", []).append(vm_info)
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_username(self):
        """Récupérer le nom d'utilisateur depuis la config"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get("username", "unknown")
        return "unknown"
```

Option B : Via le script de configuration (CLI)

```bash
# Exécuter le script de configuration
python setup_golv.py --register --username "votre_nom" --password "votre_mot_de_passe"

# Ou pour se connecter
python setup_golv.py --login --username "votre_nom" --password "votre_mot_de_passe"
```

🎯 Étape 2 : Fichier de configuration automatisé

Créez un fichier setup_golv.py :

```python
#!/usr/bin/env python3
"""
Script de configuration automatique pour GoLV
"""

import argparse
import sys
from pathlib import Path

# Ajouter le chemin du SDK
sdk_path = Path(__file__).parent / "golv"
if sdk_path.exists():
    sys.path.insert(0, str(sdk_path.parent))

from golv_setup import GoLVSetup

def main():
    parser = argparse.ArgumentParser(description="Configuration GoLV")
    parser.add_argument("--register", action="store_true", help="Créer un nouveau compte")
    parser.add_argument("--login", action="store_true", help="Se connecter à un compte existant")
    parser.add_argument("--username", required=True, help="Nom d'utilisateur")
    parser.add_argument("--password", required=True, help="Mot de passe")
    parser.add_argument("--email", help="Email (optionnel pour l'inscription)")
    parser.add_argument("--vm-type", default="python-dev", 
                       choices=["python-dev", "ubuntu", "nodejs", "docker-host"],
                       help="Type de VM à créer")
    
    args = parser.parse_args()
    setup = GoLVSetup()
    
    if args.register:
        print("📝 Création d'un nouveau compte GoLV...")
        token = setup.register_new_user(args.username, args.password, args.email)
        
        if token:
            print("🎯 Création de la VM par défaut...")
            vm_id = setup.create_default_vm(token, args.vm_type)
            
            if vm_id:
                print(f"""
✅ Configuration terminée !
   
   Compte    : {args.username}
   VM ID     : {vm_id}
   Type VM   : {args.vm_type}
   Config    : {setup.config_path}
   
   Utilisez : from golv_agent import get_golv_agent
              agent = get_golv_agent()
                """)
    
    elif args.login:
        print("🔐 Connexion au compte GoLV...")
        token = setup.login_existing_user(args.username, args.password)
        
        if token:
            print(f"""
✅ Connexion réussie !
   
   Bienvenue : {args.username}
   Token     : {token[:30]}...
   
   Configuration chargée depuis : {setup.config_path}
                """)

if __name__ == "__main__":
    main()
```

📁 Étape 3 : Fichier principal d'utilisation

```python
# Fichier : main_golv.py
"""
Exemple complet d'utilisation du SDK GoLV
"""

import sys
from pathlib import Path

# Configuration automatique
try:
    from golv_setup import GoLVSetup
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
```

🔄 Étape 4 : Intégration avec votre IA

```python
# Fichier : ia_integration.py
"""
Intégration de GoLV avec une IA
"""

from typing import List, Dict, Any
from main_golv import get_golv_agent

class GoLVForAI:
    """Interface simplifiée pour les IA"""
    
    def __init__(self):
        self.agent = get_golv_agent()
        self.command_history = []
    
    def run_safe_command(self, command: str) -> str:
        """Exécuter une commande sécurisée (pour les IA)"""
        try:
            result = self.agent.execute(command)
            self.command_history.append({
                "command": command,
                "success": result.success,
                "timestamp": "datetime.now().isoformat()"
            })
            
            if result.success:
                return f"✅ Succès:\n{result.stdout}"
            else:
                return f"❌ Erreur:\n{result.stderr}"
                
        except Exception as e:
            return f"⚠️ Exception: {str(e)}"
    
    def run_python_code(self, code: str) -> str:
        """Exécuter du code Python"""
        # Nettoyer le code
        clean_code = code.strip().replace('```python', '').replace('```', '')
        
        try:
            result = self.agent.execute_python(clean_code)
            
            self.command_history.append({
                "type": "python",
                "code_length": len(clean_code),
                "success": result.success
            })
            
            return result.stdout if result.success else f"Erreur Python: {result.stderr}"
            
        except Exception as e:
            return f"Erreur d'exécution Python: {str(e)}"
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Récupérer les informations de l'environnement"""
        commands = [
            ("python3 --version", "python_version"),
            ("which git", "git_path"),
            ("node --version 2>/dev/null || echo 'Not installed'", "node_version"),
            ("ls -la", "directory_listing"),
            ("pwd", "current_directory")
        ]
        
        info = {}
        for cmd, key in commands:
            result = self.agent.execute(cmd)
            info[key] = result.stdout.strip() if result.success else "N/A"
        
        return info
    
    def interactive_mode(self):
        """Mode interactif pour tester"""
        print("🤖 GoLV AI Terminal - Mode interactif")
        print("Tapez 'exit' pour quitter, 'help' pour l'aide")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("AI> ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    print("""
Commandes disponibles:
  python <code>  - Exécuter du code Python
  cmd <commande> - Exécuter une commande shell
  info           - Afficher l'environnement
  history        - Voir l'historique
  clear          - Effacer l'écran
  exit           - Quitter
                    """)
                elif user_input.startswith('python '):
                    code = user_input[7:]
                    print(self.run_python_code(code))
                elif user_input.startswith('cmd '):
                    cmd = user_input[4:]
                    print(self.run_safe_command(cmd))
                elif user_input == 'info':
                    info = self.get_environment_info()
                    for key, value in info.items():
                        print(f"{key}: {value}")
                elif user_input == 'history':
                    for i, hist in enumerate(self.command_history[-5:], 1):
                        print(f"{i}. {hist.get('command', hist.get('type', 'Unknown'))[:50]}...")
                elif user_input == 'clear':
                    print("\033[H\033[J")
                else:
                    print("❌ Commande non reconnue. Tapez 'help' pour l'aide.")
                    
            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break

# Utilisation pour une IA
if __name__ == "__main__":
    # Initialiser GoLV pour l'IA
    ai_terminal = GoLVForAI()
    
    # Mode interactif pour test
    ai_terminal.interactive_mode()
```

📊 Étape 5 : Script de démonstration complet

```python
# Fichier : demo_golv.py
"""
Démonstration complète de GoLV pour les IA
"""

import asyncio
from typing import List
from main_golv import get_golv_agent

class GoLVDemo:
    """Démonstration des capacités de GoLV"""
    
    def __init__(self):
        self.agent = get_golv_agent()
    
    def run_demo_sequence(self):
        """Exécuter une séquence de démonstration"""
        demos = [
            self._demo_basics,
            self._demo_python,
            self._demo_file_operations,
            self._demo_git_operations,
            self._demo_advanced_features
        ]
        
        print("🎬 DÉMONSTRATION GoLV - Terminal pour IA\n")
        
        for i, demo in enumerate(demos, 1):
            print(f"\n{'='*60}")
            print(f"ÉTAPE {i}/{len(demos)}")
            print(f"{'='*60}")
            demo()
    
    def _demo_basics(self):
        """Démonstration des bases"""
        print("🧠 1. Commandes de base")
        
        commands = [
            "echo 'Bonjour depuis GoLV!'",
            "pwd",
            "ls -la",
            "python3 --version",
            "date"
        ]
        
        for cmd in commands:
            result = self.agent.execute(cmd)
            print(f"   {cmd[:30]:<30} → {result.stdout[:50]}...")
    
    def _demo_python(self):
        """Démonstration Python"""
        print("🐍 2. Exécution de code Python")
        
        python_code = """
import numpy as np
import json

# Calculs scientifiques
data = [1, 2, 3, 4, 5]
mean = np.mean(data)
std = np.std(data)

# Structure de données
result = {
    "mean": float(mean),
    "std": float(std),
    "data": data
}

print(json.dumps(result, indent=2))
"""
        
        result = self.agent.execute_python(python_code)
        print("   Code Python exécuté avec succès!")
        print(f"   Résultat:\n{result.stdout}")
    
    def _demo_file_operations(self):
        """Démonstration des opérations fichiers"""
        print("📁 3. Opérations sur les fichiers")
        
        commands = [
            "mkdir -p /tmp/golv_demo",
            "cd /tmp/golv_demo && pwd",
            "echo 'Contenu du fichier' > test.txt",
            "cat test.txt",
            "ls -la | wc -l"
        ]
        
        for cmd in commands:
            result = self.agent.execute(cmd)
            print(f"   {cmd[:40]:<40} → {result.stdout}")
    
    def _demo_git_operations(self):
        """Démonstration Git (si disponible)"""
        print("📚 4. Opérations Git")
        
        try:
            # Vérifier si Git est disponible
            result = self.agent.execute("git --version")
            if result.success:
                print(f"   Git disponible: {result.stdout}")
                
                # Cloner un dépôt de test
                test_repo = "https://github.com/octocat/Hello-World.git"
                print(f"   Clonage du dépôt test...")
                
                clone_result = self.agent.execute(f"git clone {test_repo} /tmp/test_repo 2>/dev/null || true")
                if "Cloning into" in clone_result.stdout or clone_result.success:
                    print("   ✅ Dépôt cloné avec succès")
                    
                    # Lister les fichiers
                    list_result = self.agent.execute("ls -la /tmp/test_repo/ 2>/dev/null || echo 'N/A'")
                    print(f"   Fichiers: {list_result.stdout.split()[0]} items")
                else:
                    print("   ⚠️ Git disponible mais clonage non autorisé")
            else:
                print("   ℹ️ Git non configuré ou non autorisé")
                
        except Exception as e:
            print(f"   ⚠️ Git non disponible: {e}")
    
    def _demo_advanced_features(self):
        """Démonstration des fonctionnalités avancées"""
        print("⚡ 5. Fonctionnalités avancées")
        
        # Commandes pré-définies
        print("   Commandes pré-définies:")
        predefined = ["status", "python_test", "disk_usage"]
        
        for cmd in predefined:
            result = self.agent.predefined(cmd)
            print(f"     {cmd:<15} → {result.stdout[:40]}...")
        
        # Statut de la VM
        print("\n   📊 Statut complet de la VM:")
        status = self.agent.get_status()
        if "status" in status:
            vm_status = status["status"]
            print(f"     Existe: {vm_status.get('exists', 'N/A')}")
            print(f"     Status: {vm_status.get('status', 'N/A')}")
            print(f"     Taille: {vm_status.get('size_human', 'N/A')}")
    
    def generate_usage_example(self):
        """Générer un exemple d'utilisation pour l'IA"""
        print("\n📋 EXEMPLE D'UTILISATION POUR IA:")
        
        example = '''
from golv_integration import GoLVForAI

# Initialiser
golv = GoLVForAI()

# 1. Exécuter du code Python
result = golv.run_python_code("""
import requests
import json

# Faire une requête API
response = requests.get('https://api.github.com')
data = response.json()

print(f"Status: {response.status_code}")
print(f"Rate limit: {data.get('rate', {}).get('limit', 'N/A')}")
""")

print(result)

# 2. Exécuter une commande shell
output = golv.run_safe_command("""
git clone https://github.com/example/repo.git
cd repo
ls -la
""")

print(output)

# 3. Obtenir des informations
info = golv.get_environment_info()
print(f"Python: {info['python_version']}")
print(f"Répertoire: {info['current_directory']}")
'''
        
        print(example)

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE DE LA DÉMONSTRATION GoLV")
    print("=" * 60)
    
    try:
        demo = GoLVDemo()
        demo.run_demo_sequence()
        demo.generate_usage_example()
        
        print("\n" + "=" * 60)
        print("✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)
        print("\n🎯 GoLV est maintenant prêt pour votre IA!")
        print("   Utilisez: from golv_integration import GoLVForAI")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\nAssurez-vous d'avoir:")
        print("1. Exécuté: python setup_golv.py --register --username ...")
        print("2. Votre serveur GoLV est accessible")

if __name__ == "__main__":
    main()
```

🎯 Résumé des fichiers à créer

1. CONFIGURATION.md - Documentation complète
2. golv_setup.py - Classe de configuration
3. setup_golv.py - Script CLI pour configurer
4. main_golv.py - Point d'entrée principal
5. golv_integration.py - Interface pour IA
6. demo_golv.py - Démonstration complète

📦 Installation en une commande

```bash
# Télécharger et installer
curl -L https://raw.githubusercontent.com/gopu-inc/GoLV-VM/main/install.sh | bash

# Ou manuellement
git clone https://github.com/gopu-inc/GoLV-VM.git
cd GoLV-VM/python-sdk
pip install -e .
python setup_golv.py --register --username "votre_nom" --password "votre_mdp"
python demo_golv.py
```

🏁 Premiers pas rapides

```python
# Après installation
from golv_integration import GoLVForAI

# Initialiser
ai_terminal = GoLVForAI()

# Utiliser
result = ai_terminal.run_python_code("print('Hello AI World!')")
print(result)
```

Votre IA a maintenant accès à un terminal sécurisé! 🎉

```

## 📄 **2. Fichier `setup_golv.py`** (script de configuration CLI)

```python
#!/usr/bin/env python3
"""
Script de configuration automatique pour GoLV
Enregistrement, connexion et création de VM automatique
"""

import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# -------------------------------------------------------------------
# Configuration des chemins
# -------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".golv"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_FILE = CONFIG_DIR / "token.txt"
VM_FILE = CONFIG_DIR / "vms.json"

# Créer le dossier de configuration
CONFIG_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------------
# Constantes API
# -------------------------------------------------------------------

API_BASE_URL = "https://golv.onrender.com"
DEFAULT_VM_TYPE = "python-dev"
DEFAULT_VM_VERSION = "3.11"

# -------------------------------------------------------------------
# Classes de configuration
# -------------------------------------------------------------------

class GoLVConfig:
    """Gestionnaire de configuration GoLV"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charger la configuration depuis le fichier"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._create_default_config()
        return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Créer une configuration par défaut"""
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "users": {},
            "current_user": None,
            "vms": {},
            "settings": {
                "auto_create_vm": True,
                "default_timeout": 100,
                "security_level": "ai"
            }
        }
    
    def save(self):
        """Sauvegarder la configuration"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def register_user(self, username: str, password: str, email: str = "") -> Optional[str]:
        """Enregistrer un nouvel utilisateur via l'API"""
        import requests
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/register",
                json={
                    "username": username,
                    "password": password
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                
                # Sauvegarder l'utilisateur
                self.config["users"][username] = {
                    "username": username,
                    "email": email,
                    "registered_at": datetime.now().isoformat(),
                    "token": token,
                    "role": data.get("role", "user"),
                    "user_id": data.get("user_id")
                }
                
                # Définir comme utilisateur courant
                self.config["current_user"] = username
                
                # Sauvegarder le token séparément
                self._save_token(token)
                
                self.save()
                return token
            else:
                print(f"❌ Erreur d'enregistrement: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur API: {e}")
            return None
    
    def login_user(self, username: str, password: str) -> Optional[str]:
        """Connecter un utilisateur existant"""
        import requests
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                
                # Mettre à jour ou créer l'utilisateur
                if username not in self.config["users"]:
                    self.config["users"][username] = {}
                
                self.config["users"][username].update({
                    "username": username,
                    "last_login": datetime.now().isoformat(),
                    "token": token,
                    "user_id": data.get("user_id")
                })
                
                # Définir comme utilisateur courant
                self.config["current_user"] = username
                
                # Sauvegarder le token
                self._save_token(token)
                
                self.save()
                return token
            else:
                print(f"❌ Erreur de connexion: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur API: {e}")
            return None
    
    def _save_token(self, token: str):
        """Sauvegarder le token dans un fichier séparé"""
        with open(TOKEN_FILE, 'w') as f:
            f.write(token)
    
    def get_current_token(self) -> Optional[str]:
        """Récupérer le token de l'utilisateur courant"""
        current_user = self.config.get("current_user")
        if current_user and current_user in self.config["users"]:
            return self.config["users"][current_user].get("token")
        return None
    
    def get_current_username(self) -> Optional[str]:
        """Récupérer le nom d'utilisateur courant"""
        return self.config.get("current_user")
    
    def create_vm(self, vm_type: str = None, version: str = None) -> Optional[str]:
        """Créer une nouvelle VM pour l'utilisateur courant"""
        import requests
        
        token = self.get_current_token()
        if not token:
            print("❌ Aucun utilisateur connecté")
            return None
        
        vm_type = vm_type or DEFAULT_VM_TYPE
        version = version or DEFAULT_VM_VERSION
        
        # Générer un nom de VM
        username = self.get_current_username()
        vm_name = f"{username}-{vm_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/vms",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": vm_name,
                    "vm_type": vm_type,
                    "version": version,
                    "is_public": False,
                    "tags": ["auto-created", vm_type]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                vm_id = data.get("vm_id")
                
                if vm_id:
                    # Sauvegarder la VM
                    if "vms" not in self.config:
                        self.config["vms"] = {}
                    
                    self.config["vms"][vm_id] = {
                        "id": vm_id,
                        "name": vm_name,
                        "type": vm_type,
                        "version": version,
                        "owner": username,
                        "created_at": datetime.now().isoformat(),
                        "is_default": True
                    }
                    
                    # Marquer comme VM par défaut
                    self._set_default_vm(vm_id)
                    
                    self.save()
                    return vm_id
                else:
                    print("❌ Erreur: Pas d'ID VM retourné")
                    return None
            else:
                print(f"❌ Erreur création VM: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur API: {e}")
            return None
    
    def _set_default_vm(self, vm_id: str):
        """Définir une VM comme par défaut"""
        # Enlever le flag par défaut des autres VMs
        for vm in self.config.get("vms", {}).values():
            vm["is_default"] = False
        
        # Marquer la nouvelle VM comme par défaut
        if vm_id in self.config.get("vms", {}):
            self.config["vms"][vm_id]["is_default"] = True
    
    def get_default_vm(self) -> Optional[Dict[str, Any]]:
        """Récupérer la VM par défaut"""
        vms = self.config.get("vms", {})
        for vm in vms.values():
            if vm.get("is_default", False):
                return vm
        
        # Si aucune VM par défaut, prendre la première
        if vms:
            first_vm_id = list(vms.keys())[0]
            return vms[first_vm_id]
        
        return None
    
    def get_config_for_agent(self) -> Dict[str, Any]:
        """Récupérer la configuration pour l'agent"""
        token = self.get_current_token()
        vm = self.get_default_vm()
        
        if not token:
            raise ValueError("Aucun utilisateur connecté. Exécutez d'abord le setup.")
        
        if not vm:
            print("⚠️ Aucune VM trouvée, création d'une VM par défaut...")
            vm_id = self.create_vm()
            if vm_id:
                vm = self.config["vms"][vm_id]
            else:
                raise ValueError("Impossible de créer une VM")
        
        return {
            "api_key": token,
            "vm_config": {
                "vm_id": vm["id"],
                "vm_type": vm["type"],
                "version": vm["version"],
                "name": vm["name"]
            },
            "timeout": self.config["settings"]["default_timeout"],
            "security_level": self.config["settings"]["security_level"]
        }

# -------------------------------------------------------------------
# Fonctions utilitaires
# -------------------------------------------------------------------

def print_banner():
    """Afficher la bannière"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                  🚀 GoLV Configuration                ║
    ║        Terminal sécurisé pour les Intelligences       ║
    ║                    Artificielles                      ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)

def print_success(message: str):
    """Afficher un message de succès"""
    print(f"✅ {message}")

def print_error(message: str):
    """Afficher un message d'erreur"""
    print(f"❌ {message}")

def print_info(message: str):
    """Afficher un message d'information"""
    print(f"ℹ️  {message}")

# -------------------------------------------------------------------
# Fonctions principales
# -------------------------------------------------------------------

def register_user(args):
    """Enregistrer un nouvel utilisateur"""
    print_banner()
    print("📝 Création d'un nouveau compte GoLV")
    print("=" * 50)
    
    config = GoLVConfig()
    
    # Vérifier si l'utilisateur existe déjà
    if args.username in config.config["users"]:
        print_error(f"L'utilisateur '{args.username}' existe déjà.")
        print_info("Utilisez --login pour vous connecter.")
        return False
    
    # Enregistrer l'utilisateur
    print(f"Enregistrement de: {args.username}")
    token = config.register_user(args.username, args.password, args.email)
    
    if not token:
        print_error("Échec de l'enregistrement")
        return False
    
    print_success(f"Compte '{args.username}' créé avec succès!")
    print(f"   Token: {token[:30]}...")
    
    # Créer une VM par défaut si demandé
    if args.create_vm:
        print("\n🎯 Création de la VM par défaut...")
        vm_id = config.create_vm(args.vm_type, args.vm_version)
        
        if vm_id:
            print_success(f"VM créée: {vm_id}")
            print(f"   Type: {args.vm_type}")
            print(f"   Version: {args.vm_version}")
        else:
            print_error("Échec de la création de la VM")
    
    print("\n📍 Configuration sauvegardée dans:")
    print(f"   {CONFIG_FILE}")
    print(f"   {TOKEN_FILE}")
    
    print("\n🎉 Configuration terminée!")
    print("Vous pouvez maintenant utiliser GoLV avec:")
    print("   from golv_agent import get_golv_agent")
    print("   agent = get_golv_agent()")
    
    return True

def login_user(args):
    """Connecter un utilisateur existant"""
    print_banner()
    print("🔐 Connexion à GoLV")
    print("=" * 50)
    
    config = GoLVConfig()
    
    print(f"Connexion de: {args.username}")
    token = config.login_user(args.username, args.password)
    
    if not token:
        print_error("Échec de la connexion")
        return False
    
    print_success(f"Connecté en tant que: {args.username}")
    print(f"   Token: {token[:30]}...")
    
    # Vérifier les VMs existantes
    vm = config.get_default_vm()
    if vm:
        print(f"\n🎯 VM par défaut trouvée:")
        print(f"   ID: {vm['id']}")
        print(f"   Nom: {vm['name']}")
        print(f"   Type: {vm['type']}")
    else:
        print("\n⚠️  Aucune VM trouvée")
        if args.create_vm:
            print("Création d'une VM par défaut...")
            vm_id = config.create_vm(args.vm_type, args.vm_version)
            if vm_id:
                print_success(f"VM créée: {vm_id}")
    
    print(f"\n📍 Configuration chargée depuis:")
    print(f"   {CONFIG_FILE}")
    
    return True

def show_status(args):
    """Afficher le statut actuel"""
    print_banner()
    print("📊 Statut GoLV")
    print("=" * 50)
    
    config = GoLVConfig()
    
    current_user = config.get_current_username()
    if current_user:
        user_data = config.config["users"][current_user]
        print(f"👤 Utilisateur courant: {current_user}")
        print(f"   ID: {user_data.get('user_id', 'N/A')}")
        print(f"   Rôle: {user_data.get('role', 'N/A')}")
        print(f"   Dernière connexion: {user_data.get('last_login', 'N/A')}")
    else:
        print("👤 Aucun utilisateur connecté")
    
    # Afficher les VMs
    vms = config.config.get("vms", {})
    if vms:
        print(f"\n🎯 VMs ({len(vms)}):")
        for vm_id, vm_data in vms.items():
            default = "⭐" if vm_data.get("is_default") else "  "
            print(f"   {default} {vm_data['name']} ({vm_id[:12]}...)")
            print(f"      Type: {vm_data['type']} {vm_data['version']}")
    else:
        print("\n🎯 Aucune VM configurée")
    
    # Fichiers de configuration
    print(f"\n📁 Fichiers de configuration:")
    print(f"   Config: {CONFIG_FILE} {'✅' if CONFIG_FILE.exists() else '❌'}")
    print(f"   Token: {TOKEN_FILE} {'✅' if TOKEN_FILE.exists() else '❌'}")
    
    print(f"\n📍 Utilisez:")
    print(f"   python {sys.argv[0]} --help pour les options")

def create_vm(args):
    """Créer une nouvelle VM"""
    config = GoLVConfig()
    
    if not config.get_current_token():
        print_error("Vous devez d'abord vous connecter ou vous enregistrer")
        return False
    
    print(f"🎯 Création d'une nouvelle VM...")
    print(f"   Type: {args.vm_type}")
    print(f"   Version: {args.vm_version}")
    
    vm_id = config.create_vm(args.vm_type, args.vm_version)
    
    if vm_id:
        print_success(f"VM créée avec succès!")
        print(f"   ID: {vm_id}")
        print(f"   Nom: {config.config['vms'][vm_id]['name']}")
        return True
    else:
        print_error("Échec de la création de la VM")
        return False

# -------------------------------------------------------------------
# Point d'entrée principal
# -------------------------------------------------------------------

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Configuration GoLV - Terminal sécurisé pour IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s --register --username alice --password secret123
  %(prog)s --login --username alice --password secret123
  %(prog)s --status
  %(prog)s --create-vm --vm-type python-dev --vm-version 3.11
        """
    )
    
    # Groupes d'actions mutuellement exclusives
    action_group = parser.add_mutually_exclusive_group(required=True)
    
    action_group.add_argument(
        "--register",
        action="store_true",
        help="Créer un nouveau compte GoLV"
    )
    
    action_group.add_argument(
        "--login",
        action="store_true",
        help="Se connecter à un compte existant"
    )
    
    action_group.add_argument(
        "--status",
        action="store_true",
        help="Afficher le statut actuel"
    )
    
    action_group.add_argument(
        "--create-vm",
        action="store_true",
        help="Créer une nouvelle VM"
    )
    
    # Arguments pour l'enregistrement/connexion
    parser.add_argument(
        "--username",
        help="Nom d'utilisateur"
    )
    
    parser.add_argument(
        "--password",
        help="Mot de passe"
    )
    
    parser.add_argument(
        "--email",
        default="",
        help="Email (optionnel pour l'inscription)"
    )
    
    parser.add_argument(
        "--create-vm-auto",
        dest="create_vm",
        action="store_true",
        default=True,
        help="Créer automatiquement une VM (défaut: True)"
    )
    
    parser.add_argument(
        "--no-create-vm",
        dest="create_vm",
        action="store_false",
        help="Ne pas créer de VM automatiquement"
    )
    
    # Arguments pour la VM
    parser.add_argument(
        "--vm-type",
        default=DEFAULT_VM_TYPE,
        choices=["python-dev", "ubuntu", "nodejs", "docker-host", "debian", "wordpress"],
        help=f"Type de VM (défaut: {DEFAULT_VM_TYPE})"
    )
    
    parser.add_argument(
        "--vm-version",
        help="Version de la VM (défaut selon le type)"
    )
    
    args = parser.parse_args()
    
    try:
        # Valider les arguments
        if (args.register or args.login) and not (args.username and args.password):
            parser.error("--username et --password sont requis pour --register ou --login")
        
        if args.create_vm and not (args.register or args.login or args.status):
            parser.error("--create-vm nécessite d'être connecté. Utilisez --login d'abord.")
        
        # Exécuter l'action demandée
        if args.register:
            success = register_user(args)
        elif args.login:
            success = login_user(args)
        elif args.status:
            show_status(args)
            success = True
        elif args.create_vm:
            success = create_vm(args)
        else:
            parser.print_help()
            success = False
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Opération interrompue")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        if args.register or args.login:
            print_info("Vérifiez que votre serveur GoLV est accessible à:")
            print_info(f"   {API_BASE_URL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

📄 3. Fichier golv_agent.py (agent pré-configuré)

```python
#!/usr/bin/env python3
"""
Agent GoLV pré-configuré - Récupère automatiquement la configuration
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".golv"
CONFIG_FILE = CONFIG_DIR / "config.json"

# -------------------------------------------------------------------
# Import dynamique du SDK GoLV
# -------------------------------------------------------------------

def import_golv_sdk():
    """Importer le SDK GoLV de manière dynamique"""
    try:
        # Essayer d'importer depuis le package installé
        from golv import GoLVAgent, AgentConfig, VMConfig, CommandSecurityLevel
        return GoLVAgent, AgentConfig, VMConfig, CommandSecurityLevel
    except ImportError:
        # Essayer d'importer depuis le répertoire courant
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from golv import GoLVAgent, AgentConfig, VMConfig, CommandSecurityLevel
            return GoLVAgent, AgentConfig, VMConfig, CommandSecurityLevel
        except ImportError as e:
            print(f"❌ Impossible d'importer le SDK GoLV: {e}")
            print("\n📦 Installez le SDK GoLV avec:")
            print("   pip install golv-py")
            print("\n🔧 Ou depuis le code source:")
            print("   git clone https://github.com/gopu-inc/GoLV-VM.git")
            print("   cd GoLV-VM/python-sdk")
            print("   pip install -e .")
            sys.exit(1)

# -------------------------------------------------------------------
# Gestionnaire de configuration
# -------------------------------------------------------------------

class GoLVConfigManager:
    """Gère la configuration GoLV"""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        
    def load_config(self) -> Dict[str, Any]:
        """Charger la configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration GoLV non trouvée: {self.config_file}\n"
                "Exécutez d'abord: python setup_golv.py --register --username ..."
            )
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Récupérer la configuration pour l'agent"""
        config = self.load_config()
        
        # Vérifier l'utilisateur courant
        current_user = config.get("current_user")
        if not current_user:
            raise ValueError(
                "Aucun utilisateur connecté.\n"
                "Exécutez: python setup_golv.py --login --username ..."
            )
        
        user_data = config["users"][current_user]
        token = user_data.get("token")
        
        if not token:
            raise ValueError("Token d'API non trouvé dans la configuration")
        
        # Trouver la VM par défaut
        vms = config.get("vms", {})
        default_vm = None
        
        for vm_id, vm_data in vms.items():
            if vm_data.get("is_default", False) or vm_data.get("owner") == current_user:
                default_vm = vm_data
                break
        
        if not default_vm and vms:
            # Prendre la première VM disponible
            first_vm_id = list(vms.keys())[0]
            default_vm = vms[first_vm_id]
        
        if not default_vm:
            raise ValueError(
                "Aucune VM configurée.\n"
                "Créez une VM avec: python setup_golv.py --create-vm"
            )
        
        return {
            "api_key": token,
            "vm_config": {
                "vm_id": default_vm["id"],
                "vm_type": default_vm["type"],
                "version": default_vm.get("version", "3.11"),
                "name": default_vm["name"]
            },
            "timeout": config.get("settings", {}).get("default_timeout", 100),
            "security_level": config.get("settings", {}).get("security_level", "ai"),
            "use_command": True,
            "max_command_length": 500
        }

# -------------------------------------------------------------------
# Fonction principale pour récupérer l'agent
# -------------------------------------------------------------------

def get_golv_agent() -> GoLVAgent:
    """
    Récupérer un agent GoLV pré-configuré
    
    Returns:
        GoLVAgent: Agent configuré et prêt à l'emploi
        
    Raises:
        ValueError: Si la configuration est manquante
        ImportError: Si le SDK n'est pas installé
    """
    # Importer le SDK
    GoLVAgent, AgentConfig, VMConfig, CommandSecurityLevel = import_golv_sdk()
    
    # Charger la configuration
    config_manager = GoLVConfigManager()
    config_data = config_manager.get_agent_config()
    
    # Créer la configuration de l'agent
    vm_config = VMConfig(
        vm_id=config_data["vm_config"]["vm_id"],
        vm_type=config_data["vm_config"]["vm_type"],
        version=config_data["vm_config"]["version"],
        name=config_data["vm_config"]["name"]
    )
    
    agent_config = AgentConfig(
        api_key=config_data["api_key"],
        vm_config=vm_config,
        timeout=config_data["timeout"],
        security_level=CommandSecurityLevel(config_data["security_level"]),
        use_command=config_data["use_command"],
        max_command_length=config_data["max_command_length"]
    )
    
    # Créer et retourner l'agent
    agent = GoLVAgent(agent_config)
    print(f"✅ Agent GoLV initialisé")
    print(f"   VM: {agent.vm_id}")
    print(f"   Type: {vm_config.vm_type.value} {vm_config.version}")
    print(f"   Sécurité: {agent_config.security_level.value}")
    
    return agent

def get_golv_client():
    """
    Récupérer un client GoLV simple (pour usage avancé)
    
    Returns:
        GoLVClient: Client API GoLV
    """
    from golv import GoLVClient
    
    config_manager = GoLVConfigManager()
    config_data = config_manager.get_agent_config()
    
    client = GoLVClient(api_key=config_data["api_key"])
    return client

# -------------------------------------------------------------------
# Fonction de test
# -------------------------------------------------------------------

def test_agent():
    """Tester l'agent GoLV"""
    try:
        agent = get_golv_agent()
        
        print("\n🧪 Test des fonctionnalités de base...")
        
        # Test 1: Commande simple
        print("1. Test de commande simple...")
        result = agent.execute("echo 'GoLV Agent Test' && pwd")
        print(f"   ✅ {result.stdout}")
        
        # Test 2: Python
        print("2. Test Python...")
        result = agent.execute_python("print('Python fonctionnel'); import sys; print(f'Version: {sys.version[:20]}')")
        print(f"   ✅ {result.stdout}")
        
        # Test 3: Statut
        print("3. Vérification du statut...")
        status = agent.get_status()
        if status.get("success"):
            print(f"   ✅ VM en ligne: {status.get('vm_id')}")
        else:
            print(f"   ❌ Erreur statut: {status}")
        
        print("\n🎉 Agent GoLV fonctionnel et prêt!")
        print("\n📖 Utilisation:")
        print("   from golv_agent import get_golv_agent")
        print("   agent = get_golv_agent()")
        print("   result = agent.execute('votre_commande')")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        print("\n🔧 Vérifiez votre configuration avec:")
        print("   python setup_golv.py --status")
        return False

# -------------------------------------------------------------------
# Interface en ligne de commande
# -------------------------------------------------------------------

def interactive_shell():
    """Lancer un shell interactif avec l'agent GoLV"""
    try:
        agent = get_golv_agent()
        
        print("\n" + "="*60)
        print("🤖 GoLV Interactive Shell")
        print(f"VM: {agent.vm_id[:12]}... | Type: {agent.config.vm_config.vm_type.value}")
        print("Tapez 'exit' pour quitter, 'help' pour l'aide")
        print("="*60)
        
        while True:
            try:
                command = input(f"\ngolv:{agent.vm_id[:8]}$ ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 Au revoir!")
                    break
                
                if command.lower() == 'help':
                    print("""
Commandes disponibles:
  <commande>      - Exécuter une commande shell
  python <code>   - Exécuter du code Python
  status          - Afficher le statut de la VM
  predefined      - Liste des commandes pré-définies
  clear           - Effacer l'écran
  exit            - Quitter
                    """)
                    continue
                
                if command.lower() == 'status':
                    status = agent.get_status()
                    print(json.dumps(status, indent=2))
                    continue
                
                if command.lower() == 'predefined':
                    print("Commandes pré-définies: status, python_test, disk_usage, list_py_files, create_test_file, network_info")
                    continue
                
                if command.lower() == 'clear':
                    print("\033[H\033[J")
                    continue
                
                if command.startswith('python '):
                    code = command[7:]
                    result = agent.execute_python(code)
                else:
                    result = agent.execute(command)
                
                if result.success:
                    print(f"✅ [{result.duration_ms}ms]")
                    if result.stdout:
                        print(result.stdout)
                else:
                    print(f"❌ [{result.duration_ms}ms] Code: {result.return_code}")
                    if result.stderr:
                        print(result.stderr)
                
            except KeyboardInterrupt:
                print("\n\n⏹️  Interrompu")
                break
            except Exception as e:
                print(f"⚠️  Erreur: {e}")
                
    except Exception as e:
        print(f"❌ Impossible de démarrer le shell: {e}")

# -------------------------------------------------------------------
# Point d'entrée
# -------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent GoLV pré-configuré")
    parser.add_argument("--test", action="store_true", help="Tester l'agent")
    parser.add_argument("--shell", action="store_true", help="Lancer le shell interactif")
    parser.add_argument("--command", help="Exécuter une commande unique")
    
    args = parser.parse_args()
    
    if args.test:
        test_agent()
    elif args.shell:
        interactive_shell()
    elif args.command:
        try:
            agent = get_golv_agent()
            result = agent.execute(args.command)
            
            if result.success:
                print(f"✅ Succès [{result.duration_ms}ms]:")
                print(result.stdout)
            else:
                print(f"❌ Échec [{result.duration_ms}ms]:")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    else:
        parser.print_help()
        print("\n📖 Exemples:")
        print("  python golv_agent.py --test")
        print("  python golv_agent.py --shell")
        print("  python golv_agent.py --command 'echo Hello'")
```

📦 4. Fichier requirements.txt

```txt
# GoLV Python SDK - Dépendances principales
requests>=2.28.0
pydantic>=2.0.0
python-dotenv>=1.0.0
colorama>=0.4.6
pyyaml>=6.0

# Dépendances optionnelles pour IA
openai>=1.0.0
langchain>=0.0.300
numpy>=1.24.0
pandas>=2.0.0

# Développement
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
```

🎯 5. Fichier INSTALL.md

```markdown
# 🚀 Installation de GoLV Python SDK

## Méthode 1 : Installation rapide (recommandée)

```bash
# 1. Installer le package
pip install golv-py

# 2. Configurer votre compte
python -m golv.setup --register --username "votre_nom" --password "votre_mdp"

# 3. Tester l'installation
python -m golv.agent --test
```

Méthode 2 : Depuis les sources

```bash
# 1. Cloner le dépôt
git clone https://github.com/gopu-inc/GoLV-VM.git
cd GoLV-VM/python-sdk

# 2. Installer en mode développement
pip install -e .

# 3. Configurer
python setup_golv.py --register --username "votre_nom" --password "votre_mdp"

# 4. Lancer la démo
python demo_golv.py
```

📁 Structure des fichiers après installation

```
~/.golv/
├── config.json          # Configuration principale
├── token.txt           # Token d'API
└── vms.json           # Liste des VMs
```

🔧 Configuration manuelle

Si vous préférez configurer manuellement :

```python
# Créer le fichier ~/.golv/config.json
{
    "version": "1.0.0",
    "current_user": "votre_nom",
    "users": {
        "votre_nom": {
            "username": "votre_nom",
            "token": "VOTRE_TOKEN_API",
            "user_id": 1
        }
    },
    "vms": {
        "golv_abc123": {
            "id": "golv_abc123",
            "name": "votre-vm",
            "type": "python-dev",
            "version": "3.11",
            "is_default": true
        }
    },
    "settings": {
        "default_timeout": 100,
        "security_level": "ai"
    }
}
```

🎯 Premier test

```python
# test_golv.py
from golv_agent import get_golv_agent

agent = get_golv_agent()
result = agent.execute("echo 'Hello GoLV!'")
print(result.stdout)
```

Exécutez :

```bash
python test_golv.py
```

❓ Dépannage

"Configuration non trouvée"

```bash
python setup_golv.py --register --username "nom" --password "mdp"
```

"Impossible de se connecter au serveur"

Vérifiez que votre serveur GoLV est en ligne :

```bash
curl https://golv.onrender.com
```

"Module golv non trouvé"

```bash
pip install -e .
# ou
pip install golv-py
```

📚 Documentation

· API Reference
· Exemples complets
· Guide de sécurité

🤝 Support

· Issues GitHub : https://github.com/gopu-inc/GoLV-VM/issues
· Email : support@golv.io
· Discord : Lien Discord

```

## 🏁 **Résumé des fichiers à créer**

1. **`CONFIGURATION.md`** - Documentation complète
2. **`setup_golv.py`** - Script de configuration CLI (avec registre/login)
3. **`golv_agent.py`** - Agent pré-configuré qui charge automatiquement token et VM
4. **`requirements.txt`** - Dépendances
5. **`INSTALL.md`** - Guide d'installation

## 🚀 **Utilisation finale**

Après avoir créé tous ces fichiers :

```bash
# 1. Installation
pip install -e .

# 2. Configuration (enregistrement automatique)
python setup_golv.py --register --username "votre_nom" --password "votre_mdp"

# 3. Utilisation dans votre code
from golv_agent import get_golv_agent

# L'agent charge automatiquement token et VM configurés
agent = get_golv_agent()

# Utilisation
result = agent.execute("python3 --version")
print(result.stdout)
```

