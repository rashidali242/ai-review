import os
import boto3
from dotenv import load_dotenv

env_file = '.env.local' if os.getenv('FLASK_ENV') == 'development' else '.env.prod'
load_dotenv(env_file)

client = boto3.client("bedrock-runtime")
model_id = os.getenv('MODEL_ID')
max_tokens = os.getenv('MAX_TOKENS')

def get_bedrock_response(system, messages):
    bedrock_converse_response = client.converse(
        modelId=model_id,
        messages=messages,
        system=system,
        inferenceConfig={"maxTokens": int(max_tokens)},
    )
    assistant_message = bedrock_converse_response["output"]["message"]
    return assistant_message["content"][0]["text"]

def create_acceptance_criteria(description_text):
    system = [
        {
            "text": "You are a knowledgeable, helpful assistant that generates Acceptance Criteria based on the given task description. \
            Make your answers concise and directly provide the Acceptance Criteria without introductory statements such as \
            'Certainly!' or 'I'll Acceptance Criteria, and in proper Markdown format. Format Acceptance Criteria as a list with headings \
            like '### Acceptance Criteria'. Make sure that only provide 5 to 8 points for that Acceptance Criteria.'"
        }
    ]
    messages = []
    
    user_message = {"role": "user", "content": [{"text": f"Generate Acceptance Criteria based on this task description:\n\n{description_text}"}]}
    
    messages.append(user_message)
    return get_bedrock_response(system, messages)

def gen_test_case(criteria_text):
    system = [
        {
            "text": "You are a knowledgeable, helpful assistant that generates test case based on the given Acceptance Criteria. \
            Make your answers concise and directly provide the test case without introductory statements such as \
            'Certainly!' or 'I'll provide Test case, and in proper Markdown format. Provide only title of test case, no need body text. \
            The format of test case as a list with headings \
            like '### Test Cases'. Make sure that only provide 5 to 8 points for that test case.'"
        }
    ]
    messages = []
    
    user_message = {"role": "user", "content": [{"text": f"Generate Acceptance Criteria based on this task description:\n\n{criteria_text}"}]}
    
    messages.append(user_message)
    return get_bedrock_response(system, messages)

def validate_task_completion_with_criteria(acceptance_criteria, git_diff):
    system = [
        {
            "text": "You are a highly knowledgeable and precise assistant that evaluates code changes based on provided \
            Acceptance Criteria and a git diff. Your role is to analyze whether the git diff implements all aspects \
            of the Acceptance Criteria correctly. Provide your answers concisely, in Markdown format, and include: \
            \n\n1. A '### Evaluation' heading with a brief summary of whether the task is complete. It should not long paragraph. \
            \n2. A bullet-pointed list under a '### Justification' heading explaining how each point of the Acceptance Criteria \
            has or has not been satisfied. \
            \n3. Conclude with a '### Recommendation' section suggesting any additional changes or improvements if must necessary and it should bullet-pointed list."
        }
    ]
    messages = []
    
    # Compare Git Diff with Acceptance Criteria
    validation_message = {
        "role": "user",
        "content": [
            {
                "text": f"Based on this git diff:\n\n{git_diff}\n\n"
                        f"And this acceptance criteria:\n\n{acceptance_criteria}\n\n"
                        f"Is the task completed? Provide a detailed explanation."
            }
        ],
    }
    messages.append(validation_message)
    completion_status = get_bedrock_response(system, messages)
    
    return {
        "completion_status": completion_status,
    }