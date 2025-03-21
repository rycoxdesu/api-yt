import os
import logging
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),  # Simpan log ke file
        logging.StreamHandler()  # Tampilkan log di terminal
    ]
)

app = FastAPI()

# Path cookies
COOKIES_PATH = "cookies.txt"

class SongRequest(BaseModel):
    song: str

@app.post("/play")
async def play_song(request: SongRequest):
    song = request.song
    logging.info(f"🎵 Request lagu: {song}")

    if not song:
        logging.warning("⚠️ Parameter 'song' kosong!")
        raise HTTPException(status_code=400, detail="Song parameter is required.")

    # Cek apakah file cookies ada
    if os.path.exists(COOKIES_PATH):
        logging.info(f"✅ Cookies ditemukan: {COOKIES_PATH}")
        with open(COOKIES_PATH, "r", encoding="utf-8") as f:
            cookies_content = f.read()
            logging.info(f"📜 Isi Cookies:\n{cookies_content}")
    else:
        logging.warning(f"❌ Cookies TIDAK ditemukan: {COOKIES_PATH}")

    try:
        # Cek apakah input song berupa URL atau judul lagu
        if song.startswith("http"):
            video_url = song
            logging.info(f"🔗 Menggunakan URL langsung: {video_url}")
        else:
            # Menggunakan yt-dlp untuk mencari video YouTube berdasarkan judul
            logging.info(f"🔍 Mencari lagu di YouTube: {song}")

            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "cookies": COOKIES_PATH,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{song}", download=False)
                if "entries" in info_dict and info_dict["entries"]:
                    video_url = info_dict["entries"][0]["url"]
                    logging.info(f"✅ Lagu ditemukan: {video_url}")
                else:
                    logging.warning("❌ Tidak ada hasil ditemukan!")
                    raise HTTPException(status_code=404, detail="No results found!")

        # Menggunakan subprocess untuk stream audio
        logging.info(f"🎶 Streaming audio dari: {video_url}")
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
        logging.error(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"There was an error: {str(e)}")

# Jalankan API dengan perintah:
# uvicorn main:app --host 127.0.0.1 --port 8000
