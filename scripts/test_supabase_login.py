"""
Test Supabase login directly to diagnose authentication issues
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.supabase_client import get_supabase_client

def test_login():
    """Test direct Supabase login"""
    try:
        supabase = get_supabase_client()

        print("Testing Supabase login...")
        print("Email: admin@agentbi.com")
        print("Password: admin123")

        # Try to sign in
        response = supabase.auth.sign_in_with_password({
            "email": "admin@agentbi.com",
            "password": "admin123"
        })

        if response and response.session and response.session.user:
            print("\nLogin successful!")
            print(f"User ID: {response.session.user.id}")
            print(f"Email: {response.session.user.email}")
            print(f"Email confirmed: {response.session.user.email_confirmed_at}")
            print(f"User metadata: {response.session.user.user_metadata}")
        else:
            print("\nLogin failed: No session or user returned")

    except Exception as e:
        print(f"\nLogin failed with error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_login()
