# using small parameters llm to detect user intention under chat bot scenario
# and accumulate the user feedback
# when got enought feedback, try to train a intention detection model
import os

from langchain.output_parsers.enum import EnumOutputParser
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from enum import Enum

class UserIntent(Enum):
    CREATE_RESUME = "create_resume"
    FIND_RESUME = "find_resume"
    DELETE_RESUME = "delete_resume"
    CREATE_JOB_DESCRIPTION = "create_job_description"
    FIND_JOB_DESCRIPTION = "find_job_description"
    DELETE_JOB_DESCRIPTION = "delete_job_description"
    COMPARE_RESUME_AND_JOB_DESCRIPTION = "compare_resume_and_job_description"
    GENERATE_LANGUAGE_SENTENCE_BY_RESUME = "generate_language_sentence_by_resume"

# use the little model to detect user intention
model_name = os.getenv("MISTRAL_MODEL_NAME","open-mistral-7b")
llm = ChatMistralAI(model_name=model_name)

parser = EnumOutputParser(enum=UserIntent)
prompt = PromptTemplate(
    template="What user want to do by his instruction? only reply instruction but" +
    " not other extra content." +
    "  User'sInput: {user_input}"+ 
    "Instructions:{instructions}",
    input_variables=["user_input"],
    partial_variables={"instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser

sample = "我要查看我的简历"

if __name__ == "__main__":
    rst = chain.invoke({"user_input": sample})
    print(rst)

