import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

BOT_TOKEN = "8981240580:AAGa_iJR6cq_xn5vjy5T94ScoJ60GGY0HKg"
BOT_USERNAME = "Anidavi_bot"
ADMIN_IDS = [5654433816]

# Majburiy obuna kanallari/guruhlar — kerak bo'lsa qo'shing
REQUIRED_CHANNELS = [
    {"name": "AniDavi Official", "username": "@anidavi_official", "link": "https://t.me/anidavi_official"},
    # Qo'shimcha kanal qo'shish uchun:
    # {"name": "Kanal nomi", "username": "@kanal", "link": "https://t.me/kanal"},
]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

users_db = set()
# anime_db: { anime_id: { 'preview': file_id, 'full': file_id yoki link, 'name': str, 'info': str } }
anime_db = {}
anime_counter = [0]

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

def subscribe_keyboard():
    """Majburiy obuna tugmalari"""
    buttons = []
    for ch in REQUIRED_CHANNELS:
        buttons.append([InlineKeyboardButton(f"📢 {ch['name']}", url=ch['link'])])
    buttons.append([InlineKeyboardButton("✅ Obuna bo'ldim!", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)

async def check_subscription(user_id, bot):
    """Foydalanuvchi barcha kanallarga obuna bo'lganini tekshiradi"""
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(ch['username'], user_id)
            if member.status in [ChatMember.LEFT, ChatMember.BANNED]:
                return False
        except:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_db.add(user.id)

    # Majburiy obuna tekshirish (adminlar uchun yo'q)
    if user.id not in ADMIN_IDS:
        is_subscribed = await check_subscription(user.id, context.bot)
        if not is_subscribed:
            await update.message.reply_text(
                "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling!</b>\n\n"
                "Obuna bo'lgandan so'ng ✅ tugmasini bosing.",
                reply_markup=subscribe_keyboard(),
                parse_mode="HTML"
            )
            return

    if user.id in ADMIN_IDS:
        text = (
            f"📊 Status: {get_status(user.id)}\n"
            f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
            f"👇 Quyidagi tugmalar orqali botdan foydalaning:\n\n"
            f"📹 <b>Anime yuborish tartibi:</b>\n"
            f"1. Botga preview video yuboring\n"
            f"2. Keyin to'liq video yoki link yuboring\n"
            f"3. Anime nomini yozing\n"
            f"4. Bot kanalga avtomatik yuboradi!"
        )
    else:
        text = (
            f"📊 Status: {get_status(user.id)}\n"
            f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
            f"👇 Quyidagi tugmalar orqali botdan foydalaning:"
        )
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode="HTML")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    d = q.data

    # Obuna tekshirish
    if d == "check_sub":
        is_subscribed = await check_subscription(user.id, context.bot)
        if is_subscribed:
            await q.edit_message_text(
                f"✅ Rahmat! Botga xush kelibsiz!\n\n"
                f"📊 Status: {get_status(user.id)}\n"
                f"🆔 Sizning ID: <code>{user.id}</code>\n\n"
                f"👇 Quyidagi tugmalar orqali botdan foydalaning:",
                reply_markup=main_menu(),
                parse_mode="HTML"
            )
        else:
            await q.answer("❌ Siz hali obuna bo'lmadingiz!", show_alert=True)
        return

    # Anime ko'rish
    if d.startswith("watch_"):
        anime_id = int(d.split("_")[1])
        is_subscribed = await check_subscription(user.id, context.bot)
        if not is_subscribed:
            await q.edit_message_text(
                "⚠️ <b>Tomosha qilish uchun kanallarga obuna bo'ling!</b>",
                reply_markup=subscribe_keyboard(),
                parse_mode="HTML"
            )
            return
        anime = anime_db.get(anime_id)
        if not anime:
            await q.answer("❌ Anime topilmadi!", show_alert=True)
            return
        await q.answer()
        if anime.get('full_video'):
            await context.bot.send_video(
                chat_id=user.id,
                video=anime['full_video'],
                caption=f"🎌 <b>{anime['name']}</b>\n\n{anime['info']}",
                parse_mode="HTML"
            )
        elif anime.get('full_link'):
            await context.bot.send_message(
                chat_id=user.id,
                text=f"🎌 <b>{anime['name']}</b>\n\n{anime['info']}\n\n🔗 {anime['full_link']}",
                parse_mode="HTML"
            )
        return

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
                [InlineKeyboardButton("📺 Kanalga o'tish", url="https://t.me/anidavi_official")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )
    elif d == "guide":
        await q.edit_message_text(
            "📚 <b>Qo'llanma</b>\n\n"
            "1️⃣ Kanalga obuna bo'ling\n   👉 @anidavi_official\n\n"
            "2️⃣ Kanalda animeni toping\n\n"
            "3️⃣ Tomosha qilish tugmasini bosing\n\n"
            "4️⃣ Botda to'liq animeni ko'ring!\n\n"
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
            f"🎌 Jami animeler: <b>{len(anime_db)}</b>\n"
            f"📺 Kanal: @anidavi_official",
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

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("👇 Menyu uchun /start bosing", reply_markup=main_menu())
        return

    video = update.message.video or update.message.document
    file_id = video.file_id
    step = context.user_data.get('step', 'preview')

    if step == 'preview':
        context.user_data['preview_video'] = file_id
        context.user_data['step'] = 'full'
        await update.message.reply_text(
            "✅ Preview video saqlandi!\n\n"
            "Endi <b>to'liq animeni</b> yuboring:\n"
            "• To'liq video yuboring, YOKI\n"
            "• Video linkini yozing (YouTube va h.k.)",
            parse_mode="HTML"
        )
    elif step == 'full':
        context.user_data['full_video'] = file_id
        context.user_data['step'] = 'info'
        await update.message.reply_text(
            "✅ To'liq video saqlandi!\n\n"
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

    if user.id in ADMIN_IDS:
        step = context.user_data.get('step', 'preview')

        # Link yuborish (to'liq anime uchun)
        if step == 'full' and (text.startswith('http') or text.startswith('https')):
            context.user_data['full_link'] = text
            context.user_data['step'] = 'info'
            await update.message.reply_text(
                "✅ Link saqlandi!\n\n"
                "Endi anime ma'lumotlarini yozing:\n\n"
                "<b>Misol:</b>\n"
                "<code>Naruto Shippuden\n"
                "Qism: 1/500\n"
                "Til: O'zbek\n"
                "Janr: Aksyon</code>",
                parse_mode="HTML"
            )
            return

        # Anime ma'lumotlari
        if step == 'info':
            lines = text.strip().split('\n')
            anime_nomi = lines[0]
            qolgan = '\n'.join(f"➤ {l}" for l in lines[1:]) if len(lines) > 1 else ""

            anime_counter[0] += 1
            anime_id = anime_counter[0]

            anime_db[anime_id] = {
                'name': anime_nomi,
                'info': qolgan,
                'preview_video': context.user_data.get('preview_video'),
                'full_video': context.user_data.get('full_video'),
                'full_link': context.user_data.get('full_link'),
            }

            caption = f"🎌 <b>{anime_nomi}</b>\n\n{qolgan}\n\n➤ Kanal: @anidavi_official"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Tomosha qilish ✨", url=f"https://t.me/{BOT_USERNAME}?start=watch_{anime_id}")]
            ])

            try:
                await context.bot.send_video(
                    chat_id="@anidavi_official",
                    video=context.user_data['preview_video'],
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await update.message.reply_text(
                    f"✅ Kaналга muvaffaqiyatli yuborildi!\n"
                    f"🎌 Anime ID: <code>{anime_id}</code>",
                    parse_mode="HTML"
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Xato: {e}")

            # Tozalash
            context.user_data.clear()
            return

        # Agar hech narsa bo'lmasa
        if step == 'preview':
            await update.message.reply_text(
                "📹 Avval <b>preview video</b> yuboring!",
                parse_mode="HTML"
            )
            return

    await update.message.reply_text("👇 Menyu uchun /start bosing", reply_markup=main_menu())

async def start_with_args(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Deep link orqali anime ko'rish"""
    user = update.effective_user
    users_db.add(user.id)

    if context.args and context.args[0].startswith("watch_"):
        anime_id = int(context.args[0].split("_")[1])

        # Obuna tekshirish
        if user.id not in ADMIN_IDS:
            is_subscribed = await check_subscription(user.id, context.bot)
            if not is_subscribed:
                await update.message.reply_text(
                    "⚠️ <b>Tomosha qilish uchun kanallarga obuna bo'ling!</b>",
                    reply_markup=subscribe_keyboard(),
                    parse_mode="HTML"
                )
                return

        anime = anime_db.get(anime_id)
        if not anime:
            await update.message.reply_text("❌ Anime topilmadi!")
            return

        if anime.get('full_video'):
            await update.message.reply_video(
                video=anime['full_video'],
                caption=f"🎌 <b>{anime['name']}</b>\n\n{anime['info']}",
                parse_mode="HTML"
            )
        elif anime.get('full_link'):
            await update.message.reply_text(
                f"🎌 <b>{anime['name']}</b>\n\n{anime['info']}\n\n🔗 {anime['full_link']}",
                parse_mode="HTML"
            )
    else:
        await start(update, context)

async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin yangi majburiy kanal qo'shadi"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text(
            "❌ Format: /addchannel @kanal_username Kanal nomi\n"
            "Misol: /addchannel @anidavi2 AniDavi 2"
        )
        return
    username = context.args[0]
    name = " ".join(context.args[1:]) if len(context.args) > 1 else username
    REQUIRED_CHANNELS.append({
        "name": name,
        "username": username,
        "link": f"https://t.me/{username.lstrip('@')}"
    })
    await update.message.reply_text(f"✅ {name} ({username}) majburiy obunaga qo'shildi!")

async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Majburiy kanallar ro'yxati"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not REQUIRED_CHANNELS:
        await update.message.reply_text("📋 Majburiy kanallar yo'q!")
        return
    text = "📋 <b>Majburiy kanallar:</b>\n\n"
    for i, ch in enumerate(REQUIRED_CHANNELS, 1):
        text += f"{i}. {ch['name']} — {ch['username']}\n"
    await update.message.reply_text(text, parse_mode="HTML")

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
    app.add_handler(CommandHandler("start", start_with_args))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(CommandHandler("listchannels", listchannels))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, video_handler))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
