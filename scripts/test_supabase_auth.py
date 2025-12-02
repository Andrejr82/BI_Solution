"""
Script to test Supabase authentication directly
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.supabase_client import get_supabase_client
from app.config.settings import get_settings

async def test_supabase_auth():
    """Test Supabase authentication"""
    settings = get_settings()

    print(f"Testing Supabase Authentication...")
    print(f"URL: {settings.SUPABASE_URL}")
    print(f"Auth Enabled: {settings.USE_SUPABASE_AUTH}")
    print()

    try:
        supabase = get_supabase_client()
        print("[OK] Supabase client created successfully")

        # Test with admin credentials
        email = "admin@agentbi.com"
        password = "Admin@2024"

        print(f"\nTesting login with {email}...")

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                print(f"[OK] Login successful!")
                print(f"User ID: {response.user.id}")
                print(f"Email: {response.user.email}")
                print(f"Created at: {response.user.created_at}")

                # Try to fetch user profile
                try:
                    profile_response = supabase.table("user_profiles").select("*").eq("id", response.user.id).execute()
                    if profile_response.data and len(profile_response.data) > 0:
                        print(f"[OK] User profile found:")
                        print(f"Role: {profile_response.data[0].get('role', 'N/A')}")
                    else:
                        print("[WARN] No user profile found in user_profiles table")
                except Exception as e:
                    print(f"[WARN] Could not fetch user profile: {e}")
            else:
                print("[ERROR] Login failed: No user returned")

        except Exception as e:
            print(f"[ERROR] Login failed: {e}")
            print(f"\nThis is expected if user doesn't exist in Supabase yet.")
            print(f"You need to create the user in Supabase Auth first.")

    except Exception as e:
        print(f"[ERROR] Failed to create Supabase client: {e}")
        return

if __name__ == "__main__":
    asyncio.run(test_supabase_auth())
