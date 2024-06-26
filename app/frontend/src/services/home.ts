import client from '../utils/client';

export const getDocuments = () => {
    return client.get('/api/get_documents');
};

export const getDocumentsById = (source: string) => {
    return client.get(`/api/get_documents_by_id?id=${source}`);
};

export const deleteDocument = (id: string) => {
    return client.delete(`/api/delete_document?id=${id}`);
};

export const uploadFile = (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return client.post('/api/ingest', formData, {
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
    return client.post('/api/ingest_feedback', {
        feedbackType,
        feedbackText,
        feedbackTo,
        email,
    });
};
