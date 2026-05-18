import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

BOT_TOKEN = "8981240580:AAGa_iJR6cq_xn5vjy5T94ScoJ60GGY0HKg"
BOT_USERNAME = "Anidavi_bot"
ADMIN_IDS = [5654433816]
VIP_IDS = []

REQUIRED_CHANNELS = [
    {"name": "AniDavi Official", "username": "@anidavi_official", "link": "https://t.me/anidavi_official"},
]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

users_db = {}   # {user_id: {'name': str, 'ref': int or None}}
anime_db = {}
anime_counter = [0]

def get_status(uid):
    if uid in ADMIN_IDS: return "👑 Admin"
    if uid in VIP_IDS: return "💎 VIP"
    return "Oddiy"

def is_premium(uid):
    return uid in ADMIN_IDS or uid in VIP_IDS

def main_menu(uid):
    buttons = [
        [InlineKeyboardButton("🔍 Anime izlash", callback_data="search")],
        [InlineKeyboardButton("📚 Qo'llanma", callback_data="guide"),
         InlineKeyboardButton("💰 Reklama", callback_data="ads")],
        [InlineKeyboardButton("🤖 Bot haqida", callback_data="about"),
         InlineKeyboardButton("👥 Referal", callback_data="referal")],
        [InlineKeyboardButton("💎 VIP obuna", callback_data="vip")],
    ]
    if uid in ADMIN_IDS:
        buttons.append([InlineKeyboardButton("📊 Statistika", callback_data="stats")])
    return InlineKeyboardMarkup(buttons)

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

async def check_access(uid, bot):
    if is_premium(uid):
        return True
    return await is_subscribed(uid, bot)

def episodes_keyboard(anime_id):
    anime = anime_db.get(anime_id)
    if not anime: return back_menu()
    buttons, row = [], []
    for i in range(len(anime['episodes'])):
        row.append(InlineKeyboardButton(f"{i+1}-qism", callback_data=f"ep_{anime_id}_{i}"))
        if len(row) == 3:
            buttons.append(row); row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)

