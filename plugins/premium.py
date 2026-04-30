from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS
from database.premium_db import add_premium, remove_premium, is_premium

import re

# -------- TIME PARSER -------- #

def parse_time(time_str):
    match = re.match(r"(\d+)([hdmy])", time_str.lower())
    if not match:
        return None

    value, unit = match.groups()
    value = int(value)

    if unit == "h":
        return value * 60
    elif unit == "d":
        return value * 60 * 24
    elif unit == "m":
        return value * 60 * 24 * 30
    elif unit == "y":
        return value * 60 * 24 * 365

# -------- ADD PREMIUM -------- #

@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium_cmd(client, message: Message):
    try:
        if len(message.command) < 3:
            return await message.reply_text(
                "Usage:\n/addpremium user_id 1h/1d/1m/1y\nExample:\n/addpremium 123456789 2d"
            )

        user_id = int(message.command[1])
        time_str = message.command[2]

        minutes = parse_time(time_str)

        if minutes is None:
            return await message.reply_text("❌ Invalid format\nUse: 1h / 1d / 1m / 1y")

        await add_premium(user_id, minutes)

        await message.reply_text(f"✅ Premium added for {time_str}")

    except Exception as e:
        await message.reply_text(f"Error: {e}")

# -------- REMOVE PREMIUM -------- #

@Client.on_message(filters.command("removepremium") & filters.user(ADMINS))
async def remove_premium_cmd(client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("Usage:\n/removepremium user_id")

        user_id = int(message.command[1])

        await remove_premium(user_id)

        await message.reply_text("❌ Premium removed")

    except Exception as e:
        await message.reply_text(f"Error: {e}")

# -------- CHECK PREMIUM -------- #

@Client.on_message(filters.command("checkpremium"))
async def check_premium_cmd(client, message: Message):
    user_id = message.from_user.id

    if await is_premium(user_id):
        await message.reply_text("💎 You are PREMIUM")
    else:
        await message.reply_text("❌ You are not premium")
