from dotenv import load_dotenv
import os

from amc_api import AMCClient, Config

load_dotenv()

client = AMCClient(
    reg_no=os.getenv("AMC_REGISTER_NO"),
    dob=os.getenv("AMC_DOB"),
    config=Config(enable_logging=True)
)

# 1. Profile Test
print("=== Profile ===")
profile = client.profile()
print(f"Name: {profile.student_name}")
print(f"Register No: {profile.register_no}")
print(f"Department: {profile.department_name}")
print(f"Semester: {profile.semester}")
print(f"Email: {profile.email}")
print()

# 2. Enrolled Programmes Test
print("=== Enrolled Programmes ===")
programmes = client.enrolled_programmes()
print(f"Status: {programmes.message}")
for prog in programmes.programmes:
    print(f"- {prog.course_name} (Batch: {prog.batch}, Section: {prog.section})")
print()

# 3. Settings Test
print("=== Settings ===")
settings = client.settings()
print(f"SMS Sender Name: {settings.sms_sender_name}")
print()

# 4. Absent Days/Attendance Test
print("=== Attendance / Absent Days ===")
absent = client.absent_days()
print(f"Total Absent Days: {len(absent)}")
print()

# 5. Timetable & Day Value Test
print("=== Timetable & Day Value ===")
day_val = client.timetable_day_value()
print(f"Current Day Order/Holiday: {day_val}")
timetable_data = client.timetable(type_str="today")
if timetable_data.is_holiday:
    print(f"Today is a Holiday: {timetable_data.holiday.holiday_name}")
else:
    print("Timetable entries for today:")
    for entry in timetable_data.entries:
        print(f"- Period {entry.period}: {entry.subject_name} by {entry.staff_name}")
print()

# 6. Upcoming Day Order Test
print("=== Upcoming Day Order ===")
upcoming = client.upcoming_day_order()
print(f"Upcoming Day Order: {upcoming}")
print()

# 7. Notifications Test
print("=== Notifications ===")
notif = client.notification_count()
print(f"Notification Count: {notif.count}")
print()

# 8. Fees & Services Test
print("=== Fees ===")
fees = client.fees(balance_only=True)
print(f"Fee Balance: {fees.balance}")
service_groups = client.fee_service_groups()
print(f"Fee Service Groups: {service_groups.message} (Groups count: {len(service_groups.groups)})")
print()

# 9. News Test
print("=== News/Announcements ===")
news_items = client.news()
print(f"News count: {len(news_items)}")
print()