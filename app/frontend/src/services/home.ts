import client from '../utils/client';

export const getDocuments = () => {
    return client.get('/get_documents');
};

export const getAnswer = ({ question }: { question: string }) => {
    return client.post('/query', {
        data: question,
    });
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