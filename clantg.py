import asyncio
import json
import logging
import os

from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions
)
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError


# ================= НАСТРОЙКА =================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

TOKEN = "8649868110:AAEy17cpavp3J3wOnEWjHnCzGxLgBb3_tnI"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode="HTML"
    )
)

dp = Dispatcher()


# ================= БАЗА =================

DB_FILE = "database.json"

DEFAULT_DATABASE = {
    "ranks": {},
    "warns": {},
    "gifts": {},
    "users": {}
}


def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(
                DEFAULT_DATABASE,
                f,
                ensure_ascii=False,
                indent=4
            )
        return DEFAULT_DATABASE.copy()

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception as e:
        logging.exception(e)
        data = DEFAULT_DATABASE.copy()

    for key, value in DEFAULT_DATABASE.items():
        data.setdefault(key, value)

    return data


database = load_db()


def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(
                database,
                f,
                ensure_ascii=False,
                indent=4
            )
    except Exception as e:
        logging.exception(e)


ranks = database["ranks"]
warns = database["warns"]
gifts = database["gifts"]
users = database["users"]
money = database.setdefault("money", {})
rating = database.setdefault("rating", {})
duels = database.setdefault("duels", {})
clans = database.setdefault("clans", {})
clan_users = database.setdefault("clan_users", {})
clan_wars = database.setdefault("clan_wars", {})


# ================= РАНГИ =================

AVAILABLE_RANKS = [
    "Players",
    "ELIT",
    "DUKE",
    "GAY++",
    "HELPER",
    "MODER",
    "ADMIN"
]


# ================= ЗАПРОСЫ =================

requests = {}


# ================= ФУНКЦИИ =================

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)

        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        )

    except Exception as e:
        logging.exception(e)
        return False

OWNER_IDS = {
    6844274252
}

def is_owner(user_id: int):
    return user_id in OWNER_IDS

def get_money(user_id: int):
    uid = str(user_id)
    if uid not in money:
        money[uid] = 1000
        save_db()
    return money[uid]

def get_rating(user_id: int):
    uid = str(user_id)
    if uid not in rating:
        rating[uid] = 1000
        save_db()
    return rating[uid]


@dp.message(~F.text.startswith("/"))
async def save_user(message: Message):
    uid = str(message.from_user.id)

    if uid not in users:
        users[uid] = {
            "name": message.from_user.full_name,
            "username": message.from_user.username
        }
        save_db()


async def safe_answer(
    message: Message,
    text: str,
    **kwargs
):
    try:
        return await message.answer(
            text,
            **kwargs
        )
    except Exception as e:
        logging.exception(e)


async def safe_reply_photo(
    message: Message,
    photo,
    caption
):
    try:
        await message.answer_photo(
            photo=photo,
            caption=caption
        )
    except Exception:
        await safe_answer(
            message,
            caption
        )
        
        # ================= START =================

@dp.message(Command("start"))
async def start_cmd(message: Message):

    text = (
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
        "⚠️ /warn\n"
        "🔓 /unban\n\n"

        "🏆 Ранги:\n"
        "/rank\n"
        "/unrank\n\n"

        "📋 Профиль:\n"
        "/info\n\n"

        "✨ Добро пожаловать в Romantic Bot!"
    )

    await safe_answer(
        message,
        text
    )
    
@dp.message(Command("balance"))
async def balance_cmd(message: Message):

    balance = get_money(message.from_user.id)

    text = (
        "╔════════════════╗\n"
        "      💰 BALANCE\n"
        "╚════════════════╝\n\n"

        f"👤 <b>{message.from_user.full_name}</b>\n\n"

        f"💵 Баланс:\n"
        f"<b>{balance:,}$</b>\n\n"

        "✨ Береги свои деньги!"
    )

    await safe_answer(
        message,
        text
     )
     
@dp.message(Command("rating"))
async def rating_cmd(message: Message):

    users[str(message.from_user.id)] = {
        "username": message.from_user.username or "",
        "name": message.from_user.full_name
    }
    save_db()

    rate = get_rating(message.from_user.id)

    text = (
        "╔════════════════╗\n"
        "     ⭐ RATING ⭐\n"
        "╚════════════════╝\n\n"

        f"👤 <b>{message.from_user.full_name}</b>\n\n"

        f"⭐ Рейтинг:\n"
        f"<b>{rate}</b>\n\n"

        "✨ Повышай свой рейтинг!"
    )

    await safe_answer(
        message,
        text
    )  
    
    rating = database.setdefault("rating", {})
    
@dp.message(Command("givemoney"))
async def givemoney_cmd(message: Message):
    if not is_owner(message.from_user.id):
        return

    args = message.text.split()

    if len(args) < 3:
        await safe_answer(
            message,
            "⚠️ <b>Используй:</b>\n\n"
            "<code>/givemoney @user сумма</code>"
        )
        return

    try:
        username = args[1].replace("@", "").lower()
        amount = int(args[2])

        if amount <= 0:
            await safe_answer(
                message,
                "❌ Сумма должна быть больше 0"
            )
            return

        user_id = None

        # ищем пользователя в базе
        for uid, data in users.items():
            if data.get("username", "").lower() == username:
                user_id = str(uid)
                break

        if user_id is None:
            await safe_answer(
                message,
                "❌ Пользователь не найден\n\n"
                "Он должен хотя бы раз написать боту."
            )
            return

        if user_id not in money:
            money[user_id] = 0

        money[user_id] += amount
        save_db()

        await safe_answer(
            message,
            "╭━━━━━━━━━━━━━━╮\n"
            "     💸 <b>ＭＯＮＥＹ ＧＩＦＴ</b>\n"
            "╰━━━━━━━━━━━━━━╯\n\n"

            f"👤 Игрок:\n"
            f"<code>@{username}</code>\n\n"

            f"💵 Выдано:\n"
            f"<code>+{amount}$</code>\n\n"

            f"🏦 Баланс:\n"
            f"<code>{money[user_id]}$</code>\n\n"

            "━━━━━━━━━━━━━━\n"
            "👑 Выдано администратором"
        )

    except ValueError:
        await safe_answer(
            message,
            "❌ Пример:\n"
            "<code>/givemoney @player 5000</code>"
        )
        
        # ================= КЛАНЫ =================

CLAN_PRICE = 50000          # создание клана
CLAN_WAR_PRICE = 25000      # объявление войны
CLAN_MAX_MEMBERS = 10       # максимум участников
CLAN_START_LEVEL = 1
CLAN_START_BANK = 0
CLAN_WIN_REWARD = 50000
CLAN_WIN_RATING = 50
        # =========================
