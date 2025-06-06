import asyncio
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
        await app.send_message(-1002613019184, f"Day ( {days} / Forever ) trying new ways to contact you / waiting for your reply.")
      await asyncio.sleep(7000)
    except: await asyncio.sleep(7000)