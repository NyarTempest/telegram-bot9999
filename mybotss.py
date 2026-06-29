import asyncio
import json
import logging
import os
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
)

# ---------------- ЛОГИ ---------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------- TOKEN ---------------- #

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError(
        "Переменная окружения TOKEN отсутствует."
    )

bot = Bot(TOKEN)

dp = Dispatcher()

# ---------------- ФАЙЛ БАЗЫ ---------------- #

DB_FILE = "database.json"

DEFAULT_DB = {
    "ranks": {},
    "warns": {},
    "gifts": {},
    "roses": {}
}


def load_db():

    if not os.path.exists(DB_FILE):

        with open(
                DB_FILE,
                "w",
                encoding="utf8"
        ) as f:

            json.dump(
                DEFAULT_DB,
                f,
                ensure_ascii=False,
                indent=4
            )

        return DEFAULT_DB.copy()

    try:

        with open(
                DB_FILE,
                "r",
                encoding="utf8"
        ) as f:

            data = json.load(f)

    except Exception:

        logger.exception("Повреждена база.")

        data = DEFAULT_DB.copy()

    for key in DEFAULT_DB:

        if key not in data:
            data[key] = {}

    return data


database = load_db()


def save_db():

    with open(
            DB_FILE,
            "w",
            encoding="utf8"
    ) as f:

        json.dump(
            database,
            f,
            ensure_ascii=False,
            indent=4
        )


ranks = database["ranks"]
warns = database["warns"]
gifts = database["gifts"]
roses = database["roses"]

# ---------------- КОНСТАНТЫ ---------------- #

AVAILABLE_RANKS = (
    "Players",
    "ELIT",
    "DUKE",
    "GAY++",
    "HELPER",
    "MODER",
    "ADMIN"
)

GIFT_TYPES = {

    "bear": "🧸 Мишка",

    "bunny": "🐰 Кролик",

    "heart": "❤️ Сердце",

    "flowers": "💐 Букет",

    "ring": "💍 Кольцо"

}

users = set()

requests = {}

async def is_admin(chat_id: int, user_id: int):

    try:

        member = await bot.get_chat_member(
            chat_id,
            user_id
        )

        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        )

    except Exception:

        logger.exception("Ошибка проверки администратора")

        return False


def add_gift(user_id: int):

    uid = str(user_id)

    gifts[uid] = gifts.get(uid, 0) + 1

    save_db()


def add_rose(user_id: int):

    uid = str(user_id)

    roses[uid] = roses.get(uid, 0) + 1

    save_db()


def add_warn(user_id: int):

    uid = str(user_id)

    warns[uid] = warns.get(uid, 0) + 1

    save_db()

    return warns[uid]
    
    @dp.message()
async def logger_messages(message: Message):

    users.add(message.from_user.id)

    logger.info(

        "%s | %s | %s",

        message.from_user.id,
# ==========================================================
#               РОМАНТИЧЕСКИЕ ЗАПРОСЫ
# ==========================================================

REQUEST_LIFETIME = 300  # 5 минут


def create_keyboard(action: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💖 Принять",
                    callback_data=f"accept:{action}"
                ),
                InlineKeyboardButton(
                    text="💔 Отказать",
                    callback_data=f"decline:{action}"
                )
            ]
        ]
    )


async def send_request(
    message: Message,
    action: str,
    emoji: str,
    action_text: str
):

    if not message.reply_to_message:
        await message.answer(
            "❌ Ответьте на сообщение пользователя."
        )
        return

    sender = message.from_user
    target = message.reply_to_message.from_user

    if sender.id == target.id:
        await message.answer(
            "❌ Нельзя использовать команду на себе."
        )
        return

    if target.id in requests:
        await message.answer(
            "⚠️ У этого пользователя уже есть активный запрос."
        )
        return

    requests[target.id] = {
        "sender_id": sender.id,
        "sender_name": sender.full_name,
        "target_id": target.id,
        "action": action,
        "created": datetime.now()
    }

    await message.answer(
        f"{emoji} {sender.full_name} хочет {action_text} "
        f"{target.full_name}.",
        reply_markup=create_keyboard(action)
    )

    logger.info(
        "%s -> %s (%s)",
        sender.id,
        target.id,
        action
    )


