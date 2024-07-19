import os
import requests
from datetime import datetime
##corrected code
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_REPO_STATS_DATABASE = os.getenv('NOTION_REPO_STATS_DATABASE')
REPO_OWNER = 'PMBB-Informatics-and-Genomics'
REPO_NAME = '.github'

github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_repo_stats():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    response = requests.get(url, headers=github_headers)
    response.raise_for_status()
    return response.json()

def fetch_repo_contents():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents"
    response = requests.get(url, headers=github_headers)
    response.raise_for_status()
    return response.json()

def get_file_size(file_url):
    try:
        response = requests.get(file_url, headers=github_headers)
        response.raise_for_status()
        return len(response.content)
    except requests.RequestException:
        return 0

def post_to_notion(stats, files):
    url = "https://api.notion.com/v1/pages"

    file_details = '\n'.join([f"{file['name']} ({file['size']} bytes)" for file in files])
    
    data = {
        "parent": { "database_id": NOTION_REPO_STATS_DATABASE },
        "properties": {
            "Repository": {
                "title": [
                    {
                        "text": {
                            "content": REPO_NAME
                        }
                    }
                ]
            },
            "Stars": {
                "multi_select": [
                    {
                        "name": str(stats['stargazers_count'])
                    }
                ]
            },
            "Forks": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(stats['forks_count'])
                        }
                    }
                ]
            },
            "Open Issues": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(stats['open_issues_count'])
                        }
                    }
                ]
            },
            "Size (MB)": {
                "rich_text": [
                    {
                        "text": {
                            "content": f"{stats['size'] / 1024:.2f} MB"
                        }
                    }
                ]
            },
            "File Details": {
                "rich_text": [
                    {
                        "text": {
                            "content": file_details if file_details else "No files found"
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": stats['description'] if stats['description'] else "No description provided"
                        }
                    }
                ]
            }
        }
    }
    
    # Debug: Print the payload
    print(f"Payload: {data}")
    
    response = requests.post(url, headers=notion_headers, json=data)
    
    # Debug: Print response details
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    response.raise_for_status()
    return response.json()


repo_stats = fetch_repo_stats()
repo_contents = fetch_repo_contents()

# Create a list of file details including their sizes
file_details = [
    {'name': item['name'], 'size': get_file_size(item['download_url']) if 'download_url' in item and item['type'] == 'file' else 0}
    for item in repo_contents
]

post_to_notion(repo_stats, file_details)