def search_results_keyboard(results):
    buttons = [[InlineKeyboardButton(f"🎌 {a['name']}", callback_data=f"anime_info_{aid}")] for aid, a in results]
    buttons.append([InlineKeyboardButton("🔙 Orqaga", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)

# ===================== START =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref_id = None

    # Referal tizimi
    if context.args and context.args[0].startswith("ref_"):
        try:
            ref_id = int(context.args[0].split("_")[1])
        except: pass

    if user.id not in users_db:
        users_db[user.id] = {'name': user.full_name, 'ref': ref_id, 'refs_count': 0}
        if ref_id and ref_id in users_db and ref_id != user.id:
            users_db[ref_id]['refs_count'] = users_db[ref_id].get('refs_count', 0) + 1
            try:
                await context.bot.send_message(
                    ref_id,
                    f"🎉 Siz taklif qilgan <b>{user.full_name}</b> botga qo'shildi!\n"
                    f"Sizning referallaringiz: <b>{users_db[ref_id]['refs_count']}</b>",
                    parse_mode="HTML"
                )
            except: pass
    
    # Deep link: anime ochish
    if context.args and context.args[0].startswith("anime_"):
        anime_id = int(context.args[0].split("_")[1])
        if not await check_access(user.id, context.bot):
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
            f"📺 Jami {len(anime['episodes'])} ta qism\n\n👇 Qismni tanlang:",
            reply_markup=episodes_keyboard(anime_id), parse_mode="HTML"
        )
        return

    if not await check_access(user.id, context.bot):
        await update.message.reply_text(
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling!</b>",
            reply_markup=subscribe_keyboard(), parse_mode="HTML"
        )
        return

    extra = ""
    if user.id in ADMIN_IDS:
        extra = (
            "\n\n<b>🛠 Admin buyruqlar:</b>\n"
            "/newanime — Yangi anime\n"
            "/deleteanime nom — Anime o'chirish\n"
            "/editanime nom — Anime tahrirlash\n"
            "/addadmin @user yoki ID\n"
            "/removeadmin @user yoki ID\n"
            "/addvip @user yoki ID\n"
            "/removevip @user yoki ID\n"
            "/listvip — VIP lar\n"
            "/addchannel @username Nomi\n"
            "/removechannel @username\n"
            "/listchannels\n"
            "/broadcast Xabar"
        )

    await update.message.reply_text(
        f"📊 Status: {get_status(user.id)}\n"
        f"🆔 ID: <code>{user.id}</code>{extra}\n\n"
        f"👇 Botdan foydalaning:",
        reply_markup=main_menu(user.id), parse_mode="HTML"
    )

# ===================== ANIME QO'SHISH =====================

async def newanime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    context.user_data.clear()
    context.user_data['step'] = 'preview'
    await update.message.reply_text(
        "🎬 <b>Yangi anime!</b>\n\n<b>1-qadam:</b> Preview rasm yoki video yuboring",
        parse_mode="HTML"
    )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        if not await check_access(user.id, context.bot):
            await update.message.reply_text("⚠️ <b>Obuna bo'ling!</b>", reply_markup=subscribe_keyboard(), parse_mode="HTML")
            return
        results = list(anime_db.items())
        if results:
            await update.message.reply_text("🔍 <b>Qaysi animeni ko'rmoqchisiz?</b>", reply_markup=search_results_keyboard(results), parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Hozircha animeler yo'q!")
        return

    step = context.user_data.get('step', '')
    file_id = update.message.photo[-1].file_id

    if step == 'preview':
        context.user_data['preview'] = file_id
        context.user_data['preview_type'] = 'photo'
        context.user_data['step'] = 'info'
        await update.message.reply_text(
            "✅ Preview saqlandi!\n\n<b>2-qadam:</b> Ma'lumot yozing:\n\n"
            "<code>Naruto Shippuden\nQism: 1-500\nTil: O'zbek\nJanr: Aksyon</code>",
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text("❗ Avval /newanime yuboring!")

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        if not await check_access(user.id, context.bot):
            await update.message.reply_text("⚠️ <b>Obuna bo'ling!</b>", reply_markup=subscribe_keyboard(), parse_mode="HTML")
            return
        results = list(anime_db.items())
        if results:
            await update.message.reply_text("🔍 <b>Qaysi animeni ko'rmoqchisiz?</b>", reply_markup=search_results_keyboard(results), parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Hozircha animeler yo'q!")
        return

    video = update.message.video or update.message.document
    file_id = video.file_id
    step = context.user_data.get('step', '')

    if step == 'preview':
        context.user_data['preview'] = file_id
        context.user_data['preview_type'] = 'video'
        context.user_data['step'] = 'info'
        await update.message.reply_text(
            "✅ Preview saqlandi!\n\n<b>2-qadam:</b> Ma'lumot yozing:\n\n"
            "<code>Naruto Shippuden\nQism: 1-500\nTil: O'zbek\nJanr: Aksyon</code>",
            parse_mode="HTML"
        )
    elif step == 'episodes':
        anime_id = context.user_data.get('current_anime_id')
        if anime_id and anime_id in anime_db:
            anime_db[anime_id]['episodes'].append(file_id)
            ep_num = len(anime_db[anime_id]['episodes'])
            await update.message.reply_text(f"✅ {ep_num}-qism saqlandi! Yana yuboring yoki /done yozing.")
    elif step == 'edit_preview':
        anime_id = context.user_data.get('edit_id')
        if anime_id in anime_db:
            anime_db[anime_id]['preview'] = file_id
            anime_db[anime_id]['preview_type'] = 'video'
            context.user_data.clear()
            await update.message.reply_text("✅ Preview yangilandi!")
    else:
        await update.message.reply_text("❗ Avval /newanime yuboring!")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in users_db:
        users_db[user.id] = {'name': user.full_name, 'ref': None, 'refs_count': 0}
    text = update.message.text or ""

    # Admin: info yozish
    if user.id in ADMIN_IDS and context.user_data.get('step') == 'info':
        lines = text.strip().split('\n')
        anime_nomi = lines[0]
        info = '\n'.join(f"➤ {l}" for l in lines[1:]) if len(lines) > 1 else ""
        anime_counter[0] += 1
        anime_id = anime_counter[0]
        anime_db[anime_id] = {
            'name': anime_nomi, 'info': info,
            'preview': context.user_data.get('preview'),
            'preview_type': context.user_data.get('preview_type', 'video'),
            'episodes': []
        }
        context.user_data['current_anime_id'] = anime_id
        context.user_data['step'] = 'episodes'
        await update.message.reply_text(
            f"✅ <b>{anime_nomi}</b> saqlandi!\n\n<b>3-qadam:</b> Qismlarni yuboring\nTugagach /done yozing.",
            parse_mode="HTML"
        )
        return

    # Admin: tahrirlash
    if user.id in ADMIN_IDS and context.user_data.get('step') == 'edit_info':
        anime_id = context.user_data.get('edit_id')
        if anime_id in anime_db:
            lines = text.strip().split('\n')
            anime_db[anime_id]['name'] = lines[0]
            anime_db[anime_id]['info'] = '\n'.join(f"➤ {l}" for l in lines[1:]) if len(lines) > 1 else ""
            context.user_data.clear()
            await update.message.reply_text(f"✅ <b>{anime_db[anime_id]['name']}</b> yangilandi!", parse_mode="HTML")
        return

    if not await check_access(user.id, context.bot):
        await update.message.reply_text("⚠️ <b>Obuna bo'ling!</b>", reply_markup=subscribe_keyboard(), parse_mode="HTML")
        return

    # Anime qidirish
    if text and len(text) >= 2:
        query = text.lower().strip()
        results = [(aid, a) for aid, a in anime_db.items() if query in a['name'].lower()]
        if results:
            await update.message.reply_text(
                f"🔍 <b>'{text}' bo'yicha natijalar:</b>",
                reply_markup=search_results_keyboard(results), parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"❌ <b>'{text}'</b> topilmadi!\n\n@anidavi_official ga o'ting",
                parse_mode="HTML"
            )
        return

    await update.message.reply_text("👇 /start bosing", reply_markup=main_menu(user.id))

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    anime_id = context.user_data.get('current_anime_id')
    if not anime_id or anime_id not in anime_db:
        await update.message.reply_text("❌ Anime topilmadi!")
        return
    await finish_anime(update.message, context, anime_id)

async def finish_anime(message, context, anime_id):
    anime = anime_db[anime_id]
    caption = (
        f"🎌 <b>{anime['name']}</b>\n\n{anime['info']}\n\n"
        f"📺 {len(anime['episodes'])} ta qism\n➤ @anidavi_official"
    )
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✨ Tomosha qilish ✨", url=f"https://t.me/{BOT_USERNAME}?start=anime_{anime_id}")
    ]])
    try:
        if anime['preview_type'] == 'photo':
            await context.bot.send_photo(chat_id="@anidavi_official", photo=anime['preview'], caption=caption, reply_markup=keyboard, parse_mode="HTML")
        else:
            await context.bot.send_video(chat_id="@anidavi_official", video=anime['preview'], caption=caption, reply_markup=keyboard, parse_mode="HTML")

        # Barcha userlarga xabar
        notified = 0
        for uid in users_db:
            try:
                await context.bot.send_message(
                    uid,
                    f"🆕 <b>Yangi anime qo'shildi!</b>\n\n🎌 <b>{anime['name']}</b>\n{anime['info']}\n\n📺 {len(anime['episodes'])} ta qism",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("✨ Tomosha qilish", url=f"https://t.me/{BOT_USERNAME}?start=anime_{anime_id}")
                    ]]),
                    parse_mode="HTML"
                )
                notified += 1
            except: pass

        await message.reply_text(
            f"✅ Kanalga yuborildi!\n🎌 <b>{anime['name']}</b>\n📢 {notified} ta foydalanuvchiga xabar yuborildi!",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply_text(f"❌ Xato: {e}")
    context.user_data.clear()

# ===================== DELETE & EDIT =====================

async def deleteanime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        if anime_db:
            text = "🗑 <b>Anime o'chirish:</b>\n\n" + "\n".join([f"• <code>{aid}</code> — {a['name']}" for aid, a in anime_db.items()])
            text += "\n\nFormat: /deleteanime nom yoki ID"
        else:
            text = "❌ Animeler yo'q!"
        await update.message.reply_text(text, parse_mode="HTML")
        return

    query = " ".join(context.args).lower()
    found = None
    for aid, a in anime_db.items():
        if str(aid) == query or a['name'].lower() == query:
            found = aid
            break
    if found:
        name = anime_db[found]['name']
        del anime_db[found]
        await update.message.reply_text(f"✅ <b>{name}</b> o'chirildi!", parse_mode="HTML")
    else:
        await update.message.reply_text(f"❌ '{' '.join(context.args)}' topilmadi!")

async def editanime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        if anime_db:
            text = "✏️ <b>Anime tahrirlash:</b>\n\n" + "\n".join([f"• <code>{aid}</code> — {a['name']}" for aid, a in anime_db.items()])
            text += "\n\nFormat: /editanime nom yoki ID"
        else:
            text = "❌ Animeler yo'q!"
        await update.message.reply_text(text, parse_mode="HTML")
        return

    query = " ".join(context.args).lower()
    found = None
    for aid, a in anime_db.items():
        if str(aid) == query or a['name'].lower() == query:
            found = aid
            break
    if not found:
        await update.message.reply_text(f"❌ '{' '.join(context.args)}' topilmadi!")
        return

    context.user_data['edit_id'] = found
    anime = anime_db[found]
    await update.message.reply_text(
        f"✏️ <b>{anime['name']}</b> tahrirlanmoqda\n\n"
        f"Nima o'zgartirasiz?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Nom va ma'lumot", callback_data=f"edit_info_{found}")],
            [InlineKeyboardButton("🖼 Preview rasm/video", callback_data=f"edit_preview_{found}")],
            [InlineKeyboardButton("📺 Qism qo'shish", callback_data=f"edit_episodes_{found}")],
            [InlineKeyboardButton("❌ Bekor", callback_data="menu")]
        ]),
        parse_mode="HTML"
    )