# ==========================================================
#                    РОМАНТИЧЕСКИЕ КОМАНДЫ
# ==========================================================

@dp.message(Command("kiss"))
async def kiss(message: Message):
    await send_request(
        message,
        "kiss",
        "💋",
        "поцеловать"
    )


@dp.message(Command("hug"))
async def hug(message: Message):
    await send_request(
        message,
        "hug",
        "🤗",
        "обнять"
    )


@dp.message(Command("cuddle"))
async def cuddle(message: Message):
    await send_request(
        message,
        "cuddle",
        "🥰",
        "прижаться к"
    )


@dp.message(Command("rose"))
async def rose(message: Message):
    await send_request(
        message,
        "rose",
        "🌹",
        "подарить розу"
    )


@dp.message(Command("slap"))
async def slap(message: Message):
    await send_request(
        message,
        "slap",
        "👋",
        "шлёпнуть"
    )


@dp.message(Command("bite"))
async def bite(message: Message):
    await send_request(
        message,
        "bite",
        "😈",
        "укусить"
    )
    
    # ==========================================================
#                        ПОДАРКИ
# ==========================================================

@dp.message(Command("gift"))
async def gift(message: Message, command: CommandObject):

    if not message.reply_to_message:
        await message.answer(
            "❌ Ответьте на сообщение пользователя.\n\n"
            "Пример:\n"
            "/gift bear"
        )
        return

    if not command.args:
        await message.answer(
            "🎁 Доступные подарки:\n\n"
            "🧸 bear\n"
            "🐰 bunny\n"
            "❤️ heart\n"
            "💐 flowers\n"
            "💍 ring"
        )
        return

    gift = command.args.lower()

    if gift not in GIFT_TYPES:
        await message.answer("❌ Такого подарка нет.")
        return

    await send_request(
        message,
        f"gift:{gift}",
        "🎁",
        f"подарить {GIFT_TYPES[gift]}"
    )


# ==========================================================
#                  CALLBACK - ПРИНЯТЬ
# ==========================================================

@dp.callback_query(F.data.startswith("accept:"))
async def accept(callback: CallbackQuery):

    await callback.answer()

    req = requests.get(callback.from_user.id)

    if req is None:
        await callback.message.edit_text(
            "⌛ Запрос уже недействителен."
        )
        return

    action = req["action"]

    if action == "rose":
        add_rose(callback.from_user.id)

    elif action.startswith("gift:"):
        add_gift(callback.from_user.id)

    actions = {
        "kiss": "💋 принял(а) поцелуй",
        "hug": "🤗 принял(а) объятия",
        "cuddle": "🥰 принял(а) объятия",
        "rose": "🌹 получил(а) розу",
        "slap": "👋 получил(а) шлепок",
        "bite": "😈 позволил(а) укусить"
    }

    if action.startswith("gift:"):

        gift_name = action.split(":")[1]

        text = (
            f"🎁 {callback.from_user.full_name}\n"
            f"получил(а)\n"
            f"{GIFT_TYPES[gift_name]}\n\n"
            f"💖 От {req['sender_name']}"
        )

    else:

        text = (
            f"{actions[action]}\n\n"
            f"💖 От {req['sender_name']}"
        )

    await callback.message.edit_text(text)

    requests.pop(callback.from_user.id, None)


# ==========================================================
#                  CALLBACK - ОТКАЗАТЬ
# ==========================================================

@dp.callback_query(F.data.startswith("decline:"))
async def decline(callback: CallbackQuery):

    await callback.answer()

    req = requests.get(callback.from_user.id)

    if req is None:
        await callback.message.edit_text(
            "⌛ Запрос уже недействителен."
        )
        return

    await callback.message.edit_text(

        f"💔 {callback.from_user.full_name}\n"
        f"отклонил(а) предложение\n\n"
        f"От {req['sender_name']}"

    )

    requests.pop(callback.from_user.id, None)
    
    # ==========================================================
#                       START
# ==========================================================

