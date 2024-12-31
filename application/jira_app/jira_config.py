import os
from jira import JIRA
from dotenv import load_dotenv
import requests

# Load environment variables from the appropriate .env file
env_file = '.env.local' if os.getenv('FLASK_ENV') == 'development' else '.env.prod'
load_dotenv(env_file)

workspace = 'sl-faizrasool'
repo_slug = 'hackthon-requirement-group-a'
access_token = os.getenv("BITBUCKET_ACCESS_TOKEN")

def get_jira_connection():
    return JIRA(server=os.getenv('JIRA_URL'), basic_auth=(os.getenv('EMAIL'), os.getenv('API_TOKEN')))

def get_repositories():
    url = f'https://api.bitbucket.org/2.0/repositories/{workspace}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('values', [])
    else:
        print(f"Error fetching repositories: {response.status_code}, {response.text}")
        return []

def get_pull_request_detail(repo_slug, pr_id):
    url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    return requests.get(url, headers=headers)

def get_pull_requests(repo_slug):
    url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests'
    headers = {'Authorization': f'Bearer {access_token}'}
    return requests.get(url, headers=headers)

def pull_request_diff(pr_id):
    url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/diff'
    headers = {'Authorization': f'Bearer {access_token}'}
    return requests.get(url, headers=headers)

def convert_html_to_jira_markup(html_content):
    html_to_markup = {
        "<h3>": "h3. ",
        "</h3>": "\n",
        "<ol>": "",
        "</ol>": "",
        "<li>": "* ",
        "</li>": "\n"
    }

    for html_tag, markup in html_to_markup.items():
        html_content = html_content.replace(html_tag, markup)
    
    # Remove any leftover HTML tags that aren't part of the conversion dictionary
    html_content = html_content.replace("<br>", "\n").replace("</br>", "")
    
    return html_content