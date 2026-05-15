"""
Musaffo Chashma Tomchisi — Telegram Bot
python-telegram-bot==21.2 | Render.com worker
"""

import logging
import os
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
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8603889308:AAGH2qlllRzLAu4bwlDnJt5NHEaD_bPm9e4")
ADMIN_ID  = int(os.environ.get("ADMIN_ID", "1338737775"))

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
    "1 litr":     400,
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
    "Unda suv bir nechta filtrdan o'tib tozalanadi.\n\n"
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
    "▫️ Loyqa, Qum, Zang va katta kirlarni ushlab qoladi\n"
    "✅ Suv tiniqlashadi, keyingi filtrlar uzoq ishlaydi\n\n"
    "2️⃣ *Adsorption Filter — Ko'mir Filtri*\n"
    "▫️ Xlor, badbo'y hid va kimyoviy moddalarni yutadi\n"
    "✅ Suv maza va hidsiz bo'ladi\n\n"
    "3️⃣ *Descaling Filter — Yumshatish Filtri*\n"
    "▫️ Kalsiy va magniy tuzlarini kamaytiradi\n"
    "✅ Suv yumshoq, uskuna uzoq ishlaydi\n\n"
    "4️⃣ *RO Membrana — Asosiy Tozalash*\n"
    "▫️ Bakteriya, virus va og'ir metallarni ushlab qoladi\n"
    "✅ Premium sifatdagi ichimlik suvi hosil bo'ladi\n\n"
    "5️⃣ *Ultrafiolet (UV) — Sterilizatsiya*\n"
    "▫️ Ultrabinafsha nur orqali mikroorganizmlarni yo'q qiladi\n"
    "▫️ Kimyoviy modda qo'shmasdan dezinfeksiya qiladi\n"
    "✅ To'liq xavfsiz, sog'lom suv tayyor!\n\n"
    "━━━━━━━━━━━━━━━━━━━━━\n"
    "💧 *Filtrlash jarayoni:*\n"
    "Loyqa → Ko'mir → Yumshatish → RO → UV → 🥤 Toza suv!"
)

PRICES_TEXT = (
    "💰 *Narxlar:*\n\n"
    "🔹 19 litr (baklashka) — *12 000 so'm*\n"
    "🔹 10 litr              — *4 000 so'm*\n"
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
        [
            ["💧 Suv haqida", "💰 Narxlar"],
            ["🛒 Buyurtma berish", "📍 Manzil va kontakt"],
        ],
        resize_keyboard=True,
    )

def water_info_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🔬 Filtrlar haqida batafsil"],
            ["🏠 Asosiy menyu"],
        ],
        resize_keyboard=True,
    )

def water_type_keyboard():
    return ReplyKeyboardMarkup(
        [["19 litr", "10 litr"], ["1 litr", "🏠 Asosiy menyu"]],
        resize_keyboard=True,
    )

def confirm_keyboard():
    return ReplyKeyboardMarkup(
        [["✅ Tasdiqlash", "❌ Bekor qilish"]],
        resize_keyboard=True,
    )

def back_keyboard():
    return ReplyKeyboardMarkup([["🏠 Asosiy menyu"]], resize_keyboard=True)

# ─── Admin ga xabar yuborish ──────────────────────────────────────────────────
async def notify_admin(context: ContextTypes.DEFAULT_TYPE, d: dict, user_id: int, username: str):
    bonus_line = f"🎁 Bonus: {d['bonus']} ta bepul\n" if d.get("bonus") else ""
    uname = f"@{username}" if username else "username yo'q"
    total_str = f"{d['total']:,}".replace(",", " ")

    text = (
        "🔔 *YANGI BUYURTMA!*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism: {d['name']}\n"
        f"📞 Telefon: {d['phone']}\n"
        f"📍 Manzil: {d['address']}\n"
        f"💧 Suv turi: {d['water_type']}\n"
        f"🔢 Miqdor: {d['qty']} ta\n"
        f"💰 Jami: {total_str} so'm\n"
        + bonus_line
        + "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 Telegram: {uname}\n"
        f"🆔 User ID: `{user_id}`"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Admin ga xabar yuborishda xato: {e}")

# ─── /start ───────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Assalomu alaykum, *{user}*! 👋\n\n"
        f"*{COMPANY}* botiga xush kelibsiz!\n\n"
        "Sof ichimlik suv buyurtma qilish yoki ma'lumot olish uchun "
        "quyidagi tugmalardan foydalaning 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )
    return MAIN_MENU

# ─── SUV HAQIDA handler ───────────────────────────────────────────────────────
async def show_water_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    media_group = [InputMediaPhoto(media=url) for url in WATER_PHOTOS]
    try:
        await update.message.reply_media_group(media=media_group)
    except Exception as e:
        logger.warning(f"Rasmlarni yuborishda xato: {e}")

    await update.message.reply_text(
        WATER_INTRO,
        parse_mode="Markdown",
        reply_markup=water_info_keyboard(),
    )

async def show_filter_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        WATER_FILTERS,
        parse_mode="Markdown",
        reply_markup=water_info_keyboard(),
    )
    return MAIN_MENU

