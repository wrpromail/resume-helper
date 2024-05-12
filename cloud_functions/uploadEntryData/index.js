const functions = require('@google-cloud/functions-framework');
const { Firestore } = require('@google-cloud/firestore');
const { v4: uuidv4 } = require('uuid');
const Joi = require('joi');

const db = new Firestore();
const DEFAULT_COLLECTION = process.env.DEFAULT_COLLECTION || 'feedback';

const dataEntrySchema = Joi.object({
    entry_id: Joi.string().optional(),
}).unknown(true);

functions.http('uploadDataEntry', async (req, res) => {
    if (req.method === 'POST') {
        handlePostRequest(req, res);
    } else if (req.method === 'GET') {
        res.status(200).json({ message: `Default Collection Name: ${DEFAULT_COLLECTION}` });
    } else {
        res.status(405).json({ message: 'Method Not Allowed' });
    }
});

async function handlePostRequest(req, res) {
    try {
        const collectionName = req.body.collection_name || DEFAULT_COLLECTION;
        const data = req.body.payload;

        if (!data) {
            res.status(400).json({ error: 'Payload is required.' });
            return;
        }
        const { error, value } = Array.isArray(data) ? Joi.array().items(dataEntrySchema).validate(data) : dataEntrySchema.validate(data);
        if (error) {
            res.status(400).json({ error: `Validation error: ${error.details.map(d => d.message).join(', ')}` });
            return;
        }
        if (Array.isArray(value)) {
            await handleBatchWrite(value, collectionName);
            res.status(200).json({ message: 'Batch data written to Firestore successfully!' });
        } else {
            const entryId = value.entry_id || uuidv4();
            const docRef = db.collection(collectionName).doc(entryId);
            await docRef.set(value);
            res.status(200).json({ message: 'Data written to Firestore successfully!' });
        }
    } catch (error) {
        res.status(500).json({ error: 'Failed to write data', details: error.toString() });
    }
}

async function handleBatchWrite(dataArray, collectionName) {
    const batch = db.batch();
    dataArray.forEach((item) => {
        const docRef = db.collection(collectionName).doc(item.entry_id || uuidv4());
        batch.set(docRef, item);
    });
    await batch.commit();
}