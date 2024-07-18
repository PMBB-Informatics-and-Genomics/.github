import os
import requests
from datetime import datetime

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_ISSUES_DATABASE = os.getenv('NOTION_ISSUES_DATABASE')
REPO_OWNER = 'PMBB-Informatics-and-Genomics'
REPO_NAME = '.github'  # Update with your repository name


github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_issue_data():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    response = requests.get(url, headers=github_headers)
    response.raise_for_status()
    return response.json()

def post_to_notion(issue):
    url = "https://api.notion.com/v1/pages"
    created_date = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    updated_date = datetime.strptime(issue['updated_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
    
    data = {
        "parent": { "database_id": NOTION_ISSUES_DATABASE },
        "properties": {
            "Organization": {
                "title": [
                    {
                        "text": {
                            "content": REPO_OWNER
                        }
                    }
                ]
            },
            "Repository": {
                "multi_select": [
                    {
                        "name": REPO_NAME
                    }
                ]
            },
            "Number": {
                "number": issue['number']
            },
            "Author": {
                "rich_text": [
                    {
                        "text": {
                            "content": issue['user']['login']
                        }
                    }
                ]
            },
            "Created": {
                "rich_text": [
                    {
                        "text": {
                            "content": created_date
                        }
                    }
                ]
            },
            "Updated": {
                "rich_text": [
                    {
                        "text": {
                            "content": updated_date
                        }
                    }
                ]
            },
            "ID": {
                "multi_select": [
                    {
                        "name": str(issue['id'])
                    }
                ]
            },
            "Link": {
                "rich_text": [
                    {
                        "text": {
                            "content": issue['html_url']
                        }
                    }
                ]
            },
            "Repo": {
                "rich_text": [
                    {
                        "text": {
                            "content": f"{REPO_OWNER}/{REPO_NAME}"
                        }
                    }
                ]
            },
            "Body": {
                "rich_text": [
                    {
                        "text": {
                            "content": issue['body'] if issue['body'] else "No description provided"
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": issue['state']  # Assuming GitHub issue state ('open' or 'closed') matches status options
                }
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

issue_data = fetch_issue_data()

for issue in issue_data[:5]:  # Process the latest 5 issues
    post_to_notion(issue)