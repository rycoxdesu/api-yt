import os
import logging
import subprocess
import base64
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

# Cek dan decode cookies dari environment variable
cookies_base64 = os.getenv("COOKIES_BASE64")
if cookies_base64:
    try:
        logging.info("📥 Decode cookies dari environment variable...")
        with open(COOKIES_PATH, "wb") as f:
            f.write(base64.b64decode(cookies_base64))
        logging.info(f"✅ Cookies berhasil disimpan di: {COOKIES_PATH}")
    except Exception as e:
        logging.error(f"❌ Gagal decode cookies: {e}")

# Model request
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
    else:
        logging.warning(f"❌ Cookies TIDAK ditemukan! Streaming mungkin gagal.")

    try:
        # Jika input berupa URL, langsung pakai URL
        if song.startswith("http"):
            video_url = song
            logging.info(f"🔗 Menggunakan URL langsung: {video_url}")
        else:
            # Cari lagu di YouTube
            logging.info(f"🔍 Mencari lagu di YouTube: {song}")

            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "cookies": COOKIES_PATH if os.path.exists(COOKIES_PATH) else None,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{song}", download=False)
                if "entries" in info_dict and info_dict["entries"]:
                    video_url = info_dict["entries"][0]["url"]
                    logging.info(f"✅ Lagu ditemukan: {video_url}")
                else:
                    logging.warning("❌ Tidak ada hasil ditemukan!")
                    raise HTTPException(status_code=404, detail="No results found!")

        # Stream audio menggunakan yt-dlp
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

# Jalankan API dengan:
# uvicorn main:app --host 0.0.0.0 --port 8080
