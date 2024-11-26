# Translator

Translator is a simple command-line app that allows you to translate text from one language to another.
Translator can also be used as TCP Server if you want to use it as a service for other applications.

## Features
- Translator v1.0 by DsoftN
- This app will translate any text from one language to another.
- [translator -ver] - show version
- [translator -help] - show help
- [translator -languages] - show list of supported language codes
- [translator -detect text="Some text to translate"] - detect text language (returns "?" if not detected)
- [translator -detect input="file_path"] - detect language from text file (returns "?" if not detected)
- [translator text="Some text to translate" from="en" to="ru"] - translate text
- [translator input="file_path" output="file_path" from="en" to="ru"] - save translated text to file
- [translator -overwrite input="file_path" output="file_path" from="en" to="ru"] - overwrite output file
- [translator -server] - start server and listen on localhost port 29975

## Most Common Usage:

(1) Translate some text and show result in console:
-     USAGE  : translator [text] [from_language] [to_language]
-     EXAMPLE: translator text="This is a text i want to translate" from=en to=ru
-     OUTPUT : "Это текст, который я хочу перевести" OR "ERROR: Something went wrong"

(2) Translate a text file and save the result to another file:
-     USAGE  : translator [input=input_text_file_path] [output=output_text_file_path] [from_language] [to_language]
-     EXAMPLE: translator input="input.txt" output="output.txt" from=en to=ru
-     OUTPUT : "Translated text saved to output.txt" OR "ERROR: Something went wrong"
-     NOTE   : If the output file already exists, an error message will be shown.
             If you want to overwrite the file, add the '-o' flag.
                 [translator -o input="input.txt" output="output.txt" from=en to=ru]
             If error occurs, the created output file will contain only the error message.

## Server Usage:
1)  Start TCP server: translator -server
2)  Make TCP Client in your app and send data to 127.0.0.1:29975
3)  First send size of JSON, string containing JSON size in bytes ended with \\n
4)  Then send JSON, {"text": "This is a text i want to translate", "from": "en", "to": "ru"}
5)  If you want to shutdown the server, send string "quit" instead of JSON
6)  Wait for server response
7)  Response will be size of JSON, string containing JSON size in bytes ended with \\n
8)  Then server will send JSON, {"translated_text": "Это текст, который я хочу перевести", "status": "OK"}

## Requirements
- Python 3.10 or higher
- pip install -r requirements.txt

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for suggestions and improvements.

Feel free to explore, fork, and share your feedback!
