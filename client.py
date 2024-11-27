import socket
import json

def translator_client(text_to_translate: str, from_language: str, to_language: str, silent: bool = False) -> str:
    if text_to_translate is None:
        text_to_translate = ""
    if from_language is None:
        from_language = ""
    if to_language is None:
        to_language = ""

    # Connect to server
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 29975))
        if not silent:
            print("Client connected to server...")
    except OSError as e:
        print(f"Error: {e}")
        print("Could not connect to server. Is the server running?")
        return None

    # Creating JSON request to be translated from english to serbian cyrillic
    # ---------------------------------------------------------------------
    request_data = {
        "text": text_to_translate,
        "from": from_language,
        "to": to_language}
    
    json_request = json.dumps(request_data)

    # If you want to shutdown the server enable line below
    json_request = "quit"
    # ---------------------------------------------------------------------

    if not silent:
        print(f"Client Request: {json_request}")

    size = len(json_request)

    # Sending JSON size
    client.send(f"{size}\n".encode('utf-8'))

    # Sending JSON
    client.sendall(json_request.encode('utf-8'))

    # If you enabled line: json_request = "quit", code below will be executed
    if json_request == "quit":
        client.close()
        if not silent:
            print("Client is shutting down...")
        exit()

    # Receiving response size
    size_data = b""
    while b"\n" not in size_data:
        size_data += client.recv(1)

    size_data = size_data.decode('utf-8').strip()
    response_size = int(size_data)

    # Receiving JSON response
    response_data = b""
    while len(response_data) < response_size:
        response_data += client.recv(1024)

    # Print response
    response_json = json.loads(response_data.decode('utf-8'))
    if not silent:
        print(f"Server Response: {response_json}")
        print(f"Status: {response_json['status']}")
    client.close()

    return response_json.get("translated_text")


if __name__ == "__main__":
    # Usage example
    # --- First start the server and then run this code ---
    #
    # How to start the server?
    # 1. Open terminal
    # 2. Navigate to the folder where the server is located
    # 3. Run the command: python translator.py -server
    # 4. The server will start and listen on localhost port 29975
    #
    # How to use the client?
    # 1. Open terminal
    # 2. Navigate to the folder where the client is located
    # 3. Run the command: python client.py
    # 4. The client will connect to the server and translate the text
    #
    # Note: To start server you can use executable file translator.exe
    #    Run command in terminal: translator.exe -server

    translated_text = translator_client(
        text_to_translate="Hello, this is a test. Purpose of this test is to check if the server is working and if the translation is correct.",
        from_language="en",
        to_language="sr",
        silent=False
        )
    
    print("")
    print(translated_text)
    print("")



    