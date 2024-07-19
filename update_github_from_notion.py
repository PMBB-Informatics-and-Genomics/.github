import os
import requests

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_ISSUES_DATABASE = os.getenv('NOTION_ISSUES_DATABASE')
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

def fetch_notion_issues():
    url = f"https://api.notion.com/v1/databases/{NOTION_ISSUES_DATABASE}/query"
    response = requests.post(url, headers=notion_headers)
    response.raise_for_status()
    return response.json()

def update_github_issue(issue_id, updated_data):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_id}"
    response = requests.patch(url, headers=github_headers, json=updated_data)
    response.raise_for_status()
    return response.json()

def post_to_github_from_notion():
    notion_issues = fetch_notion_issues()
    
    for result in notion_issues['results']:
        issue_id = result['properties']['ID']['multi_select'][0]['name']
        updated_data = {
            "title": result['properties']['Repository']['title'][0]['text']['content'],
            "body": result['properties']['Body']['rich_text'][0]['text']['content'],
            "state": result['properties']['Status']['select']['name']
        }
        update_github_issue(issue_id, updated_data)

post_to_github_from_notion()
