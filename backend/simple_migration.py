"""
Simple migration script - creates tables directly via SQL
"""
import pyodbc
import sys
from pathlib import Path

# Connection string from .env
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=FAMILIA\\SQLJR,1433;"
    "DATABASE=Projeto_Caculinha;"
    "UID=AgenteVirtual;"
    "PWD=Cacula@2020;"
    "TrustServerCertificate=yes;"
)

def create_tables():
    """Create new tables"""

    print("=" * 60)
    print("   DATABASE MIGRATION - Creating New Tables")
    print("=" * 60)
    print()

    try:
        # Connect to database
        print("[*] Connecting to SQL Server...")
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        print("[OK] Connected!")
        print()

        # Create shared_conversations table
        print("[*] Creating table: shared_conversations...")

        create_shared_sql = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'shared_conversations')
        BEGIN
            CREATE TABLE shared_conversations (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                share_id VARCHAR(32) NOT NULL,
                session_id VARCHAR(255) NOT NULL,
                user_id UNIQUEIDENTIFIER NOT NULL,
                title VARCHAR(255),
                messages NVARCHAR(MAX) NOT NULL,
                is_active BIT DEFAULT 1 NOT NULL,
                expires_at DATETIMEOFFSET,
                view_count INT DEFAULT 0 NOT NULL,
                created_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET() NOT NULL,
                updated_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET() NOT NULL,
                CONSTRAINT UQ_shared_conversations_share_id UNIQUE(share_id)
            );

            CREATE INDEX idx_shared_conversations_share_id ON shared_conversations(share_id);
            CREATE INDEX idx_shared_conversations_session_id ON shared_conversations(session_id);
            CREATE INDEX idx_shared_conversations_user_id ON shared_conversations(user_id);

            PRINT 'Table shared_conversations created successfully';
        END
        ELSE
        BEGIN
            PRINT 'Table shared_conversations already exists';
        END
        """

        cursor.execute(create_shared_sql)
        conn.commit()
        print("[OK] shared_conversations table ready!")
        print()

        # Create user_preferences table
        print("[*] Creating table: user_preferences...")

        create_prefs_sql = """
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
        BEGIN
            PRINT 'Table user_preferences already exists';
        END
        """

        cursor.execute(create_prefs_sql)
        conn.commit()
        print("[OK] user_preferences table ready!")
        print()

        # Verify tables
        print("[*] Verifying tables...")
        cursor.execute("""
            SELECT TABLE_NAME,
                   (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = t.TABLE_NAME) as column_count
            FROM INFORMATION_SCHEMA.TABLES t
            WHERE TABLE_NAME IN ('shared_conversations', 'user_preferences')
            ORDER BY TABLE_NAME
        """)

        tables = cursor.fetchall()

        if tables:
            print("[OK] Tables verified:")
            for table in tables:
                print(f"   - {table[0]}: {table[1]} columns")
        else:
            print("[WARN] Warning: Could not verify tables")

        cursor.close()
        conn.close()

        print()
        print("=" * 60)
        print("[SUCCESS] Migration completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Start the backend: python run.py")
        print("  2. Test the new features in the UI")
        print()

        return True

    except pyodbc.Error as e:
        print(f"[ERROR] Database error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