# 🎁 МАГАЗИН ПОДАРКОВ
# =========================


GIFTS = {
    "rose": {
        "name": "🌹 Роза",
        "price": 500
    },

    "diamond": {
        "name": "💎 Алмаз",
        "price": 5000
    },

    "crown": {
        "name": "👑 Корона",
        "price": 10000
    },

    "heart": {
        "name": "❤️ Сердце",
        "price": 1500
    }
}



# если подарков ещё нет
try:
    gifts
except NameError:
    gifts = {}



# =========================
# 🛒 МАГАЗИН
# =========================

@dp.message(Command("gifts"))
async def gifts_cmd(message: Message):

    text = (
        "╔════════════════╗\n"
        "       🎁 GIFTS SHOP\n"
        "╚════════════════╝\n\n"
    )


    for gift_id, item in GIFTS.items():

        text += (
            f"{item['name']}\n"
            f"💵 Цена: <b>{item['price']}$</b>\n"
            f"🛒 <code>/buygift {gift_id}</code>\n\n"
        )


    await safe_answer(
        message,
        text
    )



# =========================
# 💳 ПОКУПКА
# =========================

@dp.message(Command("buygift"))
async def buygift_cmd(message: Message):

    args = message.text.split()


    if len(args) < 2:

        await safe_answer(
            message,
            "❌ Используй:\n\n"
            "<code>/buygift rose</code>"
        )

        return



    gift_id = args[1].lower()



    if gift_id not in GIFTS:

        await safe_answer(
            message,
            "❌ Такого подарка нет"
        )

        return



    user_id = str(message.from_user.id)



    balance = money.get(
        user_id,
        0
    )


    price = GIFTS[gift_id]["price"]



    if balance < price:

        await safe_answer(
            message,
            "❌ Недостаточно денег"
        )

        return



    # снимаем деньги

    money[user_id] = balance - price



    # добавляем подарок

    if user_id not in gifts:

        gifts[user_id] = []



    gifts[user_id].append(
        GIFTS[gift_id]["name"]
    )



    save_db()



    await safe_answer(
        message,

        "╔════════════════╗\n"
        "       ✅ ПОКУПКА\n"
        "╚════════════════╝\n\n"

        f"🎁 Подарок:\n"
        f"<b>{GIFTS[gift_id]['name']}</b>\n\n"

        f"💵 Потрачено:\n"
        f"<b>{price}$</b>\n\n"

        "✨ Добавлено в профиль!"
    )
    
import random
import time

# ================= WORK =================

WORK_COOLDOWN = 60
work_cooldown = {}

jobs = [
    ("🛠 Работал на стройке", (150, 600)),
    ("🚕 Подрабатывал таксистом", (200, 700)),
    ("💻 Выполнял заказы в интернете", (300, 1000)),
    ("📦 Доставлял посылки", (100, 500)),
    ("🍔 Работал в кафе", (150, 650)),
]


@dp.message(Command("work"))
async def work_cmd(message: Message):
    user_id = str(message.from_user.id)
    now = time.time()

    last_work = work_cooldown.get(user_id)

    if last_work:
        left = int(WORK_COOLDOWN - (now - last_work))
        if left > 0:
            await safe_answer(
                message,
                f"⏳ До следующей работы осталось <b>{left} сек.</b>"
            )
            return

    work_cooldown[user_id] = now

    job, reward_range = random.choice(jobs)
    reward = random.randint(*reward_range)

    # Деньги
    money[user_id] = money.get(user_id, 0) + reward

    # Рейтинг
    rating[user_id] = rating.get(user_id, 0) + 1

    save_db()

    await safe_answer(
        message,
        f"""╔════════════════╗
       💼 WORK
╚════════════════╝

{job}

💵 Зарплата:
<b>+{reward}$</b>

⭐ Рейтинг:
<b>{rating[user_id]}</b>

💰 Баланс:
<b>{money[user_id]}$</b>

⏳ Следующая работа через 60 сек.
"""
    )
    
@dp.message(Command("gift"))
async def gift_cmd(message: Message):

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение пользователя."
        )
        return

    args = message.text.split()

    if len(args) < 2:
        await safe_answer(
            message,
            "❌ Использование:\n"
            "<code>/gift rose</code>\n\n"
            "Ответьте на сообщение человека."
        )
        return

    gift_id = args[1].lower()

    if gift_id not in GIFTS:
        await safe_answer(
            message,
            "❌ Такого подарка не существует."
        )
        return

    sender = str(message.from_user.id)
    target = str(message.reply_to_message.from_user.id)

    if sender == target:
        await safe_answer(
            message,
            "❌ Нельзя подарить подарок самому себе."
        )
        return

    gift_name = GIFTS[gift_id]["name"]

    if sender not in gifts or gift_name not in gifts[sender]:
        await safe_answer(
            message,
            "❌ У вас нет такого подарка."
        )
        return

    # Забираем подарок
    gifts[sender].remove(gift_name)

    # Передаём подарок
    if target not in gifts:
        gifts[target] = []

    gifts[target].append(gift_name)

    save_db()

    await safe_answer(
        message,

        "╔══════════════════════════════╗\n"
        "         ✦ 𝑳𝑶𝑽𝑬 𝑮𝑰𝑭𝑻 ✦\n"
        "╠══════════════════════════════╣\n\n"

        "🎁 <b>ПОДАРОК</b>\n"
        f"➥ <b>{gift_name}</b>\n\n"

        "👑 <b>ОТПРАВИТЕЛЬ</b>\n"
        f"➥ {message.from_user.full_name}\n\n"

        "💖 <b>ПОЛУЧАТЕЛЬ</b>\n"
        f"➥ {message.reply_to_message.from_user.full_name}\n\n"

        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "✨ <b>Подарок успешно передан!</b>\n"
        "💞 Пусть он принесёт радость.\n\n"

        "╚══════════════════════════════╝"
    )
    
