import discord
from discord.ext import commands, tasks
import asyncio
import json
import datetime
import os

TOKEN = os.getenv("MTQzNjU2MTQwMjg2ODI2OTIyOQ.GBjARu.zzz6B1du5rV-XLIrxy0TRaG6MAN6XzIaDR5HCs")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

COOLDOWN_FILE = "cooldown.json"

# -----------------------------------------------------
# Load / Save cooldown
# -----------------------------------------------------

def load_cooldown():
    if not os.path.exists(COOLDOWN_FILE):
        return {}
    with open(COOLDOWN_FILE, "r") as f:
        return json.load(f)

def save_cooldown(data):
    with open(COOLDOWN_FILE, "w") as f:
        json.dump(data, f, indent=4)

cooldowns = load_cooldown()

# -----------------------------------------------------
# Helper: tạo bar màu
# -----------------------------------------------------

def cooldown_bar(minutes_left: int):
    if minutes_left <= 0:
        color = "🟩"
    elif minutes_left <= 10:
        color = "🟨"
    else:
        color = "🟥"

    filled = max(1, min(30, int((minutes_left / 60) * 30)))
    empty = 30 - filled

    return f"{color} |" + ("█" * filled) + ("░" * empty) + f"| {minutes_left} phút"

# -----------------------------------------------------
# Lệnh nhập số
# -----------------------------------------------------

@bot.command()
async def set(ctx, number: int, minutes: int = 60):
    user_id = str(ctx.author.id)
    now = datetime.datetime.utcnow()

    if number not in range(1, 1001):
        return await ctx.send("Số phải nằm trong khoảng 1–1000.")

    if user_id not in cooldowns:
        cooldowns[user_id] = {}

    cooldowns[user_id][str(number)] = (now + datetime.timedelta(minutes=minutes)).timestamp()
    save_cooldown(cooldowns)

    await ctx.send(f"✅ Đặt cooldown cho **tài khoản {number}**: **{minutes} phút**.")

# -----------------------------------------------------
# Lệnh check
# -----------------------------------------------------

@bot.command()
async def check(ctx):
    user_id = str(ctx.author.id)

    if user_id not in cooldowns or cooldowns[user_id] == {}:
        return await ctx.send("Bạn chưa có cooldown nào.")

    now = datetime.datetime.utcnow().timestamp()
    text = "📊 **Biểu đồ cooldown**:\n\n"

    for number, exp in sorted(cooldowns[user_id].items(), key=lambda x: int(x[0])):
        minutes_left = int((exp - now) / 60)

        bar = cooldown_bar(minutes_left)
        text += f"**Tài khoản {number}** → {bar}\n"

    await ctx.send(text)

# -----------------------------------------------------
# Background task: kiểm tra cooldown 1 phút/lần
# -----------------------------------------------------

@tasks.loop(seconds=60)
async def cooldown_watcher():
    await bot.wait_until_ready()
    now = datetime.datetime.utcnow().timestamp()

    for user_id, accounts in list(cooldowns.items()):
        for number, expiry in list(accounts.items()):
            if expiry <= now:
                try:
                    user = await bot.fetch_user(int(user_id))
                    await user.send(f"✅ **Tài khoản {number} đã về 0 phút — bạn có thể bắt cóc!**")
                except:
                    pass

                del cooldowns[user_id][number]
                save_cooldown(cooldowns)

@cooldown_watcher.before_loop
async def before():
    print("⏳ Bắt đầu kiểm tra cooldown...")

cooldown_watcher.start()

# -----------------------------------------------------
# Bot chạy
# -----------------------------------------------------

bot.run(TOKEN)
