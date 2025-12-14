"""
Supabase Client Configuration
Singleton instance for Supabase authentication and database access
"""

from supabase import create_client, Client
from app.config.settings import get_settings

settings = get_settings()

# Singleton Supabase client
_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance"""
    global _supabase_client

    # Only create client if Supabase auth is enabled
    if not settings.USE_SUPABASE_AUTH:
        raise ValueError(
            "Supabase authentication is disabled. "
            "Set USE_SUPABASE_AUTH=true in .env to enable"
        )

    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            raise ValueError(
                "Supabase credentials not configured. "
                "Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env"
            )

        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )

    return _supabase_client


# Convenience export
supabase = get_supabase_client
