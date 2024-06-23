import os
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.callbacks.manager import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
os.environ["ZHIPUAI_API_KEY"] = "359a6cfe8c6a5cf911d33e2146ef74ff.Ej1FxJtSqTA5uHGv"

chat = ChatZhipuAI(
    model="glm-4",
    temperature=0.3,
)

def get_messages(user_prompt):
    return [
        SystemMessage(content="You tell everything you know."),
        HumanMessage(content=user_prompt),
    ]

def basic_llm_chat(message_list):
    response = chat.invoke(message_list)
    return response.content

streaming_chat = ChatZhipuAI(
    model="glm-4",
    temperature=0.3,
    streaming=True,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
)

async def stream_llm_chat(message_list):
    response = await streaming_chat.agenerate([message_list])
    print(response)

if __name__ == "__main__":
    # api 调用包含输出合规检查，当输出内容可能存在问题时，接口会直接返回 400
    user_prompt = "你知道以下3个 python 库的用途是什么吗？ httpx httpx-sse PyJWT"
    messages = get_messages(user_prompt)
    response = basic_llm_chat(messages)
    print(response)

