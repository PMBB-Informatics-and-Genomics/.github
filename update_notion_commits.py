import os
import requests
##test code
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_COMMITS_DATABASE = os.getenv('NOTION_COMMITS_DATABASE')
REPO_OWNER = 'Verma-Lab'
REPO_NAME = '.github'  # Update this to your repository name

github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_commit_data():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits"
    response = requests.get(url, headers=github_headers)
    response.raise_for_status()
    return response.json()

def post_to_notion(commit):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": { "database_id": NOTION_COMMITS_DATABASE },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": commit['commit']['message']
                        }
                    }
                ]
            },
            "Committer": {
                "multi_select": [
                    {
                        "name": commit['commit']['author']['name']
                    }
                ]
            },
            "Commit Date": {
                "date": {
                    "start": commit['commit']['author']['date']
                }
            },
            "URL": {
                "url": commit['html_url']
            }
        }
    }
    
    # Print the payload for debugging
    print(f"Payload: {data}")
    
    response = requests.post(url, headers=notion_headers, json=data)
    
    # Print response content for debugging
    print(f"Response: {response.status_code}, {response.text}")
    
    response.raise_for_status()
    return response.json()

commit_data = fetch_commit_data()

for commit in commit_data[:5]:  # Process the latest 5 commits
    post_to_notion(commit)
