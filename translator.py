import googletrans
# The default googletrans package has not been updated in years and currently
# has a bug in it. You can fix this by installing the alpha release:
# pip install googletrans==3.1.0a0

import sys
import os
import socket
import json
import time


"""
This app will translate any text from one language to another.
Type 'python translator.py -h' or 'translator -h' in terminal for help.

Author: DsoftN
"""

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 29975
SERVER_BACKLOG = 5

TRANSLATE_MAX_LENGTH = 1500
TRANSLATE_PAUSE_TIME_SEC = 1.5

ARG_HELP = ["--h", "-h", "h", "--help", "-help", "help", "--info", "-info", "info", "?"]
ARG_VERSION = ["--v", "-v", "v", "--version", "-version", "version", "--ver", "-ver", "ver"]
ARG_LANGUAGES = ["--l", "-l", "l", "--languages", "-languages", "languages", "--lang", "-lang", "lang", "--langs", "-langs", "langs", "--list", "-list", "list", "--list_languages", "-list_languages", "list_languages", "--list_langs", "-list_langs", "list_langs", "--supported_languages", "-supported_languages", "supported_languages", "--supported_langs", "-supported_langs", "supported_langs", "--supported", "-supported", "supported"]
ARG_DETECT = ["--d", "-d", "d", "--detect", "-detect", "detect", "--det", "-det", "det"]
ARG_OVERWRITE = ["--o", "-o", "o", "--overwrite", "-overwrite", "overwrite", "--ow", "-ow", "ow"]
ARG_TEXT = ["text", "t", "tekst", "string", "str"]
ARG_INPUT = ["input", "i", "input_file", "file", "input_file_path", "file_path", "load", "load_file", "load_file_path", "read", "read_file", "read_file_path", "get", "get_file", "get_file_path", "inputfile", "inputfilepath", "from_file", "fromfile"]
ARG_OUTPUT = ["output", "o", "output_file", "output_file_path", "save", "save_file", "save_file_path", "write", "write_file", "write_file_path", "savetofile", "savetofilepath", "outputfile", "outputfilepath", "to_file", "tofile"]
ARG_FROM = ["from", "from_language", "from_lang", "language_from", "lang_from"]
ARG_TO = ["to", "to_language", "to_lang", "language_to", "lang_to"]
ARG_START_SERVER = ["--start_server", "-start_server", "start_server", "--server", "-server", "server", "--host", "-host", "host"]

ALL_ARGUMENTS = ARG_HELP + ARG_VERSION + ARG_DETECT + ARG_OVERWRITE + ARG_TEXT + ARG_INPUT + ARG_OUTPUT + ARG_FROM + ARG_TO + ARG_START_SERVER

SERVER_SHUTDOWN_COMMAND = ["exit", "quit", "q", "stop", "shutdown"]

# Set default values
text = None
from_language = None
to_language = None
input_file = None
output_file = None
can_overwrite = False


