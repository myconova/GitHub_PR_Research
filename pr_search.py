import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()
token = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

date_180_days_ago = datetime.now(timezone.utc) - timedelta(days=180)
date_string = date_180_days_ago.strftime("%Y-%m-%d")
print(date_string)

url = "https://api.github.com/search/issues"

query_params = {
    "q": f"is:pr is:merged created:>={date_string} merged:>={date_string}",
    "per_page": 10
}

response = requests.get(
    url,
    params=query_params, 
    headers=headers,
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['total_count']} pull requests.\n")
    print(f"Search results: {len(data['items'])}")

    for item in data["items"]:
        title = item.get("title")
        pr_url = item.get("html_url")
        repo_api_url = item.get("repository_url")
        repo_web_url = pr_url.split("/pull/")[0] if "/pull/" in pr_url else repo_api_url 

        repo_response = requests.get(repo_api_url, headers=headers)
        if repo_response.status_code == 200:
            repo_metadata = repo_response.json()
            license_data = repo_metadata.get("license") or {}
            spdx_id = license_data.get("spdx_id")

            if spdx_id == "MIT":
                print(f"Title: {title}")
                print(f"PR URL: {pr_url}")
                print(f"Repo URL: {repo_web_url}")
                print("-" * 40)
else:
    print(f"Failed to fetch data: {response.status_code}")
    print(response.text)