@dp.message(Command("start"))
async def start(message: Message):

    text = (
        "╔════════════════════╗\n"
        "      ✦ Romantic Bot ✦\n"
        "╚════════════════════╝\n\n"

        "❤️ Романтика\n"
        "💋 /kiss\n"
        "🤗 /hug\n"
        "🥰 /cuddle\n"
        "🌹 /rose\n"
        "👋 /slap\n"
        "😈 /bite\n"
        "🎁 /gift\n\n"

        "👤 Профиль\n"
        "📄 /info\n\n"

        "Добро пожаловать ❤️"
    )

    await message.answer(text)


# ==========================================================
#                       INFO
# ==========================================================

@dp.message(Command("info"))
async def info(message: Message):

    user = (
        message.reply_to_message.from_user
        if message.reply_to_message
        else message.from_user
    )

    try:
        member = await bot.get_chat_member(
            message.chat.id,
            user.id
        )

        status = member.status

    except Exception:
        status = "unknown"

    uid = str(user.id)

    rank = ranks.get(uid, "Players")

    warn_count = warns.get(uid, 0)

    rose_count = roses.get(uid, 0)

    gift_count = gifts.get(uid, 0)

    username = (
        f"@{user.username}"
        if user.username
        else "нет"
    )

    text = (
        "╔════════════════════╗\n"
        "        👤 PROFILE\n"
        "╚════════════════════╝\n\n"

        f"👤 Имя:\n"
        f"{user.full_name}\n\n"

        f"🆔 ID:\n"
        f"<code>{user.id}</code>\n\n"

        f"🏷 Username:\n"
        f"{username}\n\n"

        f"🏆 Ранг: {rank}\n"
        f"⭐ Статус: {status}\n"
        f"⚠️ Варны: {warn_count}/3\n"
        f"🌹 Розы: {rose_count}\n"
        f"🎁 Подарки: {gift_count}"
    )

    try:

        photos = await bot.get_user_profile_photos(
            user.id,
            limit=1
        )

        if photos.total_count:

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

    except Exception:

        logger.exception("Ошибка команды /info")

        await message.answer(
            text,
            parse_mode="HTML"
        )
        
        # ==========================================================
#                    ⚜️ MODERATION ⚜️
# ==========================================================

