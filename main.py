import json
import os
import asyncio
import logging
import sys
import random
import os  # Portni olish uchun kerak
from aiohttp import web # Render portini band qilish uchun
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types.web_app_info import WebAppInfo
from aiogram.filters import CommandStart, CommandObject

# --- SOZLAMALAR ---
API_TOKEN = '8400967993:AAHl9cpqZdDZ7sfe_2Tsmba0PQ2MKMYNS3w'

# Botni sozlash
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- MA'LUMOTLAR BAZASI (JSON) ---
DB_FILE = "hogwarts_data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(DB_FILE, "w") as file:
        json.dump(data, file, indent=4)

# --- OBUNANI TEKSHIRISH MANTIQI ---
async def check_subscription(user_id: int):
    # Foydalanuvchi yo kanalda, yo guruhda borligini tekshiradi (YOKI mantiqi)
    for chat_id in [CHANNEL_ID, GROUP_CHAT_ID]:
        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator', 'restricted']:
                return True
        except Exception:
            pass # Bot admin emas yoki foydalanuvchi yo'q
    return False

def get_subscription_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        # FAQAT KANAL LINKI BERILADI. Guruhniki sir saqlanadi.
        [InlineKeyboardButton(text="1️⃣ Kanalga obuna bo'lish", url=CHANNEL_INVITE_LINK)],
        [InlineKeyboardButton(text="2️⃣ Obunani tasdiqlash", callback_data="verify_subscription")]
    ])

# --- RASM ID LARINI SHU YERGA YOZING ---
HAT_IMG_ID = "AgACAgIAAxkBAAMEaYSnRQbDnr2YuCqkbNqQdg8v2W4AAk4OaxscMChI831GZTNaiJsBAAMCAAN5AAM4BA" 
GRYFFINDOR_ID = "AgACAgIAAxkBAAMHaYXIIPDphgbohdWYJEK5OA47R1MAArITaxtyUClIUB8w7cOd6M4BAAMCAAN5AAM4BA"
SLYTHERIN_ID = "AgACAgIAAxkBAAMJaYXJD5GlhcgYyejILR8JTvHz0gwAAsgTaxtyUClINaIi3c1LUW8BAAMCAAN5AAM4BA"
RAVENCLAW_ID = "AgACAgIAAxkBAAMLaYXJiweH5Eh-GTvd5Ht6L66WCjQAAtoTaxtyUClIkKj5p860ReUBAAMCAAN5AAM4BA"
HUFFLEPUFF_ID = "AgACAgIAAxkBAAMNaYXKHqkLLw-QQufj4D533Ld9QB8AAuQTaxtyUClIP6F1JQTQnokBAAMCAAN5AAM4BA"

SORTING_TOPIC_ID = 505 # Agar guruhda topic bo'lmasa None, bo'lsa raqamini yozing
GROUP_CHAT_ID = -1003369300068

CHANNEL_ID = -1003535019162
CHANNEL_INVITE_LINK = "https://t.me/garripotter_cinema"

# Faqat shundan keyingina HOUSES lug'ati kelishi kerak
HOUSES = {
    "Gryffindor": {
        "id": GRYFFINDOR_ID,
        "desc": (
            "🧙‍♂️ {mention}, sening qalbingda jasorat va qat’iyat bor!\n\n"
            
            "🦁 Sening fakulteting — <b>GRYFFINDOR!</b>\n\n"
            
            "🔥 Gryffindor — jasur, mard va yetakchi sehrgarlar uyi. Bu yerda qo‘rquv emas, jasorat hukmron.\n\n"
            
            "✨ Fakulteting bilan faxrlan!"
        ),
        "emoji": "🦁"
    },
    "Slytherin": {
        "id": SLYTHERIN_ID,
        "desc": (
            "🧙‍♂️ {mention}, sening qalbingda ulkan ambitsiyalar yashirin!\n\n"
            
            "🐍 Sening fakulteting — <b>SLYTHERIN!</b>\n\n"
            
            "🟢 Slytherin — aql, strategiya va ambitsiya fakulteti. Buyuk sehrgarlar aynan shu yerdan chiqqan.\n\n"
            
            "🔐 Sirlaringni asra!"
        ),
        "emoji": "🐍"
    },
    "Ravenclaw": {
        "id": RAVENCLAW_ID,
        "desc": (
            "🧙‍♂️ {mention}, sening zehning va aqling tengsiz!\n\n"
            
            "🦅 Sening fakulteting — <b>RAVENCLAW!</b>\n\n"
            
            "🔵 Ravenclaw — aql, bilim va donolik fakulteti. Bu yerda savollar javoblardan muhimroq.\n\n"
            
            "📘 O'rganishdan toxtama!"
        ),
        "emoji": "🦅"
    },
    "Hufflepuff": {
        "id": HUFFLEPUFF_ID,
        "desc": (
           "🧙‍♂️ {mention}, sening yuraging toza va sadoqatli!\n\n"
            
            "🦡 Sening fakulteting — <b>HUFFLEPUFF!</b>\n\n"
            
            "🟡 Hufflepuff — sodiq, mehnatkash va adolatli sehrgarlar uyi. Bu yerda har kim o‘z o‘rnini topadi.\n\n"
            
            "🤝 Xush kelibsan!"
        ),
        "emoji": "🦡"
    }
}

