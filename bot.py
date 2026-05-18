import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

BOT_TOKEN = "8981240580:AAGa_iJR6cq_xn5vjy5T94ScoJ60GGY0HKg"
CHANNEL_USERNAME = "@anidavi_official"
CHANNEL_LINK = "https://t.me/anidavi_official"
BOT_USERNAME = "@Anidavi_bot"
ADMIN_IDS = [5654433816]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

users_db = set()

def get_status(user_id):
    if user_id in ADMIN_IDS:
        return "👑 Admin"
    return "Oddiy"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Anime izlash", callback_data="search")],
        [
            InlineKeyboardButton("📚 Qo'llanma", callback_data="guide"),
            InlineKeyboardButton("💰 Reklama va Homiylik", callback_data="ads")
        ],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton("🤖 Bot haqida", callback_data="about")],
        [InlineKeyboardButton("💎 VIP obuna (cheklovlarsiz)", callback_data="vip")],
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_db.add(user.id)
    await update.message.reply_text(
        f"📊 Status: {get_status(user.id)}\n"
        f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
        f"👇 Quyidagi tugmalar orqali botdan foydalaning:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    d = q.data

    if d == "menu":
        await q.edit_message_text(
            f"📊 Status: {get_status(user.id)}\n"
            f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
            f"👇 Quyidagi tugmalar orqali botdan foydalaning:",
            reply_markup=main_menu(),
            parse_mode="HTML"
        )
    elif d == "search":
        await q.edit_message_text(
            "🔍 <b>Anime izlash</b>\n\nKanalimizga o'ting va anime qidiring:\n👉 " + CHANNEL_USERNAME,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Kanalga o'tish", url=CHANNEL_LINK)],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )
    elif d == "guide":
        await q.edit_message_text(
            "📚 <b>Qo'llanma</b>\n\n1️⃣ Kanalga obuna bo'ling\n   👉 " + CHANNEL_USERNAME + "\n\n2️⃣ Anime izlash tugmasini bosing\n\n3️⃣ Anime nomini toping\n\n4️⃣ Tomosha qilish tugmasini bosing\n\n💎 VIP obuna bilan cheklovsiz tomosha qiling!",
            reply_markup=back_menu(),
            parse_mode="HTML"
        )
    elif d == "ads":
        await q.edit_message_text(
            "💰 <b>Reklama va Homiylik</b>\n\n📢 Reklama uchun admin bilan bog'laning!\n\n💵 Narxlar: muzokarali\n\n📩 Admin: @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Admin", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )
    elif d == "stats":
        await q.edit_message_text(
            f"📊 <b>Statistika</b>\n\n👥 Jami foydalanuvchilar: <b>{len(users_db)}</b>\n📺 Kanal: {CHANNEL_USERNAME}\n🤖 Bot: {BOT_USERNAME}",
            reply_markup=back_menu(),
            parse_mode="HTML"
        )
    elif d == "about":
        await q.edit_message_text(
            "🤖 <b>Bot haqida</b>\n\n🎌 <b>AniDavi</b> - O'zbek tilida anime ko'rish uchun eng qulay bot!\n\n✨ Imkoniyatlar:\n• Anime izlash va tomosha qilish\n• O'zbek tilidagi anime\n• VIP obuna\n• Har kuni yangi animeler\n\n📺 Kanal: " + CHANNEL_USERNAME,
            reply_markup=back_menu(),
            parse_mode="HTML"
        )
    elif d == "vip":
        await q.edit_message_text(
            "💎 <b>VIP Obuna</b>\n\n✅ Cheklovsiz anime\n✅ HD sifat\n✅ Reklama yo'q\n\n💰 Narxlar:\n• 1 oy: 15,000 so'm\n• 3 oy: 35,000 so'm\n• 1 yil: 100,000 so'm\n\n📩 @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 VIP olish", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_db.add(update.effective_user.id)
    await update.message.reply_text("👇 Menyu uchun /start bosing", reply_markup=main_menu())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("❌ /broadcast Xabar matni")
        return
    msg = " ".join(context.args)
    sent = 0
    for uid in users_db:
        try:
            await context.bot.send_message(uid, f"📢 {msg}")
            sent += 1
        except:
            pass
    await update.message.reply_text(f"✅ {sent} ta foydalanuvchiga yuborildi!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
