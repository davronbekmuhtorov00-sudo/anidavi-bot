import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

BOT_TOKEN = "8981240580:AAGa_iJR6cq_xn5vjy5T94ScoJ60GGY0HKg"
BOT_USERNAME = "Anidavi_bot"
ADMIN_IDS = [5654433816]

# Majburiy obuna kanallari (qo'shish: /addchannel, o'chirish: /removechannel)
REQUIRED_CHANNELS = [
    {"name": "AniDavi Official", "username": "@anidavi_official", "link": "https://t.me/anidavi_official"},
]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

users_db = set()

# anime_db struktura:
# { anime_id: { 'name': str, 'info': str, 'preview': file_id, 'episodes': [file_id, ...] } }
anime_db = {}
anime_counter = [0]

# ===================== YORDAMCHI =====================

def get_status(uid):
    return "👑 Admin" if uid in ADMIN_IDS else "Oddiy"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Anime izlash", callback_data="search")],
        [InlineKeyboardButton("📚 Qo'llanma", callback_data="guide"),
         InlineKeyboardButton("💰 Reklama", callback_data="ads")],
        [InlineKeyboardButton("📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton("🤖 Bot haqida", callback_data="about")],
        [InlineKeyboardButton("💎 VIP obuna (cheklovlarsiz)", callback_data="vip")],
    ])

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]])

def subscribe_keyboard():
    buttons = [[InlineKeyboardButton(f"📢 {ch['name']}", url=ch['link'])] for ch in REQUIRED_CHANNELS]
    buttons.append([InlineKeyboardButton("✅ Obuna bo'ldim!", callback_data="check_sub")])
    return InlineKeyboardMarkup(buttons)

async def is_subscribed(uid, bot):
    for ch in REQUIRED_CHANNELS:
        try:
            m = await bot.get_chat_member(ch['username'], uid)
            if m.status in [ChatMember.LEFT, ChatMember.BANNED]:
                return False
        except:
            return False
    return True

