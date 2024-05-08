from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI


# OPENAI_API_KEY
llm = ChatOpenAI(temperature=0.2)

class ResumeCompare(BaseModel):
    Reqs: str = Field(description="精简的岗位要求的技能")
    Pros: str = Field(description="简历拥有者过往经验相较岗位的优势")
    Cons: str = Field(description="简历拥有者过往经验相较岗位的劣势")
    Suggestions: str = Field(description="对于简历拥有者而言应该如何准备该岗位的面试")

parser = JsonOutputParser(pydantic_object=ResumeCompare)

compare_template="""
我给你发送某人的简历内容与某岗位描述.
{format_instructions}
###简历内容:{resume}
###职位描述:{jd}
"""

prompt = PromptTemplate(
    template=compare_template,
    input_variables=["resume", "jd"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser

# fill this content when testing
Resume1 = ""
Jd1 = ""


if __name__ == "__main__":
    rst = chain.invoke({"resume": Resume1, "jd": Jd1})
    print(rst)