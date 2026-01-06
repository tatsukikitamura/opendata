import requests

TOKEN = "3oq7rayhcsdwjphug7adb7q8t2wwjtxx8k9jhxhrx7zwd8abd6y3w1n2gfwjnf08"
METRO_ALERT_URL = "https://api.odpt.org/api/v4/gtfs/realtime/tokyometro_odpt_train_alert"

def check_token():
    print(f"Testing Token: {TOKEN[:5]}... against {METRO_ALERT_URL}")
    params = {"acl:consumerKey": TOKEN}
    try:
        resp = requests.get(METRO_ALERT_URL, params=params, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Success! Token is valid for Metro.")
            print(f"Content Length: {len(resp.content)}")
        else:
            print(f"Failed. Status: {resp.status_code}")
            print(resp.text[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_token()
