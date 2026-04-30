from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS
from database.premium_db import add_premium, remove_premium, is_premium

@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium_cmd(client, message: Message):
    user_id = int(message.command[1])
    time = int(message.command[2])

    await add_premium(user_id, time)

    await message.reply_text(f"✅ Premium added for {time} minutes")

@Client.on_message(filters.command("removepremium") & filters.user(ADMINS))
async def remove_premium_cmd(client, message: Message):
    user_id = int(message.command[1])
    await remove_premium(user_id)
    await message.reply_text("❌ Premium removed")

@Client.on_message(filters.command("checkpremium"))
async def check_premium_cmd(client, message: Message):
    user_id = message.from_user.id

    if await is_premium(user_id):
        await message.reply_text("💎 You are PREMIUM")
    else:
        await message.reply_text("❌ Not premium")
