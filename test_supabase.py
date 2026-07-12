import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_db_url = os.getenv("SUPABASE_DB_URL")

print("=== Supabase Connection Test ===")
print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_KEY: {'configured' if supabase_key and 'your-supabase' not in supabase_key else 'NOT configured'}")
print(f"SUPABASE_DB_URL: {'configured' if supabase_db_url and '[YOUR-PASSWORD]' not in supabase_db_url else 'NOT configured'}")
print()

# Check if placeholders are still present
if not supabase_url or "your-project-ref" in supabase_url or not supabase_key or "your-supabase-anon-key" in supabase_key:
    print("⚠️ Warning: You are still using placeholder values in your .env file!")
    print("Please go to your Supabase Dashboard -> Project Settings -> API and copy the actual Project URL and Anon/Service Key to your .env file.")
    exit(1)

# Try connecting using direct PostgreSQL via psycopg2 if installed
try:
    import psycopg2
    print("Attempting to connect via psycopg2...")
    conn = psycopg2.connect(supabase_db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"✅ Successfully connected to Postgres! Version: {db_version[0]}")
    conn.close()
except ImportError:
    print("ℹ️ psycopg2 is not installed. If you want to connect directly via Postgres, run: pip install psycopg2-binary")
except Exception as e:
    print(f"❌ Failed to connect via PostgreSQL: {e}")

print()

# Try connecting using Supabase client library if installed
try:
    from supabase import create_client, Client
    print("Attempting to connect via supabase-py Client...")
    supabase: Client = create_client(supabase_url, supabase_key)
    # Try a simple fetch
    res = supabase.table("weekly_timetable").select("*").limit(1).execute()
    print("✅ Successfully connected via Supabase Client API!")
    print(f"Sample timetable record: {res.data}")
except ImportError:
    print("ℹ️ supabase package is not installed. If you want to use the Supabase REST Client, run: pip install supabase")
except Exception as e:
    print(f"❌ Failed to connect via Supabase Client: {e}")
