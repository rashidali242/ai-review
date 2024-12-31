import boto3

client = boto3.client("bedrock-runtime")
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
max_tokens = 200
messages = []

system = [
    {
        "text": "You are a knowledgeable, helpful assistant that answers questions given to you by users. Make your answers concise yet informative."
    }
]
user_message = {"role": "user", "content": [{"text": "What is the meaning of life?"}]}

messages.append(user_message)

bedrock_converse_response = client.converse(
    modelId=model_id,
    messages=messages,
    system=system,
    inferenceConfig={"maxTokens": max_tokens},
)
assistant_message = bedrock_converse_response["output"]["message"]
assistant_message_text = assistant_message["content"][0]["text"]

print(assistant_message_text)
