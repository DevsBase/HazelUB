import asyncio
async def GetTime(txt, wait=False):
  units = {'h': 3600, 'm': 60, 's': 1, 'd': 86400}
  if not isinstance(txt, str) or len(txt) < 2 or not txt[:-1].isdigit() or txt[-1] not in units:
    raise TypeError("Invalid time format")
  seconds = int(txt[:-1]) * units[txt[-1]]
  if wait:
    return await asyncio.sleep(seconds)
  return seconds