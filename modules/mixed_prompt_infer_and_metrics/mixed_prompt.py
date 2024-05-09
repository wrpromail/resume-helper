import os
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain.output_parsers.enum import EnumOutputParser
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_mistralai.chat_models import ChatMistralAI
# from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.callbacks import LangChainTracer
from langsmith import Client 

callbacks = [
  LangChainTracer(
    project_name=os.getenv("LANGSMITH_PROJECT_NAME"),
    client=Client(
      api_url="https://api.smith.langchain.com",
      api_key=os.getenv("LANGSMITH_API_KEY")
    )
  )
]


class StructuredParserPrompt:
    def __init__(self, llm, response_schemas: dict, prompt_template: str):
        self.llm = llm
        response_schemas_objs = []
        for k,v in response_schemas.items():
            response_schemas_objs.append(ResponseSchema(name=k,description=v))
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas_objs)
        self.format_instructions = self.output_parser.get_format_instructions()
        self.prompt = PromptTemplate(
            template=prompt_template+"\n{format_instructions}\n{input}",
            input_variables=["input"],
            partial_variables={"format_instructions": self.format_instructions}
        )
        self.chain = self.prompt | self.llm | self.output_parser

    def invoke(self, inp: str):
        return self.chain.invoke({"input": inp}, config={"callbacks": callbacks})

class EnumParserPrompt:
    def __init__(self, llm, enum_class: Enum, prompt_template: str):
        self.llm = llm
        self.parser = EnumOutputParser(enum=enum_class)
        self.format_instructions = self.parser.get_format_instructions()
        self.prompt = PromptTemplate(
            template=prompt_template + "User'sInput: {input}\nInstructions:{format_instructions}",
            input_variables=["input"],
            partial_variables={"format_instructions": self.format_instructions}
        )
        self.chain = self.prompt | self.llm | self.parser

    def invoke(self, inp: str):
        return self.chain.invoke({"input": inp}, config={"callbacks": callbacks})
    
model_name = os.getenv("MISTRAL_MODEL_NAME","open-mistral-7b")
llm_instance = ChatMistralAI(model_name=model_name)
#llm = wrap_openai(ChatOpenAI(temperature=0.2))


sd = {"id":"uuid of the entity, or like part of the id", 
      "entity_name":"what id of entity represents",
      "time_range":"the time range of users' query"}
spp = StructuredParserPrompt(llm_instance, sd, "answer the users question as best as possible.")


class UserIntent(Enum):
    FIND_SPECIFIED_RESUME = "find_specified_resume"
    CREATE_RESUME = "create_resume"
    LIST_RESUME = "list_resume"
    DELETE_RESUME = "delete_resume"
    CREATE_JOB_DESCRIPTION = "create_job_description"
    FIND_SPECIFIED_JOB_DESCRIPTION = "find_specified_job_description"
    DELETE_JOB_DESCRIPTION = "delete_job_description"
    COMPARE_RESUME_AND_JOB_DESCRIPTION = "compare_resume_and_job_description"
    GENERATE_LANGUAGE_SENTENCE_BY_RESUME = "generate_language_sentence_by_resume"

epp = EnumParserPrompt(llm_instance, UserIntent, "What user want to do by his instruction? only reply instruction but not other extra content.")

def detect_intent(input_text):
    return epp.invoke(input_text)

def extract_entities(input_text):
    return spp.invoke(input_text)


def run_prompt(input_text):
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_intent = executor.submit(detect_intent, input_text)
        future_entities = executor.submit(extract_entities, input_text)
        
        results = {}
        for future in as_completed([future_intent, future_entities]):
            result = future.result()
            if isinstance(result, UserIntent):
                results['intent'] = result
            else:
                results['entities'] = result
        return results


if __name__ == "__main__":
    user_input = "我要查看id为 cd1482c8-2242 开头的简历"
    rst = run_prompt(user_input)
    print(rst)
