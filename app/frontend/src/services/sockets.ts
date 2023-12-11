// homeService.ts
class SocketService {
    private socket: WebSocket;

    constructor() {
        this.socket = new WebSocket('ws://localhost:8000/query');
        this.setupSocket();
    }

    private setupSocket() {
        this.socket.addEventListener('message', (event) => {
            const response = JSON.parse(event.data);
            console.log(response);
            // Handle the response as needed
        });
    }

    public sendMessage(message: string) {
        this.socket.send(JSON.stringify({ data: message }));
    }

    public closeSocket() {
        this.socket.close();
    }
}

const homeService = new SocketService();
export default homeService;
