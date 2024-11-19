import requests
import time
import uuid

from suno.suno_utils import get_suno_constants

SUNO_CONSTANTS = get_suno_constants()

class suno_client:

    def __init__(self) -> None:
        self.id = str(uuid.uuid4())
        self.song_ids = {}

    def get_auth_token(self):
        response = requests.request(
            SUNO_CONSTANTS.AUTH.METHOD,
            SUNO_CONSTANTS.AUTH.API_ENDPOINT,
            headers=SUNO_CONSTANTS.AUTH.HEADERS
        )

        if response.status_code == 200 and response.json().get("jwt"):
            print("Suno Auth Success")
            return response.json()["jwt"]
        
        raise Exception("Auth Failure. Check Cookie.")
        

    def generate_songs(self, telegram_prompt):
        payload = SUNO_CONSTANTS.GENERATE.BODY

        payload.update({
            "gpt_description_prompt": telegram_prompt,
        })
        print(payload)
        
        response = requests.request(
            SUNO_CONSTANTS.GENERATE.METHOD,
            SUNO_CONSTANTS.GENERATE.API_ENDPOINT,
            headers={
                "Authorization": f"{SUNO_CONSTANTS.GENERATE.AUTH_HEADER_TYPE} {self.get_auth_token()}",
                "Content-Type": SUNO_CONSTANTS.GENERATE.REQUEST_CONTENT_TYPE
            },
            json=payload
        )

        
        if not (response.status_code == 200 and response.json()):
            raise Exception("Auth Failure. Check Cookie.")
        
        generated_response = response.json()
        # generated_response = {"id": "97dcb5a7-a919-4697-955c-e6c613ace93e", "clips": [{"id": "51614f77-ff7f-4dbc-9d0c-b2cadd333731", "video_url": "", "audio_url": "", "is_video_pending": False, "major_model_version": "v3", "model_name": "chirp-v3", "metadata": {"prompt": "", "gpt_description_prompt": "a song love in hindi", "type": "gen", "stream": True}, "is_liked": False, "user_id": "8c6b1c92-3bb2-4a24-a3fd-68b7ef7da49f", "display_name": "CunningSoundDesigners6067", "handle": "cunningsounddesigners6067", "is_handle_updated": False, "avatar_image_url": "https://cdn1.suno.ai/defaultOrange.webp", "is_trashed": False, "created_at": "2024-11-08T17:08:56.613Z", "status": "submitted", "title": "", "play_count": 0, "upvote_count": 0, "is_public": False}, {"id": "9ca0539a-80c7-426a-b2ad-07e0292c593a", "video_url": "", "audio_url": "", "is_video_pending": False, "major_model_version": "v3", "model_name": "chirp-v3", "metadata": {"prompt": "", "gpt_description_prompt": "a song love in hindi", "type": "gen", "stream": True}, "is_liked": False, "user_id": "8c6b1c92-3bb2-4a24-a3fd-68b7ef7da49f", "display_name": "CunningSoundDesigners6067", "handle": "cunningsounddesigners6067", "is_handle_updated": False, "avatar_image_url": "https://cdn1.suno.ai/defaultOrange.webp", "is_trashed": False, "created_at": "2024-11-08T17:08:56.613Z", "status": "submitted", "title": "", "play_count": 0, "upvote_count": 0, "is_public": False}], "metadata": {"prompt": "", "gpt_description_prompt": "a song love in hindi", "type": "gen", "stream": True}, "major_model_version": "v3", "status": "complete", "created_at": "2024-11-08T17:08:56.603Z", "batch_size": 1}
        print(generated_response)
        self.process_generated_songs(generated_response)


    def check_if_generated(self):
        for song_id in self.song_ids:
            response = requests.request(
                SUNO_CONSTANTS.FETCH.METHOD,
                SUNO_CONSTANTS.FETCH.API_ENDPOINT.format(song_id),
                headers={
                    "Authorization": f"{SUNO_CONSTANTS.GENERATE.AUTH_HEADER_TYPE} {self.get_auth_token()}",
                },
            )

            if response.status_code == 200 and response.json():
                self.process_generated_songs(response.json())
        

    
    def process_generated_songs(self, generate_response):
        clips = generate_response.get("clips")
        for clip in clips:
            self.song_ids[clip["id"]] = {
                "name": clip.get("title", clip["id"]),
                "url": clip["audio_url"]          
            }
        

    def get_songs(self, telegram_prompt):
        try:
            self.generate_songs(telegram_prompt)
            while self.song_ids:
                self.check_if_generated()
                for song in list(self.song_ids):
                    if self.song_ids[song]["name"] and self.song_ids[song]["url"]:
                        yield self.song_ids[song]["name"], self.song_ids[song]["url"]
                        self.song_ids.pop(song)
                time.sleep(5)
        except Exception as e:
            return f"ERROR {e}", ""
