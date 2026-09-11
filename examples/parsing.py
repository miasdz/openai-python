from typing import List

import rich
from pydantic import BaseModel

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

class Step(BaseModel):
    explanation: str
    output: str


class MathResponse(BaseModel):
    steps: List[Step]
    final_answer: str


# client = OpenAI()

completion = client.chat.completions.parse(
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful math tutor."},
        {"role": "user", "content": "solve 8x + 31 = 2"},
    ],
    response_format=MathResponse,
)

message = completion.choices[0].message
if message.parsed:
    rich.print(message.parsed.steps)

    print("answer: ", message.parsed.final_answer)
else:
    print(message.refusal)
