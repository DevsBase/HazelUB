# 🌿 HazelUB

A powerful, modular **Telegram userbot** built with [Pyrogram](https://docs.pyrogram.org/) and [PyTgCalls](https://github.com/pytgcalls/pytgcalls). HazelUB supports **multi-session management**, allowing you to run multiple Telegram accounts simultaneously with a single deployment.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue.svg)
![Pyrogram](https://img.shields.io/badge/Pyrogram-Kurigram-orange.svg)

---

## ✨ Features

- 🔄 **Multi-Session Support** — Run multiple Telegram accounts from one instance.
- 🎵 **Music & Voice Chat** — Play, pause, resume, and queue music in Telegram voice chats with built-in VC tools.
- 🔌 **Modular Plugin System** — Add or remove features by simply dropping `.py` files in the `Mods/` folder. No registration needed.
- 👑 **Sudo User System** — Grant trusted users permission to execute commands on your behalf, per-client.
- 🔁 **Message Repeater** — Schedule periodic message broadcasts to groups with pause/resume support.
- 🗄️ **Dual Database Support** — PostgreSQL for production, SQLite as an automatic fallback.
- 📖 **Built-in Help Menu** — Auto-generated inline help menu from all loaded mods.
- 🛡️ **Admin Utilities** — Ban, purge, delete, and manage chats with ease.
- 📱 **Desktop Notifications** — Get notified when HazelUB starts (via [plyer](https://github.com/kivy/plyer)).

---

## 🏗️ Architecture Overview

```
HazelUB/
│
├── Hazel/                          # Core package (entry-point & utilities)
│   ├── __init__.py                 # Global references (Tele, SQLClient, sudoers)
│   ├── __main__.py                 # python -m Hazel entry-point
│   ├── utils.py                    # Runtime helpers (async exec, etc.)
│   └── Tasks/
│       └── messageRepeater.py      # Background task: scheduled message repeater
│
├── Setup/                          # Boot & installation logic
│   ├── main.py                     # Full startup lifecycle orchestrator
│   ├── installation.py             # Dependency checks & first-time setup
│   └── utils.py                    # Config loader, signal handler, pip installer
│
├── Database/                       # Async database layer (SQLAlchemy)
│   ├── client.py                   # DBClient — engine, sessions, local state
│   ├── Tables/                     # ORM model definitions
│   │   ├── base.py                 # Declarative base
│   │   ├── loader.py               # Auto-loader for all table modules
│   │   ├── local.py                # LocalState (installed flag)
│   │   ├── sudo.py                 # Sudo user records
│   │   ├── repeatMessage.py        # Repeat message jobs
│   │   ├── repeatMessageGroup.py   # Repeat message groups
│   │   └── repeatMessageGroupChat.py
│   └── Methods/                    # Database method mixins
│       ├── sudoMethods.py          # CRUD for sudo users
│       └── repeatMethods.py        # CRUD for repeat messages
│
├── MultiSessionManagement/         # Multi-account session orchestration
│   ├── telegram.py                 # Telegram class — clients, PyTgCalls, helpers
│   ├── decorators.py               # @Tele.on_message / @Tele.on_update decorators
│   └── TelegramMethods/            # Additional method mixins
│
├── Mods/                           # Command modules (auto-loaded plugins)
│   ├── __init__.py                 # Mod auto-loader
│   ├── ping.py                     # .ping — latency & uptime
│   ├── music.py                    # .play, .pause, .resume, .skip, etc.
│   ├── ai.py                       # .ai — Gemini AI chat
│   ├── help.py                     # .help — inline help menu
│   ├── bans.py                     # .ban, .unban
│   ├── sudoers.py                  # .addsudo, .delsudo, .sudolist
│   ├── repeater.py                 # .repeat — message repeater management
│   ├── dev.py                      # .eval, .exec — developer tools
│   ├── del.py                      # .del — delete messages
│   ├── purge.py                    # .purge — bulk delete
│   ├── id.py                       # .id — get user/chat IDs
│   ├── ud.py                       # .ud — Urban Dictionary lookup
│   ├── calculator.py               # .calc — calculator
│   ├── clients.py                  # .clients — session info
│   ├── bridge.py                   # .bridge — WebSocket bridge
│   ├── vc-tools.py                 # VC helper commands
│   ├── web-tools.py                # Web utility commands
│   └── README.md                   # 📖 Guide on creating your own mod
│
├── config.py                       # User configuration (API keys, sessions)
├── restart.py                      # Process restart helper
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker support
├── .env.example                    # Environment variable template
└── LICENSE                         # MIT License
```

---

## 📋 Prerequisites

- **Python 3.13+**
- **FFmpeg** — required for voice chat / music features
- A **Telegram API ID & Hash** — get from [my.telegram.org](https://my.telegram.org/)
- A **Pyrogram session string** — generate from [telegram.tools](https://telegram.tools)
- A **Bot Token** — get from [@BotFather](https://t.me/BotFather) (enable **inline mode** too)

### Optional

- **PostgreSQL** database URL (falls back to SQLite automatically)
- **Gemini API Key** — for AI features, get from [Google AI Studio](https://aistudio.google.com/app/api-keys)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/DevsBase/HazelUB.git
cd HazelUB
```

### 2. Configure

You can configure HazelUB using **either** `config.py` **or** environment variables (`.env`).

#### Option A: Edit `config.py`

```python
API_ID = "your_api_id"
API_HASH = "your_api_hash"
SESSION = "your_pyrogram_session_string"
BOT_TOKEN = "your_bot_token"

# Optional
DB_URL = "postgresql+asyncpg://user:pass@host/dbname"
OtherSessions = ["session2", "session3"]
PREFIX = [".", "~"]
GEMINI_API_KEY = "your_gemini_key"
```

#### Option B: Use Environment Variables

Copy the example and fill in your values:

```bash
cp .env.example .env
```

```env
API_ID=your_api_id
API_HASH=your_api_hash
SESSION=your_pyrogram_session_string
BOT_TOKEN=your_bot_token
DB_URL=
OtherSessions=
PREFIX=
GEMINI_API_KEY=
```

> **Note:** Values in `config.py` take priority over environment variables. If a required key is missing from both, you will be prompted interactively.

### 3. Run

#### Local

```bash
python -m Hazel
```

On first run, HazelUB will automatically install all required packages from `requirements.txt` and restart itself.

#### Docker

```bash
docker build -t hazelub .
docker run -d --name hazelub hazelub
```

---

## ⚙️ Configuration Reference

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `API_ID` | ✅ | — | Telegram API application ID |
| `API_HASH` | ✅ | — | Telegram API application hash |
| `SESSION` | ✅ | — | Pyrogram session string for the primary account |
| `BOT_TOKEN` | ✅ | — | Bot token or bot session string (for the assistant bot) |
| `DB_URL` | ❌ | `""` (SQLite) | PostgreSQL connection URL. If empty, SQLite (`HazelUB.db`) is used |
| `OtherSessions` | ❌ | `[]` | List of additional Pyrogram session strings for multi-account |
| `PREFIX` | ❌ | `[".","~","$","^"]` | Command trigger prefixes |
| `GEMINI_API_KEY` | ❌ | `""` | Google Gemini API key for AI features |

---

## 💬 Usage

All commands are triggered using your configured prefix (default: `.`). Here are some built-in commands:

| Command | Description |
|---------|-------------|
| `.help` | Open the interactive help menu |
| `.ping` | Check latency & uptime |
| `.ai <prompt>` | Chat with Gemini AI |
| `.play <song>` | Play a song in voice chat |
| `.pause` / `.resume` | Pause or resume playback |
| `.ban` / `.unban` | Ban or unban a user (reply or mention) |
| `.del` | Delete a replied message |
| `.purge` | Bulk-delete messages |
| `.id` | Get user / chat ID |
| `.ud <word>` | Look up a word on Urban Dictionary |
| `.eval <code>` | Evaluate Python code (owner only) |
| `.addsudo <user>` | Grant sudo access |
| `.delsudo <user>` | Revoke sudo access |
| `.sudolist` | List all sudo users |

> **Tip:** All prefixes work interchangeably — `.ping`, `~ping`, `$ping`, and `^ping` do the same thing.

---

## 🔌 Creating Your Own Mod

Creating a mod is as simple as adding a `.py` file to the `Mods/` folder. Here's a minimal example:

```python
from Hazel import Tele
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message


@Tele.on_message(filters.command("hello"), sudo=True)
async def hello_command(client: Client, message: Message):
    await message.reply("**Hello!** 👋")


MOD_NAME = "Hello"
MOD_HELP = "**Usage:**\n> .hello - Sends a greeting."
```

📖 For a detailed guide, see [`Mods/README.md`](Mods/README.md).

### Key Points

- Files starting with `_` are **ignored** by the loader.
- Define `MOD_NAME` and `MOD_HELP` to appear in the `.help` menu.
- Use `sudo=True` to allow both the owner and sudo users to run the command.
- Your handler is **automatically registered** across all active client sessions.

---

## 🗄️ Database

HazelUB uses **SQLAlchemy (async)** with support for two backends:

| Backend | When Used | Connection |
|---------|-----------|------------|
| **PostgreSQL** | When `DB_URL` is set | `asyncpg` driver |
| **SQLite** | Fallback (default) | `aiosqlite` driver, file: `HazelUB.db` |

The database is accessed globally via `Hazel.SQLClient` (an instance of `DBClient`). Tables are auto-created on first startup.

### Adding a New Table

1. Create a new model file in `Database/Tables/` (e.g. `myTable.py`).
2. Import `Base` from `Database.Tables.base` and define your model.
3. The table loader (`Database/Tables/loader.py`) auto-discovers all models in the `Tables/` directory.

---

## 👥 Multi-Session Management

HazelUB can run **multiple Telegram accounts** simultaneously:

1. Set your primary session in `SESSION`.
2. Add additional session strings to `OtherSessions` in `config.py`.
3. Each session gets its own Pyrogram `Client` and `PyTgCalls` instance.
4. The `@Tele.on_message()` decorator automatically registers handlers on **all** sessions.

### Privilege Levels

| Level | Scope |
|-------|-------|
| **Owner** | The primary session (`SESSION`) — full access |
| **Sudo** | Users added via `.addsudo` — can run `sudo=True` commands |
| **User** | Additional sessions in `OtherSessions` |

---

## 🤝 Contributing

1. **Fork** the repository.
2. Create a **feature branch** (`git checkout -b feature/my-feature`).
3. **Commit** your changes (`git commit -m "Add my feature"`).
4. **Push** to the branch (`git push origin feature/my-feature`).
5. Open a **Pull Request**.

### Guidelines

- Use **type hints** on all function signatures.
- Add **docstrings** to public functions and classes.
- Follow the existing code style and module structure.
- Test your changes before submitting.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

- **Telegram Channel:** [@DevsBase](https://t.me/DevsBase)
- **Telegram:** [@Otazuki](https://t.me/Otazuki)

---

<p align="center">
  Made with ❤️ by <a href="https://t.me/DevsBase">DevsBase™</a> & <a href="https://t.me/Otazuki">Otazuki</a>
</p>
