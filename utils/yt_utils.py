from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from youtube_transcript_api.proxies import WebshareProxyConfig
import requests
from bs4 import BeautifulSoup
import json
import os

def save_video_data(video_id, video_name, captions, filename="data/transcripts.json"):
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    data = {
        "video_id": video_id,
        "video_name": video_name,
        "captions": captions
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent = 4)

    print(f"Data saved to {filename}")


def generate_transcript(video_id, lang='en'):
    try:
        # yt_api = YouTubeTranscriptApi(
        #         proxy_config = WebshareProxyConfig( # Get a free proxy from (https://www.webshare.io/) if Youtube Blocks the IP
        #         proxy_username = "<your-proxy-username>",
        #         proxy_password = "<your-proxy-password>",
        #     )
        # )
        yt_api = YouTubeTranscriptApi()
        transcript_list = yt_api.fetch(video_id, languages=[lang])

        captions = ' '.join(script.text for script in transcript_list)
        # print(captions[:200])
        return captions
            
    except NoTranscriptFound:
        print('No captions available for this video.')
        
    except Exception as e:
        print(f"Error: {e}")


def get_video_info(url):
    video_id = None
    title = None
    
    if "v=" in url:
        video_id = url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    elif "shorts/" in url:
        video_id = url.split("shorts/")[1].split("?")[0]

    if video_id:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else None
                        
        except Exception as e:
            print("Error fetching title:", e)

    return video_id, title