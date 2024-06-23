from __future__ import annotations

import json
from typing import AsyncIterable

import fastapi_poe as fp
from modal import Image, Stub, asgi_app


def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "11", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps(
            {"location": "San Francisco", "temperature": "72", "unit": unit}
        )
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def convert_currency(amount, from_currency, to_currency):
    mock_rate = {
        "USD": 1,
        "EUR": 0.9,
        "JPY": 155,
        "CNY": 7.5,
        "GBP": 0.8,
    }
    if from_currency not in mock_rate or to_currency not in mock_rate:
        return json.dumps({"error": "Currency not supported"})
    
    converted_amount = amount * mock_rate[to_currency] / mock_rate[from_currency]
    return json.dumps({
        "amount": converted_amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "converted_amount": round(converted_amount,2),
    })


tools_executables = [get_current_weather]

tools_dict_list = [
    {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "Convert a monetary amount from one currency to another",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "Amount of money to convert"
                },
                "from_currency": {
                    "type": "string",
                    "description": "Currency code from which to convert, e.g., USD, EUR"
                },
                "to_currency": {
                    "type": "string",
                    "description": "Currency code to which to convert, e.g., USD, EUR"
                }
            },
            "required": ["amount", "from_currency", "to_currency"]
        }}
    },
    {
        "type": "function",
        "function": {
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
        },
    }
]
tools = [fp.ToolDefinition(**tools_dict) for tools_dict in tools_dict_list]


class GPT35FunctionCallingBot(fp.PoeBot):
    async def get_response(
        self, request: fp.QueryRequest
    ) -> AsyncIterable[fp.PartialResponse]:
        async for msg in fp.stream_request(
            request,
            "GPT-3.5-Turbo",
            request.access_key,
            tools=tools,
            tool_executables=tools_executables,
        ):
            yield msg

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        return fp.SettingsResponse(server_bot_dependencies={"GPT-3.5-Turbo": 2})


REQUIREMENTS = ["fastapi-poe==0.0.36"]
image = Image.debian_slim().pip_install(*REQUIREMENTS)
stub = Stub("function-calling-poe")


@stub.function(image=image)
@asgi_app()
def fastapi_app():
    bot = GPT35FunctionCallingBot()
    app = fp.make_app(bot, allow_without_key=True)
    return app