import os
import logging
from requests import get

from suno.client import suno_client
from telegram.bot_config import API_URL, LAST_UPDATE_ID, BOT_LOG_PATH, NAME


if not os.path.exists('logs'):
    os.mkdir("logs")

logging.basicConfig( handlers=[ logging.FileHandler(BOT_LOG_PATH) ], format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)



def message_is_for_chatbot(message):
    if message.get("chat").get("type") == "private" or message.get("text").startswith('/'):
            return True    
    return False


# send message to private chat and reply to group chat
def sendMessage(chat_id, message, reply_id = None): 
    
    json = {
        "chat_id" : chat_id, 
        "text" : message, 
        "parse_mode" : "html",
    }
    
    if reply_id:
        json["reply_to_message_id"] = reply_id
    
    return get(API_URL + "sendMessage", json = json)
    # return get(API_URL + f"sendMessage?chat_id={id}&text={quote(message)}&parse_mode=html")
    # return get(API_URL + f"sendMessage?chat_id={chat_id}&text={parse_for_url(message)}&reply_to_message_id={reply_id}&parse_mode=html")

# get updates
def get_updates():
    
    global LAST_UPDATE_ID
    
    updates = get( API_URL + f"getUpdates?offset={LAST_UPDATE_ID+1}&timeout=100")
    
    logging.info(updates.json())

    latest_updates = updates.json()["result"]

    if len(latest_updates):
        LAST_UPDATE_ID = latest_updates[-1]["update_id"]
        logging.info(f"{len(latest_updates)} Updates fetched with LAST_UPDATE_ID = {LAST_UPDATE_ID}")
        
    return latest_updates


# filter received messages
def get_messages(updates):
    new_messages = []
    for update in updates:
        message = update.get("message", update.get("channel_post", None))
        if message and message_is_for_chatbot(message):
                new_messages.append(message)
    return new_messages

def main():

    print("checking for new message...", end='')
    logging.info("checking for new message")
    
    latest_messages = get_messages(get_updates())
    print("", end = "\r")
    
    for message in latest_messages:
        
        logging.info(f"responding to - {message}")
        
        message_content = message["text"]
        if message_content == "/start":
            response = f"Hi, I am {NAME}. Type the prompt to generate the song or /help for detailed help."
        elif message_content == "/help":
            response = "/generate <prompt>. Example /generate good song to sleep to."
        elif message_content.startswith("/generate"):
            prompt = message_content[9:].strip()
            if not prompt:
                response = "Enter your song prompt"
            else:
                client = suno_client()
                songs = client.get_songs(prompt)
                response = songs[0]
        else:
            client = suno_client()
            songs = client.get_songs(message_content)
            response = songs[0]
        response = str(response)
        
        chat_id = message.get("chat").get("id")
        print(message_content, "|", response, "|", chat_id)
    
        receiver = None
        if message.get("chat").get("type") != "private":
            receiver = message.get("message_id")
        
        res = sendMessage(chat_id, response, receiver).json()
        logging.info(f"response callback -{res}")
        
        if res.get("ok"):
            print("messege sending success")
        else:
            print("message sending Failed")
        
if __name__ == "__main__":
    while True:
        main()