def main():
    global text, from_language, to_language, input_file, output_file, can_overwrite

    # Execute args that dont require translation
    execute_arguments(sys.argv)
    # execute_arguments(["translator", 'text="neki moj tekst"', "to=ee"])

    # Check if all required arguments are provided

    # Check if text or file is provided
    if not text and not input_file:
        show_error_and_exit("Nothing to translate. Please provide text or input file.")
    if input_file is not None and not is_file_exist(input_file):
        show_error_and_exit("Input file does not exist.")

    # Check if output file is provided
    if output_file is not None:
        if is_file_exist(output_file) and not can_overwrite:
            show_error_and_exit("Output file already exists. Use -o flag to overwrite.")

    # Check language to translate from
    detected_lang_text = None
    detected_lang_file = None
    if from_language is None:
        if text is not None:
            detected_lang_text = detect_language(text)
            if not (int(detected_lang_text[1]) > 0):
                show_error_and_exit("Unable to detect language from text.")
            detected_lang_text = detected_lang_text[0]
        elif input_file is not None:
            detected_lang_file = detect_language(load_text_from_file(input_file))
            if not (int(detected_lang_file[1]) > 0):
                show_error_and_exit("Unable to detect language from file.")
            detected_lang_file = detected_lang_file[0]
        else:
            show_error_and_exit("There is no text or file to detect language from.")
    else:
        if from_language in googletrans.LANGUAGES:
            detected_lang_text = from_language
            detected_lang_file = from_language
        else:
            if from_language in googletrans.LANGCODES:
                from_language = googletrans.LANGCODES[from_language]
                detected_lang_text = from_language
                detected_lang_file = from_language
            else:
                if text is not None:
                    detected_lang_text = detect_language(text)
                    if not (int(detected_lang_text[1]) > 0):
                        show_error_and_exit("Unable to detect language from text.")
                    detected_lang_text = detected_lang_text[0]
                elif input_file is not None:
                    detected_lang_file = detect_language(load_text_from_file(input_file))
                    if not (int(detected_lang_file[1]) > 0):
                        show_error_and_exit("Unable to detect language from file.")
                    detected_lang_file = detected_lang_file[0]
                else:
                    show_error_and_exit("There is no text or file to detect language from.")

    # Check language to translate to
    if to_language is None:
        show_error_and_exit("Please provide a language to translate to.")
    if to_language not in googletrans.LANGUAGES:
        if to_language in googletrans.LANGCODES:
            to_language = googletrans.LANGCODES[to_language]
        else:
            show_error_and_exit("Invalid language to translate to.")

    # Translate text or file
    if text is not None:
        translated_text = translate_text(text, detected_lang_text, to_language)
        if output_file is not None and input_file is None:
            save_text_to_file(output_file, translated_text)
            print(f"Translated text saved to '{output_file}'")
        else:
            print(translated_text)
    if input_file is not None:
        translated_text = translate_text(load_text_from_file(input_file), detected_lang_file, to_language)
        if output_file is not None:
            save_text_to_file(output_file, translated_text)
            print(f"Translated text from '{input_file}' saved to '{output_file}'")
        else:
            print(translated_text)
    

def handle_client(client_socket: socket.socket):
    status = ""
    try:
        # Receive JSON size
        size_data = b""
        while b"\n" not in size_data:
            size_data += client_socket.recv(1)

        size_data = size_data.decode('utf-8').strip()

        try:
            expected_size = int(size_data)
        except ValueError:
            print(f"Invalid JSON size: {size_data}")
            return

        # Receive JSON
        received_data = b""
        while len(received_data) < expected_size:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            received_data += chunk
        
        
        try:
            if received_data.decode('utf-8').lower().lower() in SERVER_SHUTDOWN_COMMAND:
                print("Server shutting down...")
                client_socket.close()
                sys.exit(0)
        except UnicodeDecodeError as e:
            print(f"Error decoding JSON: {e}")
            status += "Error decoding JSON: " + str(e) + "\n"
        
        # Parse JSON
        request_data = {}
        try:
            request_data = json.loads(received_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f"Error in JSONDecoder: {e}")
            status += "Error in JSONDecoder: " + str(e) + "\n"

        # Check Language Codes
        language_from = ""
        language_to = ""
        if status == "":
            if request_data.get('from', "").lower() in googletrans.LANGUAGES:
                language_from = request_data.get('from', "").lower()
            else:
                if request_data.get('from', "").lower() in googletrans.LANGCODES:
                    language_from = googletrans.LANGCODES[request_data.get('from', "").lower()]
                else:
                    status += "Invalid language code from: " + request_data['from'] + "\n"
            if request_data.get('to', "").lower() in googletrans.LANGUAGES:
                language_to = request_data['to'].lower()
            else:
                if request_data.get('to', "").lower() in googletrans.LANGCODES:
                    language_to = googletrans.LANGCODES[request_data.get('to', "").lower()]
                else:
                    status += "Invalid language code to: " + request_data['to'] + "\n"

        # Translation
        translated_text = ""
        if status == "":
            translated_text = translate_text(request_data.get('text', ""), language_from, language_to)
        
        if status == "":
            status = "OK"
        response_data = {"translated_text": translated_text, "status": status}

        # Send response to client
        try:
            # Send JSON size
            json_response = json.dumps(response_data)
            response_bytes = json_response.encode('utf-8')
            size = len(response_bytes)
            client_socket.send(f"{size}\n".encode('utf-8'))

            # Send JSON
            client_socket.sendall(response_bytes)

        except Exception as e:
            print(f"Error. Client disconnected?: {e}")
            return

    except KeyboardInterrupt:
        print("Server shutting down...")
        client_socket.close()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        return
    finally:
        client_socket.close()

