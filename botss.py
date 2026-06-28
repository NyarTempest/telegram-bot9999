import asyncio
import json
import os

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
) 
    
from aiogram.enums import ChatMemberStatus
from aiohttp import web

import logging
logging.basicConfig(level=logging.INFO)
TOKEN=os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()



# ================= БАЗА =================

DB_FILE = "database.json"


def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass

    return {
        "ranks": {},
        "warns": {},
        "gifts": {}
    }


database = load_db()


def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(
            database,
            f,
            ensure_ascii=False,
            indent=4
        )


ranks = database["ranks"]
warns = database["warns"]
gifts = database["gifts"]

requests = {}

AVAILABLE_RANKS = [
    "Players",
    "ELIT",
    "DUKE",
    "GAY++",
    "HELPER",
    "MODER",
    "ADMIN"
]

mute_counter = 0
ban_counter = 0
kick_counter = 0


async def is_admin(chat_id: int, user_id: int):
    member = await bot.get_chat_member(
        chat_id,
        user_id
    )

    return member.status in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    )


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "╔════════════════╗\n"
        " ✦ Romantic Bot ✦\n"
        "╚════════════════╝\n\n"

        "❤️ Романтика:\n"
        "💋 /kiss\n"
        "🤗 /hug\n"
        "🥰 /cuddle\n"
        "🌹 /rose\n"
        "👋 /slap\n"
        "😈 /bite\n\n"

        "🛡 Модерация:\n"
        "🚫 /ban\n"
        "👢 /kick\n"
        "🔇 /mute\n"
        "🔊 /unmute\n"
        "⚠️ /warn\n\n"

        "🏆 Ранги:\n"
        "/rank\n"
        "/unrank\n\n"

        "📋 Профиль:\n"
        "/info"
    )
   
    
@dp.message(Command("rank"))
async def rank_cmd(message: Message,
                   command: CommandObject):

    if not await is_admin(
            message.chat.id,
            message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer(
            "❌ Ответьте на сообщение."
        )
        return

    if not command.args:
        await message.answer(
            "/rank ADMIN"
        )
        return

    rank = command.args.upper()

    if rank not in [r.upper()
                    for r in AVAILABLE_RANKS]:
        await message.answer(
            "❌ Такого ранга нет."
        )
        return

    user = message.reply_to_message.from_user

    ranks[str(user.id)] = rank
    save_db()

    try:
        if rank in ["MODER", "ADMIN"]:

            await bot.promote_chat_member(
                chat_id=message.chat.id,
                user_id=user.id,

                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,

                can_promote_members=(
                        rank == "ADMIN"
                )
            )
    except:
        pass

    await message.answer(
        f"🏆 {user.full_name}\n"
        f"получил ранг\n\n"
        f"『 {rank} 』"
    )


@dp.message(Command("unrank"))
async def unrank_cmd(message: Message):

    if not await is_admin(
            message.chat.id,
            message.from_user.id):
        return

    if not message.reply_to_message:
        return

    user = message.reply_to_message.from_user

    ranks[str(user.id)] = "Players"
    save_db()

    try:
        await bot.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,

            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_manage_chat=False,
            can_manage_video_chats=False,
            can_promote_members=False
        )
    except:
        pass

    await message.answer(
        f"❌ У {user.full_name} снят ранг."
    )
@dp.message(Command("info"))
async def info_cmd(message: Message):

    user = (
        message.reply_to_message.from_user
        if message.reply_to_message
        else message.from_user
    )

    member = await bot.get_chat_member(
        message.chat.id,
        user.id
    )

    rank = ranks.get(
        str(user.id),
        "Players"
    )

    warns_count = warns.get(
        str(user.id),
        0
    )

    gift_count = gifts.get(
        str(user.id),
        0
    )

    text = (
    "╔════════════════════╗\n"
    "      ✦ 𝑷𝑹𝑶𝑭𝑰𝑳𝑬 ✦\n"
    "╚════════════════════╝\n\n"

    "━━━━━━━━━━━━━━━━━━\n"
    f"👤 𝑵𝒂𝒎𝒆:\n{user.full_name}\n\n"

    f"🆔 𝑰𝑫:\n<code>{user.id}</code>\n\n"

    f"🏷 𝑼𝒔𝒆𝒓:\n"
    f"@{user.username if user.username else 'нет'}\n"
    "━━━━━━━━━━━━━━━━━━\n\n"

    f"🏆 𝑹𝒂𝒏𝒌: {rank}\n"
    f"⭐ Status: {member.status}\n"
    f"⚠️ 𝑾𝒂𝒓𝒏𝒔: {warns_count}/3\n"
    f"🎁 𝑮𝒊𝒇𝒕𝒔: {gift_count}\n\n"

    "━━━━━━━━━━━━━━━━━━\n"
    f"💬 Chat:\n{message.chat.title}\n"
    "━━━━━━━━━━━━━━━━━━"
)

    photos = await bot.get_user_profile_photos(
        user.id,
        limit=1
    )

    if photos.total_count > 0:
        await message.answer_photo(
            photos.photos[0][-1].file_id,
            caption=text,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text,
            parse_mode="HTML"
        )
    # ================= МОДЕРАЦИЯ =================

