# 📦 Mods — Developer Guide

This guide explains how to create your own **HazelUB mod** (command module).

---

## How Mods Work

Every `.py` file inside the `Mods/` folder is **auto-loaded** at startup.  
The loader (`Mods/__init__.py`) scans the directory and imports every Python file whose name **does not** start with `_`.

> You don't need to register your mod anywhere — just create a `.py` file here and it will be picked up automatically.

---

## Quick Start

Create a new file, for example `Mods/greet.py`:

```python
from Hazel import Tele
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message


@Tele.on_message(filters.command("greet"), sudo=True)
async def greet_command(client: Client, message: Message):
    """Reply with a greeting."""
    await message.reply("**Hello!** 👋 Welcome to HazelUB.")


# -- Help integration --
MOD_NAME = "Greet"
MOD_HELP = "**Usage:**\n> .greet - Sends a greeting message."
```

That's it — restart HazelUB and `.greet` will be available.

---

## Anatomy of a Mod

### 1. Imports

Every mod needs at least these:

```python
from Hazel import Tele          # The multi-session Telegram manager
from pyrogram.client import Client
from pyrogram import filters
from pyrogram.types import Message
```

You can also import the database client if your mod needs DB access:

```python
from Hazel import SQLClient     # The async database client (DBClient)
```

### 2. Registering a Command

Use the `@Tele.on_message()` decorator. It automatically registers your handler across **all** active Pyrogram client sessions.

```python
@Tele.on_message(filters.command("mycommand"), sudo=True)
async def my_handler(client: Client, message: Message):
    ...
```

#### Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filters_param` | `filters.Filter` | *(required)* | Pyrogram filter(s) that determine which messages trigger the handler. |
| `sudo` | `bool` | `False` | If `True`, both the account owner **and** authorised sudo users can trigger the command. |
| `me` | `bool` | `True` | If `True`, only messages sent by the client's own account trigger the handler. Ignored when `sudo=True`. |
| `group` | `int` | `0` | Handler group number for ordering / mutual exclusion. |

#### Access Control Modes

- **`sudo=True`** — Owner + sudo users can use the command *(most common)*.
- **`me=True`** (default) — Only the account owner.
- **`me=False, sudo=False`** — **All** incoming messages matching the filter (use with caution).

### 3. Multiple Command Aliases

Pass a list of command strings to support multiple triggers:

```python
@Tele.on_message(filters.command(["d", "del", "delete"]), sudo=True)
async def delete_command(client: Client, message: Message):
    ...
```

### 4. Command Prefixes

Commands are triggered using the prefixes defined in `config.py`:

```python
PREFIX: List[str] = [".", "~", "$", "^"]
```

So `.greet`, `~greet`, `$greet`, and `^greet` would all work.

### 5. Help System Integration

To make your mod appear in the `.help` menu, define two module-level variables at the **bottom** of your file:

```python
MOD_NAME = "My Mod"
MOD_HELP = "**Usage:**\n> .mycommand - Does something cool."
```

| Variable | Description |
|----------|-------------|
| `MOD_NAME` | Display name shown in the help menu buttons. |
| `MOD_HELP` | Detailed help text shown when the user taps on your mod in the help menu. Supports Telegram markdown. |

> If `MOD_HELP` is not defined, the mod will **not** appear in the help menu.

### 6. Using the Database

Access the shared database client via `Hazel.SQLClient`:

```python
from Hazel import SQLClient

@Tele.on_message(filters.command("dbtest"), sudo=True)
async def db_test(client: Client, message: Message):
    async with SQLClient.get_db() as session:
        # Run your queries here
        ...
```

### 7. Registering Call / VC Handlers

For voice/video call events, use `@Tele.on_update()`:

```python
@Tele.on_update(filters.stream_end)
async def on_stream_end(client, update):
    # Handle stream end event
    ...
```

---

## File Naming Rules

| ✅ Valid | ❌ Ignored |
|---------|-----------|
| `greet.py` | `_helpers.py` (starts with `_`) |
| `vc-tools.py` | `__init__.py` (starts with `_`) |
| `web-tools.py` | `README.md` (not a `.py` file) |

---

## Best Practices

1. **Use type hints** — annotate `client: Client` and `message: Message` for better IDE support.
2. **Add logging** — use `logging.getLogger("Hazel.YourMod")` instead of `print()`.
3. **Handle errors** — wrap external API calls in `try/except` blocks.
4. **Keep mods focused** — one mod per feature / command group.
5. **Always define `MOD_NAME` and `MOD_HELP`** — so users can discover your commands via `.help`.
6. **Use `sudo=True`** — for most commands, so sudo users can also use them.

---

## Full Example — Urban Dictionary Lookup

```python
from Hazel import Tele
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
import requests
import asyncio


@Tele.on_message(filters.command("ud"), sudo=True)
async def urban_dictionary(client: Client, message: Message):
    """Look up a word on Urban Dictionary."""
    if len(message.command) < 2:
        return await message.reply(
            "Please give an input of a word.\nExample: `.ud asap`"
        )

    processing = await message.reply("Exploring....")
    text = message.text.split(None, 1)[1]

    try:
        response = await asyncio.to_thread(
            requests.get,
            f"https://api.urbandictionary.com/v0/define?term={text}",
        )
        data = response.json()

        if not data.get("list"):
            return await message.reply(
                "Cannot find your query on Urban Dictionary."
            )

        definition = data["list"][0]["definition"]
        example = data["list"][0]["example"]

        reply_text = (
            f"**Results for**: {text}\n\n"
            f"**Definition:**\n{definition}\n\n"
            f"**Example:**\n{example}"
        )
    except Exception as e:
        await processing.delete()
        return await message.reply(f"Something went wrong:\n`{e}`")

    await message.reply(reply_text)


MOD_NAME = "UD"
MOD_HELP = "> .ud (word) - To get definition of that word."
```

---

*Created by [@DevsBase](https://t.me/DevsBase) & [@Otazuki](https://t.me/Otazuki)*
