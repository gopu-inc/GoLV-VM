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
