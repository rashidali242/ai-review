import os
from flask import Flask, request, redirect, url_for, render_template, jsonify
import markdown
import requests
import re
from json import loads
from dotenv import load_dotenv
from jira_app.task import get_ticket_details, append_to_ticket_description, add_comment_and_review_pull_request
from bedrock_app.bedrock_config import create_acceptance_criteria, gen_test_case, validate_task_completion_with_criteria
from jira_app.jira_config import get_pull_requests, pull_request_diff, get_repositories, get_pull_request_detail

# Load environment variables from .env file
env_file = ".env.local" if os.getenv("FLASK_ENV") == "development" else ".env.prod"
load_dotenv(env_file)

TICKET_ID = "SPS-2350"

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the Ticket ID from the form
        ticket_id = request.form.get('ticket_id')

        # Fetch the ticket details
        ticket_details = get_ticket_details(ticket_id)

        # Return the details to the frontend as JSON or render a template
        return jsonify(ticket_details)

    # Render the form template
    return render_template('index.html')

@app.route('/create-criteria', methods=['GET', 'POST'])
def create_criteria():
    if request.method == 'POST':
        ticket_description = request.form.get('description')
        acceptance_criteria_text = create_acceptance_criteria(ticket_description)
        return {
            "criteria": markdown.markdown(acceptance_criteria_text),
        }

@app.route('/create-test-case', methods=['GET', 'POST'])
def create_test_case():
    if request.method == 'POST':
        criteria = request.form.get('criteria')
        test_case_text = gen_test_case(criteria)
        return {
            "test_case": markdown.markdown(test_case_text)
        }
    
@app.route('/update-task', methods=['POST'])
def update_task():
    if request.method == 'POST':
        criteria = request.form.get('criteria')
        test_case = request.form.get('test_case')
        ticket_id = request.form.get('update_ticket_id')
        test_details = append_to_ticket_description(ticket_id, criteria, test_case)
        return markdown.markdown(test_details)

@app.route('/api/repositories', methods=['GET'])
def api_get_repositories():
    repositories = get_repositories()
    return jsonify(repositories)

@app.route('/pull-requests', methods=['GET','POST'])
def pull_requests():
    repo_slug = request.args.get('repo_slug')
    status = request.args.get('status')
    if repo_slug:
        response = get_pull_requests(repo_slug)
        if response.status_code == 200:
            pull_requests = response.json()
            pr_list = []
            for pr in pull_requests['values']:
                pr_data = {
                    'title': pr['title'],
                    'id': pr['id'],
                    'state': pr['state'],
                    'description': pr['description'],
                }
                pr_list.append(pr_data)
            return render_template('pull_requests.html', pr_list=pr_list, status=status, repo_slug=repo_slug)
        else:
            return f"Failed to fetch pull requests: {response.status_code}"
    return render_template('pull_requests.html', pr_list=[], status=status)

@app.route('/process-pr')
def process_pr():
    pr_id = request.args.get('pr_id')
    repo_slug = request.args.get('repo_slug')
    #ticket_id = re.search(r"SPS-\d+", request.args.get('pr_title'))
    if pr_id:
        
        pr_detail_resposne = get_pull_request_detail(repo_slug, pr_id)
        pr_detail = pr_detail_resposne.json()
        pr_detail_description = pr_detail['description']
        #return f"Ticket Ids: {pr_detail_description}"
        ticket_numbers = re.findall(r'SPS-\d+', pr_detail_description)
        unique_ticket_numbers = list(set(ticket_numbers))
        all_review_descriptions = []
        if unique_ticket_numbers:
            for ticket_id in unique_ticket_numbers:

                ticket_details = get_ticket_details(ticket_id)
                
                match = re.search(r"Acceptance Criteria(.*?)(?=\n\S|$)", ticket_details['description'], re.DOTALL)
                if match:
                    git_diff = get_pull_request_diff(pr_id)
                    acceptance_criteria = match.group(1).strip()
                    review_description = validate_task_completion_with_criteria(acceptance_criteria, git_diff)

                    all_review_descriptions.append(f"Ticket {ticket_id}: {review_description['completion_status']}")

                else:
                    all_review_descriptions.append(f"Due to no acceptance criteria in ticket {ticket_id}, PR review is failed.")

            combined_review_description = "\n\n\n".join(all_review_descriptions)
            status = add_comment_and_review_pull_request(pr_id, combined_review_description)
            return redirect(url_for('pull_requests', status=status))
        else:
            status = f"Due to no acceptance criteria in ticket, PR review is failed."
            return redirect(url_for('pull_requests', status=status))
    else:
        return "pr_id parameter is required", 400


def get_pull_request_diff(pr_id):
    response = pull_request_diff(pr_id)
    if response.status_code == 200:
        return response.text
    else:
        return f"Failed to fetch diff for PR {pr_id}: {response.status_code}"

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG") == "1")
