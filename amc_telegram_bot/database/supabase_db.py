import os
import time
import httpx
import socket
from functools import wraps
from cryptography.fernet import Fernet

# Force IPv4 to prevent hanging on broken local IPv6/NAT64 networks
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = patched_getaddrinfo

from supabase import create_client, Client
from .. import config

KEY_FILE = ".key"

def get_fernet_key():
    if config.ENCRYPTION_KEY:
        return config.ENCRYPTION_KEY.encode()

    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()

    new_key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(new_key)
    return new_key

cipher = Fernet(get_fernet_key())

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def retry_on_disconnect(func):
    """
    Decorator to retry database operations if the connection drops.
    Re-creates the Supabase client to clear any stale socket connection pools.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        global supabase
        last_ex = None
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except (httpx.HTTPError, httpx.ProtocolError, Exception) as e:
                last_ex = e
                print(f"⚠️ Database connection issue in {func.__name__} (Attempt {attempt+1}/3): {e}")
                try:
                    # Re-create client to drop the old connection pool
                    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                except Exception as init_err:
                    print(f"Failed to re-initialize Supabase client: {init_err}")
                time.sleep(0.5)
        # If all attempts failed, raise the error
        raise last_ex
    return wrapper

@retry_on_disconnect
def init_db():
    """
    Sanity check to verify connection to Supabase.
    Table creation is handled in Supabase SQL editor using supabase_schema.sql.
    """
    # Simple ping to test connectivity
    supabase.table("weekly_timetable").select("count", count="exact").limit(1).execute()
    print("✅ Connection to Supabase established successfully.")

@retry_on_disconnect
def get_cached_profile(telegram_id: int):
    res = supabase.table("student_profiles").select("*").eq("telegram_id", telegram_id).execute()
    if not res.data:
        return None
    row = res.data[0]
    return {
        "student_name": row.get("student_name"),
        "register_no": row.get("register_no"),
        "email": row.get("email"),
        "mobile": row.get("mobile"),
        "semester": row.get("semester"),
        "course_name": row.get("course_name"),
        "department_name": row.get("department_name"),
        "batch": row.get("batch"),
        "college_year": row.get("college_year")
    }

@retry_on_disconnect
def save_profile(telegram_id: int, p):
    data = {
        "telegram_id": telegram_id,
        "student_name": p.student_name,
        "register_no": p.register_no,
        "email": p.email,
        "mobile": p.mobile,
        "semester": p.semester,
        "course_name": p.course_name,
        "department_name": p.department_name,
        "batch": p.batch,
        "college_year": p.college_year
    }
    supabase.table("student_profiles").upsert(data).execute()


@retry_on_disconnect
def save_credentials(telegram_id: int, reg_no: str, dob: str):
    enc_reg = cipher.encrypt(reg_no.encode()).decode()
    enc_dob = cipher.encrypt(dob.encode()).decode()
    data = {
        "telegram_id": telegram_id,
        "encrypted_reg_no": enc_reg,
        "encrypted_dob": enc_dob
    }
    supabase.table("users").upsert(data).execute()

@retry_on_disconnect
def get_weekly_timetable(day_order: str):
    res = supabase.table("weekly_timetable").select("*").eq("day_order", day_order).order("hour").execute()
    return [
        {
            "hour": row.get("hour"),
            "code": row.get("code"),
            "name": row.get("subject_name"),
            "staff": row.get("staff")
        }
        for row in res.data
    ]

@retry_on_disconnect
def get_cached_day_order(date_str: str) -> str:
    res = supabase.table("day_orders").select("day_value").eq("date", date_str).execute()
    if not res.data:
        return None
    return res.data[0].get("day_value")

@retry_on_disconnect
def save_day_order(date_str: str, day_value: str):
    data = {
        "date": date_str,
        "day_value": day_value
    }
    supabase.table("day_orders").upsert(data).execute()

@retry_on_disconnect
def update_user_token(telegram_id: int, token: str):
    supabase.table("users").update({"api_token": token}).eq("telegram_id", telegram_id).execute()

@retry_on_disconnect
def get_credentials(telegram_id: int):
    res = supabase.table("users").select("encrypted_reg_no", "encrypted_dob", "api_token").eq("telegram_id", telegram_id).execute()
    if not res.data:
        return None
    row = res.data[0]
    dec_reg = cipher.decrypt(row.get("encrypted_reg_no").encode()).decode()
    dec_dob = cipher.decrypt(row.get("encrypted_dob").encode()).decode()
    return {
        "reg_no": dec_reg,
        "dob": dec_dob,
        "token": row.get("api_token")
    }

@retry_on_disconnect
def delete_credentials(telegram_id: int):
    # Cascade delete in PostgreSQL takes care of dependent records in attendance and profiles
    supabase.table("users").delete().eq("telegram_id", telegram_id).execute()

@retry_on_disconnect
def get_cached_attendance(telegram_id: int):
    # Use PostgREST relationship join to fetch subject name
    res = supabase.table("attendance").select(
        "attendance_date, hour_value, subject_id, subjects(subject_name)"
    ).eq("telegram_id", telegram_id).execute()
    
    return [
        {
            "date": row.get("attendance_date"),
            "hour": row.get("hour_value"),
            "subject_id": row.get("subject_id"),
            "subject_name": row.get("subjects").get("subject_name") if row.get("subjects") else None
        }
        for row in res.data
    ]

@retry_on_disconnect
def save_attendance_logs(telegram_id: int, logs, subject_map):
    # Ensure subject_map has all subject_ids from logs to prevent foreign key violations
    full_subject_map = dict(subject_map) if subject_map else {}
    
    # Fallback map for known subject IDs
    SUBJECT_FALLBACK_MAP = {
        2501: "24PCS5409-NLP-VB (Natural Language Processing)",
        2500: "24PCS5407-ASE-CM (Advanced Software Engineering)",
        2497: "24PCS5403-ADBMS-KBA (Advanced DBMS)",
        2495: "24PCS5401-DMW-KS (Data Mining & Warehousing)",
        2499: "24PCS5405-DIP-KB (Digital Image Processing)",
        2494: "24PCS5301-ADBMS LAB-KBA (Advanced DBMS Lab)",
        2498: "24PCS5405-DIP LAB-KB (Digital Image Processing Lab)"
    }
    
    # Pre-populate any missing subject IDs from the logs
    for item in logs or []:
        if item.subject_id:
            try:
                sub_id = int(item.subject_id)
                if sub_id not in full_subject_map:
                    name = SUBJECT_FALLBACK_MAP.get(sub_id, f"Subject {sub_id}")
                    full_subject_map[sub_id] = name
            except ValueError:
                pass

    # 1. Upsert subjects bulk
    if full_subject_map:
        subjects_data = [{"subject_id": int(k), "subject_name": v} for k, v in full_subject_map.items()]
        supabase.table("subjects").upsert(subjects_data).execute()
    
    # 2. Clear old attendance
    supabase.table("attendance").delete().eq("telegram_id", telegram_id).execute()
    
    # 3. Bulk insert new logs
    if logs:
        attendance_data = []
        for item in logs:
            sub_id = None
            try:
                sub_id = int(item.subject_id) if item.subject_id else None
            except ValueError:
                pass
            
            attendance_data.append({
                "telegram_id": telegram_id,
                "attendance_date": item.date,
                "hour_value": item.hour,
                "subject_id": sub_id
            })
        if attendance_data:
            supabase.table("attendance").insert(attendance_data).execute()

@retry_on_disconnect
def get_all_users():
    """
    Fetch all registered telegram_ids from the database.
    """
    res = supabase.table("users").select("telegram_id").execute()
    return [row.get("telegram_id") for row in res.data]


