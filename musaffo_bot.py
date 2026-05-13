"""
Musaffo Chashma Tomchisi — Telegram Bot
Ishlatish: pip install python-telegram-bot
"""

import logging
import asyncio
import sys
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputMediaPhoto,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ─── Token va Admin ───────────────────────────────────────────────────────────
BOT_TOKEN = "8603889308:AAGH2qlllRzLAu4bwlDnJt5NHEaD_bPm9e4"
ADMIN_ID  = 1338737775

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Conversation states ──────────────────────────────────────────────────────
(
    MAIN_MENU,
    ORDER_NAME,
    ORDER_PHONE,
    ORDER_ADDRESS,
    ORDER_TYPE,
    ORDER_QTY,
    ORDER_CONFIRM,
) = range(7)

# ─── Ma'lumotlar ──────────────────────────────────────────────────────────────
COMPANY  = "Musaffo Chashma Tomchisi"
LOCATION = "Boylata MFY, Boylata qishlog'i (Katta yo'l bo'yida afisha ilingan)"
PHONE    = "+998 77 517 04 30"

PRICES = {
    "19 litr": 12_000,
    "10 litr":  4_000,
    "1 litr":      400,
}

WATER_PHOTOS = [
    "https://i.ibb.co/0jj9LFjJ/1.jpg",
    "https://i.ibb.co/JRyjRngF/2.jpg",
    "https://i.ibb.co/Z6hp8Rn4/3.jpg",
    "https://i.ibb.co/XfwpmHvp/4.jpg",
    "https://i.ibb.co/jZP1B4sY/5.jpg",
]

WATER_INTRO = (
    "💧 *Sanoat Suv Tozalash Tizimi (RO System)*\n\n"
    "Bu apparat 20 litrli ichimlik suvi ishlab chiqarishda ishlatiladigan "
    "*ko'p bosqichli suv filtrlash uskunasi* hisoblanadi.\n"
    "Unda suv bir marta filtrdan o'tib tozalanadi.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "📊 *Asosiy ko'rsatkichlar:*\n"
    "🔹 5 bosqichli filtrlash\n"
    "🔹 20 litr hajm\n"
    "🔹 100% xavfsiz ichimlik suvi\n"
    "━━━━━━━━━━━━━━━━━━━━━"
)

WATER_FILTERS = (
    "🔬 *Filtr qismlari va vazifalari:*\n\n"
    "1️⃣ *Turbidity Filter — Loyqa Filtri*\n"
    "▫️ Loyqa, Qum, Zang va katta kirlarni ushlab qoladi\n\n"
    "2️⃣ *Adsorption Filter — Ko'mir Filtri*\n"
    "▫️ Xlor, badbo'y hid va kimyoviy moddalarni yutadi\n\n"
    "3️⃣ *Descaling Filter — Yumshatish Filtri*\n"
    "▫️ Kalsiy va magniy tuzlarini kamaytiradi\n\n"
    "4️⃣ *RO Membrana — Asosiy Tozalash*\n"
    "▫️ Bakteriya, virus va og'ir metallarni ushlab qoladi\n\n"
    "5️⃣ *Ultrafiolet (UV) — Sterilizatsiya*\n"
    "▫️ Ultrabinafsha nur orqali mikroorganizmlarni yo'q qiladi\n\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "💧 *Filtrlash jarayoni:*\n"
    "Loyqa → Ko'mir → Yumshatish → RO → UV → 🥤 Toza suv!"
)

PRICES_TEXT = (
    "💰 *Narxlar:*\n\n"
    "🔹 19 litr (baklashka) — *12 000 so'm*\n"
    "🔹 10 litr             — *4 000 so'm*\n"
    "🔹 1 litr (o'zingiz kelib olsangiz) — *400 so'm*\n\n"
    "🚚 Yetkazib berish xizmati mavjud!\n"
    "🎁 *Aksiya:* 10 ta olsangiz — 1 ta BEPUL!"
)

CONTACT_TEXT = (
    f"📍 *Manzil:* {LOCATION}\n\n"
    f"📞 *Telefon:* {PHONE}\n\n"
    "🕐 *Ish vaqti:* 08:00 – 22:00"
)

# ─── Klaviaturalar ────────────────────────────────────────────────────────────
def main_keyboard():
    return ReplyKeyboardMarkup(
        [["💧 Suv haqida", "💰 Narxlar"], ["🛒 Buyurtma berish", "📍 Manzil va kontakt"]],
        resize_keyboard=True,
    )

def water_info_keyboard():
    return ReplyKeyboardMarkup([["🔬 Filtrlar haqida batafsil"], ["🏠 Asosiy menyu"]], resize_keyboard=True)

def water_type_keyboard():
    return ReplyKeyboardMarkup([["19 litr", "10 litr"], ["1 litr", "🏠 Asosiy menyu"]], resize_keyboard=True)