def start_server():
    # Start server - check if port is already in use
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen(SERVER_BACKLOG)
        print("Server started and listening on port 29975...")
    except OSError as e:
        print(f"Error: {e}")
        print("Port is already in use. Is another instance running?")
        sys.exit(1)

    # Handle clients
    while True:
        client_socket, address = server.accept()
        print(f"New client connected: {address}")
        handle_client(client_socket)

def execute_arguments(args):
    global text, from_language, to_language, input_file, output_file, can_overwrite

    if not args:
        show_error_and_exit("Unexpected error. Command line arguments are empty.")
        return
    elif len(args) == 1:        
        show_error_and_exit("No arguments provided.")
        return
    
    args = args[1:]

    # If command line contains only one argument
    if len(args) == 1:
        arg: str = args[0]
        arg = arg.lower()

        if arg in ARG_HELP:
            show_help()
            sys.exit(0)
        elif arg in ARG_VERSION:
            show_version()
            sys.exit(0)
        elif arg in ARG_LANGUAGES:
            show_supported_languages()
            sys.exit(0)
        elif arg in ARG_DETECT:
            show_error_and_exit("Nothing to detect. Please provide text or input file.")
        elif arg in ARG_OVERWRITE:
            show_error_and_exit("Nothing to overwrite. Please provide input and output files.")
        elif arg in ARG_START_SERVER:
            start_server()
            sys.exit(0)

    # If command line contains two arguments and one of them is "-d"
    if len(args) == 2:
        if args[0].lower() in ARG_DETECT:
            arg = args[1]
        elif args[1].lower() in ARG_DETECT:
            arg = args[0]
        else:
            arg = None

        if arg is None:
            pass
        elif "=" in arg:
            argument = arg.split("=")[0].lower()
            value = arg.split("=")[1].strip("'\"")
            if argument in ARG_TEXT:
                detected = detect_language(value)
                show_detected(detected)
                sys.exit(0)
            elif argument in ARG_INPUT:
                value = load_text_from_file(value)
                detected = detect_language(value)
                show_detected(detected)
                sys.exit(0)
            else:
                show_error_and_exit(f"Expected text or input file. Unknown argument: {truncate(argument)}")
        else:
            if (arg not in ALL_ARGUMENTS):
                detected = detect_language(arg[1:-1])
                show_detected(detected)
                sys.exit(0)
            else:
                show_error_and_exit(f"Expected text or input file. Invalid argument: {truncate(arg)}")

    # If command line contains more than one argument
    for arg in args:
        if arg.lower() in ARG_OVERWRITE:
            can_overwrite = True
        elif "=" in arg:
            argument = arg.split("=")[0].lower()
            value = arg.split("=")[1].strip("'\"")
            if argument in ARG_TEXT:
                text = value
            elif argument in ARG_FROM:
                from_language = value
            elif argument in ARG_TO:
                to_language = value
            elif argument in ARG_INPUT:
                input_file = value
            elif argument in ARG_OUTPUT:
                output_file = value
            else:
                show_error_and_exit(f"Unknown argument: {truncate(argument)}")
        else:
            if (arg.lower() in ARG_HELP) or (arg.lower() in ARG_VERSION) or (arg.lower() in ARG_DETECT):
                show_error_and_exit(f"Unexpected argument: {truncate(arg)}")
            else:
                show_error_and_exit(f"Invalid argument: {truncate(arg)}")

    return

def truncate(text, max_length=65, return_length=60, invisible_text="..."):
    if len(text) > max_length:
        result = text[:int(return_length * 0.8)] + invisible_text
        result += text[-(return_length - len(result)):]
        return result
    else:
        return text

def translate_text(text, trans_from_language, trans_to_language):
    result = ""
    translator = googletrans.Translator()

    text_chunks = split_text(text)
    for idx, text_chunk in enumerate(text_chunks):
        try:
            translated_text = translator.translate(text_chunk, src=trans_from_language, dest=trans_to_language).text
            result += translated_text
            # Add pause if more chunks has left to be translated
            if idx < len(text_chunks) - 1:
                time.sleep(TRANSLATE_PAUSE_TIME_SEC)

        except Exception as e:
            show_error_and_exit(f"Failed to translate text. {e}")

    return result

