import client from '../utils/client';

export const getDocuments = () => {
    return client.get('/get_documents');
};

export const getDocumentsById = (source: string) => {
    return client.get(`/get_documents_by_id?id=${source}`);
};

export const getAnswer = async ({ question }: { question: string }) => {
    try {
        const response = await client.post('/query', {
            data: question,
        });
        return response;
    } catch (error) {
        console.error('Error fetching answer:', error);
        throw error;
    }
};

export const deleteDocument = (id: string) => {
    return client.delete(`/delete_document?id=${id}`);
};

export const uploadFile = (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return client.post('/ingest', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};

export const uploadFeedback = (
    feedbackType: string,
    feedbackText: string,
    feedbackTo: string,
    email: string
) => {
    return client.post('/ingest_feedback', {
        feedbackType,
        feedbackText,
        feedbackTo,
        email,
    });
};
