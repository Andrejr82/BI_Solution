"""
Test script for Supabase user creation with segments
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from app.config.settings import get_settings
from app.core.supabase_client import get_supabase_admin_client

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("=" * 60)
    print("1. Testing Supabase Admin Client Connection")
    print("=" * 60)
    
    settings = get_settings()
    print(f"  SUPABASE_URL: {settings.SUPABASE_URL[:30]}...")
    print(f"  SERVICE_ROLE_KEY set: {bool(settings.SUPABASE_SERVICE_ROLE_KEY)}")
    print(f"  USE_SUPABASE_AUTH: {settings.USE_SUPABASE_AUTH}")
    
    try:
        client = get_supabase_admin_client()
        print("  ✅ Admin client created successfully!")
        return client
    except Exception as e:
        print(f"  ❌ Failed to create admin client: {e}")
        return None

def test_list_users(client):
    """Test listing users"""
    print("\n" + "=" * 60)
    print("2. Testing User Listing")
    print("=" * 60)
    
    try:
        # List users from auth
        response = client.auth.admin.list_users()
        users = response
        print(f"  Found {len(users)} users in Supabase Auth")
        
        for user in users[:3]:  # Show first 3
            metadata = user.user_metadata or {}
            segments = metadata.get("allowed_segments", [])
            print(f"    - {user.email}: metadata={metadata}")
            print(f"      allowed_segments: {segments}")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to list users: {e}")
        return False

def test_create_user_with_segments(client):
    """Test creating a user with segments"""
    print("\n" + "=" * 60)
    print("3. Testing User Creation with Segments")
    print("=" * 60)
    
    test_email = "test-segments@example.com"
    test_segments = ["TECIDOS", "ARMARINHOS", "AVIAMENTOS"]
    
    try:
        # First, try to delete if exists
        try:
            existing_users = client.auth.admin.list_users()
            for user in existing_users:
                if user.email == test_email:
                    print(f"  Deleting existing test user: {user.id}")
                    client.auth.admin.delete_user(user.id)
        except:
            pass
        
        # Create user with segments
        print(f"  Creating user with segments: {test_segments}")
        auth_response = client.auth.admin.create_user({
            "email": test_email,
            "password": "TestPassword123!",
            "email_confirm": True,
            "user_metadata": {
                "username": "test-segments",
                "role": "user",
                "full_name": "Test Segments User",
                "allowed_segments": test_segments
            }
        })
        
        if auth_response.user:
            user_id = auth_response.user.id
            print(f"  ✅ User created successfully! ID: {user_id}")
            
            # Verify the metadata was saved
            verify_response = client.auth.admin.get_user_by_id(user_id)
            saved_metadata = verify_response.user.user_metadata or {}
            saved_segments = saved_metadata.get("allowed_segments", [])
            
            print(f"\n  VERIFICATION:")
            print(f"    Saved metadata: {saved_metadata}")
            print(f"    Saved segments: {saved_segments}")
            
            if saved_segments == test_segments:
                print(f"  ✅ Segments saved correctly!")
            else:
                print(f"  ❌ Segments mismatch!")
                print(f"     Expected: {test_segments}")
                print(f"     Got: {saved_segments}")
            
            # Cleanup - delete test user
            print(f"\n  Cleaning up - deleting test user...")
            client.auth.admin.delete_user(user_id)
            print(f"  ✅ Test user deleted")
            
            return True
        else:
            print(f"  ❌ User creation failed - no user returned")
            return False
            
    except Exception as e:
        print(f"  ❌ Failed to create user: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("SUPABASE USER CREATION TEST")
    print("=" * 60)
    
    client = test_supabase_connection()
    if not client:
        print("\n❌ Cannot proceed without admin client")
        return
    
    test_list_users(client)
    test_create_user_with_segments(client)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
