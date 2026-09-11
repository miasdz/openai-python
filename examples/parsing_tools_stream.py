from __future__ import annotations

import rich
from pydantic import BaseModel

import openai
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

class GetWeather(BaseModel):
    city: str
    country: str


# client = OpenAI()


with client.chat.completions.stream(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "What's the weather like in SF and New York?",
        },
    ],
    tools=[
        # because we're using `.parse_stream()`, the returned tool calls
        # will be automatically deserialized into this `GetWeather` type
        openai.pydantic_function_tool(GetWeather, name="get_weather"),
    ],
    parallel_tool_calls=True,
) as stream:
    for event in stream:
        if event.type == "tool_calls.function.arguments.delta" or event.type == "tool_calls.function.arguments.done":
            rich.get_console().print(event, width=80)

print("----\n")
rich.print(stream.get_final_completion())
