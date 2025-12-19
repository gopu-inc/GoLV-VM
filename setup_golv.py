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