@dp.message(Command("sellgift"))
async def sellgift_cmd(message: Message):

    args = message.text.split()

    if len(args) < 2:
        await safe_answer(
            message,
            "❌ Использование:\n"
            "<code>/sellgift rose</code>"
        )
        return

    gift_id = args[1].lower()

    if gift_id not in GIFTS:
        await safe_answer(
            message,
            "❌ Такого подарка нет."
        )
        return

    user_id = str(message.from_user.id)

    gift_name = GIFTS[gift_id]["name"]

    if user_id not in gifts or gift_name not in gifts[user_id]:
        await safe_answer(
            message,
            "❌ У вас нет этого подарка."
        )
        return

    # Цена продажи (50%)
    price = GIFTS[gift_id]["price"] // 2

    # Удаляем подарок
    gifts[user_id].remove(gift_name)

    # Начисляем деньги
    money[user_id] = money.get(user_id, 0) + price

    save_db()

    await safe_answer(
        message,

        "╔════════════════════╗\n"
        "      ✦ 𝑺𝑬𝑳𝑳 𝑮𝑰𝑭𝑻 ✦\n"
        "╚════════════════════╝\n\n"

        f"🎁 Продан:\n"
        f"『 <b>{gift_name}</b> 』\n\n"

        f"💵 Получено:\n"
        f"『 <b>+{price}$</b> 』\n\n"

        f"🏦 Баланс:\n"
        f"『 <b>{money[user_id]}$</b> 』\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "✅ Подарок успешно продан!"
    )
    
    from aiogram.types import Message
from aiogram.filters import Command


@dp.message(Command("top"))
async def top_cmd(message: Message):

    if not money:
        await safe_answer(
            message,
            "❌ Пока нет игроков."
        )
        return

    top_users = sorted(
        money.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    text = (
        "╔════════════════════╗\n"
        "       ✦ 𝑻𝑶𝑷 𝑩𝑨𝑳𝑨𝑵𝑪𝑬 ✦\n"
        "╚════════════════════╝\n\n"
    )

    place = 1

    for user_id, balance in top_users:

        name = users.get(
            user_id,
            "Неизвестный"
        )

        if place == 1:
            icon = "🥇"
        elif place == 2:
            icon = "🥈"
        elif place == 3:
            icon = "🥉"
        else:
            icon = f"{place}."

        text += (
            f"{icon} <b>{name}</b>\n"
            f"💵 『 {balance}$ 』\n\n"
        )

        place += 1


    await safe_answer(
        message,
        text +
        "━━━━━━━━━━━━━━━━━━"
    )
    
@dp.message(Command("pay"))
async def pay_cmd(message: Message):

    args = message.text.split()

    if len(args) < 3:
        await safe_answer(
            message,
            "⚠️ Используй:\n"
            "<code>/pay @user сумма</code>"
        )
        return


    username = args[1].replace("@", "").lower()

    try:
        amount = int(args[2])
    except ValueError:
        await safe_answer(
            message,
            "❌ Сумма должна быть числом."
        )
        return


    if amount <= 0:
        await safe_answer(
            message,
            "❌ Сумма должна быть больше 0."
        )
        return


    sender = str(message.from_user.id)


    # сохраняем отправителя
    users[sender] = {
        "username": message.from_user.username or "",
        "name": message.from_user.full_name
    }


    receiver = None

    # ищем получателя
    for uid, data in users.items():
        if data.get("username", "").lower() == username:
            receiver = str(uid)
            break


    if receiver is None:
        await safe_answer(
            message,
            "❌ Пользователь не найден.\n"
            "Он должен написать боту."
        )
        return


    if sender == receiver:
        await safe_answer(
            message,
            "❌ Нельзя отправить деньги самому себе."
        )
        return


    if money.get(sender, 0) < amount:
        await safe_answer(
            message,
            "❌ Недостаточно денег."
        )
        return


    money[sender] -= amount
    money[receiver] = money.get(receiver, 0) + amount

    save_db()


    await safe_answer(
        message,
        "╔════════════════╗\n"
        "       💸 PAY\n"
        "╚════════════════╝\n\n"

        f"👤 Отправитель:\n"
        f"<b>{message.from_user.full_name}</b>\n\n"

        f"➡️ Получатель:\n"
        f"<b>@{username}</b>\n\n"

        f"💵 Сумма:\n"
        f"<b>{amount}$</b>\n\n"

        "✅ Перевод выполнен!"
    )
    
async def send_stream_notification():

    text = (
        "╔══════════════════════╗\n"
        "      ✦ 𝑻𝑰𝑲𝑻𝑶𝑲 𝑳𝑰𝑽𝑬 ✦\n"
        "╚══════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "🔴 <b>СТРИМ НАЧАЛСЯ</b>\n\n"

        "👑 Стример:\n"
        "『 <b>ClanAmokLeaf</b> 』\n\n"

        "🎮 Статус:\n"
        "『 <b>ONLINE</b> 』\n\n"

        "🔥 Не пропусти трансляцию!\n\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "🔗 <a href='https://www.tiktok.com/@youngjay1108/live'>"
        "ОТКРЫТЬ СТРИМ</a>\n\n"

        "╔══════════════════════╗\n"
        "      Tg - ClanAmokLeaf\n"
        "╚══════════════════════╝"
    )

    await bot.send_message(
        CHAT_ID,
        text,
        disable_web_page_preview=False
    )
    
@dp.message(Command("clear"))
async def clear_cmd(
    message: Message,
    command: CommandObject
):

    if not await is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    try:
        amount = int(command.args or 10)
    except:
        amount = 10

    amount = min(amount, 100)

    deleted = 0

    try:
        async for msg in bot.get_chat_history(
            message.chat.id,
            limit=amount + 1
        ):
            try:
                await bot.delete_message(
                    message.chat.id,
                    msg.message_id
                )
                deleted += 1
            except:
                pass

    except Exception as e:
        logging.exception(e)

    await safe_answer(
        message,
        f"🧹 Удалено сообщений: {deleted}"
    )
    
@dp.message(Command("lock"))
async def lock_cmd(message: Message):

    if not await is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    try:

        await bot.set_chat_permissions(
            message.chat.id,

            ChatPermissions(
                can_send_messages=False
            )
        )

        await safe_answer(
            message,

            "╔════════════╗\n"
            "   🔒 LOCK\n"
            "╚════════════╝\n\n"

            "🚫 Чат закрыт."
        )

    except Exception as e:
        logging.exception(e)
        
@dp.message(Command("unlock"))
async def unlock_cmd(message: Message):

    if not await is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    try:

        await bot.set_chat_permissions(

            message.chat.id,

            ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_voice_notes=True,
                can_send_video_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )

        await safe_answer(
            message,

            "╔════════════╗\n"
            "   🔓 UNLOCK\n"
            "╚════════════╝\n\n"

            "✅ Чат открыт."
        )

    except Exception as e:
        logging.exception(e)
        
@dp.message(Command("duel"))
async def duel_cmd(message: Message):

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение игрока."
        )
        return

    args = message.text.split()

    if len(args) < 2:
        await safe_answer(
            message,
            "Использование:\n<code>/duel 5000</code>"
        )
        return

    try:
        amount = int(args[1])
    except:
        await safe_answer(
            message,
            "❌ Неверная ставка."
        )
        return

    if amount <= 0:
        return

    sender = message.from_user
    target = message.reply_to_message.from_user

    if sender.id == target.id:
        return

    sender_id = str(sender.id)

    if get_money(sender.id) < amount:
        await safe_answer(
            message,
            "❌ Недостаточно денег."
        )
        return

    duels[target.id] = {
        "sender": sender.id,
        "sender_name": sender.full_name,
        "target": target.id,
        "target_name": target.full_name,
        "bet": amount
    }

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚔️ Принять",
                    callback_data=f"duel_accept:{target.id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отказ",
                    callback_data=f"duel_decline:{target.id}"
                )
            ]
        ]
    )

    await safe_answer(
        message,

        "╔════════════════╗\n"
        "      ⚔️ DUEL\n"
        "╚════════════════╝\n\n"

        f"👤 {sender.full_name}\n"
        "вызывает на дуэль\n\n"

        f"💀 {target.full_name}\n\n"

        f"💰 Ставка:\n"
        f"<b>{amount}$</b>",

        reply_markup=keyboard
    ) 
    
    import random

