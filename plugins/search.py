import asyncio
from info import *
from utils imimport asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    f_sub = await force_sub(bot, message)
    if f_sub == False:
        return     
    channels = (await get_group(message.chat.id))["channels"]
    if not channels:
        return     
    if message.text.startswith("/"):
        return    
    query   = message.text 
    head    = "<u>Here are the results 👇\n\n men channel join </u> <b><i>@SGBACKUP</i></b>\n\n"
    results = ""
    try:
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]
                if name in results:
                    continue 
                results += f"<b><i>♻️ {name}\n🔗 {msg.link}</i></b>\n\n"                                                      
        if not results:
            movies = await search_imdb(query)
            buttons = []
            for movie in movies: 
                buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])
            msg = await message.reply_photo(photo="https://telegra.ph/file/0135214675399e11c0529.jpg",
                                            caption="<b><i>I couldn't find anything related to your query 😕.\nDid you mean any of these?</i></b>", 
                                            reply_markup=InlineKeyboardMarkup(buttons))
        else:
            msg = await message.reply_text(text=head+results, disable_web_page_preview=True)
        _time = (int(time()) + (5 * 60))
        await save_dlt_message(msg, _time)
        await asyncio.sleep(300)  # Auto-delete after 5 minutes (300 seconds)
        await msg.delete()
    except:
        pass

@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    clicked = update.from_user.id
    try:      
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete(2)       
    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)

    m = await update.message.edit("Searching..💥")
    id = update.data.split("_")[-1]
    query = await search_imdb(id)
    channels = (await get_group(update.message.chat.id))["channels"]
    head = "<u>I have searched for a movie with the wrong spelling but take care next time 👇\n\nPowered by </u> <b><i>@SGBACKUP</i></b>\n\n"
    results = ""
    try:
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]
                if name in results:
                    continue 
                results += f"<b><i>♻️🍿 {name}</i></b>\n\n🔗 {msg.link}</i></b>\n\n"
        if not results:          
            return await update.message.edit("Still no results found! Please request to the group admin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request to Admin 🎯", callback_data=f"request_{id}")]]))
        await update.message.edit(text=head+results, disable_web_page_preview=True)
    except Exception as e:
        await update.message.edit(f"❌ Error: `{e}`")

@Client.on_callback_query(filters.regex(r"^request"))
async def request(bot, update):
    clicked = update.from_user.id
    try:      
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete()       
    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)

    admin = (await get_group(update.message.chat.id))["user_id"]
    id = update.data.split("_")[1]
    name = await search_imdb(id)
    url = "https://www.imdb.com/title/tt" + id
    text = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
    await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request sent to admin", show_alert=True)
    await update.message.delete(60)
