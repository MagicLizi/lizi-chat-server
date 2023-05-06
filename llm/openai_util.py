import openai
import os
from typing import Union, List
from util.log import logger
openai.api_key = os.environ["LIZI_OA_KEY"]


class OpenAIUtil:

    @staticmethod
    async def chat(content: str, prompts: str,
                   temperature: Union[float, None] = 0.5,
                   n: Union[int, None] = 1, stream: Union[bool, None] = False,
                   chat_history: Union[List[str], None] = None) \
            -> str:
        messages = [
            {"role": "system", "content": prompts},
            {"role": "user", "content": content}
        ]
        if chat_history is not None:
            messages = chat_history + messages
        logger.info(f"当前发送：{messages}")
        response = await openai.ChatCompletion.acreate(
            ## model="gpt-3.5-turbo",
            model="gpt-3.5-turbo",
            temperature=temperature,
            n=n,
            stream=stream,
            messages=messages,
            max_tokens=256
        )
        assistant_message = response.choices[0].message['content']
        return assistant_message

    @staticmethod
    def sync_chat(content: str, prompts: str,
                  temperature: Union[float, None] = 0.5,
                  n: Union[int, None] = 1, stream: Union[bool, None] = False,
                  chat_history: Union[List[str], None] = None) \
            -> str:
        messages = [
            {"role": "system", "content": prompts},
            {"role": "user", "content": content}
        ]
        if chat_history is not None:
            messages = chat_history + messages
        logger.info(f"当前发送：{messages}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=temperature,
            n=n,
            stream=stream,
            messages=messages
        )
        assistant_message = response.choices[0].message['content']
        return assistant_message

    @staticmethod
    def completion(model_engine: str,
                   prompt: str, temperature: Union[float, None] = 0.5,
                   n: Union[int, None] = 1, stream: Union[bool, None] = False):
        response = openai.Completion.create(
            model=model_engine,
            prompt=prompt,
            max_tokens=256,
            temperature=temperature,
            stream=stream,
            n=n,
        )
        generated_text = response.choices[0].text.strip()
        print(f"Generated text: {generated_text}")
