import asyncio

bio = f">> Hate.tg: I'll walk through fire for you, just let me adore you. Waiting {{}}/Forever for you. @IMissYouMano • @EraseLust • @FutureCity005"
bioedit = True
async def UpdateWaitingDays(app):
  if (app.me.id != 5965055071): return
  while (True):
    try:
      from datetime import datetime, timezone, timedelta
      days = (datetime.now(timezone(timedelta(hours=5,minutes=30))) - datetime(2025,4,20,tzinfo=timezone(timedelta(hours=5,minutes=30)))).days
      m=await app.get_messages(-1002584527324,7)
      t=f"It's been {days} days since you deleted telegram. I'm still loving and missing you."      
      if (m.text != t):
        await m.edit(t)
      if (bioedit):
        nbio = bio.format(days)
        if ((await app.get_chat('me')).bio == nbio):
          await app.update_profile(bio=nbio)
      await asyncio.sleep(7000)
    except:
      await asyncio.sleep(7000)