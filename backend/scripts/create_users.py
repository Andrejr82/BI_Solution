"""
Create users.parquet file for authentication
"""
import polars as pl
import uuid
from pathlib import Path
from datetime import datetime, timezone
import json
from passlib.context import CryptContext

# Setup passlib context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Generate password hashes
admin_hash = pwd_context.hash('Admin@2024')
user_hash = pwd_context.hash('Admin@2024')

print(f"Admin hash: {admin_hash}")
print(f"Verify admin: {pwd_context.verify('Admin@2024', admin_hash)}")

admin_id = str(uuid.uuid4())
user_id = str(uuid.uuid4())

# Create users data
users_data = {
    "id": [admin_id, user_id],
    "username": ["admin", "user"],
    "email": ["admin@agentbi.com", "user@agentbi.com"],
    "full_name": ["Administrator", "Standard User"],
    "hashed_password": [admin_hash, user_hash],
    "is_active": [True, True],
    "is_superuser": [True, False],
    "role": ["admin", "user"],
    "allowed_segments": [json.dumps(["*"]), json.dumps(["*"])],
    "created_at": [datetime.now(timezone.utc), datetime.now(timezone.utc)],
    "updated_at": [datetime.now(timezone.utc), datetime.now(timezone.utc)],
    "last_login": [None, None]
}

# Create DataFrame
df = pl.DataFrame(users_data)

# Save to parquet
output_path = Path(__file__).parent / "data" / "parquet" / "users.parquet"
output_path.parent.mkdir(parents=True, exist_ok=True)

df.write_parquet(output_path)

print(f"\n[OK] Created users.parquet at {output_path}")
print(f"\nDefault credentials:")
print(f"  Admin Username: admin")
print(f"  Admin Password: Admin@2024")
print(f"\n  User Username: user")
print(f"  User Password: Admin@2024")
