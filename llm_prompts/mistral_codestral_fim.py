import os
from mistralai.client import MistralClient

api_key = os.environ["MISTRAL_API_KEY"]

client = MistralClient(api_key=api_key)

model = "codestral-latest"
prompt = "def is_odd(n): \n return n % 2 == 1 \ndef test_is_odd():"
suffix = "n = int(input('Enter a number: '))\nprint(fibonacci(n))"

response = client.completion(
    model=model,
    prompt=prompt,
    suffix=suffix,
    stop=["\n\n"]
)

print(
    f"""
{prompt}
{response.choices[0].message.content}
"""
)