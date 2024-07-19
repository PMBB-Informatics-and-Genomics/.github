import os
import requests

# Environment variable
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_ISSUES_DATABASE = os.getenv('NOTION_ISSUES_DATABASE')
REPO_OWNER = 'PMBB-Informatics-and-Genomics'
REPO_NAME = '.github'

# Headers for GitHub API
github_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Headers for Notion API
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

def fetch_github_issues():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    response = requests.get(url, headers=github_headers)
    response.raise_for_status()
    return response.json()

def update_github_issue(issue_id, updated_data):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_id}"
    response = requests.patch(url, headers=github_headers, json=updated_data)
    response.raise_for_status()
    return response.json()

def post_to_github_from_notion():
    notion_issues = fetch_notion_issues()
    github_issues = fetch_github_issues()
    
    # Create a mapping of GitHub issue numbers to their IDs
    github_issue_map = {issue['number']: issue for issue in github_issues}
    
    for result in notion_issues['results']:
        try:
            issue_id = result['properties']['ID']['multi_select'][0]['name']
            # title = result['properties']['Repository']['title'][0]['text']['content']
            
            # Handle Body property
            body_property = result['properties'].get('Body', {})
            body_rich_text = body_property.get('rich_text', [])
            body = body_rich_text[0]['text']['content'] if body_rich_text else "No description provided"
            
            # Handle Status property
            status_property = result['properties'].get('Status', {})
            status_select = status_property.get('select', {})
            state = status_select.get('name', 'open').lower() if status_property else 'open'
            
            # Determine GitHub issue number from Notion ID
            github_issue_number = int(issue_id)
            if github_issue_number in github_issue_map:
                # Update existing GitHub issue
                updated_data = {
                    # "title": title,
                    "body": body,
                    "state": state
                }
                update_github_issue(github_issue_number, updated_data)
            else:
                print(f"Issue ID {issue_id} not found in GitHub repository.")
        
        except KeyError as e:
            print(f"KeyError: {e} - {result}")
        except IndexError as e:
            print(f"IndexError: {e} - {result}")
        except Exception as e:
            print(f"Unexpected error: {e} - {result}")

post_to_github_from_notion()
