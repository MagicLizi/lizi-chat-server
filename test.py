# Note: The openai-python library support for Azure OpenAI is in preview.
import asyncio
import os
import openai

openai.api_type = "azure"
openai.api_base = "https://lizigpt.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "6d6856ed0f4947fea0bb045752c69422"


async def go():
    response = await openai.ChatCompletion.acreate(
        engine="Lizi-GPT35",
        messages=[{"role": "system", "content": "You are an AI assistant that helps people find information."},
                  {"role": "user", "content": "123"}, {"role": "assistant",
                                                       "content": "I'm sorry, I don't understand what you are trying to say. Can you please provide more context or information?"}],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    print(response)

asyncio.run(go())
