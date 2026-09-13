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
rejection_counts = {}
accepted_count = 0
max_pages = 2

for page in range(1, max_pages + 1):
    query_params = {
        "q": f"is:pr is:merged created:>={date_string} merged:>={date_string}",
        "per_page": 10, 
        "page": page,
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
                rejection_counts["REJ_MISSING_PR_URL"] = rejection_counts.get("REJ_MISSING_PR_URL", 0) + 1
                continue

            try:
                repo_response = requests.get(
                    repo_api_url, 
                    headers=headers,
                    timeout=10,
                )
            except requests.RequestException as error:
                print(f"Repository request failed: {error}")
                rejection_counts["REJ_REPO_FETCH_NETWORK_ERROR"] = rejection_counts.get("REJ_REPO_FETCH_NETWORK_ERROR", 0) + 1
                continue

            if repo_response.status_code != 200:
                rejection_counts["REJ_REPO_FETCH_HTTP_ERROR"] = rejection_counts.get("REJ_REPO_FETCH_HTTP_ERROR", 0) + 1
                continue

            repo_metadata = repo_response.json()
            repo_web_url = repo_metadata.get("html_url", repo_api_url)
            license_info = repo_metadata.get("license") or {}
            spdx_id = license_info.get("spdx_id")

            if spdx_id != "MIT":
                rejection_counts["REJ_LICENSE_NOT_ALLOWED"] = rejection_counts.get("REJ_LICENSE_NOT_ALLOWED", 0) + 1
                continue

            pr_api_url = item.get("pull_request", {}).get("url")

            if not pr_api_url:
                rejection_counts["REJ_MISSING_PR_API_URL"] = rejection_counts.get("REJ_MISSING_PR_API_URL", 0) + 1
                continue
            
            try:
                pr_detail_response = requests.get(
                    pr_api_url, 
                    headers=headers,
                    timeout=10,
                )
            except requests.RequestException as error:
                print(f"PR detail request failed: {error}")
                rejection_counts["REJ_PR_FETCH_NETWORK_ERROR"] = rejection_counts.get("REJ_PR_FETCH_NETWORK_ERROR", 0) + 1
                continue

            if pr_detail_response.status_code != 200:
                rejection_counts["REJ_PR_FETCH_HTTP_ERROR"] = rejection_counts.get("REJ_PR_FETCH_HTTP_ERROR", 0) + 1
                continue

            pr_metadata = pr_detail_response.json()
            additions = pr_metadata.get("additions")
            deletions = pr_metadata.get("deletions")

            if additions is None or deletions is None:
                rejection_counts["REJ_MISSING_ADDITIONS_DELETIONS"] = rejection_counts.get("REJ_MISSING_ADDITIONS_DELETIONS", 0) + 1
                continue

            total_changes = additions + deletions

            if total_changes < 500:
                accepted_count += 1
                print(f"Title: {title}")
                print(f"PR URL: {pr_url}")
                print(f"Repo URL: {repo_web_url}")
                print(f"Additions: {additions}")
                print(f"Deletions: {deletions}")
                print(f"Total Changes: {total_changes}")
                print("-" * 40)
            else:
                rejection_counts["REJ_SIZE_TOO_LARGE"] = rejection_counts.get("REJ_SIZE_TOO_LARGE", 0) + 1

print("\n" + "=" * 40)
print(f"Accepted: {accepted_count}")
print(f"Rejections:")
for code, count in sorted(rejection_counts.items()):
    print(f" {code}: {count}")