# ===================== BUTTON =====================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    d = q.data

    if d == "check_sub":
        if await check_access(user.id, context.bot):
            await q.edit_message_text(
                f"✅ Xush kelibsiz!\n📊 Status: {get_status(user.id)}\n🆔 ID: <code>{user.id}</code>\n\n👇 Botdan foydalaning:",
                reply_markup=main_menu(user.id), parse_mode="HTML"
            )
        else:
            await q.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)
        return

    if d.startswith("edit_info_"):
        anime_id = int(d.split("_")[2])
        context.user_data['edit_id'] = anime_id
        context.user_data['step'] = 'edit_info'
        await q.edit_message_text(
            f"✏️ Yangi ma'lumot yozing:\n\n"
            "<code>Anime nomi\nQism: 1-12\nTil: O'zbek\nJanr: Drama</code>",
            parse_mode="HTML"
        )
        return

    if d.startswith("edit_preview_"):
        anime_id = int(d.split("_")[2])
        context.user_data['edit_id'] = anime_id
        context.user_data['step'] = 'edit_preview'
        await q.edit_message_text("🖼 Yangi preview rasm yoki video yuboring:")
        return

    if d.startswith("edit_episodes_"):
        anime_id = int(d.split("_")[2])
        context.user_data['edit_id'] = anime_id
        context.user_data['current_anime_id'] = anime_id
        context.user_data['step'] = 'episodes'
        await q.edit_message_text("📺 Yangi qismlarni yuboring, tugagach /done yozing:")
        return

    if d.startswith("anime_info_"):
        anime_id = int(d.split("_")[2])
        if not await check_access(user.id, context.bot):
            await q.edit_message_text("⚠️ <b>Obuna bo'ling!</b>", reply_markup=subscribe_keyboard(), parse_mode="HTML")
            return
        anime = anime_db.get(anime_id)
        if not anime:
            await q.answer("❌ Topilmadi!", show_alert=True)
            return
        await q.edit_message_text(
            f"🎌 <b>{anime['name']}</b>\n\n{anime['info']}\n\n📺 {len(anime['episodes'])} ta qism\n\n👇 Qismni tanlang:",
            reply_markup=episodes_keyboard(anime_id), parse_mode="HTML"
        )
        return

    if d.startswith("ep_"):
        parts = d.split("_")
        anime_id, ep_index = int(parts[1]), int(parts[2])
        if not await check_access(user.id, context.bot):
            await q.edit_message_text("⚠️ <b>Obuna bo'ling!</b>", reply_markup=subscribe_keyboard(), parse_mode="HTML")
            return
        anime = anime_db.get(anime_id)
        if not anime or ep_index >= len(anime['episodes']):
            await q.answer("❌ Qism topilmadi!", show_alert=True)
            return
        await context.bot.send_video(
            chat_id=user.id, video=anime['episodes'][ep_index],
            caption=f"🎌 <b>{anime['name']}</b> — {ep_index+1}-qism", parse_mode="HTML"
        )
        return

    if d == "referal":
        ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user.id}"
        count = users_db.get(user.id, {}).get('refs_count', 0)
        await q.edit_message_text(
            f"👥 <b>Referal tizimi</b>\n\n"
            f"Do'stlaringizni taklif qiling!\n\n"
            f"🔗 Sizning havolangiz:\n<code>{ref_link}</code>\n\n"
            f"👥 Siz taklif qilganlar: <b>{count}</b> ta",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Ulashish", switch_inline_query=f"AniDavi botiga qo'shiling: {ref_link}")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]),
            parse_mode="HTML"
        )
        return

    if d == "menu":
        await q.edit_message_text(
            f"📊 Status: {get_status(user.id)}\n🆔 ID: <code>{user.id}</code>\n\n👇 Botdan foydalaning:",
            reply_markup=main_menu(user.id), parse_mode="HTML"
        )
    elif d == "search":
        await q.edit_message_text(
            "🔍 <b>Anime izlash</b>\n\n"
            "• Anime nomini yozing\n"
            "• Rasm yoki video yuboring\n\n"
            "Kanaldan ham qidirish mumkin:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Kanalga o'tish", url="https://t.me/anidavi_official")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]), parse_mode="HTML"
        )
    elif d == "guide":
        await q.edit_message_text(
            "📚 <b>Qo'llanma</b>\n\n"
            "1️⃣ Kanalga obuna bo'ling 👉 @anidavi_official\n\n"
            "2️⃣ Anime nom yozing yoki rasm/video yuboring\n\n"
            "3️⃣ ✨ Tomosha qilish tugmasini bosing\n\n"
            "4️⃣ Qismni tanlang va tomosha qiling!\n\n"
            "💎 VIP bilan obunasiz, cheklovsiz tomosha!",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "ads":
        await q.edit_message_text(
            "💰 <b>Reklama va Homiylik</b>\n\n📢 Narxlar: muzokarali\n📩 @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Admin", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]), parse_mode="HTML"
        )
    elif d == "stats":
        if user.id not in ADMIN_IDS:
            await q.answer("❌ Ruxsat yo'q!", show_alert=True)
            return
        await q.edit_message_text(
            f"📊 <b>Statistika</b>\n\n"
            f"👥 Foydalanuvchilar: <b>{len(users_db)}</b>\n"
            f"🎌 Animeler: <b>{len(anime_db)}</b>\n"
            f"💎 VIP lar: <b>{len(VIP_IDS)}</b>\n"
            f"👑 Adminlar: <b>{len(ADMIN_IDS)}</b>\n"
            f"📢 Majburiy kanallar: <b>{len(REQUIRED_CHANNELS)}</b>",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "about":
        await q.edit_message_text(
            "🤖 <b>AniDavi Bot</b>\n\n"
            "🎌 O'zbek tilida anime ko'rish uchun eng qulay bot!\n\n"
            "✨ Nom yoki rasm/video bilan qidirish\n"
            "✨ Qismlar bo'yicha tomosha\n"
            "✨ Yangi anime xabarlari\n"
            "✨ Referal tizimi\n"
            "✨ VIP — obunasiz, cheklovsiz!\n\n"
            "📺 @anidavi_official",
            reply_markup=back_menu(), parse_mode="HTML"
        )
    elif d == "vip":
        await q.edit_message_text(
            "💎 <b>VIP Obuna</b>\n\n"
            "✅ Majburiy obunasiz kirish\n"
            "✅ Cheklovsiz anime\n"
            "✅ HD sifat\n"
            "✅ Reklama yo'q\n\n"
            "💰 1 oy: 15,000 so'm\n"
            "💰 3 oy: 35,000 so'm\n"
            "💰 1 yil: 100,000 so'm\n\n"
            "📩 To'lov uchun: @anidavi_admin",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 VIP olish", url="https://t.me/anidavi_admin")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data="menu")]
            ]), parse_mode="HTML"
        )

