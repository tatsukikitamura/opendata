
import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import Optional, List, Dict

class FareScraper:
    BASE_URL = "https://transit.yahoo.co.jp/search/print"

    @staticmethod
    def get_fare(from_station: str, to_station: str, via_stations: List[str] = []) -> Dict:
        """
        Scrape Yahoo Transit to get total fare and details.
        params:
            from_station: Departure station name
            to_station: Destination station name
            via_stations: List of via station names
        return:
            Dict with "total_fare" (int) and other details, or None on error
        """
        try:
            # URL Encoding
            from_enc = urllib.parse.quote(from_station)
            to_enc = urllib.parse.quote(to_station)
            
            # Construct URL
            url = f"{FareScraper.BASE_URL}?from={from_enc}&to={to_enc}"
            for v in via_stations:
                v_enc = urllib.parse.quote(v)
                url += f"&via={v_enc}"

            print(f"[FareScraper] Requesting: {url}")
            
            # Request
            # Add User-Agent to avoid being blocked potentially
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[FareScraper] Error: Status {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Summary Section
            route_summary = soup.find("div", class_="routeSummary")
            if not route_summary:
                print("[FareScraper] Error: Route summary not found")
                return {"error": "Parse Error: No summary"}

            # Parse Total Fare
            # Example: "IC優先：824円" or "現金優先：824円"
            fare_text = route_summary.find("li", class_="fare").get_text()
            # Extract number
            import re
            match = re.search(r'([0-9,]+)円', fare_text)
            if match:
                total_fare = int(match.group(1).replace(',', ''))
            else:
                total_fare = 0
                
            return {
                "from": from_station,
                "to": to_station,
                "via": via_stations,
                "total_fare": total_fare,
                "fare_raw": fare_text
            }

        except Exception as e:
            print(f"[FareScraper] Exception: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Internal Test
    result = FareScraper.get_fare("千葉", "高田馬場", ["東京"])
    print(result)
