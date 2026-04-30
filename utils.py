# Don't Remove Credit @VJ_Bots

import logging, asyncio, os, re, random, pytz, aiohttp, requests, string, json, http.client
from datetime import date, datetime, timedelta
from config import SHORTLINK_API, SHORTLINK_URL, ADMINS
from shortzy import Shortzy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TOKENS = {}
VERIFIED = {}

# 🔥 PREMIUM SYSTEM (TIME BASED)
PREMIUM_USERS = {}

# ---------------- SHORTLINK ---------------- #

async def get_verify_shorted_link(link):
    if SHORTLINK_URL == "api.shareus.io":
        url = f'https://{SHORTLINK_URL}/easy_api'
        params = {
            "key": SHORTLINK_API,
            "link": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.text()
                    return data
        except Exception as e:
            logger.error(e)
            return link
    else:
        shortzy = Shortzy(api_key=SHORTLINK_API, base_site=SHORTLINK_URL)
        link = await shortzy.convert(link)
        return link

# ---------------- TOKEN SYSTEM ---------------- #

async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            return not TKN[token]
    return False

async def get_token(bot, userid, link):
    user = await bot.get_users(userid)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{link}verify-{user.id}-{token}"
    shortened_verify_url = await get_verify_shorted_link(link)
    return str(shortened_verify_url)

# ---------------- PREMIUM SYSTEM ---------------- #

def add_premium_user(user_id, minutes):
    expire = datetime.now() + timedelta(minutes=minutes)
    PREMIUM_USERS[user_id] = expire

def remove_premium_user(user_id):
    PREMIUM_USERS.pop(user_id, None)

def is_premium_user(user_id):
    if user_id in PREMIUM_USERS:
        if datetime.now() < PREMIUM_USERS[user_id]:
            return True
        else:
            PREMIUM_USERS.pop(user_id)
            return False
    return False

# ---------------- VERIFY ---------------- #

async def verify_user(bot, userid, token):
    user = await bot.get_users(userid)

    TOKENS[user.id] = {token: True}
    today = date.today()
    VERIFIED[user.id] = str(today)

    # 🎁 12 HOURS PREMIUM (720 min)
    add_premium_user(user.id, 720)

# ---------------- CHECK ---------------- #

async def check_verification(bot, userid):
    user = await bot.get_users(userid)

    # 🔥 ADMIN BYPASS
    if user.id in ADMINS:
        return True

    # 🔥 PREMIUM BYPASS
    if is_premium_user(user.id):
        return True

    today = date.today()

    if user.id in VERIFIED.keys():
        EXP = VERIFIED[user.id]
        years, month, day = EXP.split('-')
        comp = date(int(years), int(month), int(day))

        if comp < today:
            return False
        else:
            return True
    else:
        return False