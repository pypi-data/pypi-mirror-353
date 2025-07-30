# 🚀 AuthNex - Secure Telegram Authentication Bot

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/AuthNex?style=for-the-badge)](https://pypi.org/project/AuthNex/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/RyomenSukuna53/AuthNex?style=for-the-badge&logo=github)](https://github.com/RyomenSukuna53/AuthNex/stargazers)

---

## 🔥 Features

- 🔐 **Secure Multi-Step Login**: Email + Password + OTP verification
- ⚡ **Fast & Lightweight**: Built on Pyrogram with async support
- 📊 **Session Tracking**: Monitor login timestamps & user activity
- 🧩 **Modular Architecture**: Easy to extend and maintain
- 🤖 **Telegram Bot Integration**: Friendly UX with interactive commands

---

## 🛠️ Installation

```bash
git clone https://github.com/RyomenSukuna53/AuthNex.git
cd AuthNex
pip install -r requirements.txt


---

⚙️ Configuration

Create a .env file with:

Variable	Description

API_ID	Your Telegram API ID
API_HASH	Your Telegram API Hash
BOT_TOKEN	Telegram Bot Token
MONGO_URI	MongoDB connection string


Example:

API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890
BOT_TOKEN=123456789:ABCDefGhiJKlmNoPQRsTUVwxyz
MONGO_URI=mongodb+srv://user:pass@cluster0.mongodb.net/mydb


---

🤖 Usage

Start the bot

python -m AuthNex

Commands

Command	Description

/login	Initiate login (Email + Password + OTP)
/info	Get user info by email



---

💡 Example

/login
📧 Please enter your mail to login:
user@example.com
🔐 Enter your password:
********
📨 OTP sent! Please enter it now:
12345
✅ Login verified for user@example.com


---

📱 Useful Links






---

📝 License

This project is licensed under the MIT License.


---

🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check issues page.


---

Made with ❤️ by Kuro__

---

**Explanation:**

- Stylish badges using [shields.io](https://shields.io/) (Python, License, stars, PyPI)
- Clear tables for env variables & commands
- Code blocks for commands & config samples
- Buttons linked to GitHub repo, Telegram bot, PyPI page
- Simple, clean, professional, and readable
