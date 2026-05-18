import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

BOT_TOKEN = "8981240580:AAGa_iJR6cq_xn5vjy5T94ScoJ60GGY0HKg"
CHANNEL_USERNAME = "@anidavi_official"
CHANNEL_LINK = "https://t.me/anidavi_official"
BOT_USERNAME = "Anidavi_bot"
ADMIN_IDS = [5654433816]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
users_db = set()

def get_status(user_id):
    return "👑 Admin" if user_id in ADMIN_IDS else "Oddiy"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Anime izlash", callback_data="search")],
        [InlineKeyboardButton("📚 Qo'llanma", callback_data="guide"),
         InlineKeyboardButton("💰 Reklama va Homiylik", callback_data="ads")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton("🤖 Bot haqida", callback_data="about")],
        [InlineKeyboardButton("💎 VIP obuna (cheklovlarsiz)", callback_data="vip")],
    ])

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_db.add(user.id)
    if user.id in ADMIN_IDS:
        text = (
            f"📊 Status: {get_status(user.id)}\n"
            f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
            f"👇 Quyidagi tugmalar orqali botdan foydalaning:\n\n"
            f"📹 <b>Kanalga video yuborish:</b>\n"
            f"1. Botga video yuboring\n"
            f"2. Keyin anime ma'lumotlarini yozing\n"
            f"3. Bot avtomatik kanalga yuboradi!"
        )
    else:
        text = (
            f"📊 Status: {get_status(user.id)}\n"
            f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
            f"👇 Quyidagi tugmalar orqali botdan foydalaning:"
        )
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode="HTML")

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("👇 Menyu uchun /start bosing", reply_markup=main_menu())
        return

    video = update.message.video or update.message.document
    context.user_data['pending_video'] = video.file_id
    context.user_data['waiting_caption'] = True

    await update.message.reply_text(
        "✅ Video qabul qilindi!\n\n"
        "Endi anime ma'lumotlarini yozing:\n\n"
        "<b>Misol:</b>\n"
        "<code>Naruto Shippuden\n"
        "Qism: 1/500\n"
        "Til: O'zbek\n"
        "Janr: Aksyon</code>",
        parse_mode="HTML"
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_db.add(user.id)
    text = update.message.text or ""

    if user.id in ADMIN_IDS and context.user_data.get('waiting_caption'):
        context.user_data['waiting_caption'] = False
        file_id = context.user_data.get('pending_video')

        if not file_id:
            await update.message.reply_text("❌ Avval video yuboring!")
            return

        lines = text.strip().split('\n')
        anime_nomi = lines[0] if lines else "Anime"
        qolgan = '\n'.join(f"➤ {l}" for l in lines[1:]) if len(lines) > 1 else ""

        caption = f"🎌 <b>{anime_nomi}</b>\n\n{qolgan}\n\n➤ Kanal: @anidavi_official"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Tomosha qilish ✨", url=f"https://t.me/{BOT_USERNAME}")]
        ])

        try:
            await context.bot.send_video(
                chat_id=CHANNEL_USERNAME,
                video=file_id,
                caption=caption,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await update.message.reply_text("✅ Kanalga muvaffaqiyatli yuborildi! 🎉")
        except Exception as e:
            await update.message.reply_text(
                f"❌ Xato yuz berdi: {e}\n\n"
                "Botni kanalga admin qilganingizni tekshiring!"
            )
        context.user_data.pop('pending_video', None)
        return

    await update.message.reply_text("👇 Menyu uchun /start bosing", reply_markup=main_menu())

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
            reply_markup=main_menu(), parse_mode="HTML"
        )
    elif d == "search":
        await q.edit_message_text(
            "🔍 <b>Anime izlash</b>\n\nKanalimizga o'ting:\n👉 @anidavi_official",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Kanalga o'tish", url=CHANNEL_LINK)],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )
    elif d == "guide":
        await q.edit_message_text(
            "📚 <b>Qo'llanma</b>\n\n"
            "1️⃣ Kanalga obuna bo'ling\n   👉 @anidavi_official\n\n"
            "2️⃣ Anime izlash tugmasini bosing\n\n"
            "3️⃣ Anime nomini toping\n\n"
            "4️⃣ Tomosha qilish tugmasini bosing\n\n"
            "💎 VIP obuna bilan cheklovsiz tomosha qiling!",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "ads":
        await q.edit_message_text(
            "💰 <b>Reklama va Homiylik</b>\n\n"
            "📢 Reklama uchun admin bilan bog'laning!\n"
            "💵 Narxlar: muzokarali\n\n"
            "📩 Admin: @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Admin", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )
    elif d == "stats":
        await q.edit_message_text(
            f"📊 <b>Statistika</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{len(users_db)}</b>\n"
            f"📺 Kanal: @anidavi_official\n"
            f"🤖 Bot: @{BOT_USERNAME}",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "about":
        await q.edit_message_text(
            "🤖 <b>Bot haqida</b>\n\n"
            "🎌 <b>AniDavi</b> - O'zbek tilida anime ko'rish uchun eng qulay bot!\n\n"
            "✨ Imkoniyatlar:\n"
            "• Anime izlash va tomosha qilish\n"
            "• O'zbek tilidagi anime\n"
            "• VIP obuna\n"
            "• Har kuni yangi animeler\n\n"
            "📺 Kanal: @anidavi_official",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "vip":
        await q.edit_message_text(
            "💎 <b>VIP Obuna</b>\n\n"
            "✅ Cheklovsiz anime\n"
            "✅ HD sifat\n"
            "✅ Reklama yo'q\n\n"
            "💰 Narxlar:\n"
            "• 1 oy: 15,000 so'm\n"
            "• 3 oy: 35,000 so'm\n"
            "• 1 yil: 100,000 so'm\n\n"
            "📩 @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 VIP olish", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )

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
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, video_handler))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
