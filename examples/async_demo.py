#!/usr/bin/env -S poetry run python

import asyncio

from openai import AsyncOpenAI
import configparser

config_path = '/home/miasdz/桌面/py-test/study/config.ini'
config = configparser.ConfigParser()
config.read(config_path)

llm_type = config['common']['llm']
api_key = config[llm_type]['OPENAI_API_KEY']
base_url = config[llm_type]['OPENAI_API_BASE_URL']
model = config[llm_type]['OPENAI_API_MODEL']

print(llm_type, base_url, model, api_key)


# gets API Key from environment variable OPENAI_API_KEY
client = AsyncOpenAI(base_url=base_url,
    api_key=api_key)


async def main() -> None:
    stream = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            },
        ],
        stream=True,
    )
    async for chunk in stream:
        if not chunk.choices:
            continue

        print(chunk.choices[0].delta.content, end="")
    print()


asyncio.run(main())
