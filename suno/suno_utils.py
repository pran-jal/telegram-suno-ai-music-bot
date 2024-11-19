from suno.suno_config import SUNO_AUTH_TOKEN_COOKIE



class SunoAuthUtils:

    API_ENDPOINT = "https://clerk.suno.com/v1/client/sessions/sess_2oZlr4MzGx1bkyTBKbBROvqEJnO/tokens?_clerk_js_version=5.31.2"
    METHOD = "post"
    HEADERS = {
        "Cookie": SUNO_AUTH_TOKEN_COOKIE
    }



class SunoGenerateUtils:

    METHOD = "post"
    API_ENDPOINT = "https://studio-api.prod.suno.com/api/generate/v2/"
    # BODY = "{{gpt_description_prompt:{},mv:chirp-v3-5,prompt:,metadata:{{lyrics_model:default}},make_instrumental:false,user_uploaded_images_b64:[],generation_type:TEXT}}"
    BODY = {
        "mv":"chirp-v3-5",
        "prompt":"",
        "metadata":{
            "lyrics_model":"default"
        },
        "make_instrumental":False,
        "user_uploaded_images_b64":[],
        "generation_type":"TEXT"
    }
    AUTH_HEADER_TYPE = "Bearer"
    REQUEST_CONTENT_TYPE = "text/plain;charset=UTF-8"



class SunoCheckFetchUtils:

    METHOD="get"
    API_ENDPOINT="https://studio-api.prod.suno.com/api/feed/v2?ids={}"
    AUTH_HEADER_TYPE = "Bearer"



class SunoUtils:
    AUTH = SunoAuthUtils()
    GENERATE = SunoGenerateUtils()
    FETCH = SunoCheckFetchUtils()



def get_suno_constants():
    return SunoUtils()