import pandas as pd
import uuid
from datetime import datetime, timezone
import os
from app.config.security import get_password_hash

# Path to parquet file
PARQUET_FILE = "data/parquet/users.parquet"

def add_test_user():
    if not os.path.exists(PARQUET_FILE):
        print(f"Error: {PARQUET_FILE} not found!")
        return

    df = pd.read_parquet(PARQUET_FILE)
    
    # Check if user already exists
    if "user" in df["username"].values:
        print("User 'user' already exists.")
        return

    # Create new user
    new_user = {
        "id": str(uuid.uuid4()),
        "username": "user",
        "email": "user@agentbi.com",
        "hashed_password": get_password_hash("User@2024"),
        "full_name": "Test User",
        "role": "user",
        "is_active": True,
        "is_superuser": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_login": None
    }

    # Append to dataframe
    df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    
    # Save back to parquet
    df.to_parquet(PARQUET_FILE)
    print("User 'user' added successfully.")
    print(df[["username", "role"]])

if __name__ == "__main__":
    add_test_user()
