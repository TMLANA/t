import subprocess
import os
import json
import ffmpeg
import asyncio
from youtube_dl import YoutubeDL
from pyrogram.types import Message

def raw_converter(source, output):
    subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-i",
            source,
            "-f",
            "s16le",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-acodec",
            "pcm_s16le",
            output,
        ],
        stdin=None,
        stdout=None,
        stderr=None,
        cwd=None,
    )

async def transcode(file_path: str):
    file_name = file_path.split(".")[0] + ".raw"
    if os.path.isfile(file_name):
        return file_name
    cmd = ["ffmpeg", "-y", "-i", file_path, "-f", "s16le", "-ac", "2", '-vn', "-ar", "48000", "-acodec", "pcm_s16le", file_name]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    if proc.returncode != 0:
        print(f"Transcode failed for {file_path}")
        return None
    return file_name


# got this from somewhere
def get_resolution(info_dict):
    if {"width", "height"} <= info_dict.keys():
        width = int(info_dict['width'])
        height = int(info_dict['height'])
    # https://support.google.com/youtube/answer/6375112
    elif info_dict['height'] == 1080:
        width = 1920
        height = 1080
    elif info_dict['height'] == 720:
        width = 1280
        height = 720
    elif info_dict['height'] == 480:
        width = 854
        height = 480
    elif info_dict['height'] == 360:
        width = 640
        height = 360
    elif info_dict['height'] == 240:
        width = 426
        height = 240
    return (width, height)

async def yt_download(ytlink):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
        'writethumbnail': False
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(ytlink, download=False)
        res = get_resolution(info_dict)
        ydl.process_info(info_dict)
        _file = ydl.prepare_filename(info_dict)
        return _file, res

async def tg_download(m: Message):
    if not os.path.isdir("temp"):
        os.mkdir("temp")
    path = await m.download()
    return path

# ignore
async def _transcode(file_path: str):
    file_name = file_path.split(".")[0] + ".raw"
    if os.path.isfile(file_name):
        return file_name
    proc = await asyncio.create_subprocess_shell(
        f"ffmpeg -y -i {file_path} -f s16le -ac 2 -ar 48000 -acodec pcm_s16le {file_name}",
        asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()
    if proc.returncode != 0:
        print(f"Transcode failed for {file_path}")
        return None
    return file_name

# ignore
async def __transcode(filename: str):
    file_name = filename.split(".")[0] + ".raw"
    ffmpeg.input(filename).output(
        file_name,
        format="s16le",
        acodec="pcm_s16le",
        ac=2,
        ar="48k",
        
        loglevel="error",
    ).overwrite_output().run_async()
    if os.path.exists(file_name):
        return file_name