"""
Test script for new endpoints
Tests Share, Preferences, and Insights endpoints
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, text
from app.config.database import async_session
from app.infrastructure.database.models import SharedConversation, UserPreference


async def test_tables():
    """Test that tables exist and are accessible"""

    print("=" * 60)
    print("   TESTING DATABASE TABLES")
    print("=" * 60)
    print()

    try:
        async with async_session() as session:
            # Test shared_conversations table
            print("[TEST 1] Testing shared_conversations table...")
            result = await session.execute(
                text("SELECT COUNT(*) FROM shared_conversations")
            )
            count = result.scalar()
            print(f"[OK] shared_conversations table accessible (rows: {count})")

            # Test user_preferences table
            print("[TEST 2] Testing user_preferences table...")
            result = await session.execute(
                text("SELECT COUNT(*) FROM user_preferences")
            )
            count = result.scalar()
            print(f"[OK] user_preferences table accessible (rows: {count})")

            print()
            print("[SUCCESS] All table tests passed!")
            return True

    except Exception as e:
        print(f"[ERROR] Table test failed: {e}")
        return False


async def test_models():
    """Test that SQLAlchemy models work"""

    print()
    print("=" * 60)
    print("   TESTING SQLALCHEMY MODELS")
    print("=" * 60)
    print()

    try:
        async with async_session() as session:
            # Test SharedConversation model
            print("[TEST 3] Testing SharedConversation model...")
            result = await session.execute(select(SharedConversation).limit(1))
            print("[OK] SharedConversation model works")

            # Test UserPreference model
            print("[TEST 4] Testing UserPreference model...")
            result = await session.execute(select(UserPreference).limit(1))
            print("[OK] UserPreference model works")

            print()
            print("[SUCCESS] All model tests passed!")
            return True

    except Exception as e:
        print(f"[ERROR] Model test failed: {e}")
        return False


async def test_endpoints_import():
    """Test that endpoint modules can be imported"""

    print()
    print("=" * 60)
    print("   TESTING ENDPOINT IMPORTS")
    print("=" * 60)
    print()

    try:
        print("[TEST 5] Importing shared endpoints...")
        from app.api.v1.endpoints import shared
        print(f"[OK] Shared endpoints imported (router: {shared.router.prefix})")

        print("[TEST 6] Importing preferences endpoints...")
        from app.api.v1.endpoints import preferences
        print(f"[OK] Preferences endpoints imported (router: {preferences.router.prefix})")

        print("[TEST 7] Importing insights endpoints...")
        from app.api.v1.endpoints import insights
        print(f"[OK] Insights endpoints imported (router: {insights.router.prefix})")

        print()
        print("[SUCCESS] All endpoint imports passed!")
        return True

    except Exception as e:
        print(f"[ERROR] Endpoint import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""

    print("\n")
    print("#" * 60)
    print("#  NEW FEATURES - VALIDATION TESTS")
    print("#" * 60)
    print()

    results = []

    # Test 1: Tables
    results.append(await test_tables())

    # Test 2: Models
    results.append(await test_models())

    # Test 3: Endpoints
    results.append(await test_endpoints_import())

    # Summary
    print()
    print("=" * 60)
    print("   TEST SUMMARY")
    print("=" * 60)
    print()

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if all(results):
        print("[SUCCESS] All tests passed! Ready to start the server.")
        print()
        print("Next steps:")
        print("  1. Start server: python run.py")
        print("  2. Go to http://localhost:8000/docs")
        print("  3. Test new endpoints in Swagger UI")
        print()
        return 0
    else:
        print("[FAILURE] Some tests failed. Please fix the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
