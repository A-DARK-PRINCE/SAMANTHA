import asyncio
import glob
import os
import subprocess
import time
from asyncio.exceptions import TimeoutError

import requests
from bs4 import BeautifulSoup
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pylast import User
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import DocumentAttributeVideo

from Elizabeth.events import register
from Elizabeth.utils import progress


# For song module
def getmusic(get, DEFAULT_AUDIO_QUALITY):
    search = get

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }

    html = requests.get(
        "https://www.youtube.com/results?search_query=" +
        search,
        headers=headers).text
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        if "/watch?v=" in link.get("href"):
            # May change when Youtube Website may get updated in the future.
            video_link = link.get("href")


# For getvideosong
def getmusicvideo(cat):
    search = cat
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }
    html = requests.get(
        "https://www.youtube.com/results?search_query=" +
        search,
        headers=headers).text
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a"):
        if "/watch?v=" in link.get("href"):
            # May change when Youtube Website may get updated in the future.
            video_link = link.get("href")
            break
    video_link = "http://www.youtube.com/" + video_link
    command = 'youtube-dl -f "[filesize<50M]" --merge-output-format mp4 ' + video_link
    os.system(command)


@register(outgoing=True, pattern=r"^\.song (.*)")
async def _(event):
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    reply = await event.get_reply_message()
    if event.pattern_match.group(1):
        query = event.pattern_match.group(1)
        await event.edit("`Wait..! I am finding your song..`")
    elif reply.message:
        query = reply.message
        await event.edit("`Wait..! I am finding your song..`")
    else:
        await event.edit("`What I am Supposed to find?`")
        return

    getmusic(str(query), "320k")
    l = glob.glob("*.mp3")
    loa = l[0]
    img_extensions = ["webp", "jpg", "jpeg", "webp"]
    img_filenames = [
        fn_img
        for fn_img in os.listdir()
        if any(fn_img.endswith(ext_img) for ext_img in img_extensions)
    ]
    thumb_image = img_filenames[0]
    await event.edit("`Yeah.. Uploading your song..`")
    c_time = time.time()
    await event.client.send_file(
        event.chat_id,
        loa,
        force_document=True,
        thumb=thumb_image,
        allow_cache=False,
        caption=query,
        reply_to=reply_to_id,
        progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
            progress(d, t, event, c_time, "[UPLOAD]", loa)
        ),
    )
    await event.delete()
    os.system("rm -rf *.mp3")
    os.remove(thumb_image)
    subprocess.check_output("rm -rf *.mp3", shell=True)