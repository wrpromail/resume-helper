require("dotenv").config();
const {ChatPromptTemplate} = require("@langchain/core/prompts");
const {SystemMessagePromptTemplate, HumanMessagePromptTemplate} = require("@langchain/core/prompts");

const prompt = ChatPromptTemplate.fromTemplate(`What are three good names for a company that makes {product}?`)

async function runPrompt() {
    const detailed_prompt = await prompt.format({
        product: "colorful socks",
    });
    console.log(detailed_prompt);    
}

runPrompt();


const promptFromMessages = ChatPromptTemplate.fromMessages([
    SystemMessagePromptTemplate.fromTemplate(
      "You are an expert at picking company names."
    ),
    HumanMessagePromptTemplate.fromTemplate(
      "What are three good names for a company that makes {product}?"
    )
]);

const messages_prompt = promptFromMessages.formatMessages({
    product: "shiny objects"
});

console.log(messages_prompt);