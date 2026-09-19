import os
import random
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# SETTINGS
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# =========================
# USER DATA
# =========================

users = {}

# =========================
# QUIZ QUESTIONS
# =========================

QUESTIONS = [
    {
        "question": "Which blockchain is known for fast, low-cost transactions?",
        "options": ["Ethereum", "Solana", "Bitcoin", "Litecoin"],
        "answer": 1,
    },
    {
        "question": "What does NFT stand for?",
        "options": [
            "New Finance Token",
            "Non-Fungible Token",
            "Network Fund Transfer",
            "Next Future Technology",
        ],
        "answer": 1,
    },
    {
        "question": "What does DAO stand for?",
        "options": [
            "Digital Asset Operation",
            "Decentralized Autonomous Organization",
            "Distributed Account Online",
            "Digital Automated Office",
        ],
        "answer": 1,
    },
    {
        "question": "What is a crypto wallet mainly used for?",
        "options": [
            "Managing crypto assets",
            "Making phone calls",
            "Creating websites",
            "Sending emails",
        ],
        "answer": 0,
    },
    {
        "question": "What does HODL mean in crypto culture?",
        "options": [
            "Hold On for Dear Life",
            "High Online Digital Ledger",
            "Hold Digital Liquidity",
            "Home Of Digital Liquidity",
        ],
        "answer": 0,
    },
]

# =========================
# USER FUNCTIONS
# =========================

def get_user(user):
    if user.id not in users:
        users[user.id] = {
            "name": user.first_name or "Goblin",
            "xp": 0,
            "raid_xp": 0,
            "quiz_xp": 0,
            "game_xp": 0,
        }

    return users[user.id]


def add_xp(user, amount, category):
    data = get_user(user)
    data["xp"] += amount
    data[category] += amount


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user)

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Raid", callback_data="raid"),
            InlineKeyboardButton("🧠 Quiz", callback_data="quiz"),
        ],
        [
            InlineKeyboardButton("🎮 Games", callback_data="games"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
        ],
        [
            InlineKeyboardButton("👤 My Stats", callback_data="stats"),
            InlineKeyboardButton("🎁 Rewards", callback_data="rewards"),
        ],
    ]

    await update.message.reply_text(
        "👹 Welcome to Goblin Raid HQ!\n\n"
        "⚔️ Live Raids\n"
        "🧠 Goblin Quizzes\n"
        "🎮 Mini-Games\n"
        "🏆 XP & Leaderboards\n"
        "🎁 Rewards\n"
        "🔔 Community Alerts\n\n"
        "The Goblins are ready! 👹🔥",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =========================
# RAID
# =========================

async def raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚔️ GOBLIN RAID\n\n"
        "No raid is active right now.\n\n"
        "When the Goblin team launches a raid, "
        "the target and progress will appear here."
    )


async def joinraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_xp(user, 10, "raid_xp")

    await update.message.reply_text(
        "👹 RAID PARTICIPATION RECORDED!\n\n"
        "⭐ +10 XP\n"
        "Stay ready for the next Goblin raid! ⚔️"
    )


async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 RAID PROGRESS\n\n"
        "⚔️ No active raid at the moment.\n"
        "Use /raid when a raid is live."
    )


# =========================
# QUIZ
# =========================

async def send_quiz(chat_id, context):
    question = random.choice(QUESTIONS)

    buttons = []

    for index, option in enumerate(question["options"]):
        callback = f"answer:{question['answer']}:{index}"
        buttons.append(
            [InlineKeyboardButton(option, callback_data=callback)]
        )

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🧠 GOBLIN QUESTION\n\n"
            + question["question"]
            + "\n\nChoose your answer 👇"
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_quiz(update.effective_chat.id, context)


async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    parts = query.data.split(":")
    correct = int(parts[1])
    selected = int(parts[2])

    if selected == correct:
        add_xp(user, 20, "quiz_xp")

        await query.edit_message_text(
            "🧠 CORRECT! 👹🔥\n\n"
            "+20 XP\n"
            "Keep climbing the Goblin leaderboard!"
        )
    else:
        await query.edit_message_text(
            "❌ WRONG ANSWER!\n\n"
            "Stay sharp, Goblin. 👹"
        )


