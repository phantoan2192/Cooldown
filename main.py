import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Lấy TOKEN từ Secrets
DATA_FILE = "cooldown.json"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents)  # Không cần dấu !


# ---------------------------
# Tải / lưu JSON
# ---------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

cooldowns = load_data()


# ---------------------------
# Tính thời gian còn lại
# ---------------------------
def remaining_minutes(end_timestamp):
    now = datetime.now().timestamp()
    diff = end_timestamp - now
    return max(0, int(diff // 60))


# ---------------------------
# Màu biểu đồ cooldown
# ---------------------------
def get_color(mins):
    if mins == 0:
        return "🟩"  # xanh
    if mins <= 10:
        return "🟨"  # vàng
    return "🟥"  # đỏ


# ---------------------------
# Xử lý tin nhắn nhập số
# ---------------------------
@bot.event
async def on_message(msg):
    if msg.author.bot:
        return

    text = msg.content.strip()

    # Nếu chỉ nhập số → cooldown = 60 phút
    if text.isdigit():
        num = text

        now = datetime.now()
        end = now + timedelta(minutes=60)

        cooldowns[num] = {
            "start": now.timestamp(),
            "end": end.timestamp(),
            "user_id": msg.author.id,
            "channel_id": msg.channel.id
        }
        save_data(cooldowns)

        await msg.channel.send(
            f"✅ **Tài khoản {num}** đặt cooldown **60 phút**\n"
            f"⏳ Bắt đầu lúc **{now.strftime('%H:%M:%S')}**\n"
            f"{msg.author.mention}"
        )
        return

    # Nếu nhập dạng "1 45" → cooldown = 45 phút
    parts = text.split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        num = parts[0]
        mins = int(parts[1])

        now = datetime.now()
        end = now + timedelta(minutes=mins)

        cooldowns[num] = {
            "start": now.timestamp(),
            "end": end.timestamp(),
            "user_id": msg.author.id,
            "channel_id": msg.channel.id
        }
        save_data(cooldowns)

        await msg.channel.send(
            f"✅ **Tài khoản {num}** đặt cooldown **{mins} phút**\n"
            f"⏳ Bắt đầu lúc **{now.strftime('%H:%M:%S')}**\n"
            f"{msg.author.mention}"
        )
        return

    # Lệnh check cooldown
    if text == "check":
        if not cooldowns:
            await msg.channel.send("📭 Không có cooldown nào.")
            return

        result = "📊 **Biểu đồ Cooldown**\n\n"
        for num, info in cooldowns.items():
            mins = remaining_minutes(info["end"])
            result += f"{get_color(mins)} **Tài khoản {num}** — {mins} phút còn lại\n"

        await msg.channel.send(result)
        return


# ---------------------------
# Kiểm tra cooldown mỗi 10 giây
# ---------------------------
@tasks.loop(seconds=10)
async def check_cd():
    now = datetime.now().timestamp()
    expired = []

    for num, info in cooldowns.items():
        if now >= info["end"]:
            expired.append(num)

            user = bot.get_user(info["user_id"])
            channel = bot.get_channel(info["channel_id"])

            if channel and user:
                await channel.send(
                    f"⏰ **Tài khoản {num} đã hết cooldown!** {user.mention}"
                )

    for num in expired:
        del cooldowns[num]

    if expired:
        save_data(cooldowns)


@bot.event
async def on_ready():
    print(f"✅ Bot đã chạy: {bot.user}")
    check_cd.start()


bot.run(TOKEN)