@dp.message(Command("ban"))
async def ban_cmd(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer(
            "╔════════════════╗\n"
            "      🚫 BAN 🚫\n"
            "╚════════════════╝\n\n"
            "❌ Ответьте на сообщение пользователя."
        )
        return

    user = message.reply_to_message.from_user

    await bot.ban_chat_member(
        message.chat.id,
        user.id
    )

    await message.answer(
    "╔════════════════════╗\n"
    "      ✦ 𝑩𝑨𝑵 𝑺𝒀𝑺𝑻𝑬𝑴 ✦\n"
    "╚════════════════════╝\n\n"

    "━━━━━━━━━━━━━━━━━━\n"
    f"👤 𝑼𝒔𝒆𝒓:\n"
    f"『 {user.full_name} 』\n\n"

    f"🆔 𝑰𝑫:\n"
    f"『 {user.id} 』\n\n"

    f"⏳ 𝑻𝒊𝒎𝒆:\n"
        f"👮 𝑴𝒐𝒅𝒆𝒓𝒂𝒕𝒐𝒓:\n"
    f"『 {message.from_user.full_name} 』\n"
    "━━━━━━━━━━━━━━━━━━\n\n"

    "⛔ 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
    "『 𝑩𝑨𝑵𝑵𝑬𝑫 』"
)


@dp.message(Command("unban"))
async def unban_cmd(message: Message, command: CommandObject):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not command.args:
        await message.answer(
            "╔════════════════╗\n"
            "     🔓 UNBAN 🔓\n"
            "╚════════════════╝\n\n"
            "Использование:\n/unban ID"
        )
        return

    try:
        user_id = int(command.args)

        await bot.unban_chat_member(
            message.chat.id,
            user_id
        )

        await message.answer(
            "╔════════════════╗\n"
            "     🔓 UNBAN 🔓\n"
            "╚════════════════╝\n\n"
            f"✅ Пользователь <code>{user_id}</code>\n"
            "разбанен."
        , parse_mode="HTML")

    except:
        await message.answer("❌ Неверный ID.")


@dp.message(Command("kick"))
async def kick_cmd(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        return

    user = message.reply_to_message.from_user

    await bot.ban_chat_member(
        message.chat.id,
        user.id
    )

    await bot.unban_chat_member(
        message.chat.id,
        user.id
    )

    await message.answer(
        "╔════════════════╗\n"
        "      👢 KICK 👢\n"
        "╚════════════════╝\n\n"
        f"❌ {user.full_name}\n"
        "исключён из чата."
    )


@dp.message(Command("mute"))
async def mute_cmd(
        message: Message,
        command: CommandObject):

    if not await is_admin(
            message.chat.id,
            message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение.")
        return

    user = message.reply_to_message.from_user

    arg = command.args if command.args else "30"
    minutes = int(arg)
    until = datetime.now() + timedelta(minutes=minutes)

    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user.id,
        permissions=ChatPermissions(
            can_send_messages=False
        ),
        until_date=until
    )

    await message.answer(
    "╔════════════════════╗\n"
    "     ✦ 𝑴𝑼𝑻𝑬 𝑺𝒀𝑺𝑻𝑬𝑴 ✦\n"
    "╚════════════════════╝\n\n"

    "━━━━━━━━━━━━━━━━━━\n"
    f"👤 𝑼𝒔𝒆𝒓:\n"
    f"『 {user.full_name} 』\n\n"

    f"⏳ 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:\n"
        f"👮 𝑩𝒚:\n"
    f"『 {message.from_user.full_name} 』\n"
    "━━━━━━━━━━━━━━━━━━\n\n"

    "🔇 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
    "『 𝑴𝑼𝑻𝑬𝑫 』"
)


@dp.message(Command("unmute"))
async def unmute_cmd(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение.")
        return

    user = message.reply_to_message.from_user

    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    await message.answer(
        "╔════════════════╗\n"
        "    🔊 UNMUTE 🔊\n"
        "╚════════════════╝\n\n"
        f"✅ {user.full_name}\n"
        "снова может писать."
    )


@dp.message(Command("warn"))
async def warn_cmd(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer("❌ Ответьте на сообщение.")
        return

    user = message.reply_to_message.from_user
    uid = str(user.id)

    warns[uid] = warns.get(uid, 0) + 1
    save_db()

    count = warns[uid]

    if count >= 3:

        await bot.ban_chat_member(
            message.chat.id,
            user.id
        )

        warns[uid] = 0
        save_db()

        await message.answer(
            "╔════════════════╗\n"
            "      ⚠️ WARN ⚠️\n"
            "╚════════════════╝\n\n"
            f"🚫 {user.full_name}\n"
            "получил 3/3 варна и был забанен."
        )

    else:

        await message.answer(
    "╔════════════════════╗\n"
    "     ✦ 𝑾𝑨𝑹𝑵 𝑺𝒀𝑺𝑻𝑬𝑴 ✦\n"
    "╚════════════════════╝\n\n"

    "━━━━━━━━━━━━━━━━━━\n"
    f"👤 𝑼𝒔𝒆𝒓:\n"
    f"『 {user.full_name} 』\n\n"

    f"⚠️ 𝑾𝒂𝒓𝒏𝒔:\n"
    f"『 {count}/3 』\n\n"

    f"👮 𝑩𝒚:\n"
    f"『 {message.from_user.full_name} 』\n"
    "━━━━━━━━━━━━━━━━━━\n\n"

    "⚠️ 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
    "『 𝑾𝑨𝑹𝑵𝑬𝑫 』"
)
# ================= РОМАНТИКА =================

async def create_request(message: Message,
                         action: str,
                         emoji: str,
                         text: str):

    if not message.reply_to_message:
        await message.answer(
            "💔 Ответьте на сообщение пользователя."
        )
        return

    sender = message.from_user
    target = message.reply_to_message.from_user

    if sender.id == target.id:
        await message.answer(
            "🥺 Нельзя использовать команду на себе."
        )
        return

    requests[target.id] = {
        "sender": sender.full_name,
        "action": action
    }

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💖 𝑷𝒓𝒊𝒏𝒚𝒂𝒕𝒊𝒆",
                    callback_data=f"accept_{action}"
                ),
                InlineKeyboardButton(
                    text="💔 𝑶𝒕𝒌𝒂𝒛",
                    callback_data=f"decline_{action}"
                )
            ]
        ]
    )

    await message.answer(
        "╔════════════════════╗\n"
        "      ✦ 𝑹𝑶𝑴𝑨𝑵𝑪𝑬 ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        f"💌 𝑶𝒕:\n"
        f"『 {sender.full_name} 』\n\n"

        f"{emoji} 𝑯𝒐𝒄𝒆𝒕:\n"
        f"『 {text} 』\n\n"

        f"💕 𝑲𝒐𝒎𝒖:\n"
        f"『 {target.full_name} 』\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"💖 {target.full_name}, принимаешь предложение?",
        reply_markup=keyboard
    )


