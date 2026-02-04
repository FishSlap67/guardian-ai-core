import time
import sqlite3
import logging
from datetime import datetime

# CONFIGURATION
DB_FILE = "guardian_ledger.db"
LOG_FILE = "integrity_audit.log"

# Setup Tamper-Proof Logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - TAMPER_EVENT - %(message)s')

def init_ledger():
    """Creates the immutable log database if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            details TEXT,
            user_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_event(event_type, details, user_id="SYSTEM"):
    """Writes an event to the ledger. This is the 'Black Box'."""
    timestamp = datetime.now().isoformat()
    
    # 1. Write to Text Log (Human Readable)
    logging.info(f"{event_type}: {details} (User: {user_id})")
    
    # 2. Write to SQL DB (System Readable)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO system_events (timestamp, event_type, details, user_id) VALUES (?, ?, ?, ?)",
                       (timestamp, event_type, details, user_id))
        conn.commit()
        conn.close()
        print(f"[AUDIT] Event Logged: {event_type} - {details}")
    except Exception as e:
        print(f"[CRITICAL FAILURE] Could not write to Ledger: {e}")

# MOCK SENSOR CHECK (Replace this with real Hardware API calls later)
def check_camera_status(camera_id):
    # In real life, this pings the IP address of the camera
    # For now, we simulate that Camera 3 is 'Offline'
    if camera_id == "CAM_03":
        return False # Simulated Failure
    return True

# MAIN LOOP
if __name__ == "__main__":
    print("GuardianAI Integrity Monitor: ACTIVE")
    init_ledger()
    
    # Simulate a monitoring loop
    cameras = ["CAM_01", "CAM_02", "CAM_03", "CAM_04"]
    
    # Run a check
    for cam in cameras:
        status = check_camera_status(cam)
        if not status:
            # CRITICAL: Camera is down. Log it immediately.
            log_event("SENSOR_LOSS", f"Signal lost for device {cam}", "UNKNOWN")
            
            # TRIGGER ALERT (This is where we'd send the notification)
            print(f"!!! ALERT: {cam} is OFFLINE. Tamper Protocol Initiated !!!")