import axios from 'axios';
import config from '../config';
import Authentication from '../auth';

const client = axios.create({
    baseURL: config.backendUrl,
    timeout: 600000,
    headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
    },
});

client.interceptors.request.use(async (req) => {
    let token = await Authentication.getToken();
    req.headers['Authorization'] = token;
    return req;
});

client.interceptors.response.use(
    (response) => {
        return response.data;
    },
    (error) => {
        const errorMessage =
            'An internal error occurred. Please try again in a few seconds.';
        if (
            error.response === undefined ||
            error.response.status === undefined ||
            error.response.status >= 500
        ) {
            return Promise.reject(errorMessage);
        } else {
            if (error.response.status === 401) {
                Authentication.doLogout();
                return Promise.reject('Login required.');
            } else if (error.response.status === 403)
                return Promise.reject(
                    'You do not have the right to perform this operation.'
                );
            else
                return Promise.reject(
                    error.response &&
                        error.response.data &&
                        error.response.data.error
                        ? error.response.data.error
                        : errorMessage
                );
        }
    }
);

export default client;
