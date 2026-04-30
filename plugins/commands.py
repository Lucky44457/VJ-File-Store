# Don't Remove Credit Tg - @VJ_Bots

import os
import logging
import random
import asyncio
from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from utils import verify_user, check_token, check_verification, get_token, is_premium_user
from config import *
import re
import json
import base64
from urllib.parse import quote_plus
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)

BATCH_FILES = {}

# ---------------- START ---------------- #

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    username = client.me.username
    user_id = message.from_user.id

    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(user_id, message.from_user.mention))

    # NORMAL START (NO VERIFY HERE)
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('💝 YouTube', url='https://youtube.com/@Tech_VJ')
        ],[
            InlineKeyboardButton('Support', url='https://t.me/vj_bot_disscussion'),
            InlineKeyboardButton('Update', url='https://t.me/vj_bots')
        ]]
        await message.reply_text("Welcome 👋")
        return

    data = message.command[1]

    # ---------------- VERIFY ---------------- #
    if data.startswith("verify"):
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]

        if str(user_id) != str(userid):
            return await message.reply_text("Invalid link ❌")

        is_valid = await check_token(client, userid, token)

        if is_valid:
            await verify_user(client, userid, token)
            await message.reply_text("✅ Verified!\n🎁 12hr premium unlocked")
        else:
            await message.reply_text("Expired link ❌")
        return

    # ---------------- BATCH ---------------- #
    elif data.startswith("BATCH"):

        # 🔥 VERIFY CHECK (UPDATED)
        if VERIFY_MODE:
            if user_id not in ADMINS and not is_premium_user(user_id):
                if not await check_verification(client, user_id):
                    btn = [[
                        InlineKeyboardButton("Verify", url=await get_token(client, user_id, f"https://telegram.me/{username}?start="))
                    ]]
                    return await message.reply_text("🔐 Verify first", reply_markup=InlineKeyboardMarkup(btn))

        await message.reply("Sending batch files...")

    # ---------------- FILE ---------------- #
    try:
        pre, decode_file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)

        # 🔥 VERIFY CHECK (UPDATED)
        if VERIFY_MODE:
            if user_id not in ADMINS and not is_premium_user(user_id):
                if not await check_verification(client, user_id):
                    btn = [[
                        InlineKeyboardButton("Verify", url=await get_token(client, user_id, f"https://telegram.me/{username}?start="))
                    ]]
                    return await message.reply_text("🔐 Verify first", reply_markup=InlineKeyboardMarkup(btn))

        msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))

        if msg.media:
            media = getattr(msg, msg.media.value)
            title = media.file_name

            await msg.copy(chat_id=user_id)

        else:
            await msg.copy(chat_id=user_id)

    except Exception as e:
        print(e)

# ---------------- SHORTENER ---------------- #

@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        return await m.reply("Send API key")

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("API updated")

# ---------------- BASE SITE ---------------- #

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    cmd = m.command

    if len(cmd) == 1:
        return await m.reply("Send domain")

    elif len(cmd) == 2:
        base_site = cmd[1].strip()

        if not domain(base_site):
            return await m.reply("Invalid domain")

        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("Updated")
