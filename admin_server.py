import os
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Import database methods and amc_api client
from amc_telegram_bot.database.supabase_db import (
    get_all_users,
    get_credentials,
    save_credentials,
    delete_credentials,
    get_cached_profile,
    save_profile
)
from amc_api import AMCClient, Config
from amc_api.exceptions import LoginError

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(__file__), "amc_admin_dashboard")

class AdminDashboardHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Override to suppress default stdout spam logs
        pass

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # REST API: Get all users
        if path == "/api/users":
            try:
                user_ids = get_all_users()
                users_list = []
                for telegram_id in user_ids:
                    creds = get_credentials(telegram_id)
                    profile = get_cached_profile(telegram_id) or {}
                    
                    users_list.append({
                        "telegram_id": telegram_id,
                        "register_no": creds.get("reg_no") if creds else "N/A",
                        "dob": creds.get("dob") if creds else "N/A",
                        "student_name": profile.get("student_name", "Not Cached"),
                        "email": profile.get("email", ""),
                        "mobile": profile.get("mobile", ""),
                        "semester": profile.get("semester", ""),
                        "course_name": profile.get("course_name", ""),
                        "department_name": profile.get("department_name", ""),
                        "batch": profile.get("batch", ""),
                        "college_year": profile.get("college_year", "")
                    })
                self.send_json({"success": True, "users": users_list})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 500)
            return

        # Serve static frontend files
        if path == "/" or path == "":
            file_path = os.path.join(STATIC_DIR, "index.html")
            content_type = "text/html"
        else:
            file_path = os.path.join(STATIC_DIR, path.lstrip("/"))
            if path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".js"):
                content_type = "application/javascript"
            elif path.endswith(".png"):
                content_type = "image/png"
            elif path.endswith(".jpg") or path.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif path.endswith(".svg"):
                content_type = "image/svg+xml"
            else:
                content_type = "text/plain"

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        
        try:
            body = json.loads(post_data) if post_data else {}
        except Exception:
            self.send_json({"success": False, "error": "Invalid JSON"}, 400)
            return

        # API: Add / Update User
        if path in ("/api/users/add", "/api/users/update"):
            telegram_id = body.get("telegram_id")
            reg_no = body.get("register_no")
            dob = body.get("dob")

            if not telegram_id or not reg_no or not dob:
                self.send_json({"success": False, "error": "Missing required fields"}, 400)
                return

            try:
                telegram_id = int(telegram_id)
            except ValueError:
                self.send_json({"success": False, "error": "Telegram ID must be an integer"}, 400)
                return

            # Verify credentials via portal login first
            try:
                config = Config(enable_logging=False)
                client = AMCClient(reg_no=reg_no, dob=dob, config=config)
                profile = client.profile()
            except LoginError:
                self.send_json({"success": False, "error": "Invalid Register Number or DOB"}, 400)
                return
            except Exception as e:
                self.send_json({"success": False, "error": f"College portal error: {str(e)}"}, 500)
                return

            try:
                # Save to database
                save_credentials(telegram_id, reg_no, dob)
                
                # Update user token if logged in
                if client.session.api_token:
                    from amc_telegram_bot.database.supabase_db import update_user_token
                    update_user_token(telegram_id, client.session.api_token)

                # Save profile cache
                save_profile(telegram_id, profile)

                # Clear session manager cache to prevent stale credentials
                from amc_telegram_bot.utils.session_manager import session_manager
                session_manager.remove_client(telegram_id)

                self.send_json({
                    "success": True, 
                    "message": "User saved and verified successfully",
                    "student_name": profile.student_name
                })
            except Exception as e:
                self.send_json({"success": False, "error": f"Database error: {str(e)}"}, 500)
            return

        # API: Delete User
        elif path == "/api/users/delete":
            telegram_id = body.get("telegram_id")
            if not telegram_id:
                self.send_json({"success": False, "error": "Missing Telegram ID"}, 400)
                return

            try:
                telegram_id = int(telegram_id)
                delete_credentials(telegram_id)
                
                # Clear session manager client cache
                from amc_telegram_bot.utils.session_manager import session_manager
                session_manager.remove_client(telegram_id)

                self.send_json({"success": True, "message": "User deleted successfully"})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 500)
            return

        self.send_json({"success": False, "error": "Endpoint not found"}, 404)

def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, AdminDashboardHandler)
    print(f"🚀 Admin Dashboard running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Admin Dashboard server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
