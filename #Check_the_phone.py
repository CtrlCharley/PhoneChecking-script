import pyodbc
import requests
import logging

logging.basicConfig(filename='phone_number_checks.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

conn_str = (
    r"Driver={SQLite ODBC Driver};"
    r"Server=127.0.0.1;"
    r"Database=test.db;"
)

conn = pyodbc.connect(conn_str)
c = conn.cursor()

c.execute("PRAGMA table_info(users)")
columns = [column[1] for column in c.fetchall()]
if "telegram" not in columns:
    c.execute("ALTER TABLE users ADD COLUMN telegram TEXT")
#if "whatsapp" not in columns:
 #   c.execute("ALTER TABLE users ADD COLUMN whatsapp TEXT")
if "viber" not in columns:
    c.execute("ALTER TABLE users ADD COLUMN viber TEXT")
conn.commit()

c.execute("SELECT phone_number FROM users")

for row in c.fetchall():
    phone_number = row[0]
    
    telegram_url = f"https://api.telegram.org/bot<TOKEN>/getChatMember?chat_id=@telegram_channel_username&user_id={phone_number}"
    telegram_response = requests.get(telegram_url)
    if telegram_response.json().get("ok") and telegram_response.json().get("result"):
        logging.info(f"{phone_number} is associated with Telegram.")
        c.execute("UPDATE users SET telegram = ? WHERE phone_number = ?", (True, phone_number))
    
    #whatsapp_url = f"https://api.twilio.com/2010-04-01/Accounts/<YOUR_TWILIO_ACCOUNT_SID>/Messages.json"
    #whatsapp_payload = {"To": f"whatsapp:{phone_number}", "From": "whatsapp:<YOUR_TWILIO_WHATSAPP_NUMBER>", "Body": "Test message from Twilio."}
    #whatsapp_response = requests.post(whatsapp_url, data=whatsapp_payload, auth=("<YOUR_TWILIO_ACCOUNT_SID>", "<YOUR_TWILIO_AUTH_TOKEN>"))
    #if whatsapp_response.status_code == 201:
     #   logging.info(f"{phone_number} is associated with WhatsApp.")
      #  c.execute("UPDATE users SET whatsapp = ? WHERE phone_number = ?", (True, phone_number))
    
    viber_url = f"https://chatapi.viber.com/pa/get_account_info"
    viber_payload = {"id": "<TOKEN>", "phone": phone_number}
    viber_response = requests.post(viber_url, json=viber_payload, headers={"X-Viber-Auth-Token": "<YOUR_VIBER_AUTH_TOKEN>"})
    if viber_response.json().get("status") == 0:
        logging.info(f"{phone_number} is associated with Viber.")
        c.execute("UPDATE users SET viber = ? WHERE phone_number = ?", (True, phone_number))

conn.commit()
conn.close()
