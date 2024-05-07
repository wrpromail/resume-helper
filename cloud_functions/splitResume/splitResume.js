const functions = require('@google-cloud/functions-framework');
const pdfParse = require('pdf-parse');
const {ChatPromptTemplate} = require("@langchain/core/prompts");
const { ChatOpenAI } = require("@langchain/openai");
const { StringOutputParser } = require("@langchain/core/output_parsers");
const fs = require('fs').promises;

const model = new ChatOpenAI({modelName: "gpt-3.5-turbo-1106"});
const prompt = ChatPromptTemplate.fromTemplate(`请根据下面的工作简历，提取出若干项具体的工作内容 {resume}?`)
const outputParser = new StringOutputParser();
const chain = prompt.pipe(model).pipe(outputParser);

async function handleChainInvoke(resumeContent) {
    try {
        const response = await chain.invoke({
            resume: sampleResume,
        });
        return response;
    } catch (error) {
        console.error(error);
        return null;
    }
}

functions.http('extractText', async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).send('Method Not Allowed');
    }

    try {
        let textContent;

        // 检查是否有文件上传
        if (req.files && Object.keys(req.files).length > 0) {
            const file = req.files.file; // 假设文件上传在 'file' 键下
            const fileType = file.mimetype;

            if (fileType === 'application/pdf') {
                // 处理 PDF 文件
                const dataBuffer = await fs.readFile(file.tempFilePath);
                const data = await pdfParse(dataBuffer);
                textContent = data.text;
            } else if (fileType === 'text/plain') {
                // 处理 TXT 文件
                textContent = await fs.readFile(file.tempFilePath, { encoding: 'utf8' });
            } else {
                return res.status(400).send('Unsupported file type.');
            }
        } else if (req.body && typeof req.body.text === 'string') {
            // 处理用户直接发送的文本
            textContent = req.body.text;
        } else {
            return res.status(400).send('No valid input provided.');
        }

        const rst = await handleChainInvoke(textContent);
        if (!rst) {
            return res.status(500).send('Error processing input');
        }

        // 处理文本内容，如分割为行
        const lines = rst.split('\n').filter(line => line.trim() !== '');
        res.json({ lines });
    } catch (error) {
        console.error('Error processing input:', error);
        res.status(500).send('Error processing input');
    } finally {
        // 清理：如果存在，删除临时文件
        if (req.files && req.files.file && req.files.file.tempFilePath) {
            await fs.unlink(req.files.file.tempFilePath);
        }
    }
});