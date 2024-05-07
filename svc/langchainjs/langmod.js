require("dotenv").config();
const { ChatOpenAI } = require("@langchain/openai");
const { HumanMessage } = require("@langchain/core/messages");

const model = new ChatOpenAI({modelName: "gpt-3.5-turbo-1106"});

async function runModel() {
    const response = await model.invoke([
        new HumanMessage("Hello, Tell me a joke")
    ]);
    console.log(response);    
}

runModel();
