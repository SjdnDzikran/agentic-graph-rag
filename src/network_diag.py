import socket
import ssl
import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Fallback loading
if not os.environ.get("NEO4J_AURA"):
     load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

uri = os.environ.get("NEO4J_AURA")

if not uri:
    print("❌ NEO4J_AURA not found in environment.")
    sys.exit(1)

print(f"Target URI: {uri}")

# Parse URI
try:
    parsed = urlparse(uri)
    scheme = parsed.scheme
    hostname = parsed.hostname
    port = parsed.port or 7687 # Default bolt port
except Exception as e:
    print(f"❌ Failed to parse URI: {e}")
    sys.exit(1)

print(f"Hostname: {hostname}")
print(f"Port: {port}")

# 1. DNS Resolution
print("\n--- 1. DNS Resolution ---")
try:
    ip_address = socket.gethostbyname(hostname)
    print(f"✅ DNS Resolved: {hostname} -> {ip_address}")
except socket.gaierror as e:
    print(f"❌ DNS Resolution Failed: {e}")
    print("Possible causes: No internet, DNS server issues, or typo in hostname.")
    sys.exit(1)

# 2. TCP Connection
print("\n--- 2. TCP Connection ---")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    result = sock.connect_ex((hostname, port))
    if result == 0:
        print(f"✅ TCP Connection Successful to {hostname}:{port}")
    else:
        print(f"❌ TCP Connection Failed. Error code: {result}")
        print("Possible causes: Firewall blocking port 7687, corporate proxy, or server down.")
        sock.close()
        sys.exit(1)
except Exception as e:
    print(f"❌ TCP Connection Error: {e}")
    sock.close()
    sys.exit(1)

# 3. SSL Handshake (if applicable)
print("\n--- 3. SSL Handshake ---")
if "s" in scheme: # neo4j+s or neo4j+ssc
    try:
        context = ssl.create_default_context()
        if "ssc" in scheme:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            print("Mode: Self-Signed Certificate (SSC) - Skipping verification")
        else:
            print("Mode: Full SSL Verification")
        
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"✅ SSL Handshake Successful. Cipher: {ssock.cipher()}")
            print(f"Server Certificate: {ssock.getpeercert() if 'ssc' not in scheme else 'Skipped'}")
    except ssl.SSLError as e:
        print(f"❌ SSL Handshake Failed: {e}")
        print("Possible causes: MITM proxy, clock skew, or invalid certificate.")
    except Exception as e:
        print(f"❌ SSL Error: {e}")
else:
    print("Skipping SSL check (not requested in URI scheme).")

sock.close()
print("\n--- Diagnostics Complete ---")
