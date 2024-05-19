# clipboard_to_api.py

import os
import pyperclip
import requests
import time
from threading import Event

def get_clipboard_content_after_target(target: str) -> str:
    """
    Extracts the string after the target from the clipboard content.
    
    Args:
        target (str): The string to search for in the clipboard content.
    
    Returns:
        str: The string after the target in the clipboard content or an empty string if target is not found.
    """
    clipboard_content = pyperclip.paste()
    target_index = clipboard_content.find(target)
    if target_index != -1:
        return clipboard_content[target_index + len(target):].strip()
    return ""

url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}

waiting_for_response = Event()

def main_loop() -> None:
    """
    Main loop to continuously check clipboard content for a target string,
    send a request to the API with the extracted message, and handle the response.
    """
    global waiting_for_response

    target_prefix = os.getenv("TARGET_PREFIX", "#¤")

    while True:
        if not waiting_for_response.is_set():
            # Get user message from clipboard after target_prefix
            user_message = get_clipboard_content_after_target(target_prefix)
            print(user_message)
            if user_message:
                history = []
                pyperclip.copy("loading")  # Write "loading" to clipboar
                history.append({"role": "user", "content": user_message})
                data = {
                    "mode": "chat",
                    "character": "Example",
                    "messages": history
                }

                waiting_for_response.set()

                try:
                    response = requests.post(url, headers=headers, json=data, verify=False)
                    response.raise_for_status()
                    assistant_message = response.json()['choices'][0]['message']['content']
                    print(assistant_message)
                    pyperclip.copy(assistant_message)  # Write "loading" to clipboard 
                except requests.RequestException as e:
                    print(f"API request failed: {e}")
                
                waiting_for_response.clear()

        time.sleep(1)

if __name__ == "__main__":
    main_loop()
