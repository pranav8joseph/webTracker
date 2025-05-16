import subprocess
import re
from datetime import datetime

# File to save logs
LOG_FILE = "C:/Users/prana/OneDrive/Desktop/code/webTracker/dns_logs.txt"

# Regex pattern to extract domain names from tcpdump output
DNS_REGEX = re.compile(r"(\? )([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")

def log(message):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")

def sniff_dns():
    print("Starting DNS sniffing...")
    try:
        # Run tcpdump and capture DNS traffic
        proc = subprocess.Popen(
            ["tcpdump", "-l", "-n", "-i", "any", "udp port 53"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        for line in proc.stdout:
            match = DNS_REGEX.search(line)
            if match:
                domain = match.group(2)
                log(domain)

    except KeyboardInterrupt:
        print("Stopping DNS sniffing...")
    except Exception as e:
        log(f"Error: {e}")

if __name__ == "__main__":
    sniff_dns()