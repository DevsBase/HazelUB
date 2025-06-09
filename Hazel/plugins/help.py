from subprocess import getoutput as r
from pyrogram import Client, filters
from Hazel import *
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

files = r("ls Hazel/plugins").split('\n')
help_data = {}
help_list = []

for f in files:
  if f.endswith('.py') and not f.startswith('__pycache__'):
    try:
      mod = __import__(f"Hazel.plugins.{f[:-3]}", fromlist=["MOD_NAME", "MOD_HELP"])
      if hasattr(mod, 'MOD_NAME') and hasattr(mod, 'MOD_HELP'):
        help_data[mod.MOD_NAME] = mod.MOD_HELP
        help_list.append(mod.MOD_NAME)
    except: pass

async def help_page(p=1, limit=10):
  s = (p - 1) * limit
  e = s + limit
  max_p = (len(help_list) + limit - 1) // limit
  btns, row = [], []
  for name in help_list[s:e]:
    row.append(InlineKeyboardButton(name, callback_data=f"help:{name}:{p}"))
    if len(row) == 2:
      btns.append(row)
      row = []
  if row: btns.append(row)
  nav = []
  if p > 1: nav.append(InlineKeyboardButton("🔙 Back", callback_data=f"helppage:{p-1}"))
  if e < len(help_list): nav.append(InlineKeyboardButton("Next 🔜", callback_data=f"helppage:{p+1}"))
  if nav: btns.append(nav)
  return InlineKeyboardMarkup(btns), p, max_p

@bot.on_inline_query(filters.regex('help'))
async def help_query(_, q):
  markup, page, total = await help_page()
  res = InlineQueryResultArticle(
    title="Help",
    input_message_content=InputTextMessageContent(
      f"**Click buttons below to get the module info**\nPage {page}/{total}"
    ),
    reply_markup=markup
  )
  await q.answer([res])

@bot.on_callback_query(filters.regex('^help:'))
async def help_info(_, q):
  parts = q.data.split(":")
  name = parts[1]
  page = int(parts[2]) if len(parts) > 2 else 1
  if name in help_data:
    txt = f"**⚡ Help for the module: {name}**\n\n{help_data[name]}"
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"helppage:{page}")]])
    await q.edit_message_text(txt, reply_markup=btn)

@bot.on_callback_query(filters.regex('^helppage:'))
async def page_btn(_, q):
  page = int(q.data.split(":")[1])
  markup, p, total = await help_page(page)
  await q.edit_message_text(
    f"**Click buttons below to get the module info**\nPage {p}/{total}",
    reply_markup=markup
  )
  
@on_message(filters.command("help", prefixes=HANDLER) & filters.me)
async def help_func(app, message):
  results = await app.get_inline_bot_results(bot.me.username, 'help')
  await app.send_inline_bot_result(
    chat_id=message.chat.id,
    query_id=results.query_id,
    result_id=results.results[0].id
  )