def confirm_keyboard():
    return ReplyKeyboardMarkup([["✅ Tasdiqlash", "❌ Bekor qilish"]], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([["🏠 Asosiy menyu"]], resize_keyboard=True)

# ─── Handlerlar ───────────────────────────────────────────────────────────────
async def notify_admin(context: ContextTypes.DEFAULT_TYPE, d: dict, user_id: int, username: str):
    bonus_line = f"🎁 Bonus: {d['bonus']} ta bepul\n" if d.get("bonus") else ""
    uname = f"@{username}" if username else "username yo'q"
    total_str = f"{d['total']:,}".replace(",", " ")
    text = (
        "🔔 *YANGI BUYURTMA!*\n"
        f"👤 Ism: {d['name']}\n"
        f"📞 Telefon: {d['phone']}\n"
        f"📍 Manzil: {d['address']}\n"
        f"💧 Suv turi: {d['water_type']}\n"
        f"🔢 Miqdor: {d['qty']} ta\n"
        f"💰 Jami: {total_str} so'm\n" + bonus_line +
        f"📱 Telegram: {uname}\nID: `{user_id}`"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Admin xatosi: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Assalomu alaykum! *{COMPANY}* botiga xush kelibsiz!",
        parse_mode="Markdown", reply_markup=main_keyboard()
    )
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "💧 Suv haqida":
        media_group = [InputMediaPhoto(media=url) for url in WATER_PHOTOS]
        try: await update.message.reply_media_group(media=media_group)
        except: pass
        await update.message.reply_text(WATER_INTRO, parse_mode="Markdown", reply_markup=water_info_keyboard())
    elif text == "🔬 Filtrlar haqida batafsil":
        await update.message.reply_text(WATER_FILTERS, parse_mode="Markdown", reply_markup=water_info_keyboard())
    elif text == "💰 Narxlar":
        await update.message.reply_text(PRICES_TEXT, parse_mode="Markdown", reply_markup=main_keyboard())
    elif text == "📍 Manzil va kontakt":
        await update.message.reply_text(CONTACT_TEXT, parse_mode="Markdown", reply_markup=main_keyboard())
    elif text == "🛒 Buyurtma berish":
        await update.message.reply_text("Ismingizni kiriting:", reply_markup=back_keyboard())
        return ORDER_NAME
    elif text == "🏠 Asosiy menyu":
        await update.message.reply_text("Bosh menyu", reply_markup=main_keyboard())
    return MAIN_MENU

async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu": return await back_to_main(update, context)
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni yuboring:", 
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📱 Raqamni yuborish", request_contact=True)], ["🏠 Asosiy menyu"]], resize_keyboard=True))
    return ORDER_PHONE

async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu": return await back_to_main(update, context)
    phone = update.message.contact.phone_number if update.message.contact else update.message.text
    context.user_data["phone"] = phone
    await update.message.reply_text("Manzilingizni kiriting:", reply_markup=back_keyboard())
    return ORDER_ADDRESS

async def order_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu": return await back_to_main(update, context)
    context.user_data["address"] = update.message.text
    await update.message.reply_text("Suv hajmini tanlang:", reply_markup=water_type_keyboard())
    return ORDER_TYPE

async def order_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu": return await back_to_main(update, context)
    if update.message.text not in PRICES: return ORDER_TYPE
    context.user_data["water_type"] = update.message.text
    await update.message.reply_text("Nechta buyurtma qilasiz?", reply_markup=back_keyboard())
    return ORDER_QTY

async def order_qty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu": return await back_to_main(update, context)
    try:
        qty = int(update.message.text)
        if qty < 1: raise ValueError
    except: return ORDER_QTY
    d = context.user_data
    d["qty"] = qty
    d["total"] = PRICES[d["water_type"]] * qty
    d["bonus"] = qty // 10
    summary = f"👤 Ism: {d['name']}\n💧 Hajm: {d['water_type']}\n🔢 Miqdor: {qty}\n💰 Jami: {d['total']:,} so'm\nTasdiqlaysizmi?"
    await update.message.reply_text(summary, reply_markup=confirm_keyboard())
    return ORDER_CONFIRM

async def order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "✅ Tasdiqlash":
        await update.message.reply_text("Buyurtma qabul qilindi!", reply_markup=main_keyboard())
        await notify_admin(context, context.user_data, update.effective_user.id, update.effective_user.username)
        context.user_data.clear()
        return MAIN_MENU
    return await back_to_main(update, context)

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Asosiy menyu", reply_markup=main_keyboard())
    return MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Yordam uchun: /start", reply_markup=main_keyboard())
    return MAIN_MENU

# ─── MAIN (TUZATILGAN QISIM) ──────────────────────────────────────────────────
async def main():
    # Application yaratish
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlerlarni qo'shish
    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_command))

    # Render uchun botni ishga tushirish
    async with app:
        await app.initialize()
        await app.start()
        logger.info("Bot 3.12 versiyada ishga tushdi!")
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Bot to'xtab qolmasligi uchun
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
