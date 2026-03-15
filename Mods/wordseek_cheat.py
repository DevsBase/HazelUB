import re
import asyncio
import requests
import logging
from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele

logger = logging.getLogger(__name__)

# ── Unicode bold → ASCII ──────────────────────────────────────────────────────

def unbold(text: str) -> str:
    result = []
    for ch in text:
        cp = ord(ch)
        if 0x1D5D4 <= cp <= 0x1D5ED:
            result.append(chr(ord("A") + cp - 0x1D5D4))
        elif 0x1D5EE <= cp <= 0x1D607:
            result.append(chr(ord("A") + cp - 0x1D5EE))
        else:
            result.append(ch)
    return "".join(result)

EMOJI_COLOR = {"🟩": "green", "🟨": "yellow", "🟥": "red"}

# ── Parser ────────────────────────────────────────────────────────────────────

def parse_message(text: str):
    m = re.search(r"(\d)-letter", text, re.IGNORECASE)
    word_length = int(m.group(1)) if m else None
    clues = []

    for line in text.splitlines():
        colors  = [EMOJI_COLOR[ch] for ch in line if ch in EMOJI_COLOR]
        letters = re.sub(r"[^A-Z]", "", unbold(line).upper())
        if colors and letters and len(colors) == len(letters):
            word_length = word_length or len(letters)
            clues.append((letters, colors))

    won = bool(clues) and all(c == "green" for c in clues[-1][1])
    return clues, word_length, won

# ── Constraint builder ────────────────────────────────────────────────────────

def build_constraints(clues):
    correct, present, absent, min_count = {}, {}, set(), {}

    for word, colors in clues:
        confirmed, has_red = {}, set()

        for i, (letter, color) in enumerate(zip(word, colors)):
            if color in ("green", "yellow"):
                confirmed[letter] = confirmed.get(letter, 0) + 1
            elif color == "red":
                has_red.add(letter)

        for letter, count in confirmed.items():
            min_count[letter] = max(min_count.get(letter, 0), count)

        for letter in has_red:
            if confirmed.get(letter, 0) == 0:
                absent.add(letter)

        for i, (letter, color) in enumerate(zip(word, colors)):
            if color == "green":
                correct[i] = letter
            elif color == "yellow":
                present.setdefault(letter, set()).add(i)

    absent -= set(min_count.keys())
    return correct, present, absent, min_count

# ── Word filter ───────────────────────────────────────────────────────────────

def word_matches(word, correct, present, absent, min_count):
    word = word.upper()
    if any(word[pos] != letter for pos, letter in correct.items()):
        return False
    if any(letter in word for letter in absent):
        return False
    if any(word.count(letter) < count for letter, count in min_count.items()):
        return False
    for letter, bad_positions in present.items():
        if any(pos < len(word) and word[pos] == letter for pos in bad_positions):
            return False
    return True

# ── Datamuse fetch ────────────────────────────────────────────────────────────

def fetch_candidates(word_length, correct):
    pattern = ["?"] * word_length
    for pos, letter in correct.items():
        pattern[pos] = letter.lower()

    try:
        resp  = requests.get(
            "https://api.datamuse.com/words",
            params={"sp": "".join(pattern), "md": "f", "max": 1000},
            timeout=10
        )
        result = []
        for item in resp.json():
            word = item["word"]
            if len(word) != word_length or not word.isalpha():
                continue
            freq = 0.0
            for tag in item.get("tags", []):
                if tag.startswith("f:"):
                    try: freq = float(tag[2:])
                    except ValueError: pass
            if freq >= 0.1:
                result.append((word.upper(), freq))
        return result
    except Exception as e:
        logger.error(f"[WordSeek] Datamuse error: {e}")
        return []

# ── Solver ────────────────────────────────────────────────────────────────────

def get_best_guess(message_text: str):
    clues, word_length, won = parse_message(message_text)
    if won:
        return None, [], True
    if not clues or not word_length:
        return None, [], False

    correct, present, absent, min_count = build_constraints(clues)
    guessed   = {w for w, _ in clues}
    raw       = fetch_candidates(word_length, correct)
    candidates = sorted(
        [(w, f) for w, f in raw if w not in guessed and word_matches(w, correct, present, absent, min_count)],
        key=lambda x: -x[1]
    )

    best  = candidates[0][0] if candidates else None
    top10 = [w for w, _ in candidates[:10]]
    return best, top10, False

# ── State ─────────────────────────────────────────────────────────────────────

game_data: dict = {}

# ── Commands ──────────────────────────────────────────────────────────────────
@Tele.on_message(filters.command("ws_cheat") & filters.group, sudo=True)
async def wordseek_cheat(c: Client, m: Message):
    cid  = getattr(c.me, "id")
    chat = getattr(m.chat, "id")

    if cid not in game_data:
        game_data[cid] = {"chats": []}

    chats = game_data[cid]["chats"]

    if chat in chats:
        chats.remove(chat)
        return await m.reply("WordSeek cheat **disabled** for this chat.")

    chats.append(chat)
    await m.reply("WordSeek cheat **enabled**. Starting game...")
    await c.send_message(chat, "/new@wordseekbot")
    await asyncio.sleep(1)
    await c.send_message(chat, "lover")


@Tele.on_message(filters.user("WordSeekBot"), group=101)
async def on_game_message(c: Client, m: Message):
    cid  = getattr(c.me, "id")
    chat = getattr(m.chat, "id")

    if cid not in game_data or chat not in game_data[cid].get("chats", []):
        return

    guess, top, won = await asyncio.to_thread(get_best_guess, m.text or "")
    if guess:
        await asyncio.sleep(1)
        await c.send_message(chat_id=chat, text=guess.lower())
    logger.info(f"cannot guess the word: {m.text}, guess: {guess}, top: {top}")


MOD_CONFIG = {
    "name": "WordSeek",
    "help": "**.ws_cheat** — Toggle auto-cheat for WordSeek bot in the current group.",
    "works": WORKS.GROUP,
    "usable": USABLE.OWNER & USABLE.SUDO,
    "requires": [
        "requests"
    ] 
}