import config from '../config.js';
import authService from '../auth.js'; // Assuming you have the auth service from your Keycloak integration

class SocketService {
    private socket: WebSocket;

    constructor() {
        this.socket = new WebSocket(config.backendUrl + '/ws/query');
        this.setupSocket();
    }

    private setupSocket() {
        this.socket.addEventListener('open', () => {
            const userId = authService.getUserId(); // Get user ID from auth service
            if (userId) {
                // Send the user ID to the server upon connection
                this.socket.send(JSON.stringify({ type: 'init', userId }));
            }
        });

        this.socket.addEventListener('message', (event) => {
            const response = JSON.parse(event.data);
            console.log(response);
            // Handle the response as needed
        });
    }

    public sendMessage(message: string) {
        const userId = authService.getUserId(); // Retrieve user ID before sending a message
        this.socket.send(JSON.stringify({ data: message, userId }));
    }

    public closeSocket() {
        this.socket.close();
    }
}

const homeService = new SocketService();
export default homeService;
