import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ============================================================
# SOZLAMALAR - BU YERGA O'Z MA'LUMOTLARINGIZNI KIRITING
# ============================================================
BOT_TOKEN = "8981240580:AAGa_iJR6cq_xn5vjy5T94ScoJ60GGY0HKg"
CHANNEL_USERNAME = "@anidavi_official"
BOT_USERNAME = "@Anidavi_bot"
ADMIN_IDS = [5654433816]
# ============================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Foydalanuvchilar statistikasi (oddiy holatda - xotirada saqlanadi)
users_db = set()

# ================= YORDAMCHI FUNKSIYALAR =================

def get_status(user_id: int) -> str:
    """Foydalanuvchi statusini qaytaradi"""
    if user_id in ADMIN_IDS:
        return "👑 Admin"
    # VIP tizimni kengaytirish mumkin
    return "Oddiy"

def get_main_keyboard():
    """Asosiy menyu klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("🔍 Anime izlash", callback_data="anime_search")],
        [
            InlineKeyboardButton("📚 Qo'llanma", callback_data="guide"),
            InlineKeyboardButton("💰 Reklama va Homiylik", callback_data="ads")
        ],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton("🤖 Bot haqida", callback_data="about")],
        [InlineKeyboardButton("💎 VIP obuna (cheklovlarsiz)", callback_data="vip")],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Orqaga tugmasi"""
    keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]]
    return InlineKeyboardMarkup(keyboard)

