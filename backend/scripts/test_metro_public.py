import requests

METRO_PUBLIC_URL_CANDIDATE = "https://api-public.odpt.org/api/v4/gtfs/realtime/tokyometro_odpt_train_alert"

def check_metro_public():
    print(f"Testing {METRO_PUBLIC_URL_CANDIDATE}...")
    try:
        resp = requests.get(METRO_PUBLIC_URL_CANDIDATE, timeout=10)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Success! Public endpoint exists.")
        else:
            print("Failed. No public endpoint found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_metro_public()
