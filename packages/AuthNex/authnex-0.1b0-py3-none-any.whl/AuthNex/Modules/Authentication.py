import random
from pyrogram.enums import ParseMode
from AuthNex.Database import sessions_col
from AuthNex.Modules import HelperBot

async def authentication_code(mail: str) -> int:
    """
    Generate and send an authentication code to the user
    who is logged in with the given mail.
    """
    session_data = await sessions_col.find_one({"mail": mail})

    if not session_data:
        raise ValueError("No active session found for this mail.")

    user_id = session_data.get("_id")  # Telegram user ID

    code = random.randint(10000, 99999)

    await HelperBot.send_message(
        chat_id=user_id,
        text=f"🔐 Your Authentication Code: `{code}`",
        parse_mode=ParseMode.MARKDOWN
    )

    return code
