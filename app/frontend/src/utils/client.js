import axios from 'axios';
import config from '../config.js';

const client = axios.create({
    baseURL: config.backendUrl,
    timeout: 600000,
    headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
    },
});

client.interceptors.response.use(
    (response) => {
        return response.data;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default client;