def split_text(text: str, max_length: int = TRANSLATE_MAX_LENGTH, minimum_chunk_length_percent_of_max_length: int = 10) -> list[str]:
    if len(text) <= max_length:
        return [text]
    
    result = []

    # Split points sorted from most important to least important
    split_points = ["\n", ".", "!", "?", " "]

    # Try to split text by most important split points
    while text:
        pos = max_length
        if len(text) <= max_length:
            result.append(text)
            break

        for split_point in split_points:
            pos = text.rfind(split_point, 0, max_length)

            if pos == -1 or pos < (max_length * minimum_chunk_length_percent_of_max_length // 100):
                continue

            result.append(text[:pos + 1])
            text = text[pos + 1:]
            break
        else:
            result.append(text[:max_length])
            text = text[max_length:]

    return result

def detect_language(text):
    try:
        translator = googletrans.Translator()
        detected_language = translator.detect(text).lang
        confidence = translator.detect(text).confidence
        return (detected_language, confidence)
    except Exception as e:
        show_error_and_exit(f"Failed to detect language. {e}")

def show_supported_languages():
    print("SUPPORTED LANGUAGES:\n")
    for language_code in googletrans.LANGUAGES:
        print(f"{googletrans.LANGUAGES[language_code].capitalize()} ({language_code})")

def show_detected(detected_language):
    print("DETECTED LANGUAGE: ", end="")
    if detected_language[0] in googletrans.LANGUAGES:
        if int(detected_language[1]) > 0:
            print(f"{googletrans.LANGUAGES[detected_language[0]].capitalize()} ({detected_language[0]}) (confidence: {int(detected_language[1] * 100)} %)")
        else:
            print("Unknown language (?)")
    else:
        print("?")

def load_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    except Exception as e:
        show_error_and_exit(f"Failed to load text from file. {e}")

def save_text_to_file(file_path, text):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        show_error_and_exit(f"Failed to save text to file. {e}")

def is_file_exist(file_path):
    return os.path.isfile(file_path)

def show_help():
    help_message = """Translator v1.0 by DsoftN
This app will translate any text from one language to another.
[translator -ver] - show version
[translator -help] - show help
[translator -languages] - show list of supported language codes
[translator -detect text="Some text to translate"] - detect text language (returns "?" if not detected)
[translator -detect input="file_path"] - detect language from text file (returns "?" if not detected)
[translator text="Some text to translate" from="en" to="ru"] - translate text
[translator input="file_path" output="file_path" from="en" to="ru"] - save translated text to file
[translator -overwrite input="file_path" output="file_path" from="en" to="ru"] - overwrite output file
[translator -server] - start server and listen on localhost port 29975

MOST COMMON USAGE:

(1) Translate some text and show result in console:
    USAGE  : translator [text] [from_language] [to_language]
    EXAMPLE: translator text="This is a text i want to translate" from=en to=ru
    OUTPUT : "Это текст, который я хочу перевести" OR "ERROR: Something went wrong"

(2) Translate a text file and save the result to another file:
    USAGE  : translator [input=input_text_file_path] [output=output_text_file_path] [from_language] [to_language]
    EXAMPLE: translator input="input.txt" output="output.txt" from=en to=ru
    OUTPUT : "Translated text saved to output.txt" OR "ERROR: Something went wrong"
    NOTE   : If the output file already exists, an error message will be shown.
             If you want to overwrite the file, add the '-o' flag.
                 [translator -o input="input.txt" output="output.txt" from=en to=ru]
             If error occurs, the created output file will contain only the error message.

SERVER USAGE:
1)  Start TCP server: translator -server
2)  Make TCP Client in your app and send data to 127.0.0.1:29975
3)  First send size of JSON, string containing JSON size in bytes ended with \\n
4)  Then send JSON, {"text": "This is a text i want to translate", "from": "en", "to": "ru"}
5)  If you want to shutdown the server, send string "quit" instead of JSON
6)  Wait for server response
7)  Response will be size of JSON, string containing JSON size in bytes ended with \\n
8)  Then server will send JSON, {"translated_text": "Это текст, который я хочу перевести", "status": "OK"}
"""
    
    print(help_message)

def show_version():
    print("Translator v1.0 by DsoftN")

def show_error_and_exit(error_message):
    print("Translator v1.0 by DsoftN")
    print("Error: ", error_message)
    print("")
    print("Type 'translator -h' for help.")

    sys.exit(1)


if __name__ == '__main__':
    main()

    


