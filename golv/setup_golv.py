from typing import Optional
from .client import GoLVClient
from .models import VMConfig, VMType


class GoLVSetup:
    """
    Point d'entrée principal du SDK GoLV.

    Exemple :
        setup = GoLVSetup()
        setup.login("user", "password")
        client = setup.client
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://golv.onrender.com",
    ):
        self.base_url = base_url
        self.api_key = api_key

        # Client API interne
        self.client = GoLVClient(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    # ---------- AUTH ----------

    def login(self, username: str, password: str) -> str:
        """
        Authentifie l'utilisateur et stocke la clé API.
        """
        token = self.client.authenticate(username, password)
        self.api_key = token
        return token

    # ---------- VM HELPERS ----------

    def create_vm_config(
        self,
        name: Optional[str] = None,
        vm_type: VMType = VMType.UBUNTU,
        version: str = "22.04 LTS",
        is_public: bool = False,
    ) -> VMConfig:
        """
        Crée une configuration de VM prête à l'emploi.
        """
        return VMConfig(
            name=name,
            vm_type=vm_type,
            version=version,
            is_public=is_public,
        )

    def create_default_vm(self, name: Optional[str] = None) -> VMConfig:
        """
        Raccourci pour une VM Ubuntu par défaut.
        """
        return self.create_vm_config(name=name)

    # ---------- ACCESS ----------

    def get_client(self) -> GoLVClient:
        """
        Retourne le client API configuré.
        """
        return self.client

    def __repr__(self) -> str:
        auth_state = "authenticated" if self.api_key else "unauthenticated"
        return (
            f"<GoLVSetup base_url={self.base_url!r} "
            f"state={auth_state}>"
        )
