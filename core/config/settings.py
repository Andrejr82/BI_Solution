"""
Arquivo bridge - Redireciona para SafeSettings
ZERO execução durante importação
"""

# Redirecionar todas as importações para SafeSettings
from .safe_settings import get_safe_settings

# Para compatibilidade com imports antigos
def get_settings():
    """Alias para get_safe_settings()"""
    return get_safe_settings()

# NUNCA criar instância na importação!
# settings = None  # Removido para evitar qualquer execução