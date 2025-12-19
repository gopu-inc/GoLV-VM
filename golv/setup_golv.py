from typing import Optional
from .client import GoLVClient
from .models import VMConfig, VMType


class GoLVSetup:
    """
    Classe d'initialisation et de configuration du SDK GoLV.
    Sert de point d'entrée simple pour les utilisateurs.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://golv-app.onrender.com",
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        self.client = GoLVClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def create_default_vm(self, name: Optional[str] = None) -> VMConfig:
        """
        Crée une configuration de VM par défaut (Ubuntu).
        """
        return VMConfig(
            name=name,
            vm_type=VMType.UBUNTU,
        )

    def connect(self) -> GoLVClient:
        """
        Retourne le client prêt à être utilisé.
        """
        return self.client

    def __repr__(self) -> str:
        return (
            f"<GoLVSetup base_url={self.base_url!r} "
            f"timeout={self.timeout}s>"
        )