RAW_DATA = load_data()
USER_HOUSES = {int(k): v for k, v in RAW_DATA.items()}

# --- RENDER PORTINI ALDASH UCHUN KICHIK SERVER ---
async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render avtomatik beradigan PORT ni oladi, bo'lmasa 10000
    port = int(os.environ.get("PORT", 10000)) 
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server {port} portida ishga tushdi.")

# --- BOT LOGIKASI (ID olish) ---
@dp.message(F.photo)
async def get_photo_id(message: types.Message):
    file_id = message.photo[-1].file_id
    await message.reply(f"🖼 <b>Rasm ID:</b>\n<code>{file_id}</code>", parse_mode="HTML")

# --- YANGI A'ZO KELGANDA (KIRISH XABARINI O'CHIRISH VA KUTIB OLISH) ---
@dp.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Kirish xabarini o'chirolmadim: {e}")

    bot_info = await bot.get_me() # Botning yuzerini avtomatik olish

    for user in message.new_chat_members:
        if user.id == bot.id: continue
        
        user_mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        
        # 1-JARAYON (Flow 1): Agar mijoz avval test yechgan bo'lsa
        if user.id in USER_HOUSES:
            USER_HOUSES[user.id]["in_club"] = True # Statusni faollashtiramiz
            save_data(USER_HOUSES)
            
            caption_text = f"🧙‍♂️ <b>Xush kelibsiz, {user_mention}!</b>\n\nSiz allaqachon testdan o'tgansiz. Fakultetingizni guruhda e'lon qilish uchun qalpoqni kiying."
            tugma = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🎩 Fakultetimni e'lon qilish", callback_data=f"wear_hat_{user.id}")
            ]])
        
        # 2-JARAYON (Flow 2): Agar mijoz test yechmagan bo'lsa
        else:
            bot_url = f"https://t.me/{bot_info.username}?start=sort"
            caption_text = f"🧙‍♂️ <b>Xush kelibsiz, {user_mention}!</b>\n\nFakultetingizni aniqlash uchun botga o'tib, maxsus testni yechishingiz kerak."
            tugma = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🪄 Shaxsiyda test ishlash", url=bot_url)
            ]])
        
        await bot.send_photo(
            chat_id=message.chat.id, 
            message_thread_id=SORTING_TOPIC_ID, 
            photo=HAT_IMG_ID, 
            caption=caption_text, 
            reply_markup=tugma, 
            parse_mode="HTML"
        )
# --- A'ZO CHIQIB KETGANDA (LEFT XABARINI O'CHIRISH VA STATUSNI YANGILASH) ---
@dp.message(F.left_chat_member)
async def delete_left_message(message: types.Message):
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Chiqish xabarini o'chirolmadim: {e}")
        
    left_user_id = message.left_chat_member.id
    # Agar chiqib ketgan odam bazada bo'lsa, uni klubdan o'chiramiz
    if left_user_id in USER_HOUSES:
        USER_HOUSES[left_user_id]["in_club"] = False
        save_data(USER_HOUSES)