@dp.callback_query(
    F.data.startswith("duel_accept:")
)
async def duel_accept(
    callback: CallbackQuery
):

    target_id = int(
        callback.data.split(":")[1]
    )

    if callback.from_user.id != target_id:
        return

    if target_id not in duels:
        return

    duel = duels.pop(target_id)

    sender = str(duel["sender"])
    target = str(duel["target"])
    bet = duel["bet"]

    if money.get(target, 0) < bet:
        await callback.message.edit_text(
            "❌ У игрока нет денег."
        )
        return

    money[sender] -= bet
    money[target] -= bet

    winner = random.choice([
        sender,
        target
    ])

    prize = bet * 2

    money[winner] += prize

    rating[winner] = rating.get(
        winner,
        1000
    ) + 10

    save_db()

    winner_name = (
        duel["sender_name"]
        if winner == sender
        else duel["target_name"]
    )

    await callback.message.edit_text(

        "╔════════════════╗\n"
        "     ⚔️ BATTLE\n"
        "╚════════════════╝\n\n"

        f"💥 Дуэль завершена!\n\n"

        f"🏆 Победитель:\n"
        f"<b>{winner_name}</b>\n\n"

        f"💰 Выигрыш:\n"
        f"<b>{prize}$</b>\n\n"

        "⭐ +10 рейтинга"
    )
    
@dp.callback_query(
    F.data.startswith(
        "duel_decline:"
    )
)
async def duel_decline(
    callback: CallbackQuery
):

    target_id = int(
        callback.data.split(":")[1]
    )

    if callback.from_user.id != target_id:
        return

    if target_id in duels:
        duel = duels.pop(target_id)

        await callback.message.edit_text(

            "╔════════════════╗\n"
            "      💔 DUEL\n"
            "╚════════════════╝\n\n"

            f"{duel['target_name']}\n"
            "отказался от дуэли."
        )
        
        CLAN_PRICE = 50000

@dp.message(Command("createclan"))
async def createclan_cmd(message: Message):

    args = message.text.split()

    if len(args) < 2:
        await safe_answer(
            message,
            "Использование:\n/createclan название"
        )
        return

    uid = str(message.from_user.id)

    if uid in clan_users:
        await safe_answer(
            message,
            "❌ Вы уже состоите в клане."
        )
        return

    name = args[1]

    if name in clans:
        await safe_answer(
            message,
            "❌ Такой клан уже существует."
        )
        return

    if get_money(message.from_user.id) < CLAN_PRICE:
        await safe_answer(
            message,
            f"❌ Нужно {CLAN_PRICE}$"
        )
        return

    money[uid] -= CLAN_PRICE

    clans[name] = {
        "owner": uid,
        "members": [uid],
        "bank": 0,
        "rating": 0,
        "wins": 0,
        "level": 1
    }

    clan_users[uid] = name

    save_db()

    await safe_answer(
        message,
        f"🏰 Клан <b>{name}</b> создан!"
    )
    
