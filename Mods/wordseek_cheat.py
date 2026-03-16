import re
import random
import asyncio
import requests
import logging
from Hazel.enums import USABLE, WORKS
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Hazel import Tele

logger = logging.getLogger(__name__)

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


OPENERS: dict[int, list[str]] = {
    4: ["area", "also", "able", "open", "unit", "each", "idea", "into", "once", "item"],
    5: ["arose", "stare", "crane", "slate", "crate", "snare", "trace", "later", "alter", "tales"],
    6: ["stoner", "tinsel", "alerts", "insole", "nested", "stolen", "tailor", "trails", "reason", "detail"],
}
_last_opener: dict[int, str] = {}

def pick_opener(length: int) -> str:
    pool = OPENERS.get(length, OPENERS[5])
    last = _last_opener.get(length)
    choices = [w for w in pool if w != last] or pool
    word = random.choice(choices)
    _last_opener[length] = word
    return word

EMOJI_COLOR = {"🟩": "green", "🟨": "yellow", "🟥": "red"}

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

def fetch_candidates(word_length: int, correct: dict) -> list:
    pattern = ["?"] * word_length
    for pos, letter in correct.items():
        pattern[pos] = letter.lower()

    try:
        resp = requests.get(
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
            result.append((word.upper(), freq))
        return result
    except Exception as e:
        logger.error(f"[WordSeek] Datamuse error: {e}")
        return []

def _sort(pairs: list) -> list:
    return sorted(pairs, key=lambda x: -x[1])

def get_best_guess(message_text: str, blacklist: set | None = None):
    blacklist = {w.upper() for w in blacklist} if blacklist else set()

    clues, word_length, won = parse_message(message_text)
    if won:
        return None, [], True
    if not clues or not word_length:
        return None, [], False

    correct, present, absent, min_count = build_constraints(clues)
    guessed = {w for w, _ in clues} | blacklist
    raw = fetch_candidates(word_length, correct)

    # Tier 1: full constraints, common words
    candidates = _sort([(w, f) for w, f in raw if f >= 1.0 and w not in guessed and word_matches(w, correct, present, absent, min_count)])
    # Tier 2: full constraints, any freq
    if not candidates:
        candidates = _sort([(w, f) for w, f in raw if w not in guessed and word_matches(w, correct, present, absent, min_count)])
    # Tier 3: drop yellow/green position rules, keep absent + freq
    if not candidates:
        candidates = _sort([(w, f) for w, f in raw if f >= 1.0 and w not in guessed and not any(l in w for l in absent)])
    # Tier 4: drop yellow/green position rules, keep absent
    if not candidates:
        candidates = _sort([(w, f) for w, f in raw if w not in guessed and not any(l in w for l in absent)])
    # Tier 5: drop everything except not-already-guessed — always produces a guess
    if not candidates:
        candidates = _sort([(w, f) for w, f in raw if w not in guessed])

    best  = candidates[0][0] if candidates else None
    top10 = [w for w, _ in candidates[:10]]
    return best, top10, False

# ── State ─────────────────────────────────────────────────────────────────────

game_data: dict = {}

def _data(cid: int) -> dict:
    if cid not in game_data:
        game_data[cid] = {"chats": [], "auto": [], "blacklist": {}, "last_clue": {}}
    return game_data[cid]

def _get_blacklist(data: dict, chat: int, length: int) -> set:
    """Return the blacklist set for a specific chat+word_length combo."""
    return data["blacklist"].setdefault(chat, {}).setdefault(length, set())

def _add_to_blacklist(data: dict, chat: int, word: str):
    """Add an invalid word to the blacklist for its chat+length."""
    length = len(word)
    bl = _get_blacklist(data, chat, length)
    bl.add(word.upper())
    logger.info(f"[WordSeek] Blacklisted '{word.upper()}' (len={length}) in chat {chat}. Total: {len(bl)}")

# ── Commands ──────────────────────────────────────────────────────────────────

@Tele.on_message(filters.command("ws_cheat") & filters.group, sudo=True)
async def wordseek_cheat(c: Client, m: Message):
    cid  = getattr(c.me, "id")
    chat = getattr(m.chat, "id")
    data = _data(cid)
    args = (getattr(m, "text") or "").split()
    auto = len(args) > 1 and args[1].lower() == "auto"

    if auto:
        if chat in data["auto"]:
            data["auto"].remove(chat)
            return await m.reply("WordSeek **auto-start disabled** for this chat.")
        data["auto"].append(chat)
        if chat not in data["chats"]:
            data["chats"].append(chat)
            await m.reply("WordSeek **auto-start enabled** and cheat **started**.")
            await asyncio.sleep(1)
            await c.send_message(chat, "/new@wordseekbot")
            await asyncio.sleep(1)
            await c.send_message(chat, pick_opener(5))
        else:
            await m.reply("WordSeek **auto-start enabled** for this chat.")
        return

    if chat in data["chats"]:
        data["chats"].remove(chat)
        return await m.reply("WordSeek cheat **disabled** for this chat.")

    data["chats"].append(chat)
    await m.reply("WordSeek cheat **enabled**. Starting game...")
    await asyncio.sleep(1)
    await c.send_message(chat, "/new@wordseekbot")
    await asyncio.sleep(1)
    await c.send_message(chat, pick_opener(5))


@Tele.on_message(filters.user("WordSeekBot"), group=101)
async def on_game_message(c: Client, m: Message):
    cid  = getattr(c.me, "id")
    chat = getattr(m.chat, "id")
    data = _data(cid)
    text = getattr(m, "text") or ""

    # ── Detect "/newN" prompts (auto-restart) ────────────────────────────────
    new_match = re.search(r"/new(\d)", text, re.IGNORECASE)
    if new_match:
        if chat in data["auto"]:
            length = new_match.group(1)
            await asyncio.sleep(1)
            await c.send_message(chat, f"/new{length}@wordseekbot")
            await asyncio.sleep(1)
            await c.send_message(chat, pick_opener(int(length)))
        return

    # ── Detect "X is not a valid N-letter word." ─────────────────────────────
    invalid_match = re.search(
        r"([A-Za-z]+)\s+is\s+not\s+a\s+valid\s+(\d+)-letter\s+word",
        text,
        re.IGNORECASE
    )
    if invalid_match:
        xWord = invalid_match.group(1)
        _add_to_blacklist(data, chat, xWord)
        if chat in data["chats"]:
            last_clue = data["last_clue"].get(chat)
            if last_clue:
                _, word_length, _ = parse_message(last_clue)
                bl = _get_blacklist(data, chat, word_length) if word_length else set()
                guess, top, won = await asyncio.to_thread(get_best_guess, last_clue, bl)
                if not won and guess:
                    await asyncio.sleep(1)
                    await c.send_message(chat_id=chat, text=guess.lower())
                else:
                    logger.info(f"[WordSeek] No re-guess after blacklist | top: {top}")
        return

    if chat not in data["chats"]:
        return

    # ── Normal clue message: cache it, then guess ────────────────────────────
    if any(ch in text for ch in EMOJI_COLOR):
        data["last_clue"][chat] = text

    _, word_length, _ = parse_message(text)
    bl = _get_blacklist(data, chat, word_length) if word_length else set()

    guess, top, won = await asyncio.to_thread(get_best_guess, text, bl)
    if not won and guess:
        await asyncio.sleep(1)
        await c.send_message(chat_id=chat, text=guess.lower())
    elif not guess:
        logger.info(f"[WordSeek] No guess found | top: {top} | text: {text}")


MOD_CONFIG = {
    "name": "WordSeek",
    "help": (
        "**Usage:**\n"
        "**.ws_cheat** — Toggle auto-cheat for WordSeek bot in the current group.\n"
        "**.ws_cheat auto** — Toggle auto-start a new game after each win."
    ),
    "works": WORKS.GROUP,
    "usable": USABLE.OWNER & USABLE.SUDO,
    "requires": [
        "requests"
    ]
}