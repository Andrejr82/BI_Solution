"""
Run database migrations for new tables
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.config.database import async_engine, async_session


async def run_migration():
    """Execute migration to create new tables"""

    print("🔄 Starting database migration...")

    # SQL Server compatible migration
    migration_sql = """
    -- Table: shared_conversations
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'shared_conversations')
    BEGIN
        CREATE TABLE shared_conversations (
            id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
            share_id VARCHAR(32) UNIQUE NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            user_id UNIQUEIDENTIFIER NOT NULL,
            title VARCHAR(255),
            messages NVARCHAR(MAX) NOT NULL,
            is_active BIT DEFAULT 1 NOT NULL,
            expires_at DATETIMEOFFSET,
            view_count INT DEFAULT 0 NOT NULL,
            created_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET() NOT NULL,
            updated_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET() NOT NULL
        );

        CREATE INDEX idx_shared_conversations_share_id ON shared_conversations(share_id);
        CREATE INDEX idx_shared_conversations_session_id ON shared_conversations(session_id);
        CREATE INDEX idx_shared_conversations_user_id ON shared_conversations(user_id);

        PRINT 'Table shared_conversations created successfully';
    END
    ELSE
        PRINT 'Table shared_conversations already exists';

    -- Table: user_preferences
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_preferences')
    BEGIN
        CREATE TABLE user_preferences (
            id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
            user_id UNIQUEIDENTIFIER NOT NULL,
            [key] VARCHAR(100) NOT NULL,
            value NVARCHAR(MAX) NOT NULL,
            context NVARCHAR(MAX),
            created_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET() NOT NULL,
            updated_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET() NOT NULL,
            CONSTRAINT UQ_user_preferences_user_key UNIQUE(user_id, [key])
        );

        CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
        CREATE INDEX idx_user_preferences_key ON user_preferences([key]);

        PRINT 'Table user_preferences created successfully';
    END
    ELSE
        PRINT 'Table user_preferences already exists';
    """

    try:
        async with async_engine.begin() as conn:
            # Split by GO statements and execute each batch
            statements = migration_sql.split(';')

            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    print(f"Executing: {stmt[:50]}...")
                    await conn.execute(text(stmt))

        print("✅ Migration completed successfully!")
        print("\nCreated tables:")
        print("  - shared_conversations")
        print("  - user_preferences")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


async def verify_tables():
    """Verify that tables were created"""

    print("\n🔍 Verifying tables...")

    verify_sql = """
    SELECT
        TABLE_NAME,
        (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = t.TABLE_NAME) as column_count
    FROM INFORMATION_SCHEMA.TABLES t
    WHERE TABLE_NAME IN ('shared_conversations', 'user_preferences')
    """

    try:
        async with async_session() as session:
            result = await session.execute(text(verify_sql))
            tables = result.fetchall()

            if tables:
                print("✅ Tables verified:")
                for table in tables:
                    print(f"  - {table[0]} ({table[1]} columns)")
                return True
            else:
                print("⚠️ No tables found")
                return False

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


async def main():
    """Main migration function"""

    print("=" * 60)
    print("   DATABASE MIGRATION - New Tables")
    print("=" * 60)
    print()

    # Run migration
    success = await run_migration()

    if success:
        # Verify tables
        await verify_tables()
        print("\n🎉 All done! You can now start the server.")
    else:
        print("\n❌ Migration failed. Please check the error above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