# ================= КОМАНДЫ =================

@dp.message(Command("kiss"))
async def kiss(message: Message):
    await create_request(
        message,
        "kiss",
        "💋",
        "Поцеловать"
    )


@dp.message(Command("hug"))
async def hug(message: Message):
    await create_request(
        message,
        "hug",
        "🤗",
        "Обнять"
    )


@dp.message(Command("cuddle"))
async def cuddle(message: Message):
    await create_request(
        message,
        "cuddle",
        "🥰",
        "Прижаться к"
    )


@dp.message(Command("rose"))
async def rose(message: Message):
    await create_request(
        message,
        "rose",
        "🌹",
        "Подарить розу"
    )


@dp.message(Command("slap"))
async def slap(message: Message):
    await create_request(
        message,
        "slap",
        "👋",
        "Шлёпнуть"
    )


@dp.message(Command("bite"))
async def bite(message: Message):
    await create_request(
        message,
        "bite",
        "😈",
        "Укусить"
    )


# ================= ПРИНЯТЬ =================

@dp.callback_query(F.data.startswith("accept_"))
async def accept(callback: CallbackQuery):

    if callback.from_user.id not in requests:
        return

    req = requests[callback.from_user.id]

    actions = {
        "kiss": "💋 принял(а) поцелуй",
        "hug": "🤗 принял(а) объятия",
        "cuddle": "🥰 прижался(ась)",
        "rose": "🌹 принял(а) розу",
        "slap": "👋 получил(а) шлепок",
        "bite": "😈 позволил(а) укусить"
    }

    await callback.message.edit_text(
        "╔════════════════════╗\n"
        "        ✦ 𝑳𝑶𝑽𝑬 ✦\n"
        "╚════════════════════╝\n\n"

        f"💖 {callback.from_user.full_name}\n"
        f"{actions.get(req['action'])}\n\n"

        f"💕 От:\n"
        f"『 {req['sender']} 』"
    )

    del requests[callback.from_user.id]


# ============= ОТКАЗАТЬ =============

@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: CallbackQuery):

    if callback.from_user.id not in requests:
        return

    req = requests[callback.from_user.id]

    await callback.message.edit_text(
        "╔════════════════╗\n"
        "✦ BROKEN HEART ✦\n"
        "╚════════════════╝\n\n"

        f"💔 {callback.from_user.full_name}\n"
        "отклонил(а) предложение\n\n"

        f"💌 От:\n"
        f"『 {req['sender']} 』 ",
        parse_mode="HTML"
    )

    del requests[callback.from_user.id]
    # ================= ЗАПУСК =================

    async def health(request):
    return web.Response(text="Bot is running")

async def start_web():
    app = web.Application()
    app.router.add_get("/", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    async def main():
    logging.info("Starting bot")

    await start_web()

    me = await bot.get_me()
    logging.info(f"Logged in as {me.username}")

    await dp.start_polling(bot)
