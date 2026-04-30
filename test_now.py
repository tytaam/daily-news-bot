"""
Run this file to TEST the bot right now — sends news immediately.
python test_now.py
"""
import asyncio
import os
import sys

# Make sure bot.py is importable
sys.path.insert(0, os.path.dirname(__file__))
from bot import send_daily_news

print("🧪 Testing the Daily News Bot...")
asyncio.run(send_daily_news())
print("✅ Done! Check your Telegram.")