# ─── Asosiy menyu ─────────────────────────────────────────────────────────────
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    if text == "💧 Suv haqida":
        await show_water_info(update, context)
        return MAIN_MENU

    elif text == "🔬 Filtrlar haqida batafsil":
        return await show_filter_details(update, context)

    elif text == "💰 Narxlar":
        await update.message.reply_text(
            PRICES_TEXT, parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif text == "📍 Manzil va kontakt":
        await update.message.reply_text(
            CONTACT_TEXT, parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif text == "🛒 Buyurtma berish":
        await update.message.reply_text(
            "📝 *Buyurtma uchun ro'yxatdan o'tish*\n\n"
            "Ismingiz yoki tashkilot nomini kiriting:",
            parse_mode="Markdown",
            reply_markup=back_keyboard(),
        )
        return ORDER_NAME

    elif text == "🏠 Asosiy menyu":
        await update.message.reply_text(
            "🏠 Bosh menyuga qaytdingiz.", reply_markup=main_keyboard()
        )

    else:
        await update.message.reply_text(
            "Iltimos, quyidagi tugmalardan birini tanlang 👇",
            reply_markup=main_keyboard(),
        )

    return MAIN_MENU

# ─── Buyurtma qadamlari ───────────────────────────────────────────────────────
async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu":
        return await back_to_main(update, context)

    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "📞 Telefon raqamingizni kiriting:\n_(masalan: +998 90 123 45 67)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [
                [KeyboardButton("📱 Raqamni yuborish", request_contact=True)],
                ["🏠 Asosiy menyu"],
            ],
            resize_keyboard=True,
        ),
    )
    return ORDER_PHONE


async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text and update.message.text == "🏠 Asosiy menyu":
        return await back_to_main(update, context)

    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = update.message.text

    context.user_data["phone"] = phone
    await update.message.reply_text(
        "🏠 Yetkazib berish manzilingizni kiriting:",
        reply_markup=back_keyboard(),
    )
    return ORDER_ADDRESS


async def order_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu":
        return await back_to_main(update, context)

    context.user_data["address"] = update.message.text
    await update.message.reply_text(
        "💧 Qaysi hajmdagi suv kerak?\n\n"
        "🔹 19 litr — 12 000 so'm\n"
        "🔹 10 litr — 4 000 so'm\n"
        "🔹 1 litr  — 400 so'm\n\n"
        "🎁 10 ta olsangiz 1 ta BEPUL!",
        reply_markup=water_type_keyboard(),
    )
    return ORDER_TYPE


async def order_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🏠 Asosiy menyu":
        return await back_to_main(update, context)

    if text not in PRICES:
        await update.message.reply_text(
            "Iltimos, suv turini tanlang:", reply_markup=water_type_keyboard()
        )
        return ORDER_TYPE

    context.user_data["water_type"] = text
    await update.message.reply_text(
        f"✅ *{text}* tanlandi!\n\nNechta suv buyurtma qilasiz? _(raqam kiriting)_",
        parse_mode="Markdown",
        reply_markup=back_keyboard(),
    )
    return ORDER_QTY


