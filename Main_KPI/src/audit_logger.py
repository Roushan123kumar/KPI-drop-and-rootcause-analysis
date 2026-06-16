#User Action → Capture Data → Add Timestamp → Write to CSV → Store permanently

#sequential logging algorithm 
import csv
import os
from datetime import datetime


LOG_FILE = "logs/audit_logs.csv"


def log_event(user, action, details):
    
    # create logs folder if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # write header if file is new
        if not file_exists:
            writer.writerow(["timestamp", "user", "action", "details"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user,
            action,
            details
        ])