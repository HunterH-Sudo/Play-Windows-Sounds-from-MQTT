import os
import logging
import winsound
import ssl
import traceback
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MQTT_BROKER = "MQTT-Broker-Address" 
MQTT_PORT = 443  # Cloudflare always uses 443 for the public side
MQTT_USERNAME = "MQTT-Username"
MQTT_PASSWORD = "MQTT-Password"
MQTT_TOPIC = "MQTT-Topic"
SOUND_DIR = r"C:\Windows\Media"

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logging.info("SUCCESS: Connected to Cloudflare and Upgraded to WebSocket!")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Connection failed. Reason Code: {reason_code}")
        # Common codes: 4 = Bad Username/Password, 5 = Not Authorized

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode().strip()
        if not payload.lower().endswith('.wav'):
            payload += '.wav'
        
        sound_path = os.path.normpath(os.path.join(SOUND_DIR, payload))
        
        if os.path.exists(sound_path):
            logging.info(f"Received trigger. Playing: {payload}")
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        else:
            logging.warning(f"File not found in {SOUND_DIR}: {payload}")
    except Exception:
        logging.error(f"Playback error:\n{traceback.format_exc()}")

if __name__ == "__main__":
    try:
        client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2, 
            client_id="Windows_Meme_Player",
            transport="websockets"
        )

        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        # FIX: Explicitly set the Path and the Host header
        client.ws_set_options(
            path="/mqtt", 
            headers={"Host": "mqtt2.harringtonassistant.com"}
        )

        # SSL Configuration
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        # Adding this just in case Cloudflare's SNI is acting up
        client.tls_insecure_set(True) 

        client.on_connect = on_connect
        client.on_message = on_message

        logging.info(f"Attempting Secure WebSocket connection to {MQTT_BROKER}...")
        
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_forever()

    except Exception:
        logging.critical(f"\n--- FATAL ERROR ---\n{traceback.format_exc()}")
    finally:
        print("\n" + "="*50)
        input("Window Locked. Press ENTER to close...")