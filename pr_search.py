import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
token = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

six_months_ago = datetime.now() - timedelta(days=180)
date_string = six_months_ago.strftime("%Y-%m-%d")
print(date_string)

response = requests.get("https://api.github.com/rate_limit", headers=headers)

print(response.status_code)
print(response.json())