# ================= KOMANDALAR =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot boshlanganda"""
    user = update.effective_user
    users_db.add(user.id)

    status = get_status(user.id)

    text = (
        f"📊 Status: {status}\n"
        f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
        f"👇 Quyidagi tugmalar orqali botdan foydalaning:"
    )

    await update.message.reply_text(
        text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam komandasi"""
    await update.message.reply_text(
        "📚 <b>Yordam</b>\n\n"
        "/start - Botni boshlash\n"
        "/help - Yordam\n"
        "/search [anime nomi] - Anime izlash\n\n"
        "Barcha funksiyalar tugmalar orqali ham mavjud!",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )

# ================= CALLBACK HANDLER =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalar bosilganda"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    # ── Asosiy menyu ──
    if data == "back_main":
        status = get_status(user.id)
        text = (
            f"📊 Status: {status}\n"
            f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
            f"👇 Quyidagi tugmalar orqali botdan foydalaning:"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )

    # ── Anime izlash ──
    elif data == "anime_search":
        text = (
            "🔍 <b>Anime izlash</b>\n\n"
            f"Kanalimizga o'ting va anime nomini qidiring:\n"
            f"👉 {CHANNEL_USERNAME}\n\n"
            "Yoki quyida anime nomini yozing (masalan: <code>/search Naruto</code>)"
        )
        keyboard = [
            [InlineKeyboardButton("📺 Kanalga o'tish", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]
        ]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    # ── Qo'llanma ──
    elif data == "guide":
        text = (
            "📚 <b>Qo'llanma</b>\n\n"
            "1️⃣ Kanalga obuna bo'ling\n"
            f"   👉 {CHANNEL_USERNAME}\n\n"
            "2️⃣ Anime izlash tugmasini bosing\n\n"
            "3️⃣ Anime nomini kiriting\n\n"
            "4️⃣ <b>Tomosha qilish</b> tugmasini bosing\n\n"
            "💎 VIP obuna bilan cheklovsiz tomosha qiling!"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )

    # ── Reklama va Homiylik ──
    elif data == "ads":
        text = (
            "💰 <b>Reklama va Homiylik</b>\n\n"
            "📢 Reklamaga buyurtma berish uchun admin bilan bog'laning:\n\n"
            "💵 <b>Narxlar:</b>\n"
            "• Post reklama: muzokarali\n"
            "• Bot orqali reklama: muzokarali\n\n"
            "🤝 <b>Homiylik:</b>\n"
            "Kanalimizni qo'llab-quvvatlashingiz mumkin!\n\n"
            "📩 Admin: @admin_username"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )

    # ── Statistika ──
    elif data == "stats":
        total_users = len(users_db)
        text = (
            "📊 <b>Statistika</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
            f"📺 Kanal: {CHANNEL_USERNAME}\n"
            f"🤖 Bot: @Anidavi_bot\n\n"
            "📈 Har kuni yangi foydalanuvchilar qo'shilmoqda!"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )

    # ── Bot haqida ──
    elif data == "about":
        text = (
            "🤖 <b>Bot haqida</b>\n\n"
            "🎌 <b>AniDavi</b> - O'zbek tilida anime ko'rish uchun eng qulay bot!\n\n"
            "✨ <b>Imkoniyatlar:</b>\n"
            "• Anime izlash va tomosha qilish\n"
            "• O'zbek tilidagi anime\n"
            "• VIP obuna - cheklovsiz kontent\n"
            "• Har kuni yangi animeler\n\n"
            "📺 Kanal: @anidavi_official\n"
            "🤖 Bot: @Anidavi_bot\n"
            "👨‍💻 Yaratuvchi: @admin_username"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )

    # ── VIP obuna ──
    elif data == "vip":
        text = (
            "💎 <b>VIP Obuna</b>\n\n"
            "🌟 VIP obuna afzalliklari:\n\n"
            "✅ Cheklovsiz anime tomosha qilish\n"
            "✅ HD sifatda yuklab olish\n"
            "✅ Yangi animelarga erta kirish\n"
            "✅ Reklama yo'q\n"
            "✅ Maxsus VIP kanal\n\n"
            "💰 <b>Narxlar:</b>\n"
            "• 1 oy: 15,000 so'm\n"
            "• 3 oy: 35,000 so'm\n"
            "• 1 yil: 100,000 so'm\n\n"
            "📩 VIP olish uchun admin bilan bog'laning: @admin_username"
        )
        keyboard = [
            [InlineKeyboardButton("📩 Admin bilan bog'lanish", url="https://t.me/admin_username")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_main")]
        ]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

# ================= ADMIN PANEL =================

async def send_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: kanalga post yuborish"""
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Bu buyruq faqat adminlar uchun!")
        return

    text = (
        "👨‍💻 <b>Admin Panel</b>\n\n"
        "Kanalga post yuborish uchun quyidagi formatda yozing:\n\n"
        "<code>/post\n"
        "Anime nomi\n"
        "Qism: 1/12\n"
        "Til: O'zbek\n"
        "Janr: Drama\n"
        "Havola: https://...\n"
        "</code>"
    )
    await update.message.reply_text(text, parse_mode="HTML")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: barcha foydalanuvchilarga xabar yuborish"""
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Bu buyruq faqat adminlar uchun!")
        return

    if not context.args:
        await update.message.reply_text("❌ Xabar kiriting: /broadcast Xabar matni")
        return

    message = " ".join(context.args)
    sent = 0
    failed = 0

    for uid in users_db:
        try:
            await context.bot.send_message(uid, f"📢 <b>Yangilik:</b>\n\n{message}", parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ Xabar yuborildi!\n"
        f"📨 Muvaffaqiyatli: {sent}\n"
        f"❌ Xato: {failed}"
    )

# ================= KANAL POST HANDLER =================

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kanal postlariga 'Tomosha qilish' tugmasi qo'shish"""
    # Bu funksiya channel_post handler bilan ishlaydi
    pass

# ================= XABAR HANDLER =================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oddiy xabarlarni qayta ishlash"""
    user = update.effective_user
    users_db.add(user.id)
    text = update.message.text.lower() if update.message.text else ""

    if "anime" in text or "izlash" in text:
        await update.message.reply_text(
            f"🔍 Anime izlash uchun kanalga o'ting:\n👉 {CHANNEL_USERNAME}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Kanalga o'tish",
                    url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]
            ])
        )
    else:
        await update.message.reply_text(
            "👇 Menyu uchun /start bosing",
            reply_markup=get_main_keyboard()
        )

# ================= BOTNI ISHGA TUSHIRISH =================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Komandalar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("post", send_post))

    # Tugmalar
    app.add_handler(CallbackQueryHandler(button_handler))

    # Xabarlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
