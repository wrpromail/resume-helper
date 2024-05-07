import os

from langchain_core.output_parsers import NumberedListOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI

# model available
# open-mistral-7b
# open-mixtral-8x7b
# open-mixtral-8x22b
# mistral-small-latest
# mistral-medium-latest
# mistral-large-latest#
model_name = os.getenv("MISTRAL_MODEL_NAME","mistral-small-latest")  # MISTRAL_MODEL_NAME

# MISTRAL_API_KEY
llm = ChatMistralAI(model_name=model_name)

def generate_prompt(language: str = "English"):
    return "the following sentence is what someone did in his past working experience, nowadays, he want to find a job that require {language} speaking skills, please generate several {language} sentence as first person view about this.".format(language=language)

# Comma separated output parser it not working well
parser = NumberedListOutputParser()

prompt = PromptTemplate(
    template=generate_prompt("French") + " {subject}",
    input_variables=["subject"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser

sample = "开发和维护多种编程语言，包括C/C++、Python、Java、Typescript和Golang等的产品及工具。"

if __name__ == "__main__":
    rst = chain.invoke({"subject": sample})
    print(rst)