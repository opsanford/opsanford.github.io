import sys
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
            body = b""
            try:
                while not b"\r\n\r\n" in request:
                    tmp= client_socket.recv(1024)
                    if not tmp:
                        raise TimeoutError("No data received")
                    request += tmp
                if request[-4:] != b"\r\n\r\n":
                    # assuming there is a body
                    request, body = request.split(b"\r\n\r\n")
                request = request.decode("utf-8")

                # read request body
                content_length = 0
                for line in request.split("\r\n"):
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":")[1].strip())
                        break
                if content_length == 0: body = b""
                while len(body) < content_length:
                    tmp = client_socket.recv(min(1024, content_length - len(body)))
                    if not tmp:
                        raise TimeoutError("No data received")
                    body += tmp
                body = body.decode("utf-8")
                if body: print("\nRequest body:\n" + body)

            except (UnicodeDecodeError, TimeoutError):
                traceback.print_exc()
                continue

            print(f"Request was:\n{request}")

            # Handle request
            response = self.handle_request(request, body)

            client_socket.sendall(response)
            client_socket.close()

    def handle_request(self, request, body):

        response = f"Thank you for your request:\n\n{request}"
        if body: response += "\r\n\r\n" + body
        response = response.encode("utf-8")

        headers = "HTTP/1.1 200 OK\r\n"
        headers += f"Content-Length: {len(response)}\r\n"
        headers += "Content-Type: text/plain\r\n\r\n"
        headers = headers.encode("utf-8")

        return headers + response

def main(args):
    port = 8080
    if len(args) > 1:
        port = int(args[1])
    server = Server(port)
    server.run()

if __name__ == "__main__":
    main(sys.argv)
