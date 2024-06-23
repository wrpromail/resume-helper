import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

api_key = os.environ["MISTRAL_API_KEY"]

client = MistralClient(api_key=api_key)

model = "codestral-latest"

# chat with the model
messages = [
    ChatMessage(role="user", content="Write a function for fibonacci")
]
chat_response = client.chat(
    model=model,
    messages=messages
)
print(chat_response.choices[0].message.content)

