const fs = require('fs');
const axios = require('axios');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

async function compressAndVerify() {
  try {
    // 从命令行参数中获取文件路径和请求正文
    const argv = yargs(hideBin(process.argv)).options({
      file: {
        type: 'string',
        default: 'input.txt',
        describe: 'Path to the input file'
      },
      body: {
        type: 'string',
        default: '{}',
        describe: 'Request body as a JSON string'
      }
    }).argv;

    // 从文件中读取文本内容
    const fileContent = await fs.promises.readFile(argv.file, 'utf8');

    // 将文本内容压缩为一行
    const compressedContent = fileContent.replace(/\s+/g, ' ').trim();

    // 解析请求正文
    const requestBody = JSON.parse(argv.body);

    // 向 Cloud Function 发送请求进行验证
    const response = await axios.post('https://us-central1-your-project-id.cloudfunctions.net/verifyText',
     requestBody, {
        headers: {
            'Content-Type': 'application/json'
        }
    });

    console.log('Verification result:', response.data);
  } catch (error) {
    console.error('Error:', error);
  }
}

compressAndVerify();