# =========================
# GAMES
# =========================

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "🎯 Guess The Number",
                callback_data="guess_start",
            )
        ],
        [
            InlineKeyboardButton(
                "⚡ Reaction Challenge",
                callback_data="reaction",
            )
        ],
    ]

    await update.message.reply_text(
        "🎮 GOBLIN GAMES\n\nChoose your game 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    if query.data == "guess_start":
        number = random.randint(1, 5)
        context.user_data["guess_number"] = number

        buttons = []

        for number_option in range(1, 6):
            buttons.append(
                [
                    InlineKeyboardButton(
                        str(number_option),
                        callback_data=f"guess:{number_option}",
                    )
                ]
            )

        await query.edit_message_text(
            "🎯 GUESS THE NUMBER\n\n"
            "I'm thinking of a number from 1 to 5.\n"
            "Choose one 👇",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif query.data.startswith("guess:"):
        selected = int(query.data.split(":")[1])
        correct = context.user_data.get("guess_number")

        if selected == correct:
            add_xp(user, 25, "game_xp")

            await query.edit_message_text(
                "🎯🔥 BULLSEYE!\n\n"
                "+25 XP\n"
                "Goblin instincts activated! 👹"
            )
        else:
            await query.edit_message_text(
                "❌ Wrong!\n\n"
                f"The number was {correct}.\n"
                "Try again, Goblin. 👹"
            )

    elif query.data == "reaction":
        add_xp(user, 10, "game_xp")

        await query.edit_message_text(
            "⚡ REACTION CHALLENGE COMPLETE!\n\n"
            "+10 XP 👹🔥"
        )


# =========================
# LEADERBOARD
# =========================

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        await update.message.reply_text(
            "🏆 No Goblin activity yet."
        )
        return

    ranking = sorted(
        users.values(),
        key=lambda user: user["xp"],
        reverse=True,
    )

    text = "🏆 GOBLIN LEADERBOARD\n\n"

    for position, user in enumerate(ranking[:10], start=1):
        text += (
            f"{position}. "
            f"{user['name']} — "
            f"{user['xp']} XP\n"
        )

    await update.message.reply_text(text)


# =========================
# MY STATS
# =========================

async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user(user)

    await update.message.reply_text(
        "👤 YOUR GOBLIN STATS\n\n"
        f"👹 Goblin: {data['name']}\n"
        f"⭐ Total XP: {data['xp']}\n"
        f"⚔️ Raid XP: {data['raid_xp']}\n"
        f"🧠 Quiz XP: {data['quiz_xp']}\n"
        f"🎮 Game XP: {data['game_xp']}"
    )


# =========================
# REWARDS
# =========================

async def rewards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 GOBLIN REWARDS\n\n"
        "Earn XP through:\n"
        "⚔️ Raids\n"
        "🧠 Quizzes\n"
        "🎮 Games\n"
        "🎉 Community events\n\n"
        "More rewards coming soon! 👹🔥"
    )


# =========================
# FAQ / RULES / ALERTS
# =========================

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 GOBLIN RULES\n\n"
        "1. No spam.\n"
        "2. No fake engagement.\n"
        "3. Respect the community.\n"
        "4. Follow raid instructions.\n"
        "5. Have fun! 👹"
    )


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ GOBLIN FAQ\n\n"
        "/raid - Active raid\n"
        "/quiz - Goblin quiz\n"
        "/games - Mini-games\n"
        "/leaderboard - XP rankings\n"
        "/mystats - Your statistics\n"
        "/rewards - Rewards information"
    )


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔔 GOBLIN ALERTS\n\n"
        "Raid alerts and community announcements "
        "will appear here."
    )


async def socials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 GOBLIN SOCIALS\n\n"
        "Add your official X, Telegram and website "
        "links here."
    )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛠️ GOBLIN SUPPORT\n\n"
        "Contact the Goblin admins for assistance."
    )


# =========================
# AUTOMATIC 5-MINUTE QUESTIONS
# =========================

async def automatic_question(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data

    await send_quiz(chat_id, context)


async def startquestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Remove existing question timers
    for job in context.job_queue.get_jobs_by_name("goblin_questions"):
        job.schedule_removal()

    context.job_queue.run_repeating(
        automatic_question,
        interval=300,
        first=300,
        chat_id=chat_id,
        name="goblin_questions",
        data=chat_id,
    )

    await update.message.reply_text(
        "🧠👹 GOBLIN QUESTIONS ACTIVATED!\n\n"
        "A new question will drop every 5 minutes.\n\n"
        "⭐ Correct answer = +20 XP"
    )


# =========================
# BUTTON HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "quiz":
        await send_quiz(query.message.chat_id, context)

    elif query.data == "games":
        buttons = [
            [
                InlineKeyboardButton(
                    "🎯 Guess The Number",
                    callback_data="guess_start",
                )
            ],
            [
                InlineKeyboardButton(
                    "⚡ Reaction Challenge",
                    callback_data="reaction",
                )
            ],
        ]

        await query.edit_message_text(
            "🎮 GOBLIN GAMES\n\nChoose your game 👇",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    elif query.data == "leaderboard":
        ranking = sorted(
            users.values(),
            key=lambda user: user["xp"],
            reverse=True,
        )

        text = "🏆 GOBLIN LEADERBOARD\n\n"

        for position, user in enumerate(ranking[:10], start=1):
            text += (
                f"{position}. "
                f"{user['name']} — "
                f"{user['xp']} XP\n"
            )

        await query.edit_message_text(text)

    elif query.data == "stats":
        user = query.from_user
        data = get_user(user)

        await query.edit_message_text(
            "👤 YOUR STATS\n\n"
            f"⭐ XP: {data['xp']}\n"
            f"⚔️ Raid XP: {data['raid_xp']}\n"
            f"🧠 Quiz XP: {data['quiz_xp']}\n"
            f"🎮 Game XP: {data['game_xp']}"
        )

    elif query.data == "rewards":
        await query.edit_message_text(
            "🎁 Earn XP through raids, quizzes, games "
            "and community events. 👹🔥"
        )

    elif query.data == "raid":
        await query.edit_message_text(
            "⚔️ GOBLIN RAID\n\n"
            "No raid is active right now."
        )


# =========================
# MAIN
# =========================

def main():
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN is missing. Add BOT_TOKEN in Railway Variables."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("raid", raid))
    app.add_handler(CommandHandler("joinraid", joinraid))
    app.add_handler(CommandHandler("progress", progress))

    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("games", games))

    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("mystats", mystats))
    app.add_handler(CommandHandler("rewards", rewards))

    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("faq", faq))
    app.add_handler(CommandHandler("alerts", alerts))
    app.add_handler(CommandHandler("socials", socials))
    app.add_handler(CommandHandler("support", support))

    app.add_handler(CommandHandler("startquestion", startquestion))

    app.add_handler(
        CallbackQueryHandler(
            quiz_answer,
            pattern=r"^answer:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            game_callback,
            pattern=r"^(guess_start|guess:|reaction)$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("👹 Goblin Raid HQ is running!")

    app.run_polling()


if __name__ == "__main__":
    main()
