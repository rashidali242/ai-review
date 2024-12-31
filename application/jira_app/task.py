from .jira_config import get_jira_connection, convert_html_to_jira_markup
import requests
import os
PROJECT_KEY = "SPS"


jira_object = get_jira_connection()

def get_ticket_details(ticket_id):
    try:
        # Fetch the issue by ticket ID
        issue = jira_object.issue(ticket_id)
        
        ticket_details = {
            "ticket_id": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
        }

        return ticket_details
    
        # Print ticket details
        # print(f"Ticket ID: {issue.key}")
        # print(f"Summary: {issue.fields.summary}")
        # print(f"Description: {issue.fields.description}")
        # print(f"Status: {issue.fields.status.name}")
        # print(f"Assignee: {issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned'}")
        # print(f"Reporter: {issue.fields.reporter.displayName}")
        # print(f"Priority: {issue.fields.priority.name if issue.fields.priority else 'None'}")
        # print(f"Created: {issue.fields.created}")
        # print(f"Updated: {issue.fields.updated}")
    except Exception as e:
        return(f"Error fetching ticket details: {e}")

def append_to_ticket_description(ticket_id, text_to_append, test_case_text):
    try:
        issue = jira_object.issue(ticket_id)
        
        existing_description = issue.fields.description or ""
        
        # Append the new text
        updated_description = f"{existing_description}\n\n{convert_html_to_jira_markup(text_to_append)}\n\n{convert_html_to_jira_markup(test_case_text)}"
        
        # Update the issue description
        issue.update(fields={"description": updated_description})
        
        return (f"Description updated successfully for ticket {ticket_id}.")
    
    except Exception as e:
        return(f"Error updating ticket description: {e}")
    
def add_comment_and_review_pull_request(pr_id, review_comment):
    
    workspace = 'sl-faizrasool'
    repo_slug = 'hackthon-requirement-group-a'
    access_token = os.getenv("BITBUCKET_ACCESS_TOKEN")
    
    comment_url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    comment_data = {
        "content": {
            "raw": review_comment
        }
    }

    comment_response = requests.post(comment_url, headers=headers, json=comment_data)

    if comment_response.status_code == 201:
        print("Comment added successfully.")
        review_url = f'https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}'
    
        review_data = {
            "state": "OPEN" #DECLINED
        }
        review_response = requests.put(review_url, headers=headers, json=review_data)
        if review_response.status_code == 200:
            return ("PR Review successfully.")
        else:
            return (f"Failed to review PR: {review_response.status_code}, {review_response.text}")
    else:
        print(f"Failed to add comment: {comment_response.status_code}, {comment_response.text}")
    