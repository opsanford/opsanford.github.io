#!/bin/python3

import socket
import os
import urllib
import traceback
from urllib.parse import unquote

text_file_extensions = {"html": "text/html", "css": "text/css", "js": "application/javascript",
"json": "application/json", "md": "text/markdown"}
for t in ["txt", "py", "bat", "java", "ini"]:
    text_file_extensions[t] = "text/plain"

binary_file_extensions = {"ico": "image/x-icon", "png": "image/png", "jpg": "image/jpeg",
"wasm": "application/wasm", "pdf": "application/pdf"}

class Server:

    def __init__(self, port: int):
        self.port = port
        # html file that is returned for empty HTTP GET requests
        self.default_page = "index.html"

    def run(self):
        """
        Run the server loop
        """
        # Create server socket using IPv4 addresses and TCP
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of port if we start program again after a crash
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Say on which machine and port we want to listen to connections
        host = socket.gethostname()
        server_address = ("0.0.0.0", self.port)
        try:
            server_socket.bind(server_address)
        except PermissionError:
            return "socket_permission"
        # Start listening
        server_socket.listen()

        while True:
            print()
            print(f"Waiting for incoming request on {host}:{self.port}")
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
                while len(body) < content_length:
                    tmp = client_socket.recv(min(1024, content_length - len(body)))
                    if not tmp:
                        raise TimeoutError("No data received")
                    body += tmp
                body = body.decode("utf-8")
                print("Request body:")
                print(body)
            except (UnicodeDecodeError, TimeoutError):
                traceback.print_exc()
                continue

            print(request)

            # We are only interested in the first line and the part after
            # the GET/ and before the "HTTP/1.1"
            request = request.split("\r\n")[0]
            keyword = request.split(" ")[0]
            request = request.split(" ")[1]
            request = request.split("HTTP")[0]
            request = request[1:]
            print(f"Received {keyword} request for {request}")

            if request.startswith("api/"):
                response = self.handle_api_request(keyword, request[4:], body)

            elif keyword == "GET":
                # Handle GET request
                response = self.handle_get_request(request)
            else:
                response = f"Bad request: {request}".encode("utf-8")
                response = create_headers(response, "204 No Content", "text/plain") \
                       + response

            client_socket.sendall(response)
            client_socket.close()

    def handle_get_request(self, request):

        if request == "": request = self.default_page

        status_code = "200 OK"
        media_type = "text/plain"
        response = f"Bad request: {request}".encode("utf-8")

        try :
            filepath = unquote(request)
            if filepath.startswith("/") or ".." in filepath:
                return create_text_response("Nope", "403 Forbidden")

            file_extension = filepath.split(".")[-1]

            if file_extension in text_file_extensions:
                with open(filepath, "rt") as file:
                    response = file.read().encode("utf-8")
                media_type = text_file_extensions[file_extension]
            elif file_extension in binary_file_extensions:
                with open(filepath, "rb") as file:
                    response = file.read()
                media_type = binary_file_extensions[file_extension]

        except (FileNotFoundError, OSError):
            return create_text_response(f"File {filepath} not found",
                                        "404 Not found")

        headers = create_headers(response, status_code, media_type)
        return headers + response

    def handle_api_request(self, keyword, request, body):
        spl = request.split("?")
        api_method = spl[0]
        if len(spl) > 1: options = process_api_options(spl[1])
        else: options = dict()

        if api_method == "search":
            if not "query" in options:
                return create_text_response("Missing query!", "400 Bad request")
            result = search(options["query"])
            return create_text_response(result)

        return create_text_response("Unknown api method:\n" + request, "404 Not found")

def create_text_response(text : str, status_code = "200 OK") -> bytes:
    response = text.encode("utf-8")
    headers = create_headers(response, status_code, "text/plain")
    return headers + response

def create_headers(response, status_code, media_type) -> bytes:

    headers = f"HTTP/1.1 {status_code}\r\n"
    headers += f"Content-Length: {len(response)}\r\n"
    headers += f"Content-Type: {media_type}\r\n"
    headers += "\r\n"
    headers = headers.encode("utf-8")
    return headers

def process_api_options(option_str) -> dict[str, str]:
    options = dict()
    for part in option_str.split("&"):
        if not "=" in part: continue
        key, value = part.split("=")
        options[unquote(key)] = unquote(value)
    return options

def search(query) -> str:
    try:
        print(f"Searching for {query}")
        query_parts = query.split("/")
        query_end = query_parts[-1]
        directory_path = query[:len(query)-len(query_end)]
        if not directory_path: directory_path = "."
        files = os.listdir(directory_path)

        if len(query_end) != 0:
            response = []
            for file in files:
                if query_end in file:
                    response.append(file)
        else:
            response = files
        return str(response)
    except Exception as e:
        traceback.print_exc()
        return "Error: " + str(e)

def main(port = 80):
    # Port: 80 for standard HTTP (but requires sudo / admin), 8080 else
    server = Server(port)
    error = server.run()

    # if we arrive here, something went wrong
    if error == "socket_permission":
        main(port = 8080)

if __name__ == "__main__":
    main()
