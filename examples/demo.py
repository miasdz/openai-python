#!/usr/bin/env -S poetry run python

from openai import OpenAI
import configparser

config_path = '/home/miasdz/桌面/py-test/study/config.ini'
config = configparser.ConfigParser()
config.read(config_path)

llm_type = config['common']['llm']
api_key = config[llm_type]['OPENAI_API_KEY']
base_url = config[llm_type]['OPENAI_API_BASE_URL']
model = config[llm_type]['OPENAI_API_MODEL']

print(llm_type, base_url, model, api_key)

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)
# gets API Key from environment variable OPENAI_API_KEY
# client = OpenAI()

# Non-streaming:
print("----- standard request -----")
completion = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        },
    ],
)
print(completion.choices[0].message.content)

# Streaming:
print("----- streaming request -----")
stream = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue

    print(chunk.choices[0].delta.content, end="")
print()

# Response headers:
print("----- custom response headers test -----")
response = client.chat.completions.with_raw_response.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
)
completion = response.parse()
print(response.request_id)
print(completion.choices[0].message.content)
