import os
import asyncio
import anthropic
import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# ─────────────────────────────────────────
# CONFIG — fill these in (or use .env file)
# ─────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your_anthropic_api_key_here")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_telegram_bot_token_here")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id_here")

# ─────────────────────────────────────────
# FETCH + SIMPLIFY NEWS USING CLAUDE
# ─────────────────────────────────────────
def get_news_summary() -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = """
You are a friendly news assistant that explains the news like you're talking to a 9th grader.
Search the web and find the TOP news stories from the LAST 24 HOURS covering:
- 📈 Stock market & economy (what went up, what went down, why)
- 💰 Futures & commodities (oil, gold, crypto, etc.)
- 🌍 World news & wars (any conflicts or major events)
- 🏛️ Politics (US and international — what's happening with leaders and governments)
- 💼 Business (big company news, layoffs, mergers)
- 🌎 Anything else major that happened

For EACH story:
1. Give it a fun emoji headline
2. Explain it in 2-3 simple sentences — like you're texting a friend
3. Tell them WHY it matters in one sentence (keep it real and relatable)

Use short sentences. No fancy words. If you use a big word, explain it right away.
Write it like a smart, casual friend summarizing the news — not a boring newspaper.

Format it nicely for Telegram with spacing between each story.
Start with: "☀️ Good morning! Here's what happened in the world today:\n\n"
End with: "\n\n📱 That's your morning briefing — stay informed!"
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    # Pull out all text blocks from the response
    result = ""
    for block in message.content:
        if block.type == "text":
            result += block.text

    return result if result else "⚠️ Couldn't fetch today's news. Try again later!"


# ─────────────────────────────────────────
# SEND TO TELEGRAM
# ─────────────────────────────────────────
async def send_daily_news():
    print("🔍 Fetching today's news...")
    summary = get_news_summary()

    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

    # Telegram has a 4096 char limit per message — split if needed
    MAX_LEN = 4000
    chunks = [summary[i:i+MAX_LEN] for i in range(0, len(summary), MAX_LEN)]

    for chunk in chunks:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=chunk,
            parse_mode="Markdown"
        )
        await asyncio.sleep(1)

    print("✅ News sent successfully!")


# ─────────────────────────────────────────
# SCHEDULER — runs every day at 6:00 AM PST
# ─────────────────────────────────────────
async def main():
    scheduler = AsyncIOScheduler()
    pst = pytz.timezone("America/Los_Angeles")

    scheduler.add_job(
        send_daily_news,
        trigger=CronTrigger(hour=6, minute=0, timezone=pst),
        id="daily_news",
        name="Daily Morning News",
        replace_existing=True
    )

    scheduler.start()
    print("🤖 Daily News Bot is running!")
    print("📅 Will send news every morning at 6:00 AM PST")
    print("💡 Tip: Send /test in Telegram to test it now (see README)")

    # Keep the bot alive forever
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
