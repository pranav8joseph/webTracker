import subprocess, os, re, smtplib
from datetime import datetime
from email.mime.text import MIMEText

# ────────── CONFIG ──────────
WG_INTERFACE      = "meowVPNtest"
IPHONE_PUBLIC_KEY = "i9d3mzJHSVtj2XqhpUQKfwwO8R8cCJL+1ktmec6sLHg="
MAX_AGE_SEC       = 200                     # silence > this ⇒ offline

STATUS_LOG        = r"C:/Users/prana/OneDrive/Desktop/code/webTracker/vpn_status_log.txt"
LAST_STATUS_FILE  = r"C:/Users/prana/OneDrive/Desktop/code/webTracker/last_status.txt"

SENDER_EMAIL      = "meowpivpn@gmail.com"
APP_PASSWORD      = "xynzyrcazhkpjbzh"
RECEIVER_EMAIL    = "pranav8joseph@gmail.com"

# regex: matches “…handshake: 3 seconds ago”, “1 minute ago”, or “(none)”
HS_RE = re.compile(
    r"latest handshake:\s+((?P<age>\d+)\s+(?P<unit>second|minute)s?|\(none\))",
    flags=re.I
)

# ────────── HELPERS ──────────
def log(msg: str):
    ts = datetime.utcnow().isoformat()
    with open(STATUS_LOG, "a", encoding="utf-8") as f:
        f.write(f"{ts} - {msg}\n")

def send_email(subj: str, body: str):
    msg = MIMEText(body)
    msg["Subject"], msg["From"], msg["To"] = subj, SENDER_EMAIL, RECEIVER_EMAIL
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(SENDER_EMAIL, APP_PASSWORD)
        s.send_message(msg)
    print("Email sent.")

def read_last_status() -> str:
    return open(LAST_STATUS_FILE).read().strip() if os.path.exists(LAST_STATUS_FILE) else "unknown"

def write_last_status(st: str):
    with open(LAST_STATUS_FILE, "w") as f:
        f.write(st)

# ────────── MAIN CHECK ──────────
def check_vpn_status():
    try:
        out = subprocess.check_output(["wg", "show", WG_INTERFACE], text=True)
        print("[DEBUG] wg show output:\n", out)

        current = "disconnected"

        if IPHONE_PUBLIC_KEY in out:
            m = HS_RE.search(out)
            if m:
                if "(none)" not in m.group(0).lower():
                    age = int(m.group("age"))
                    unit = m.group("unit")
                    age_sec = age if unit.startswith("second") else age * 60
                    if age_sec <= MAX_AGE_SEC:
                        current = "connected"

        prev = read_last_status()
        if current != prev:
            log(f"VPN status {prev.upper()} -> {current.upper()}")
            write_last_status(current)
            subject = "VPN Connected" if current == "connected" else "VPN Disconnected"
            body    = "Your iPhone VPN has reconnected." if current == "connected" \
                      else "ALERT: Your iPhone VPN was disconnected."
            send_email(subject, body)
        else:
            log(f"VPN status: {current}")

    except Exception as e:
        log(f"Error: {e}")
        print("[ERROR]", e)

if __name__ == "__main__":
    check_vpn_status()
