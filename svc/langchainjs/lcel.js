require("dotenv").config();
const {ChatPromptTemplate} = require("@langchain/core/prompts");
const { ChatOpenAI } = require("@langchain/openai");
const { StringOutputParser } = require("@langchain/core/output_parsers");

const model = new ChatOpenAI({modelName: "gpt-3.5-turbo-1106"});
const prompt = ChatPromptTemplate.fromTemplate(`请根据下面的工作简历，提取出若干项具体的工作内容 {resume}?`)
const outputParser = new StringOutputParser();
const chain = prompt.pipe(model).pipe(outputParser);

const sampleResume = `
write some sample resume
`;

async function handleChainInvoke() {
    const response = await chain.invoke({
        resume: sampleResume,
    });
    console.log(response);
}

handleChainInvoke();
