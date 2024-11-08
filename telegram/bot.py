from requests import get

from logger_config import get_logger
from suno.client import suno_client
from telegram.bot_config import API_URL, BOT_LOG_PATH, NAME



logger = get_logger(BOT_LOG_PATH)


class TelegramBot:

    def __init__(self) -> None:
        self.LAST_UPDATE_ID = -1


    def message_is_for_chatbot(self, message):
        if message.get("chat").get("type") == "private" or message.get("text").startswith('/'):
            return True
        return False


    def sendAudio(self, chat_id, audio, title, prompt):
        print(prompt, "|", audio, "|", title, "|", chat_id)

        res = get(API_URL + "sendAudio", data = {
            "chat_id" : chat_id, 
            "title" :  title,
            "performer": "Suno.com"
        }, files={
            "audio": get(audio).content,
        }).json()

        logger.info(f"response callback -{res}")
    
        if res.get("ok"):
            print("messege sending success")
        else:
            print("message sending Failed")


    # send message to private chat
    def sendMessage(self, chat_id, response, prompt):
        response = str(response)
        print(prompt, "|", response, "|", chat_id)
    
        res = get(API_URL + "sendMessage", json = {
            "chat_id" : chat_id, 
            "text" : response, 
            "parse_mode" : "html",
        }).json()

        logger.info(f"response callback -{res}")
    
        if res.get("ok"):
            print("messege sending success")
        else:
            print("message sending Failed")


    # get updates
    def get_updates(self):
                
        updates = get( API_URL + f"getUpdates?offset={self.LAST_UPDATE_ID+1}&timeout=100")
        
        logger.info(updates.json())

        latest_updates = updates.json()["result"]

        if len(latest_updates):
            self.LAST_UPDATE_ID = latest_updates[-1]["update_id"]
            logger.info(f"{len(latest_updates)} Updates fetched with LAST_UPDATE_ID = {self.LAST_UPDATE_ID}")
            
        new_messages = []
        for update in latest_updates:
            message = update.get("message", update.get("channel_post", None))
            if message and self.message_is_for_chatbot(message):
                new_messages.append(message)
        
        return new_messages
    

    def handle_message(self, message):
        logger.info(f"responding to - {message}")
            
        message_content = message["text"]
        chat_id = message.get("chat").get("id")

        if message_content == "/start":
            self.sendMessage(chat_id, f"Hi, I am {NAME}. Type the prompt to generate the song or /help for detailed help.", message_content)
        
        elif message_content == "/help":
            self.sendMessage(chat_id, "/generate <prompt>. Example /generate good song to sleep to.", message_content)
        
        else:
            if message_content.startswith("/generate"):
                message_content = message_content[9:].strip()
            
            if not message_content:
                self.sendMessage(chat_id, "Enter your song prompt", message_content)
            
            client = suno_client()
            for song_name, song_url in client.get_songs(message_content):
                self.sendAudio(chat_id, song_url, song_name, message_content)


    def run(self):
        while True:
            print("checking for new message...", end='')
            logger.info("checking for new message")
        
            latest_messages = self.get_updates()
            print("", end = "\r")
        
            for message in latest_messages:
                self.handle_message(message)