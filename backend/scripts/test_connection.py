"""
Test SQL Server Connection
Tests connection to both Default Instance and SQLEXPRESS
"""
import pyodbc
import os
from dotenv import load_dotenv

def test_connection():
    load_dotenv()
    
    # Base connection string parts
    driver = "{ODBC Driver 17 for SQL Server}"
    # Tentar ler do .env ou usar default
    user = os.getenv("DB_USER", "sa")
    password = os.getenv("DB_PASSWORD", "password")
    
    instances = [
        ("localhost", "Default Instance"),
        ("localhost\\SQLEXPRESS", "SQLEXPRESS Instance"),
        (".\\SQLEXPRESS", "SQLEXPRESS (dot)"),
        ("127.0.0.1", "IP Loopback")
    ]
    
    print(f"Testing connections with user='{user}'...")
    
    for server, name in instances:
        print(f"\nTesting {name} ({server})...")
        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE=master;"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
            "Connection Timeout=5;"
        )
        
        try:
            conn = pyodbc.connect(conn_str)
            print(f"✅ SUCCESS! Connected to {name}")
            
            # Get version
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            row = cursor.fetchone()
            print(f"   Version: {row[0].splitlines()[0]}")
            
            conn.close()
            return server # Return the working server
            
        except Exception as e:
            print(f"❌ FAILED: {e}")

    return None

if __name__ == "__main__":
    test_connection()
