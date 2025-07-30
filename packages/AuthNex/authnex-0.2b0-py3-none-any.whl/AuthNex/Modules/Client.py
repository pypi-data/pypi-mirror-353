from pyrogram import Client
from pyrogram.types import Message
from AuthNex.Database import user_col, sessions_col
import random
import asyncio
from AuthNex import app

class AuthClient(Client):
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        bot_token: str,
        coins: int,
        mail: str,
        password: str,
        name: str,
        token: str,
        start_msg: str = None,
        notify_id: int = None,
        session_name: str = "AuthNexBot"
    ):
        super().__init__(session_name, api_id=api_id, api_hash=api_hash, bot_token=bot_token)
        self.mail = mail
        self.password = password
        self.name = name
        self.token = token
        self.coins = coins
        self.auth_user = None
        self.auth_connected = False
        self.start_msg = start_msg
        self.notify_id = notify_id  # user_id or channel_id to notify

    async def start(self):
        await super().start()

        user = await user_col.find_one({"Mail": self.mail})
        if not user:
            raise ValueError("❌ Email not registered in AuthNex.")

        if (
            user.get("Password") != self.password or
            user.get("Name") != self.name or
            user.get("token") != self.token
        ):
            raise ValueError("❌ Invalid AuthNex credentials or token mismatch.")

        self.auth_user = user
        self.coins = user.get("coins", self.coins)
        self.auth_connected = True

        print(f"✅ Pyrogram + AuthNex connected as {self.name} with {self.coins} AuthCoins.")

        # ⏩ Send start message if provided
        if self.start_msg and self.notify_id:
            try:
                await self.send_message(self.notify_id, self.start_msg)
            except Exception as e:
                print(f"⚠️ Failed to send start_msg: {e}")

    async def stop(self, *args):
        await super().stop()
        self.auth_user = None
        self.auth_connected = False
        print("❌ Disconnected from AuthNex and Bot.")

    async def auth_login(client: Client, message: Message, api_id, api_hash, bot_token, notify_id):
    user_id = message.from_user.id
    await message.reply("📧 Send your AuthNex email:")
    mail_msg = await client.listen(user_id)
    mail = mail_msg.text.strip()

    await client.send_message(user_id, "🔒 Send your password:")
    pass_msg = await client.listen(user_id)
    password = pass_msg.text.strip()

    user = await user_col.find_one({"Mail": mail})
    if not user:
        return await client.send_message(user_id, "❌ Email not found.")
    if user.get("Password") != password:
        return await client.send_message(user_id, "❌ Wrong password.")

    otp = str(random.randint(100000, 999999))
    await client.send_message(user_id, f"🔐 Your OTP is: `{otp}`")

    await client.send_message(user_id, "✉️ Please enter OTP:")
    otp_msg = await client.listen(user_id)
    if otp_msg.text.strip() != otp:
        return await client.send_message(user_id, "❌ Invalid OTP.")

    # ✅ Reward if first login
    already_logged = await sessions_col.find_one({"_id": user["_id"]})
    if not already_logged:
        await user_col.update_one({"Mail": mail}, {"$inc": {"AuthCoins": 100, "GamesPlayed": +1}})
        await sessions_col.insert_one({"_id": user["_id"], "mail": mail})
        await client.send_message(user_id, "🎉 First-time login — 100 AuthCoins added!")

    AuthClient(
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        coins=user.get("coins", 0),
        mail=mail,
        password=password,
        name=user.get("Name"),
        token=user.get("token"),
        start_msg="🚀 **Bot Started Successfully with AuthNex!**",
        notify_id=notify_id  # channel or user to notify
    )

    await app.send_message(user_id, "✅ Logged in & Bot Started via AuthClient.")
