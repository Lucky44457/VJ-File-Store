# Don't Remove Credit @VJ_Bots

import re
from pyrogram import filters, Client
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from config import ADMINS, LOG_CHANNEL, PUBLIC_FILE_STORE, WEBSITE_URL, WEBSITE_URL_MODE
from plugins.users_api import get_user, get_short_link
import os
import json
import base64

# ---------------- ALLOWED ---------------- #

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False


# ---------------- AUTO LINK (FILE SEND) ---------------- #

@Client.on_message((filters.document | filters.video | filters.audio) & filters.private & filters.create(allowed))
async def incoming_gen_link(bot, message):
    username = (await bot.get_me()).username

    post = await message.copy(LOG_CHANNEL)
    file_id = str(post.id)

    # ✅ FIXED (NO strip("="))
    string = f"file_{file_id}"
    outstr = base64.urlsafe_b64encode(string.encode()).decode()

    user_id = message.from_user.id
    user = await get_user(user_id)

    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?Tech_VJ={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"

    if user["base_site"] and user["shortener_api"]:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ HERE IS YOUR LINK:\n\n🖇️ SHORT LINK :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ HERE IS YOUR LINK:\n\n🔗 ORIGINAL LINK :- {share_link}</b>")


# ---------------- /link COMMAND ---------------- #

@Client.on_message(filters.command(['link']) & filters.create(allowed))
async def gen_link_s(bot, message):
    username = (await bot.get_me()).username
    replied = message.reply_to_message

    if not replied:
        return await message.reply('Reply to a message to get a shareable link.')

    post = await replied.copy(LOG_CHANNEL)
    file_id = str(post.id)

    # ✅ FIXED (NO strip("="))
    string = f"file_{file_id}"
    outstr = base64.urlsafe_b64encode(string.encode()).decode()

    user_id = message.from_user.id
    user = await get_user(user_id)

    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?Tech_VJ={outstr}"
    else:
        share_link = f"https://t.me/{username}?start={outstr}"

    if user["base_site"] and user["shortener_api"]:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ HERE IS YOUR LINK:\n\n🖇️ SHORT LINK :- {short_link}</b>")
    else:
        await message.reply(f"<b>⭕ HERE IS YOUR LINK:\n\n🔗 ORIGINAL LINK :- {share_link}</b>")


# ---------------- BATCH ---------------- #

@Client.on_message(filters.command(['batch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    username = (await bot.get_me()).username

    if " " not in message.text:
        return await message.reply("Use correct format.\nExample /batch link1 link2")

    links = message.text.strip().split(" ")
    if len(links) != 3:
        return await message.reply("Use correct format.\nExample /batch link1 link2")

    cmd, first, last = links

    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    match = regex.match(first)
    if not match:
        return await message.reply('Invalid link')

    f_chat_id = match.group(4)
    f_msg_id = int(match.group(5))

    if f_chat_id.isnumeric():
        f_chat_id = int("-100" + f_chat_id)

    match = regex.match(last)
    if not match:
        return await message.reply('Invalid link')

    l_chat_id = match.group(4)
    l_msg_id = int(match.group(5))

    if l_chat_id.isnumeric():
        l_chat_id = int("-100" + l_chat_id)

    if f_chat_id != l_chat_id:
        return await message.reply("Chat ids not matched.")

    try:
        await bot.get_chat(f_chat_id)
    except:
        return await message.reply("Make bot admin in channel")

    sts = await message.reply("Generating batch link...")

    outlist = []

    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        if msg.empty or msg.service:
            continue

        outlist.append({
            "channel_id": f_chat_id,
            "msg_id": msg.id
        })

    file_path = f"batch_{message.from_user.id}.json"
    with open(file_path, "w+") as f:
        json.dump(outlist, f)

    post = await bot.send_document(LOG_CHANNEL, file_path)
    os.remove(file_path)

    file_id = base64.urlsafe_b64encode(str(post.id).encode()).decode()

    if WEBSITE_URL_MODE:
        share_link = f"{WEBSITE_URL}?Tech_VJ=BATCH-{file_id}"
    else:
        share_link = f"https://t.me/{username}?start=BATCH-{file_id}"

    await sts.edit(f"<b>⭕ Batch Link:\n\n{share_link}</b>")
