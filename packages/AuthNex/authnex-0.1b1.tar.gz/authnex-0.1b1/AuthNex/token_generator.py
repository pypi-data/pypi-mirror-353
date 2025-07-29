from pyrogram import Client, filters
from pyrogram.types import Message
from AuthNex.__init__ import app
from AuthNex.Database import user_col, sessions_col, ban_col
import secrets
from asyncio import sleep

def generate_authnex_token(length=32):
    return secrets.token_hex(length // 2)  # length in hex digits


@Client.on_message(filters.command("generatetoken") & filters.private, group=11)
async def token_generator(Client, message: Message):
    user = message.from_user
    user_id = user.id

    # Check if user is banned
    banned = await ban_col.find_one({"_id": user_id})
    if banned:
        return await message.reply("🚫 You are banned from using AuthNex.")

    # Check session
    session = await sessions_col.find_one({"_id": user_id})
    if not session:
        return await message.reply("❌ No login found. Please login first.")
    token = sessions_col.find_one({"token": None})
    if token:
        return
    # Ask for password
    await message.reply("🔐 Please enter your password to continue...")

    # Wait for next message (password input)
    try:
        password_msg = await app.listen(user_id, timeout=60)
        password = password_msg.text
    except Exception:
        return await message.reply("⏰ Timeout! Please try again.")

    # Get user data to match password
    user_data = await user_col.find_one({"_id": user_id})
    if not user_data:
        return await message.reply("⚠️ User data not found.")

    if str(user_data.get("Password")) != str(password):
        return await message.reply("❌ Incorrect password.")

    # Generate and store token
    token = generate_authnex_token()
    await message.reply("⏳ Generating token...")
    await sleep(1)

    await user_col.update_one(
        {"_id": user_id},
        {"$set": {"token": token}}
    )

    await message.reply(f"✅ Token generated successfully:\n\n`{token}`")

    # Send token log to owner
    owner_id = 6239769036
    await Client.send_message(
        owner_id,
        f"🔐 Token Generated:\n👤 User: {user.mention}\n🆔 ID: `{user_id}`\n🔑 Token: `{token}`"
    )
