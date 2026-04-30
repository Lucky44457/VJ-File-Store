# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

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

def get_size(size):
    """Get size in readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def formate_file_name(file_name):
    chars = ["[", "]", "(", ")"]
    for c in chars:
        file_name = file_name.replace(c, "")
    file_name = '@VJ_Botz ' + ' '.join(filter(lambda x: not x.startswith('http') and not x.startswith('@') and not x.startswith('www.'), file_name.split()))
    return file_name

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    username = client.me.username
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')
            ],[
            InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
            InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')
            ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        if CLONE_MODE == True:
            buttons.append([InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ', callback_data='clone')])
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, client.me.mention),
            reply_markup=reply_markup
        )
        return

    data = message.command[1]
    
    # Handling verify link logic
    if data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid:
            await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all files till today midnight.</b>",
                protect_content=True
            )
            await verify_user(client, userid, token)
        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )

    # Handling BATCH verification and processing
    elif data.split("-", 1)[0] == "BATCH":
        try:
            user_id = message.from_user.id
            if VERIFY_MODE:
                if user_id not in ADMINS and not is_premium_user(user_id):
                    if not await check_verification(client, user_id):
                        btn = [[
                            InlineKeyboardButton("Verify", url=await get_token(client, user_id, f"https://telegram.me/{username}?start="))
                        ],[
                            InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                        ]]
                        return await message.reply_text(
                            text="<b>You are not verified !\nKindly verify to continue !</b>",
                            protect_content=True,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )

            sts = await message.reply("**🔺 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ**")
            file_id = data.split("-", 1)[1]
            msgs = BATCH_FILES.get(file_id)
            if not msgs:
                decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")
                msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
                media = getattr(msg, msg.media.value)
                file = await client.download_media(media.file_id)
                try: 
                    with open(file) as file_data:
                        msgs = json.loads(file_data.read())
                except:
                    await sts.edit("FAILED")
                    return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
                os.remove(file)
                BATCH_FILES[file_id] = msgs
                
            filesarr = []
            for msg_item in msgs:
                channel_id = int(msg_item.get("channel_id"))
                msgid = msg_item.get("msg_id")
                info = await client.get_messages(channel_id, int(msgid))
                if info.media:
                    file_type = info.media
                    file = getattr(info, file_type.value)
                    f_caption = getattr(info, 'caption', '')
                    if f_caption:
                        f_caption = f"@VJ_Bots {f_caption.html}"
                    
                    title = formate_file_name(getattr(file, "file_name", ""))
                    size = get_size(int(file.file_size))
                    
                    if BATCH_FILE_CAPTION:
                        try:
                            f_caption = BATCH_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                        except:
                            pass
                    
                    reply_markup = None
                    if STREAM_MODE:
                        if info.video or info.document:
                            stream = f"{URL}watch/{str(info.id)}/{quote_plus(get_name(info))}?hash={get_hash(info)}"
                            download = f"{URL}{str(info.id)}/{quote_plus(get_name(info))}?hash={get_hash(info)}"
                            btn_stream = [[
                                InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                                InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                            ],[
                                InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                            ]]
                            reply_markup = InlineKeyboardMarkup(btn_stream)

                    try:
                        msg_sent = await info.copy(chat_id=user_id, caption=f_caption, protect_content=False, reply_markup=reply_markup)
                        filesarr.append(msg_sent)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        msg_sent = await info.copy(chat_id=user_id, caption=f_caption, protect_content=False, reply_markup=reply_markup)
                        filesarr.append(msg_sent)
                    except:
                        continue
                await asyncio.sleep(1) 
            
            await sts.delete()
            if AUTO_DELETE_MODE:
                k = await client.send_message(chat_id=user_id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u></b>.")
                await asyncio.sleep(AUTO_DELETE_TIME)
                for x in filesarr:
                    try: await x.delete()
                    except: pass
                await k.edit_text("<b>Your All Files/Videos have been deleted!</b>")
            return

        except Exception as e:
            return await message.reply_text(f"**Error - {e}**")

    # Handling single file verification and processing
    else:
        try:
            pre, decode_file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            user_id = message.from_user.id

            if VERIFY_MODE:
                if user_id not in ADMINS and not is_premium_user(user_id):
                    if not await check_verification(client, user_id):
                        btn = [[
                            InlineKeyboardButton("Verify", url=await get_token(client, user_id, f"https://telegram.me/{username}?start="))
                        ],[
                            InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                        ]]
                        return await message.reply_text(
                            text="<b>You are not verified !\nKindly verify to continue !</b>",
                            protect_content=True,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )

            msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
            if msg.media:
                media = getattr(msg, msg.media.value)
                title = formate_file_name(media.file_name)
                size = get_size(media.file_size)
                f_caption = f"@VJ_Bots <code>{title}</code>"
                
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption='')
                    except:
                        pass
                
                reply_markup = None
                if STREAM_MODE:
                    if msg.video or msg.document:
                        stream = f"{URL}watch/{str(msg.id)}/{quote_plus(get_name(msg))}?hash={get_hash(msg)}"
                        download = f"{URL}{str(msg.id)}/{quote_plus(get_name(msg))}?hash={get_hash(msg)}"
                        btn_stream = [[
                            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                        ],[
                            InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                        ]]
                        reply_markup = InlineKeyboardMarkup(btn_stream)

                del_msg = await msg.copy(chat_id=user_id, caption=f_caption, reply_markup=reply_markup, protect_content=False)
                
                if AUTO_DELETE_MODE:
                    k = await client.send_message(chat_id=user_id, text=f"<b><u>IMPORTANT</u></b>\n\nDeleted in <b>{AUTO_DELETE} minutes</b>.")
                    await asyncio.sleep(AUTO_DELETE_TIME)
                    try: await del_msg.delete()
                    except: pass
                    await k.edit_text("<b>File deleted successfully!</b>")
            else:
                await msg.copy(chat_id=user_id, protect_content=False)
            return
        except Exception as e:
            logger.error(e)

# API and Site Handlers
@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    if len(m.command) == 1:
        return await m.reply(script.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"]))
    api = m.command[1].strip()
    await update_user_info(user_id, {"shortener_api": api})
    await m.reply(f"<b>Shortener API updated to:</b> {api}")

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    if len(m.command) == 1:
        return await m.reply("Usage: `/base_site domain.com`")
    base_site = m.command[1].strip()
    await update_user_info(user_id, {"base_site": base_site})
    await m.reply(f"<b>Base Site updated to:</b> {base_site}")

# Callback Query Handler
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "about":
        buttons = [[InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'), InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')]]
        await query.message.edit_text(text=script.ABOUT_TXT.format(client.me.mention), reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data == "start":
        buttons = [[InlineKeyboardButton('💝 sᴜʙsᴄʀɪʙᴇ ᴍʏ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ', url='https://youtube.com/@Tech_VJ')],
                   [InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'), InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')],
                   [InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'), InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')]]
        await query.message.edit_text(text=script.START_TXT.format(query.from_user.mention, client.me.mention), reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data == "help":
        buttons = [[InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'), InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')]]
        await query.message.edit_text(text=script.HELP_TXT, reply_markup=InlineKeyboardMarkup(buttons))
