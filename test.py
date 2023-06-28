# test.py
#
# Author: MagicLizi 
# Email: jiali@magiclizi.com | lizi@xd.com
# Created Time: 2023/5/24 11:35
import openai
import os

openai.api_key = os.environ["LIZI_OA_KEY"]

history_list = []


def chat(role, msg):
    history_list.append({"role": role, "content": msg})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history_list,
        functions=[
            {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            }
        ],
        function_call="auto",
    )
    print(completion.choices[0].message)

    history_list.append(completion.choices[0].message)


chat('user', "What's the weather like in Boston?")
