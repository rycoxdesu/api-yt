from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import subprocess

app = FastAPI()

# Path cookies
COOKIES_PATH = "cookies.txt"

class SongRequest(BaseModel):
    song: str

@app.post("/play")
async def play_song(request: SongRequest):
    song = request.song
    if not song:
        raise HTTPException(status_code=400, detail="Song parameter is required.")

    try:
        # Cek apakah input song berupa URL atau judul lagu
        if song.startswith("http"):
            video_url = song
        else:
            # Menggunakan yt-dlp untuk mencari video YouTube berdasarkan judul
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
                'cookies': COOKIES_PATH,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{song}", download=False)
                if 'entries' in info_dict and info_dict['entries']:
                    video_url = info_dict['entries'][0]['url']
                else:
                    raise HTTPException(status_code=404, detail="No results found!")

        # Menggunakan subprocess untuk stream audio
        process = subprocess.Popen(
            [
                "yt-dlp", "-f", "bestaudio", "--cookies", COOKIES_PATH,
                "-o", "-", video_url
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return {"message": "Streaming audio...", "stream_url": video_url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error: {str(e)}")

# Jalankan API dengan perintah:
# uvicorn main:app --host 127.0.0.1 --port 8000
