import os
import random
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================
# SETTINGS
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# The bot will send automatic questions to the chat where /startquestion
# is used by an admin.
QUESTION_INTERVAL = 5 * 60

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# =========================
# DATA
# =========================

users = {}

active_raid = None
question_chat_id = None

questions = [
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
        "question": "What does HODL mean in crypto culture?",
        "options": [
            "Hold On for Dear Life",
            "High Online Digital Ledger",
            "Hold Digital Liquidity",
            "Home Of Decentralized Liquidity",
        ],
        "answer": 0,
    },
    {
        "question": "What is a crypto wallet mainly used for?",
        "options": [
            "Storing and managing crypto assets",
            "Mining Bitcoin automatically",
            "Creating internet connections",
            "Buying mobile data",
        ],
        "answer": 0,
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
]

# =========================
# USER SYSTEM
# =========================

def get_user(user):
    user_id = user.id

    if user_id not in users:
        users[user_id] = {
            "name": user.first_name or "Goblin",
            "xp": 0,
            "quiz_xp": 0,
            "game_xp": 0,
            "raid_xp": 0,
            "referrals": 0,
        }

    return users[user_id]


def add_xp(user, amount, category="xp"):
    data = get_user(user)

    data["xp"] += amount

    if category in data:
        data[category] += amount


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_user(user)

    keyboard = [
        [
            InlineKeyboardButton("⚔️ Active Raid", callback_data="raid"),
            InlineKeyboardButton("🧠 Quiz", callback_data="quiz"),
        ],
        [
            InlineKeyboardButton("🎮 Games", callback_data="games"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
        ],
        [
            InlineKeyboardButton("👤 My Stats", callback_data="mystats"),
            InlineKeyboardButton("🎁 Rewards", callback_data="rewards"),
        ],
    ]

    await update.message.reply_text(
        f"👹 Welcome to **Goblin Raid HQ**, {user.first_name}!\n\n"
        "⚔️ Live Raids\n"
        "🧠 Goblin Quizzes\n"
        "🎮 Mini-Games\n"
        "🏆 XP & Leaderboards\n"
        "🎁 Rewards\n"
        "🔔 Community Alerts\n\n"
        "The Goblins are ready. 👹🔥",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# =========================
# RAID
# =========================

async def raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not active_raid:
        await update.message.reply_text(
            "👹 No raid is active right now.\n\n"
            "Stay ready, Goblin. ⚔️"
        )
        return

    await update.message.reply_text(
        f"⚔️ **GOBLIN RAID — LIVE**\n\n"
        f"🎯 Target: {active_raid['url']}\n\n"
        f"🔁 Reposts: {active_raid['reposts']}/{active_raid['repost_target']}\n"
        f"💬 Comments: {active_raid['comments']}/{active_raid['comment_target']}\n"
        f"❤️ Likes: {active_raid['likes']}/{active_raid['like_target']}\n\n"
        "🔥 Hit the target and smash the raid!",
        parse_mode="Markdown",
    )


async def joinraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not active_raid:
        await update.message.reply_text("⚔️
