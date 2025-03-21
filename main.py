from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import subprocess

app = FastAPI()

class SongRequest(BaseModel):
    song: str

@app.post("/play")
async def play_song(request: SongRequest):
    song = request.song
    if not song:
        raise HTTPException(status_code=400, detail="Song parameter is required.")

    try:
        # Menggunakan yt-dlp untuk mencari video YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '-',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(song, download=False)
            video_url = info_dict.get("url", None)

            if not video_url:
                raise HTTPException(status_code=404, detail="No results found!")

            # Menggunakan subprocess untuk streaming audio
            process = subprocess.Popen(
                ["yt-dlp", "-f", "bestaudio/best", "--extract-audio", "--audio-format", "mp3", video_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return {"message": "Song is being played", "video_url": video_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There was an error: {str(e)}")