@dp.message(Command("clan"))
async def clan_cmd(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        await safe_answer(
            message,
            "❌ Вы не состоите в клане."
        )
        return

    clan_name = clan_users[uid]
    clan = clans[clan_name]

    text = (
        "╔════════════════╗\n"
        "      🏰 CLAN\n"
        "╚════════════════╝\n\n"

        f"🏰 Название:\n"
        f"<b>{clan_name}</b>\n\n"

        f"👑 Глава:\n"
        f"<b>{users[clan['owner']]['name']}</b>\n\n"

        f"👥 Участников:\n"
        f"<b>{len(clan['members'])}</b>\n\n"

        f"💰 Банк:\n"
        f"<b>{clan['bank']}$</b>\n\n"

        f"⭐ Рейтинг:\n"
        f"<b>{clan['rating']}</b>\n\n"

        f"🏆 Побед:\n"
        f"<b>{clan['wins']}</b>"
        f"<b>{clan['bank']}</b>"
    )

    await safe_answer(
        message,
        text
    )
    
@dp.message(Command("clandeposit"))
async def clan_deposit(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        return

    args = message.text.split()

    if len(args) < 2:
        return

    amount = int(args[1])

    if money.get(uid,0) < amount:
        return

    clan = clans[clan_users[uid]]

    money[uid] -= amount
    clan["bank"] += amount

    save_db()

    await safe_answer(
        message,
        f"💰 В банк клана внесено {amount}$"
    )
    
@dp.message(Command("leaveclan"))
async def leaveclan(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        return

    clan_name = clan_users[uid]

    clans[clan_name]["members"].remove(uid)

    del clan_users[uid]

    save_db()

    await safe_answer(
        message,
        "🚪 Вы покинули клан."
    )
    
@dp.message(Command("topclans"))
async def topclans(message: Message):

    top = sorted(
        clans.items(),
        key=lambda x: x[1]["rating"],
        reverse=True
    )[:10]

    text = (
        "╔════════════════╗\n"
        "     🏆 CLANS\n"
        "╚════════════════╝\n\n"
    )

    for i,(name,data) in enumerate(top,1):

        text += (
            f"{i}. 🏰 {name}\n"
            f"⭐ {data['rating']}\n\n"
        )

    await safe_answer(
        message,
        text
    )
    
@dp.message(Command("clanwar"))
async def clanwar_cmd(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        return

    my_clan = clan_users[uid]

    if clans[my_clan]["owner"] != uid:
        await safe_answer(
            message,
            "❌ Только глава клана может объявить войну."
        )
        return

    args = message.text.split()

    if len(args) < 2:
        await safe_answer(
            message,
            "Использование:\n/clanwar название"
        )
        return

    enemy = args[1]

    if enemy not in clans:
        await safe_answer(
            message,
            "❌ Клан не найден."
        )
        return

    if enemy == my_clan:
        return

    clan_wars[enemy] = {
        "attacker": my_clan,
        "defender": enemy
    }

    save_db()

    await safe_answer(
        message,

        "╔════════════════╗\n"
        "      ⚔️ WAR\n"
        "╚════════════════╝\n\n"

        f"🏰 {my_clan}\n"
        "объявил войну\n\n"

        f"🏰 {enemy}\n\n"

        "Используйте:\n"
        "<code>/acceptwar</code>"
    )
    
    import random

@dp.message(Command("acceptwar"))
async def acceptwar_cmd(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        return

    clan = clan_users[uid]

    if clan not in clan_wars:
        return

    war = clan_wars.pop(clan)

    attacker = war["attacker"]
    defender = war["defender"]

    attack_power = 0
    defend_power = 0

    for member in clans[attacker]["members"]:
        attack_power += get_rating(member)

    for member in clans[defender]["members"]:
        defend_power += get_rating(member)

    winner = random.choices(
        [attacker, defender],
        weights=[
            attack_power,
            defend_power
        ]
    )[0]

    loser = defender if winner == attacker else attacker

    clans[winner]["wins"] += 1
    clans[winner]["rating"] += 50

    clans[loser]["rating"] = max(
        0,
        clans[loser]["rating"] - 20
    )

    reward = 10000

    clans[winner]["bank"] += reward

    save_db()

    await safe_answer(
        message,

        "╔════════════════╗\n"
        "    ⚔️ CLAN WAR\n"
        "╚════════════════╝\n\n"

        f"🔥 {attacker}\n"
        f"⚔️ {defender}\n\n"

        f"🏆 Победитель:\n"
        f"<b>{winner}</b>\n\n"

        f"💰 Награда:\n"
        f"<b>{reward}$</b>\n\n"

        f"⭐ +50 рейтинга"
    )
    
@dp.message(Command("clandeposit"))
async def clandeposit_cmd(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        await safe_answer(
            message,
            "❌ Вы не состоите в клане."
        )
        return

    args = message.text.split()

    if len(args) < 2:
        return

    try:
        amount = int(args[1])
    except:
        return

    if amount <= 0:
        return

    if money.get(uid, 0) < amount:
        await safe_answer(
            message,
            "❌ Недостаточно денег."
        )
        return

    clan = clan_users[uid]

    money[uid] -= amount
    clans[clan]["bank"] += amount

    save_db()

    await safe_answer(
        message,

        "╔════════════════╗\n"
        "      🏦 КАЗНА\n"
        "╚════════════════╝\n\n"

        f"🏰 Клан:\n"
        f"<b>{clan}</b>\n\n"

        f"💰 Внесено:\n"
        f"<b>{amount}$</b>\n\n"

        f"🏦 Баланс:\n"
        f"<b>{clans[clan]['bank']}$</b>"
    )
    
@dp.message(Command("clanwithdraw"))
async def clanwithdraw_cmd(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        return

    clan = clan_users[uid]

    if clans[clan]["owner"] != uid:
        await safe_answer(
            message,
            "❌ Только глава клана."
        )
        return

    args = message.text.split()

    if len(args) < 2:
        return

    amount = int(args[1])

    if clans[clan]["bank"] < amount:
        await safe_answer(
            message,
            "❌ В казне недостаточно денег."
        )
        return

    clans[clan]["bank"] -= amount
    money[uid] += amount

    save_db()

    await safe_answer(
        message,
        f"💸 Из казны снято {amount}$"
    )
    
@dp.message(Command("clanbank"))
async def clanbank_cmd(message: Message):

    uid = str(message.from_user.id)

    if uid not in clan_users:
        return

    clan = clan_users[uid]

    await safe_answer(
        message,

        "╔════════════════╗\n"
        "      🏦 КАЗНА\n"
        "╚════════════════╝\n\n"

        f"🏰 Клан:\n"
        f"<b>{clan}</b>\n\n"

        f"💰 Баланс:\n"
        f"<b>{clans[clan]['bank']}$</b>\n\n"

        f"⭐ Уровень:\n"
        f"<b>{clans[clan]['level']}</b>"
    )
    # ================= BAN / UNBAN =================

def parse_time(text: str | None):
    """
    30m = 30 минут
    2h  = 2 часа
    7d  = 7 дней
    None = навсегда
    """

    if not text:
        return None

    text = text.lower().strip()

    try:
        if text.endswith("m"):
            return timedelta(minutes=int(text[:-1]))

        if text.endswith("h"):
            return timedelta(hours=int(text[:-1]))

        if text.endswith("d"):
            return timedelta(days=int(text[:-1]))

        return timedelta(minutes=int(text))

    except ValueError:
        return None


@dp.message(Command("ban"))
async def ban_cmd(message: Message, command: CommandObject):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение пользователя."
        )
        return

    user = message.reply_to_message.from_user

    if user.id == message.from_user.id:
        await safe_answer(
            message,
            "❌ Нельзя забанить самого себя."
        )
        return

    if await is_admin(message.chat.id, user.id):
        await safe_answer(
            message,
            "❌ Нельзя забанить администратора."
        )
        return

    delta = parse_time(command.args)

    until = None

    if delta:
        until = datetime.now(timezone.utc) + delta

    try:

        await bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            until_date=until
        )

        if until:

            duration = command.args

            until_text = until.strftime("%d.%m.%Y %H:%M")

            status = "ВРЕМЕННЫЙ БАН"

        else:

            duration = "Навсегда"

            until_text = "∞"

            status = "ПОСТОЯННЫЙ БАН"

        await safe_answer(
            message,

            "╔════════════════════╗\n"
            "      ✦ 𝑩𝑨𝑵 𝑺𝒀𝑺𝑻𝑬𝑴 ✦\n"
            "╚════════════════════╝\n\n"

            "━━━━━━━━━━━━━━━━━━\n"

            f"👤 𝑼𝒔𝒆𝒓:\n"
            f"『 {user.full_name} 』\n\n"

            f"🆔 ID:\n"
            f"『 {user.id} 』\n\n"

            f"⏳ 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:\n"
            f"『 {duration} 』\n\n"

            f"🕒 𝑼𝒏𝒕𝒊𝒍:\n"
            f"『 {until_text} 』\n\n"

            f"👮 𝑴𝒐𝒅𝒆𝒓:\n"
            f"『 {message.from_user.full_name} 』\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            f"⛔ 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
            f"『 {status} 』"
        )

    except TelegramForbiddenError:

        await safe_answer(
            message,
            "❌ У бота недостаточно прав."
        )

    except TelegramBadRequest as e:

        await safe_answer(
            message,
            f"❌ {e.message}"
        )

    except Exception as e:

        logging.exception(e)

        await safe_answer(
            message,
            "❌ Не удалось забанить пользователя."
        )


@dp.message(Command("unban"))
async def unban_cmd(
    message: Message,
    command: CommandObject
):

    if not await is_admin(
        message.chat.id,
        message.from_user.id
    ):
        return

    if not command.args:

        await safe_answer(
            message,
            "Использование:\n/unban ID"
        )
        return

    try:

        user_id = int(command.args)

    except ValueError:

        await safe_answer(
            message,
            "❌ ID должен быть числом."
        )
        return

    try:

        await bot.unban_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            only_if_banned=False
        )

        await safe_answer(

            message,

            "╔════════════════╗\n"
            "     🔓 UNBAN 🔓\n"
            "╚════════════════╝\n\n"

            f"✅ Пользователь\n"
            f"<code>{user_id}</code>\n"
            "успешно разбанен."
        )

    except TelegramBadRequest as e:

        await safe_answer(
            message,
            f"❌ {e.message}"
        )

    except Exception as e:

        logging.exception(e)

        await safe_answer(
            message,
            "❌ Не удалось выполнить разбан."
        )
        
        # ================= KICK =================

@dp.message(Command("kick"))
async def kick_cmd(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение пользователя."
        )
        return

    user = message.reply_to_message.from_user

    if user.id == message.from_user.id:
        await safe_answer(
            message,
            "❌ Нельзя исключить самого себя."
        )
        return

    if await is_admin(message.chat.id, user.id):
        await safe_answer(
            message,
            "❌ Нельзя исключить администратора."
        )
        return

    try:

        await bot.ban_chat_member(
            message.chat.id,
            user.id
        )

        await bot.unban_chat_member(
            message.chat.id,
            user.id,
            only_if_banned=True
        )

        await safe_answer(
            message,

            "╔════════════════════╗\n"
            "      ✦ 𝑲𝑰𝑪𝑲 ✦\n"
            "╚════════════════════╝\n\n"

            "━━━━━━━━━━━━━━━━━━\n"

            f"👤 𝑼𝒔𝒆𝒓:\n"
            f"『 {user.full_name} 』\n\n"

            f"👮 𝑴𝒐𝒅𝒆𝒓:\n"
            f"『 {message.from_user.full_name} 』\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "👢 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
            "『 KICKED 』"
        )

    except Exception as e:

        logging.exception(e)

        await safe_answer(
            message,
            "❌ Не удалось исключить пользователя."
        )


# ================= MUTE =================

@dp.message(Command("mute"))
async def mute_cmd(
    message: Message,
    command: CommandObject
):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение."
        )
        return

    user = message.reply_to_message.from_user

    if user.id == message.from_user.id:
        await safe_answer(
            message,
            "❌ Нельзя замутить самого себя."
        )
        return

    if await is_admin(message.chat.id, user.id):
        await safe_answer(
            message,
            "❌ Нельзя замутить администратора."
        )
        return

    delta = parse_time(command.args)

    if delta is None:
        delta = timedelta(minutes=30)

    until = datetime.now(timezone.utc) + delta

    try:

        await bot.restrict_chat_member(

            chat_id=message.chat.id,

            user_id=user.id,

            permissions=ChatPermissions(
                can_send_messages=False
            ),

            until_date=until
        )

        await safe_answer(

            message,

            "╔════════════════════╗\n"
            "     ✦ 𝑴𝑼𝑻𝑬 ✦\n"
            "╚════════════════════╝\n\n"

            "━━━━━━━━━━━━━━━━━━\n"

            f"👤 𝑼𝒔𝒆𝒓:\n"
            f"『 {user.full_name} 』\n\n"

            f"⏳ 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:\n"
            f"『 {command.args or '30m'} 』\n\n"

            f"🕒 𝑼𝒏𝒕𝒊𝒍:\n"
            f"『 {until.strftime('%d.%m.%Y %H:%M')} 』\n\n"

            f"👮 𝑴𝒐𝒅𝒆𝒓:\n"
            f"『 {message.from_user.full_name} 』\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "🔇 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
            "『 MUTED 』"
        )

    except Exception as e:

        logging.exception(e)

        await safe_answer(
            message,
            "❌ Не удалось выдать мут."
        )


# ================= UNMUTE =================

@dp.message(Command("unmute"))
async def unmute_cmd(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение."
        )
        return

    user = message.reply_to_message.from_user

    try:

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

        await safe_answer(

            message,

            "╔════════════════════╗\n"
            "     ✦ 𝑼𝑵𝑴𝑼𝑻𝑬 ✦\n"
            "╚════════════════════╝\n\n"

            "━━━━━━━━━━━━━━━━━━\n"

            f"👤 𝑼𝒔𝒆𝒓:\n"
            f"『 {user.full_name} 』\n\n"

            f"👮 𝑴𝒐𝒅𝒆𝒓:\n"
            f"『 {message.from_user.full_name} 』\n"

            "━━━━━━━━━━━━━━━━━━\n\n"

            "🔊 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
            "『 UNMUTED 』"
        )

    except Exception as e:

        logging.exception(e)

        await safe_answer(
            message,
            "❌ Не удалось снять мут."
        )
        
        # ================= WARN =================

@dp.message(Command("warn"))
async def warn_cmd(message: Message):

    if not await is_admin(message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение пользователя."
        )
        return

    user = message.reply_to_message.from_user

    if user.id == message.from_user.id:
        await safe_answer(
            message,
            "❌ Нельзя выдать варн самому себе."
        )
        return

    if await is_admin(message.chat.id, user.id):
        await safe_answer(
            message,
            "❌ Нельзя выдать варн администратору."
        )
        return

    uid = str(user.id)

    warns[uid] = warns.get(uid, 0) + 1
    save_db()

    count = warns[uid]

    if count >= 3:

        try:
            await bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=user.id
            )

            warns[uid] = 0
            save_db()

            await safe_answer(
                message,

                "╔════════════════════╗\n"
                "      ✦ 𝑾𝑨𝑹𝑵 ✦\n"
                "╚════════════════════╝\n\n"

                "━━━━━━━━━━━━━━━━━━\n"

                f"👤 𝑼𝒔𝒆𝒓:\n"
                f"『 {user.full_name} 』\n\n"

                "⚠️ 𝑾𝒂𝒓𝒏𝒔:\n"
                "『 3/3 』\n\n"

                f"👮 𝑴𝒐𝒅𝒆𝒓:\n"
                f"『 {message.from_user.full_name} 』\n"

                "━━━━━━━━━━━━━━━━━━\n\n"

                "🚫 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
                "『 BANNED 』"
            )

        except Exception as e:

            logging.exception(e)

            await safe_answer(
                message,
                "❌ Не удалось забанить пользователя."
            )

        return

    await safe_answer(

        message,

        "╔════════════════════╗\n"
        "      ✦ 𝑾𝑨𝑹𝑵 ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"👤 𝑼𝒔𝒆𝒓:\n"
        f"『 {user.full_name} 』\n\n"

        f"⚠️ 𝑾𝒂𝒓𝒏𝒔:\n"
        f"『 {count}/3 』\n\n"

        f"👮 𝑴𝒐𝒅𝒆𝒓:\n"
        f"『 {message.from_user.full_name} 』\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "⚠️ 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
        "『 WARNED 』"
    )
        
        # ================= RANK =================

@dp.message(Command("rank"))
async def rank_cmd(
        message: Message,
        command: CommandObject
):

    if not await is_admin(
            message.chat.id,
            message.from_user.id):
        return

    if not message.reply_to_message:
        await safe_answer(
            message,
            "❌ Ответьте на сообщение пользователя."
        )
        return

    if not command.args:

        await safe_answer(
            message,

            "Использование:\n"
            "/rank ADMIN"
        )
        return

    user = message.reply_to_message.from_user

    if user.id == message.from_user.id:

        await safe_answer(
            message,
            "❌ Нельзя изменить собственный ранг."
        )
        return

    rank = command.args.upper()

    available = [
        r.upper()
        for r in AVAILABLE_RANKS
    ]

    if rank not in available:

        await safe_answer(
            message,
            "❌ Такого ранга нет."
        )
        return

    ranks[str(user.id)] = rank

    save_db()

    try:

        if rank == "MODER":

            await bot.promote_chat_member(

                chat_id=message.chat.id,

                user_id=user.id,

                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True
            )

        elif rank == "ADMIN":

            await bot.promote_chat_member(

                chat_id=message.chat.id,

                user_id=user.id,

                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_promote_members=True
            )

    except Exception as e:

        logging.exception(e)

    await safe_answer(

        message,

        "╔════════════════════╗\n"
        "      ✦ 𝑹𝑨𝑵𝑲 ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"👤 𝑼𝒔𝒆𝒓:\n"
        f"『 {user.full_name} 』\n\n"

        f"🏆 𝑹𝒂𝒏𝒌:\n"
        f"『 {rank} 』\n\n"

        f"👮 𝑩𝒚:\n"
        f"『 {message.from_user.full_name} 』\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "✅ 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
        "『 UPDATED 』"
    )


# ================= UNRANK =================

@dp.message(Command("unrank"))
async def unrank_cmd(message: Message):

    if not await is_admin(
            message.chat.id,
            message.from_user.id):
        return

    if not message.reply_to_message:

        await safe_answer(
            message,
            "❌ Ответьте на сообщение пользователя."
        )
        return

    user = message.reply_to_message.from_user

    ranks[str(user.id)] = "Players"

    save_db()

    try:

        await bot.promote_chat_member(

            chat_id=message.chat.id,

            user_id=user.id,

            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )

    except Exception as e:

        logging.exception(e)

    await safe_answer(

        message,

        "╔════════════════════╗\n"
        "     ✦ 𝑼𝑵𝑹𝑨𝑵𝑲 ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"👤 𝑼𝒔𝒆𝒓:\n"
        f"『 {user.full_name} 』\n\n"

        "🏆 𝑹𝒂𝒏𝒌:\n"
        "『 Players 』\n\n"

        f"👮 𝑩𝒚:\n"
        f"『 {message.from_user.full_name} 』\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "❌ 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
        "『 REMOVED 』"
    )
    
    # ================= PROFILE =================

@dp.message(Command("info"))
async def info_cmd(message: Message):

    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    try:
        member = await bot.get_chat_member(
            message.chat.id,
            user.id
        )

        status = member.status

    except Exception:

        status = "unknown"

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

    username = (
        f"@{user.username}"
        if user.username
        else "нет"
    )

    status_names = {
        "creator": "👑 Creator",
        "administrator": "🛡 Administrator",
        "member": "👤 Member",
        "restricted": "🔇 Muted",
        "left": "🚪 Left",
        "kicked": "🚫 Banned"
    }

    status = status_names.get(
        status,
        status
    )

    text = (

        "╔════════════════════╗\n"
        "      ✦ 𝑷𝑹𝑶𝑭𝑰𝑳𝑬 ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"👤 𝑵𝒂𝒎𝒆:\n"
        f"『 {user.full_name} 』\n\n"

        f"🆔 𝑰𝑫:\n"
        f"『 <code>{user.id}</code> 』\n\n"

        f"🏷 𝑼𝒔𝒆𝒓:\n"
        f"『 {username} 』\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🏆 𝑹𝒂𝒏𝒌:\n"
        f"『 {rank} 』\n\n"

        f"⭐ 𝑺𝒕𝒂𝒕𝒖𝒔:\n"
        f"『 {status} 』\n\n"

        f"⚠️ 𝑾𝒂𝒓𝒏𝒔:\n"
        f"『 {warns_count}/3 』\n\n"

        f"🎁 𝑮𝒊𝒇𝒕𝒔:\n"
        f"『 {gift_count} 』\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"💬 𝑪𝒉𝒂𝒕:\n"
        f"『 {message.chat.title} 』\n"

        "━━━━━━━━━━━━━━━━━━"
    )

    try:

        photos = await bot.get_user_profile_photos(
            user.id,
            limit=1
        )

        if photos.total_count:

            await message.answer_photo(
                photo=photos.photos[0][-1].file_id,
                caption=text
            )

        else:

            await safe_answer(
                message,
                text
            )

    except Exception as e:

        logging.exception(e)

        await safe_answer(
            message,
            text
        )
        
        # ================= ROMANCE =================

ROMANCE_ACTIONS = {
    "kiss": {
        "emoji": "💋",
        "text": "Поцеловать"
    },
    "hug": {
        "emoji": "🤗",
        "text": "Обнять"
    },
    "cuddle": {
        "emoji": "🥰",
        "text": "Прижаться"
    },
    "rose": {
        "emoji": "🌹",
        "text": "Подарить розу"
    },
    "slap": {
        "emoji": "👋",
        "text": "Шлёпнуть"
    },
    "bite": {
        "emoji": "😈",
        "text": "Укусить"
    }
}


async def create_request(
        message: Message,
        action: str
):

    if not message.reply_to_message:

        await safe_answer(
            message,
            "💔 Ответьте на сообщение пользователя."
        )
        return

    sender = message.from_user
    target = message.reply_to_message.from_user

    if sender.id == target.id:

        await safe_answer(
            message,
            "🥺 Нельзя использовать команду на себе."
        )
        return

    if target.id in requests:

        await safe_answer(
            message,
            "❌ У пользователя уже есть активный запрос."
        )
        return

    data = ROMANCE_ACTIONS[action]

    requests[target.id] = {

        "sender_id": sender.id,

        "sender_name": sender.full_name,

        "target_name": target.full_name,

        "action": action,

        "created": datetime.now(timezone.utc)

    }

    keyboard = InlineKeyboardMarkup(

        inline_keyboard=[

            [

                InlineKeyboardButton(

                    text="💖 Принять",

                    callback_data=f"accept:{target.id}"

                ),

                InlineKeyboardButton(

                    text="💔 Отказать",

                    callback_data=f"decline:{target.id}"

                )

            ]

        ]

    )

    await safe_answer(

        message,

        "╔════════════════════╗\n"
        "      ✦ 𝑹𝑶𝑴𝑨𝑵𝑪𝑬 ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"💌 𝑶𝒕:\n"
        f"『 {sender.full_name} 』\n\n"

        f"{data['emoji']} 𝑯𝒐𝒄𝒆𝒕:\n"
        f"『 {data['text']} 』\n\n"

        f"💕 𝑲𝒐𝒎𝒖:\n"
        f"『 {target.full_name} 』\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        f"{target.full_name}, принимаешь предложение?",

        reply_markup=keyboard

    )


# ================= COMMANDS =================


@dp.message(Command("kiss"))
async def kiss(message: Message):
    await create_request(
        message,
        "kiss"
    )


@dp.message(Command("hug"))
async def hug(message: Message):
    await create_request(
        message,
        "hug"
    )


@dp.message(Command("cuddle"))
async def cuddle(message: Message):
    await create_request(
        message,
        "cuddle"
    )


@dp.message(Command("rose"))
async def rose(message: Message):
    await create_request(
        message,
        "rose"
    )


@dp.message(Command("slap"))
async def slap(message: Message):
    await create_request(
        message,
        "slap"
    )


@dp.message(Command("bite"))
async def bite(message: Message):
    await create_request(
        message,
        "bite"
    )
    
    # ================= CALLBACKS =================

ROMANCE_ACCEPT_TEXT = {
    "kiss": "💋 принял(а) поцелуй",
    "hug": "🤗 принял(а) объятия",
    "cuddle": "🥰 прижался(ась)",
    "rose": "🌹 принял(а) розу",
    "slap": "👋 получил(а) шлепок",
    "bite": "😈 позволил(а) укусить"
}


@dp.callback_query(F.data.startswith("accept:"))
async def romance_accept(callback: CallbackQuery):

    try:

        target_id = int(callback.data.split(":")[1])

    except (IndexError, ValueError):

        await callback.answer(
            "Ошибка.",
            show_alert=True
        )
        return

    if callback.from_user.id != target_id:

        await callback.answer(
            "❌ Это не ваш запрос.",
            show_alert=True
        )
        return

    if target_id not in requests:

        await callback.answer(
            "❌ Запрос уже недействителен.",
            show_alert=True
        )
        return

    req = requests.pop(target_id)

    await callback.answer(
        "💖 Принято!"
    )

    await callback.message.edit_text(

        "╔════════════════════╗\n"
        "        ✦ 𝑳𝑶𝑽𝑬 ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"💖 {callback.from_user.full_name}\n"
        f"{ROMANCE_ACCEPT_TEXT[req['action']]}\n\n"

        f"💕 От:\n"
        f"『 {req['sender_name']} 』\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "❤️ Статус:\n"
        "『 ACCEPTED 』"
    )


@dp.callback_query(F.data.startswith("decline:"))
async def romance_decline(callback: CallbackQuery):

    try:

        target_id = int(callback.data.split(":")[1])

    except (IndexError, ValueError):

        await callback.answer(
            "Ошибка.",
            show_alert=True
        )
        return

    if callback.from_user.id != target_id:

        await callback.answer(
            "❌ Это не ваш запрос.",
            show_alert=True
        )
        return

    if target_id not in requests:

        await callback.answer(
            "❌ Запрос уже недействителен.",
            show_alert=True
        )
        return

    req = requests.pop(target_id)

    await callback.answer(
        "💔 Отказано."
    )

    await callback.message.edit_text(

        "╔════════════════════╗\n"
        "     ✦ BROKEN HEART ✦\n"
        "╚════════════════════╝\n\n"

        "━━━━━━━━━━━━━━━━━━\n"

        f"💔 {callback.from_user.full_name}\n"
        "отклонил(а) предложение\n\n"

        f"💌 От:\n"
        f"『 {req['sender_name']} 』\n"

        "━━━━━━━━━━━━━━━━━━\n\n"

        "💔 Статус:\n"
        "『 DECLINED 』"
    )
    
    # ================= ЗАПУСК =================

async def main():
    logging.info("Romantic Bot запущен.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())