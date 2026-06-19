import http.server
import socketserver
import threading
import paho.mqtt.client as mqtt
import json
import smtplib
from email.message import EmailMessage
import time
import webbrowser # <-- NEW: Added this module!

# ==========================================
# 1. EMAIL CONFIGURATION
# ==========================================
EMAIL_ADDRESS = "aravindhanvadivel02@gmail.com"
EMAIL_PASSWORD = "ffuu jcgr urdy kgvt" # Put your newly generated password here!
DESTINATION_EMAIL = "aravindhan.tv2006@gmail.com"

# ==========================================
# 2. MQTT CONFIGURATION
# ==========================================
BROKER_IP = "10.172.99.147"
TOPIC = "factory/node1/sensors"
COOLDOWN_SECONDS = 60
last_email_time = 0

# ==========================================
# MODULE A: THE WEB SERVER
# ==========================================
def start_web_server():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Allow the port to be reused immediately if you restart the script
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅ [WEB SERVER] Dashboard is LIVE at: http://localhost:{PORT}")
        httpd.serve_forever()

# ==========================================
# MODULE B: THE EMAIL ALERT MANAGER
# ==========================================
def send_alert_email(subject, body):
    global last_email_time
    current_time = time.time()
    
    if current_time - last_email_time < COOLDOWN_SECONDS:
        print("⏳ [COOLDOWN] Skipping duplicate email to prevent spam...")
        return

    print(f"📧 [EMAIL] Sending Alert: {subject}")
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = DESTINATION_EMAIL

        # Connect to Gmail securely
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("✅ [EMAIL] Sent successfully!")
        last_email_time = current_time
    except Exception as e:
        print(f"❌ [EMAIL] Failed to send: {e}")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode('utf-8'))
    
    if payload.get('alert_inner') == 1:
        subject = "CRITICAL: Node 1 Core Temp Alert!"
        body = f"The inner temperature of Node 1 has breached safe limits.\nCurrent Temp: {payload.get('inner_temp')} C\nPlease check the physical unit immediately."
        send_alert_email(subject, body)
        
    elif payload.get('alert_surr') == 1:
        subject = "WARNING: Node 1 Ambient Temp Alert"
        body = f"The room temperature around Node 1 is too high.\nCurrent Temp: {payload.get('surr_temp')} C."
        send_alert_email(subject, body)

def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    
    print(f"📡 [MQTT] Connecting to Switchboard at {BROKER_IP}...")
    try:
        client.connect(BROKER_IP, 1883, 60)
        client.subscribe(TOPIC)
        print("✅ [MQTT] Alert Manager is listening for emergencies...")
        client.loop_forever()
    except ConnectionRefusedError:
        print("❌ [MQTT] ERROR: Could not connect to Mosquitto. Is the service running?")

# ==========================================
# MAIN EXECUTION (Starts both modules at once)
# ==========================================
if __name__ == "__main__":
    print("🚀 Starting Factory IoT Hub...")
    
    # 1. Start the Web Server in a background thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # NEW: Automatically open the browser!
    print("🌐 Opening Dashboard in your browser...")
    webbrowser.open("http://localhost:8000")
    
    # 2. Start the MQTT Listener in the main thread
    start_mqtt()