# --- TAQSIMLASH JARAYONI (GURUHDA E'LON QILISH) ---
@dp.callback_query(F.data.startswith("wear_hat_"))
async def sorting_hat_process(callback: types.CallbackQuery):
    target_id = int(callback.data.split("_")[2])
    
    if callback.from_user.id != target_id:
        await callback.answer("Bu siz uchun emas! ✋", show_alert=True)
        return
    
    # Ehtiyot chorasi: Agar bazada bo'lmasa, uni testga yuboramiz
    if target_id not in USER_HOUSES:
        await callback.answer("Siz hali test ishlamagansiz! Avval shaxsiyda test yeching.", show_alert=True)
        return
        
    # MUHIM O'ZGARISH: Tasodifiy emas, bazadagi haqiqiy natijani olamiz
    house_name = USER_HOUSES[target_id]["house"]
    house_data = HOUSES[house_name]
    
    await callback.answer("Ma'lumotlaringiz o'qilmoqda...", show_alert=False)
    await callback.message.delete()
    
    user_mention = f"<a href='tg://user?id={target_id}'>{callback.from_user.first_name}</a>"
    final_caption = house_data['desc'].format(mention=user_mention)
    
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        message_thread_id=SORTING_TOPIC_ID,
        photo=house_data['id'],
        caption=final_caption,
        parse_mode="HTML"
    )

# --- STATISTIKA (RO'YXAT) - ANONIM ADMINLARNI HAM QO'LLAB-QUVVATLAYDI ---
@dp.message(Command("statistika"))
async def show_statistics(message: types.Message):
    is_admin = False

    # 1-TEKSHIRUV: Agar Anonim Admin bo'lsa (GroupAnonymousBot ID: 1087968824)
    # Yoki xabar to'g'ridan-to'g'ri kanal/guruh nomidan yozilgan bo'lsa
    if message.from_user.id == 1087968824 or (message.sender_chat and message.sender_chat.id == message.chat.id):
        is_admin = True
    else:
        # 2-TEKSHIRUV: Oddiy admin yoki Creator ekanligini tekshiramiz
        try:
            member = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in ['administrator', 'creator']:
                is_admin = True
        except:
            pass

    # Agar admin bo'lmasa, to'xtatamiz
    if not is_admin:
        await message.reply("⛔️ <b>Bu buyruq faqat Hogwarts direktori uchun!</b>", parse_mode="HTML")
        return

    # 2. Ma'lumotlarni yig'amiz (Faqat guruhdagilarni)
    stats = {
        "Gryffindor": [],
        "Slytherin": [],
        "Ravenclaw": [],
        "Hufflepuff": []
    }
    
    for user_id, info in USER_HOUSES.items():
        if info.get("in_club", False): # DIQQAT: Faqat klubdagilar o'tadi
            h_name = info["house"]
            if h_name in stats:
                stats[h_name].append(info["mention"])
            
    # 3. Chiroyli matn tuzamiz
    text = "📜 <b>HOGWARTS O'QUVCHILARI RO'YXATI:</b>\n\n"
    
    # Gryffindor
    text += f"🦁 <b>Gryffindor ({len(stats['Gryffindor'])}):</b>\n"
    text += ", ".join(stats['Gryffindor']) if stats['Gryffindor'] else "<i>Hozircha hech kim yo'q</i>"
    text += "\n\n"
    
    # Slytherin
    text += f"🐍 <b>Slytherin ({len(stats['Slytherin'])}):</b>\n"
    text += ", ".join(stats['Slytherin']) if stats['Slytherin'] else "<i>Hozircha hech kim yo'q</i>"
    text += "\n\n"

    # Ravenclaw
    text += f"🦅 <b>Ravenclaw ({len(stats['Ravenclaw'])}):</b>\n"
    text += ", ".join(stats['Ravenclaw']) if stats['Ravenclaw'] else "<i>Hozircha hech kim yo'q</i>"
    text += "\n\n"

    # Hufflepuff
    text += f"🦡 <b>Hufflepuff ({len(stats['Hufflepuff'])}):</b>\n"
    text += ", ".join(stats['Hufflepuff']) if stats['Hufflepuff'] else "<i>Hozircha hech kim yo'q</i>"
    
    await message.reply(text, parse_mode="HTML")
    
