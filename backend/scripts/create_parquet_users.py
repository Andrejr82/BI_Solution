"""
Create users.parquet file for authentication when SQL Server is not available

Password: admin123
Pre-generated hash using bcrypt
"""
import polars as pl
import uuid
from pathlib import Path
from datetime import datetime, timezone

# Use a pre-generated bcrypt hash for "admin123"
# Generated using: bcrypt.hashpw(b"admin123", bcrypt.gensalt())
ADMIN_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UrFDxeZQJK8K"

# Create users data
users_data = {
    "id": [str(uuid.uuid4())],
    "username": ["admin"],
    "email": ["admin@agentbi.com"],
    "full_name": ["Administrator"],
    "hashed_password": [ADMIN_PASSWORD_HASH],
    "is_active": [True],
    "is_superuser": [True],
    "role": ["admin"],
    "created_at": [datetime.now(timezone.utc)],
    "updated_at": [datetime.now(timezone.utc)],
    "last_login": [None]
}

# Create DataFrame
df = pl.DataFrame(users_data)

# Save to parquet
output_path = Path(__file__).parent.parent.parent / "data" / "parquet" / "users.parquet"
output_path.parent.mkdir(parents=True, exist_ok=True)

df.write_parquet(output_path)

print(f"[OK] Created users.parquet at {output_path}")
print(f"\nDefault credentials:")
print(f"  Username: admin")
print(f"  Password: admin123")
print(f"\nUser details:")
print(df)
