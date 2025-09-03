class Afk:
  async def set_afk(self, user_id: str, reason: str | None = None) -> None:
    from ..tables.afk import AFK
    async with self.Session() as session:
      afk = await session.get(AFK, user_id)
      if not afk:
        afk = AFK(user_id=user_id, reason=reason, is_afk=True)
        session.add(afk)
      else:
        afk.reason = reason
        afk.is_afk = True
      await session.commit()

  async def remove_afk(self, user_id: str) -> None:
    from ..tables.afk import AFK
    async with self.Session() as session:
      afk = await session.get(AFK, user_id)
      if afk:
        afk.is_afk = False
        afk.reason = None
        await session.commit()

  async def is_afk(self, user_id: str) -> bool:
    from ..tables.afk import AFK
    async with self.Session() as session:
      afk = await session.get(AFK, user_id)
      return afk.is_afk if afk else False

  async def get_afk_reason(self, user_id: str) -> str | None:
    from ..tables.afk import AFK
    async with self.Session() as session:
      afk = await session.get(AFK, user_id)
      return afk.reason if afk and afk.is_afk else None