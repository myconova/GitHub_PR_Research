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

search_url = "https://api.github.com/search/issues"

query_params = {
    "q": f"is:pr is:merged created:>={date_string} merged:>={date_string}",
    "per_page": 10
}

try:
    response = requests.get(
        search_url,
        params=query_params, 
        headers=headers,
        timeout=10,
    )
except requests.RequestException as error:
    print(f"An error occurred: {error}")
    raise SystemExit(1)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['total_count']} pull requests.\n")
    print(f"Search results: {len(data['items'])}")

    for item in data["items"]:
        title = item.get("title")
        pr_url = item.get("html_url")
        repo_api_url = item.get("repository_url")

        if not pr_url or not repo_api_url:
            continue

        try:
            repo_response = requests.get(
                repo_api_url, 
                headers=headers,
                timeout=10,
            )
        except requests.RequestException as error:
            print(f"Repository request failed: {error}")
            continue

        if repo_response.status_code != 200:
            continue

        repo_metadata = repo_response.json()
        repo_web_url = repo_metadata.get("html_url", repo_api_url)
        license_info = repo_metadata.get("license") or {}
        spdx_id = license_info.get("spdx_id")

        if spdx_id != "MIT":
            continue

        pr_api_url = item.get("pull_request", {}).get("url")

        if not pr_api_url:
            continue
        
        try:
            pr_detail_response = requests.get(
                pr_api_url, 
                headers=headers,
                timeout=10,
            )
        except requests.RequestException as error:
            print(f"PR detail request failed: {error}")
            continue

        if pr_detail_response.status_code != 200:
            continue

        pr_metadata = pr_detail_response.json()
        additions = pr_metadata.get("additions")
        deletions = pr_metadata.get("deletions")

        if additions is None or deletions is None:
            continue

        total_changes = additions + deletions

        if total_changes < 500:
            print(f"Title: {title}")
            print(f"PR URL: {pr_url}")
            print(f"Repo URL: {repo_web_url}")
            print(f"Additions: {additions}")
            print(f"Deletions: {deletions}")
            print(f"Total Changes: {total_changes}")
            print("-" * 40)

else:
    print(f"Failed to fetch data: {response.status_code}")
    print(response.text)