async def order_qty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "🏠 Asosiy menyu":
        return await back_to_main(update, context)

    try:
        qty = int(update.message.text)
        if qty < 1:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "⚠️ Iltimos, to'g'ri son kiriting (masalan: 5):",
            reply_markup=back_keyboard(),
        )
        return ORDER_QTY

    context.user_data["qty"] = qty
    water_type = context.user_data["water_type"]
    price = PRICES[water_type]
    total = price * qty
    bonus = qty // 10

    context.user_data["total"] = total
    context.user_data["bonus"] = bonus

    bonus_text = (
        f"\n\n🎁 *Bonus:* {bonus} ta bepul suv (10 tadan 1 ta qoida)!" if bonus else ""
    )
    total_str = f"{total:,}".replace(",", " ")

    summary = (
        "📋 *Buyurtma ma'lumotlari:*\n\n"
        f"👤 Ism: {context.user_data['name']}\n"
        f"📞 Telefon: {context.user_data['phone']}\n"
        f"📍 Manzil: {context.user_data['address']}\n"
        f"💧 Suv turi: {water_type}\n"
        f"🔢 Miqdor: {qty} ta\n"
        f"💰 Narx: {total_str} so'm"
        + bonus_text
        + "\n\nBuyurtmani tasdiqlaymizmi?"
    )

    await update.message.reply_text(
        summary, parse_mode="Markdown", reply_markup=confirm_keyboard()
    )
    return ORDER_CONFIRM


async def order_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text

    if text == "✅ Tasdiqlash":
        d = context.user_data
        bonus_line = f"🎁 Bonus: {d['bonus']} ta bepul\n" if d.get("bonus") else ""
        total_str = f"{d['total']:,}".replace(",", " ")

        msg = (
            "🎉 *Buyurtmangiz qabul qilindi!*\n\n"
            f"👤 {d['name']}\n"
            f"📞 {d['phone']}\n"
            f"📍 {d['address']}\n"
            f"💧 {d['water_type']} × {d['qty']} ta\n"
            f"💰 {total_str} so'm\n"
            + bonus_line
            + "\n✅ Tez orada operatorimiz siz bilan bog'lanadi!\n\n"
            f"📞 Savollar uchun: {PHONE}"
        )
        await update.message.reply_text(
            msg, parse_mode="Markdown", reply_markup=main_keyboard()
        )

        user = update.effective_user
        await notify_admin(context, d, user.id, user.username)

        context.user_data.clear()
        return MAIN_MENU

    elif text == "❌ Bekor qilish":
        await update.message.reply_text(
            "❌ Buyurtma bekor qilindi.\nBosh menyuga qaytdingiz.",
            reply_markup=main_keyboard(),
        )
        context.user_data.clear()
        return MAIN_MENU

    else:
        await update.message.reply_text(
            "Iltimos, tasdiqlang yoki bekor qiling:",
            reply_markup=confirm_keyboard(),
        )
        return ORDER_CONFIRM

# ─── Orqaga qaytish ───────────────────────────────────────────────────────────
async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "🏠 Bosh menyuga qaytdingiz.", reply_markup=main_keyboard()
    )
    return MAIN_MENU

# ─── /help ────────────────────────────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "ℹ️ *Yordam*\n\n"
        "/start — Botni qayta ishga tushirish\n"
        "/help  — Yordam\n\n"
        "Buyurtma berish yoki ma'lumot olish uchun "
        "quyidagi tugmalardan foydalaning 👇",
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )
    return MAIN_MENU

# ─── main ─────────────────────────────────────────────────────────────────────
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU:    [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            ORDER_NAME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name)],
            ORDER_PHONE:  [
                MessageHandler(filters.CONTACT, order_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone),
            ],
            ORDER_ADDRESS:[MessageHandler(filters.TEXT & ~filters.COMMAND, order_address)],
            ORDER_TYPE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, order_type)],
            ORDER_QTY:    [MessageHandler(filters.TEXT & ~filters.COMMAND, order_qty)],
            ORDER_CONFIRM:[MessageHandler(filters.TEXT & ~filters.COMMAND, order_confirm)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
        ],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_command))

    logger.info("Bot ishga tushdi...")

    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        # bot to'xtatilguncha kutadi
        await app.updater.idle()
        await app.stop()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
