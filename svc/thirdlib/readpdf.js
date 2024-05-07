const pdfParse = require('pdf-parse');
const fs = require('fs');
/*
const path = require('path);
const windowsPath = path.join(...)
*/


const pdfFilePath = 'D:/resume-helper/TAM.pdf';

fs.readFile(pdfFilePath, async (err, pdfBuffer) => {
    if (err) {
        console.error(err);
        return;
    }

    try {
        const data = await pdfParse(pdfBuffer);
        console.log(data.text);
    } catch (error) {
        console.error(error);
    }
});