def episodes_keyboard(anime_id):
    anime = anime_db.get(anime_id)
    if not anime:
        return back_menu()
    buttons = []
    row = []
    for i, _ in enumerate(anime['episodes'], 1):
        row.append(InlineKeyboardButton(f"{i}-qism", callback_data=f"ep_{anime_id}_{i-1}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)

# ===================== /start =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_db.add(user.id)

    # Deep link: tomosha qilish
    if context.args and context.args[0].startswith("anime_"):
        anime_id = int(context.args[0].split("_")[1])
        if user.id not in ADMIN_IDS:
            if not await is_subscribed(user.id, context.bot):
                await update.message.reply_text(
                    "⚠️ <b>Tomosha qilish uchun avval obuna bo'ling!</b>",
                    reply_markup=subscribe_keyboard(), parse_mode="HTML"
                )
                return
        anime = anime_db.get(anime_id)
        if not anime:
            await update.message.reply_text("❌ Anime topilmadi!")
            return
        await update.message.reply_text(
            f"🎌 <b>{anime['name']}</b>\n\n{anime['info']}\n\n"
            f"📺 Jami {len(anime['episodes'])} ta qism mavjud\n\n"
            f"👇 Qismni tanlang:",
            reply_markup=episodes_keyboard(anime_id),
            parse_mode="HTML"
        )
        return

    # Oddiy start
    if user.id not in ADMIN_IDS:
        if not await is_subscribed(user.id, context.bot):
            await update.message.reply_text(
                "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling!</b>",
                reply_markup=subscribe_keyboard(), parse_mode="HTML"
            )
            return

    if user.id in ADMIN_IDS:
        extra = (
            "\n\n📹 <b>Anime qo'shish:</b> /newanime\n"
            "📋 <b>Kanallar:</b> /listchannels\n"
            "➕ <b>Kanal qo'shish:</b> /addchannel @username Nomi\n"
            "➖ <b>Kanal o'chirish:</b> /removechannel @username\n"
            "📢 <b>Xabar yuborish:</b> /broadcast Xabar"
        )
    else:
        extra = ""

    await update.message.reply_text(
        f"📊 Status: {get_status(user.id)}\n"
        f"🆔 ID: <code>{user.id}</code>{extra}\n\n"
        f"👇 Quyidagi tugmalar orqali botdan foydalaning:",
        reply_markup=main_menu(), parse_mode="HTML"
    )

# ===================== ADMIN: ANIME QO'SHISH =====================

async def newanime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    context.user_data.clear()
    context.user_data['step'] = 'preview'
    await update.message.reply_text(
        "🎬 <b>Yangi anime qo'shish boshlandi!</b>\n\n"
        "<b>1-qadam:</b> Preview video yuboring (10-15 sekund)",
        parse_mode="HTML"
    )

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("👇 /start bosing", reply_markup=main_menu())
        return

    video = update.message.video or update.message.document
    file_id = video.file_id
    step = context.user_data.get('step', '')

    if step == 'preview':
        context.user_data['preview'] = file_id
        context.user_data['step'] = 'info'
        await update.message.reply_text(
            "✅ Preview video saqlandi!\n\n"
            "<b>2-qadam:</b> Anime ma'lumotlarini yozing:\n\n"
            "<code>Naruto Shippuden\n"
            "Qism: 1-500\n"
            "Til: O'zbek\n"
            "Janr: Aksyon</code>",
            parse_mode="HTML"
        )

    elif step == 'episodes':
        anime_id = context.user_data.get('current_anime_id')
        if anime_id and anime_id in anime_db:
            anime_db[anime_id]['episodes'].append(file_id)
            ep_num = len(anime_db[anime_id]['episodes'])
            await update.message.reply_text(
                f"✅ {ep_num}-qism saqlandi!\n\n"
                f"Yana qism yuborish mumkin yoki /done yozing.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Tugatish", callback_data=f"done_{anime_id}")]
                ])
            )
    else:
        await update.message.reply_text(
            "❗ Avval /newanime buyrug'ini yuboring!",
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_db.add(user.id)
    text = update.message.text or ""

    if user.id in ADMIN_IDS:
        step = context.user_data.get('step', '')

        if step == 'info':
            lines = text.strip().split('\n')
            anime_nomi = lines[0]
            info = '\n'.join(f"➤ {l}" for l in lines[1:]) if len(lines) > 1 else ""

            anime_counter[0] += 1
            anime_id = anime_counter[0]
            anime_db[anime_id] = {
                'name': anime_nomi,
                'info': info,
                'preview': context.user_data.get('preview'),
                'episodes': []
            }
            context.user_data['current_anime_id'] = anime_id
            context.user_data['step'] = 'episodes'

            await update.message.reply_text(
                f"✅ Ma'lumot saqlandi!\n\n"
                f"<b>3-qadam:</b> Endi qismlarni yuboring!\n"
                f"Birinchi qismdan boshlang — bot tartib bilan saqlaydi.\n\n"
                f"Hammasini yuborb bo'lgach /done yozing.",
                parse_mode="HTML"
            )
            return

    await update.message.reply_text("👇 /start bosing", reply_markup=main_menu())

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        return
    anime_id = context.user_data.get('current_anime_id')
    if not anime_id or anime_id not in anime_db:
        await update.message.reply_text("❌ Anime topilmadi!")
        return

    await finish_anime(update.message, context, anime_id)

async def finish_anime(message, context, anime_id):
    anime = anime_db[anime_id]
    caption = (
        f"🎌 <b>{anime['name']}</b>\n\n"
        f"{anime['info']}\n\n"
        f"📺 {len(anime['episodes'])} ta qism\n"
        f"➤ Kanal: @anidavi_official"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Tomosha qilish ✨",
            url=f"https://t.me/{BOT_USERNAME}?start=anime_{anime_id}")]
    ])
    try:
        await context.bot.send_video(
            chat_id="@anidavi_official",
            video=anime['preview'],
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await message.reply_text(
            f"✅ Kaналга yuborildi!\n"
            f"🎌 <b>{anime['name']}</b>\n"
            f"📺 {len(anime['episodes'])} ta qism",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply_text(f"❌ Xato: {e}")
    context.user_data.clear()

# ===================== BUTTON HANDLER =====================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    d = q.data

    if d == "check_sub":
        if await is_subscribed(user.id, context.bot):
            await q.edit_message_text(
                f"✅ Xush kelibsiz!\n\n"
                f"📊 Status: {get_status(user.id)}\n"
                f"🆔 ID: <code>{user.id}</code>\n\n"
                f"👇 Botdan foydalaning:",
                reply_markup=main_menu(), parse_mode="HTML"
            )
        else:
            await q.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)
        return

    # Qism ko'rish
    if d.startswith("ep_"):
        parts = d.split("_")
        anime_id = int(parts[1])
        ep_index = int(parts[2])
        if user.id not in ADMIN_IDS and not await is_subscribed(user.id, context.bot):
            await q.edit_message_text(
                "⚠️ <b>Obuna bo'ling!</b>",
                reply_markup=subscribe_keyboard(), parse_mode="HTML"
            )
            return
        anime = anime_db.get(anime_id)
        if not anime or ep_index >= len(anime['episodes']):
            await q.answer("❌ Qism topilmadi!", show_alert=True)
            return
        await context.bot.send_video(
            chat_id=user.id,
            video=anime['episodes'][ep_index],
            caption=f"🎌 <b>{anime['name']}</b> — {ep_index+1}-qism",
            parse_mode="HTML"
        )
        return

    if d.startswith("done_"):
        anime_id = int(d.split("_")[1])
        await finish_anime(q.message, context, anime_id)
        return

    if d == "menu":
        await q.edit_message_text(
            f"📊 Status: {get_status(user.id)}\n"
            f"🆔 ID: <code>{user.id}</code>\n\n"
            f"👇 Botdan foydalaning:",
            reply_markup=main_menu(), parse_mode="HTML"
        )
    elif d == "search":
        await q.edit_message_text(
            "🔍 <b>Anime izlash</b>\n\nKanalimizga o'ting:\n👉 @anidavi_official",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Kanalga o'tish", url="https://t.me/anidavi_official")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]), parse_mode="HTML"
        )
    elif d == "guide":
        await q.edit_message_text(
            "📚 <b>Qo'llanma</b>\n\n"
            "1️⃣ Kanalga obuna bo'ling 👉 @anidavi_official\n\n"
            "2️⃣ Kanalda animeni toping\n\n"
            "3️⃣ ✨ Tomosha qilish tugmasini bosing\n\n"
            "4️⃣ Botda qismlarni tanlang va tomosha qiling!\n\n"
            "💎 VIP obuna bilan cheklovsiz!",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "ads":
        await q.edit_message_text(
            "💰 <b>Reklama va Homiylik</b>\n\n"
            "📢 Reklama: muzokarali\n📩 Admin: @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Admin", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]), parse_mode="HTML"
        )
    elif d == "stats":
        await q.edit_message_text(
            f"📊 <b>Statistika</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{len(users_db)}</b>\n"
            f"🎌 Animeler: <b>{len(anime_db)}</b>\n"
            f"📺 Kanal: @anidavi_official",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "about":
        await q.edit_message_text(
            "🤖 <b>AniDavi Bot</b>\n\n"
            "🎌 O'zbek tilida anime ko'rish uchun eng qulay bot!\n\n"
            "✨ Qismlar bo'yicha tomosha qilish\n"
            "✨ Har kuni yangi animeler\n"
            "✨ VIP obuna\n\n"
            "📺 @anidavi_official",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "vip":
        await q.edit_message_text(
            "💎 <b>VIP Obuna</b>\n\n"
            "✅ Cheklovsiz anime\n✅ HD sifat\n✅ Reklama yo'q\n\n"
            "💰 1 oy: 15,000 so'm\n💰 3 oy: 35,000 so'm\n💰 1 yil: 100,000 so'm\n\n"
            "📩 @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 VIP olish", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]), parse_mode="HTML"
        )

# ===================== ADMIN KOMANDALAR =====================

async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Format: /addchannel @username Kanal nomi")
        return
    username = context.args[0]
    name = " ".join(context.args[1:])
    REQUIRED_CHANNELS.append({"name": name, "username": username, "link": f"https://t.me/{username.lstrip('@')}"})
    await update.message.reply_text(f"✅ {name} ({username}) qo'shildi!")

async def removechannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    if not context.args:
        await update.message.reply_text("Format: /removechannel @username")
        return
    username = context.args[0]
    before = len(REQUIRED_CHANNELS)
    REQUIRED_CHANNELS[:] = [ch for ch in REQUIRED_CHANNELS if ch['username'] != username]
    if len(REQUIRED_CHANNELS) < before:
        await update.message.reply_text(f"✅ {username} o'chirildi!")
    else:
        await update.message.reply_text(f"❌ {username} topilmadi!")

async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ===================== MAIN =====================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newanime", newanime))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(CommandHandler("removechannel", removechannel))
    app.add_handler(CommandHandler("listchannels", listchannels))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, video_handler))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
