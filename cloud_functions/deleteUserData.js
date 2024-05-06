const functions = require('@google-cloud/functions-framework');
const { Firestore } = require('@google-cloud/firestore');

const firestore = new Firestore();

functions.http('deleteUserData', async (req, res) => {
    if (req.method !== 'DELETE') {
        res.status(405).send('Method Not Allowed');
        return;
    }

    const userId = req.query.userId; // 或者从 req.params 中获取，根据你的 URL 设计决定
    if (!userId) {
        return res.status(400).send('User ID is required');
    }

    try {
        await firestore.collection('user_info').doc(userId).delete();
        const collections = ['job_description', 'compare_result', 'basic_resume'];
        for (const collection of collections) {
            const snapshot = await firestore.collection(collection).where('user_id', '==', userId).get();
            snapshot.forEach(doc => {
                doc.ref.delete();
            });
        }
        res.send('User data deleted successfully');
    } catch (error) {
        console.error('Error deleting user data:', error);
        res.status(500).send('Error deleting user data');
    }
});