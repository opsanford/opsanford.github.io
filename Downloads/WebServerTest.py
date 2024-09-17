import socket

class Server:

    def __init__(self, port: int):
        self.port = port

    def run(self):
        """
        Run the server loop
        """
        # Create server socket using IPv4 addresses and TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of port if we start program again after a crash
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Say on which machine and port we want to listen to connections
        server_address = ("0.0.0.0", self.port)
        server_socket.bind(server_address)
        # Start listening
        server_socket.listen()

        while True:
            print()
            print(f"Waiting for incoming request on port {self.port}")
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(5.0)
            print(f"Received request from {client_address}")

            # Read bytes from client in rounds
            request = b""
            while request.find(b"\r\n\r\n") == -1:
                request += client_socket.recv(1024)
            request = request.decode("utf-8")
            print(f"Request was: {request}")

            # Handle request
            response = self.handle_request(request)

            client_socket.sendall(response)
            client_socket.close()

    def handle_request(self, request):

        response = f"Thank you for your request: {request}" 
        response = response.encode("utf-8")

        headers = "HTTP/1.1 200 OK\r\n"
        headers += f"Content-Length: {len(response)}\r\n"
        headers += "Content-Type: text/plain\r\n"
        
        return response

def main():
    # Port should be 8080, but there are problems with windows permissions
    server = Server(80)
    server.run()

if __name__ == "__main__":
    main()
