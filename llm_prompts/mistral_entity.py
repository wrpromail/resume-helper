import os

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI


model_name = os.getenv("MISTRAL_MODEL_NAME","open-mistral-7b")
llm = ChatMistralAI(model_name=model_name)

response_schemas = [
    ResponseSchema(name='id',description='uuid of the entity'),
    ResponseSchema(name='entity_name', description='what id of entity represents'),
    ResponseSchema(name='time_range', description='the time range of users\s query'),
]
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

format_instructions = output_parser.get_format_instructions()
prompt = PromptTemplate(
    template="answer the users question as best as possible.\n{format_instructions}\n{question}",
    input_variables=["question"],
    partial_variables={"format_instructions": format_instructions}
)

chain = prompt | llm | output_parser

if __name__ == "__main__":
    # {'id': 'cd1482c8-2242-46ec-896c-ef80717ea890', 'entity_name': 'resume', 'time_range': ''}
    ques = "我要查看id为 cd1482c8-2242-46ec-896c-ef80717ea890 的简历"
    rst = chain.invoke({"question": ques})
    print(rst)