# ===================== ADMIN KOMANDALAR =====================

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("Format:\n/addadmin @username\n/addadmin 123456789")
        return
    try:
        arg = context.args[0]
        new_id = (await context.bot.get_chat(arg)).id if arg.startswith("@") else int(arg)
        if new_id in ADMIN_IDS:
            await update.message.reply_text("⚠️ Allaqachon admin!")
            return
        ADMIN_IDS.append(new_id)
        await update.message.reply_text(f"✅ {arg} admin qilindi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("Format:\n/removeadmin @username\n/removeadmin 123456789")
        return
    try:
        arg = context.args[0]
        rem_id = (await context.bot.get_chat(arg)).id if arg.startswith("@") else int(arg)
        if rem_id == 5654433816:
            await update.message.reply_text("❌ Asosiy adminni o'chirib bo'lmaydi!")
            return
        if rem_id in ADMIN_IDS:
            ADMIN_IDS.remove(rem_id)
            await update.message.reply_text("✅ Admin o'chirildi!")
        else:
            await update.message.reply_text("❌ Admin emas!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def addvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("Format:\n/addvip @username\n/addvip 123456789")
        return
    try:
        arg = context.args[0]
        new_id = (await context.bot.get_chat(arg)).id if arg.startswith("@") else int(arg)
        if new_id in VIP_IDS:
            await update.message.reply_text("⚠️ Allaqachon VIP!")
            return
        VIP_IDS.append(new_id)
        try:
            await context.bot.send_message(new_id, "🎉 Tabriklaymiz! Sizga <b>💎 VIP obuna</b> berildi!\n\nEndi barcha animeni obunasiz ko'rishingiz mumkin!", parse_mode="HTML")
        except: pass
        await update.message.reply_text(f"✅ {arg} VIP qilindi!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def removevip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("Format:\n/removevip @username\n/removevip 123456789")
        return
    try:
        arg = context.args[0]
        rem_id = (await context.bot.get_chat(arg)).id if arg.startswith("@") else int(arg)
        if rem_id in VIP_IDS:
            VIP_IDS.remove(rem_id)
            await update.message.reply_text("✅ VIP o'chirildi!")
        else:
            await update.message.reply_text("❌ Bu foydalanuvchi VIP emas!")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")

async def listvip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not VIP_IDS:
        await update.message.reply_text("💎 VIP foydalanuvchilar yo'q!")
        return
    text = "💎 <b>VIP foydalanuvchilar:</b>\n\n"
    for i, uid in enumerate(VIP_IDS, 1):
        name = users_db.get(uid, {}).get('name', str(uid))
        text += f"{i}. {name} — <code>{uid}</code>\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if len(context.args) < 2:
        await update.message.reply_text("Format: /addchannel @username Kanal nomi")
        return
    username, name = context.args[0], " ".join(context.args[1:])
    REQUIRED_CHANNELS.append({"name": name, "username": username, "link": f"https://t.me/{username.lstrip('@')}"})
    await update.message.reply_text(f"✅ {name} ({username}) qo'shildi!")

async def removechannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("Format: /removechannel @username")
        return
    username = context.args[0]
    before = len(REQUIRED_CHANNELS)
    REQUIRED_CHANNELS[:] = [ch for ch in REQUIRED_CHANNELS if ch['username'] != username]
    await update.message.reply_text("✅ O'chirildi!" if len(REQUIRED_CHANNELS) < before else "❌ Topilmadi!")

async def listchannels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not REQUIRED_CHANNELS:
        await update.message.reply_text("📋 Majburiy kanallar yo'q!")
        return
    text = "📋 <b>Majburiy kanallar:</b>\n\n"
    for i, ch in enumerate(REQUIRED_CHANNELS, 1):
        text += f"{i}. {ch['name']} — {ch['username']}\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("❌ /broadcast Xabar matni")
        return
    msg = " ".join(context.args)
    sent = 0
    for uid in users_db:
        try:
            await context.bot.send_message(uid, f"📢 {msg}")
            sent += 1
        except: pass
    await update.message.reply_text(f"✅ {sent} ta foydalanuvchiga yuborildi!")

# ===================== MAIN =====================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newanime", newanime))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("deleteanime", deleteanime))
    app.add_handler(CommandHandler("editanime", editanime))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("addvip", addvip))
    app.add_handler(CommandHandler("removevip", removevip))
    app.add_handler(CommandHandler("listvip", listvip))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(CommandHandler("removechannel", removechannel))
    app.add_handler(CommandHandler("listchannels", listchannels))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, video_handler))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