# --- OBUNANI TASDIQLASH TUGMASI BOSILGANDA ---
@dp.callback_query(F.data == "verify_subscription")
async def verify_sub_handler(callback: types.CallbackQuery):
    is_subbed = await check_subscription(callback.from_user.id)
    if is_subbed:
        await callback.message.delete()
        await callback.answer("Obuna tasdiqlandi! Xush kelibsiz 🪄", show_alert=False)
        
        # Testni boshlash uchun WebApp tugmasini beramiz
        user_mention = f"<a href='tg://user?id={callback.from_user.id}'>{callback.from_user.first_name}</a>"
        caption_text = f"🧙‍♂️ <b>Xush kelibsiz, {user_mention}!</b>\n\n🏰 Sizni Hogwarts sehrgarlar maktabining fakultetlaridan biriga taqsimlashimiz kerak.\n\n👇Pastdagi tugmani bosib fakultetingizni aniqlang."
        web_app_btn = InlineKeyboardButton(text="Testdan o'tish", web_app=WebAppInfo(url="https://abdoollox.github.io/SortingWebApp/"))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_btn]])
        
        await bot.send_photo(chat_id=callback.message.chat.id, photo=HAT_IMG_ID, caption=caption_text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await callback.answer("Hali a'zo bo'lmapsiz! Iltimos, kanal yoki guruhga qo'shiling.", show_alert=True)

# --- LICHKADA YOKI DEEP LINK ORQALI KELGANLAR UCHUN (/start) ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    
    try:
        await message.delete()
    except Exception:
        pass

    # 1. MAJBURIY OBUNA TEKSHIRUVI (BARCHA UCHUN)
    is_subbed = await check_subscription(user_id)
    if not is_subbed:
        await bot.send_message(
            chat_id=message.chat.id,
            text="✋ <b>To'xtang! Shlyapa sizni tanimayapti.</b>\n\n🧙‍♂️Taqsimlovchi shlyapadan foydalanish uchun kanalimizga obuna bo'lishingiz kerak!\n\n👇Pastdagi tugma orqali kanalga a'zo bo'ling va tasdiqlang:",
            reply_markup=get_subscription_keyboard(),
            parse_mode="HTML"
        )
        return # Kod shu yerda to'xtaydi

    # 2. DEEP LINK TEKSHIRUVI (WebApp dan natija qaytsa)
    args = command.args 
    
    if args and args.startswith("res_"):
        parts = args.split("_")
        
        if len(parts) >= 6:
            house_name = parts[1]
            g_pts, s_pts, r_pts, h_pts = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
        else:
            house_name = parts[1]
            g_pts, s_pts, r_pts, h_pts = 5, 0, 0, 0 
        
        if house_name in HOUSES:
            house_data = HOUSES[house_name]
            
            # BAZAGA YOZISH (ENDI BALLAR HAM SAQLANADI)
            USER_HOUSES[user_id] = {
                "house": house_name,
                "name": message.from_user.first_name,
                "mention": f"<a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>",
                "in_club": False,
                "g_pts": g_pts, # YANGLIK
                "s_pts": s_pts, # YANGLIK
                "r_pts": r_pts, # YANGLIK
                "h_pts": h_pts  # YANGLIK
            }
            
            try:
                member = await bot.get_chat_member(chat_id=GROUP_CHAT_ID, user_id=user_id)
                if member.status in ['member', 'administrator', 'creator', 'restricted']:
                    USER_HOUSES[user_id]["in_club"] = True
            except Exception:
                pass 
                
            save_data(USER_HOUSES)
            
            def make_bar(pts, color_emoji):
                blocks = pts  
                empty = 5 - pts 
                return (color_emoji * blocks) + ("⬛" * empty)
            
            stats_text = (
                f"\n\n📊 <b>Statistik tahlil:</b>\n\n"
                f"🦁 <b>Gryffindor: {g_pts * 20}%</b>\n"
                f"↳ {make_bar(g_pts, '🟥')}\n"
                f"🦅 <b>Ravenclaw: {r_pts * 20}%</b>\n"
                f"↳ {make_bar(r_pts, '🟦')}\n"
                f"🐍 <b>Slytherin: {s_pts * 20}%</b>\n"
                f"↳ {make_bar(s_pts, '🟩')}\n"
                f"🦡 <b>Hufflepuff: {h_pts * 20}%</b>\n"
                f"↳ {make_bar(h_pts, '🟨')}"
            )
            
            user_mention = f"<a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
            final_caption = house_data['desc'].format(mention=user_mention) + stats_text
            
            web_app_btn = InlineKeyboardButton(text="Qayta ishlash", web_app=WebAppInfo(url="https://abdoollox.github.io/SortingWebApp/"))
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_btn]])
            
            await bot.send_photo(chat_id=message.chat.id, photo=house_data['id'], caption=final_caption, reply_markup=keyboard, parse_mode="HTML")

            if USER_HOUSES[user_id]["in_club"]:
                try:
                    await bot.send_photo(chat_id=GROUP_CHAT_ID, message_thread_id=SORTING_TOPIC_ID, photo=house_data['id'], caption=f"📣 <b>Yangi o'quvchi taqsimlandi!</b>\n\n{final_caption}", parse_mode="HTML")
                except Exception as e:
                    logging.warning(f"Guruhga e'lon qilib bo'lmadi: {e}")
        return

   # 3. ESKI FOYDALANUVCHILAR UCHUN
    if user_id in USER_HOUSES:
        user_data = USER_HOUSES[user_id]
        current_house = user_data["house"]
        house_data = HOUSES[current_house]
        
        caption_text = f"✋ Siz allaqachon <b>{current_house}</b> {house_data['emoji']} fakultetiga taqsimlangansiz!\n\n"
        
        # XAVFSIZLIK: Agar mijoz bazasida ballar saqlangan bo'lsa, grafik chizamiz
        if "g_pts" in user_data:
            g_pts, s_pts, r_pts, h_pts = user_data["g_pts"], user_data["s_pts"], user_data["r_pts"], user_data["h_pts"]
            
            def make_bar(pts, color_emoji):
                blocks = pts  
                empty = 5 - pts 
                return (color_emoji * blocks) + ("⬛" * empty)
                
            stats_text = (
                f"📊 <b>Sizning oxirgi tahlilingiz:</b>\n\n"
                f"🦁 <b>Gryffindor: {g_pts * 20}%</b>\n"
                f"↳ {make_bar(g_pts, '🟥')}\n"
                f"🦅 <b>Ravenclaw: {r_pts * 20}%</b>\n"
                f"↳ {make_bar(r_pts, '🟦')}\n"
                f"🐍 <b>Slytherin: {s_pts * 20}%</b>\n"
                f"↳ {make_bar(s_pts, '🟩')}\n"
                f"🦡 <b>Hufflepuff: {h_pts * 20}%</b>\n"
                f"↳ {make_bar(h_pts, '🟨')}\n\n"
            )
            caption_text += stats_text # Grafikni asosiy matnga ulaymiz
            
        caption_text += "Fikringizni o'zgartirdingizmi yoki qayta sinab ko'rmoqchimisiz? Pastdagi tugma orqali testni qayta ishlashingiz mumkin."
        
        web_app_btn = InlineKeyboardButton(text="Qayta ishlash", web_app=WebAppInfo(url="https://abdoollox.github.io/SortingWebApp/"))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_btn]])
        
        await bot.send_photo(chat_id=message.chat.id, photo=house_data['id'], caption=caption_text, reply_markup=keyboard, parse_mode="HTML")
        return

    # 4. YANGI FOYDALANUVCHILAR UCHUN (OBUNADAN O'TGANLAR)
    user_mention = f"<a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
    caption_text = f"🧙‍♂️ <b>Xush kelibsiz, {user_mention}!</b>\n\nSizni fakultetga taqsimlashimiz kerak. Pastdagi tugmani bosib testni boshlang."
    web_app_btn = InlineKeyboardButton(text="🧙 Qalpoqni kiyish", web_app=WebAppInfo(url="https://abdoollox.github.io/SortingWebApp/"))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_btn]])
    
    await bot.send_photo(chat_id=message.chat.id, photo=HAT_IMG_ID, caption=caption_text, reply_markup=keyboard, parse_mode="HTML")
    
# --- ASOSIY ISHGA TUSHIRISH ---
async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # MUHIM: Web serverni fonda ishga tushiramiz (Render uchun)
    asyncio.create_task(start_web_server()) 
    
    # Botni polling rejimida ishga tushiramiz
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot to'xtadi!")