@dp.message(Command("warn"))
async def warn(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer(
            "❌ <b>У вас недостаточно прав.</b>",
            parse_mode="HTML"
        )
        return

    if not message.reply_to_message:
        await message.answer(
            "⚠️ Ответьте на сообщение пользователя.",
            parse_mode="HTML"
        )
        return

    user = message.reply_to_message.from_user

    count = add_warn(user.id)

    await message.answer(
        f"""
╔══════════════════════╗
        ⚠️ WARNING
╚══════════════════════╝

👤 <b>Пользователь</b>

{user.full_name}

📊 Предупреждений

<code>{count}/3</code>
""",
        parse_mode="HTML"
    )

    if count >= 3:

        try:

            await bot.ban_chat_member(
                message.chat.id,
                user.id
            )

            await message.answer(
                f"""
╔══════════════════════╗
          🚫 AUTO BAN
╚══════════════════════╝

👤 {user.full_name}

❌ Получил 3 предупреждения

⛔ Пользователь автоматически заблокирован.
""",
                parse_mode="HTML"
            )

        except Exception:
            logger.exception("AutoBan")


# ==========================================================
#                         MUTE
# ==========================================================

@dp.message(Command("mute"))
async def mute(message: Message, command: CommandObject):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await message.answer(
            "⚠️ Ответьте на сообщение."
        )
        return

    if not command.args:
        await message.answer(
            "<b>Использование</b>\n\n"
            "<code>/mute 10</code>",
            parse_mode="HTML"
        )
        return

    try:

        minutes = int(command.args)

    except ValueError:

        await message.answer(
            "❌ Нужно указать число."
        )

        return

    until = datetime.now() + timedelta(minutes=minutes)

    try:

        await bot.restrict_chat_member(

            chat_id=message.chat.id,

            user_id=message.reply_to_message.from_user.id,

            permissions=ChatPermissions(
                can_send_messages=False
            ),

            until_date=until

        )

        await message.answer(
            f"""
╔══════════════════════╗
            🔇 MUTE
╚══════════════════════╝

👤 Пользователь

<b>{message.reply_to_message.from_user.full_name}</b>

⏳ Время

<b>{minutes} минут</b>

━━━━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="HTML"
        )

    except Exception:

        logger.exception("Mute")


# ==========================================================
#                       UNMUTE
# ==========================================================

@dp.message(Command("unmute"))
async def unmute(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        return

    try:

        await bot.restrict_chat_member(

            chat_id=message.chat.id,

            user_id=message.reply_to_message.from_user.id,

            permissions=ChatPermissions(

                can_send_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_send_polls=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_documents=True,
                can_send_voice_notes=True,
                can_send_video_notes=True,
                can_send_audios=True

            )

        )

        await message.answer(
            f"""
╔══════════════════════╗
          🔊 UNMUTE
╚══════════════════════╝

👤 Пользователь

<b>{message.reply_to_message.from_user.full_name}</b>

✅ Ограничения сняты.
""",
            parse_mode="HTML"
        )

    except Exception:

        logger.exception("Unmute")
        
        # ==========================================================
#                           BAN
# ==========================================================

@dp.message(Command("ban"))
async def ban(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        await message.answer(
            "❌ <b>У вас недостаточно прав.</b>",
            parse_mode="HTML"
        )
        return

    if not message.reply_to_message:
        await message.answer(
            "⚠️ Ответьте на сообщение пользователя.",
            parse_mode="HTML"
        )
        return

    user = message.reply_to_message.from_user

    try:

        await bot.ban_chat_member(
            message.chat.id,
            user.id
        )

        await message.answer(
            f"""
╔══════════════════════╗
            🚫 BAN
╚══════════════════════╝

👤 Пользователь

<b>{user.full_name}</b>

⛔ Заблокирован администратором.

━━━━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="HTML"
        )

    except Exception:
        logger.exception("Ban")


# ==========================================================
#                         UNBAN
# ==========================================================

@dp.message(Command("unban"))
async def unban(message: Message, command: CommandObject):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not command.args:
        await message.answer(
            "<b>Использование:</b>\n\n"
            "<code>/unban ID</code>",
            parse_mode="HTML"
        )
        return

    try:

        uid = int(command.args)

        await bot.unban_chat_member(
            message.chat.id,
            uid
        )

        await message.answer(
            f"""
╔══════════════════════╗
          ✅ UNBAN
╚══════════════════════╝

🆔 Пользователь

<code>{uid}</code>

🔓 Успешно разблокирован.

━━━━━━━━━━━━━━━━━━━━━━
""",
            parse_mode="HTML"
        )

    except Exception:
        logger.exception("Unban
        
        # ==========================================================
#                 ОЧИСТКА ПРОСРОЧЕННЫХ ЗАПРОСОВ
# ==========================================================

async def request_cleaner():

    while True:

        now = datetime.now()

        expired = []

        for uid, req in requests.items():

            if (now - req["created"]).total_seconds() > REQUEST_LIFETIME:
                expired.append(uid)

        for uid in expired:
            requests.pop(uid, None)

        await asyncio.sleep(30)


# ==========================================================
#                 ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК
# ==========================================================

@dp.errors()
async def errors_handler(event):

    logger.exception(
        "Произошла ошибка: %s",
        event.exception
    )

    return True


# ==========================================================
#                        MAIN
# ==========================================================

async def main():

    logger.info("===================================")
    logger.info("Запуск бота...")
    logger.info("===================================")

    try:

        # Удаляем старый webhook
        await bot.delete_webhook(
            drop_pending_updates=False
        )

        # Очистка старых запросов
        asyncio.create_task(
            request_cleaner()
        )

        # Запуск polling
        await dp.start_polling(bot)

    finally:

        logger.info("Закрытие сессии...")

        await bot.session.close()


# ==========================================================
#                       START APP
# ==========================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        logger.info("Бот остановлен.")

    except Exception:

        logger.exception("Критическая ошибка запуска.")