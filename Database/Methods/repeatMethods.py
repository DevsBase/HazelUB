class RepeatMethods:
    # ---------- Groups ----------

    async def create_group(self, name: str, user_id: int):
        name = (name.replace(' ', '')).lower()
        group = {
            "userId": user_id,
            "name": name
        }
        result = await self.repeat_groups.insert_one(group)
        group["_id"] = result.inserted_id
        return group

    async def get_group(self, group_id: str, user_id: int):
        # Note: Using string IDs for Mongo compatibility or ObjectId if needed
        from bson import ObjectId
        try:
            gid = ObjectId(group_id) if isinstance(group_id, str) else group_id
        except:
            return None
        x = await self.repeat_groups.find_one({"_id": gid})
        if x and x.get("userId") == user_id:
            return x

    async def get_group_by_name(self, name: str, user_id: int):
        name = (name.replace(' ', '')).lower()
        x = await self.repeat_groups.find_one({"name": name, "userId": user_id})
        return x
    
    async def get_groups(self, user_id: int):
        cursor = self.repeat_groups.find({"userId": user_id})
        return await cursor.to_list(length=None)

    async def delete_group(self, group_id: str, user_id: int):
        from bson import ObjectId
        try:
            gid = ObjectId(group_id) if isinstance(group_id, str) else group_id
        except:
            raise Exception('Invalid Group ID')
            
        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
            
        await self.repeat_group_chats.delete_many({"group_id": gid})
        await self.repeat_groups.delete_one({"_id": gid})

    # ---------- Group Chats ----------

    async def add_chat_to_group(self, group_id: str, chat_id: int, user_id: int):
        from bson import ObjectId
        gid = ObjectId(group_id) if isinstance(group_id, str) else group_id
        
        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
            
        row = {
            "group_id": gid,
            "chat_id": chat_id,
            "userId": user_id
        }
        await self.repeat_group_chats.insert_one(row)
        return row

    async def remove_chat_from_group(self, group_id: str, chat_id: int, user_id: int):
        from bson import ObjectId
        gid = ObjectId(group_id) if isinstance(group_id, str) else group_id

        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
            
        await self.repeat_group_chats.delete_one({
            "group_id": gid,
            "chat_id": chat_id
        })

    async def get_group_chats(self, group_id: str, user_id: int) -> list[int]:
        from bson import ObjectId
        gid = ObjectId(group_id) if isinstance(group_id, str) else group_id

        group = await self.get_group(group_id, user_id)
        if not group:
            raise Exception('The group is not found or it does not belongs to you')
            
        cursor = self.repeat_group_chats.find({"group_id": gid})
        chats = await cursor.to_list(length=None)
        return [x["chat_id"] for x in chats]

    # ---------- Repeat Messages ----------

    async def create_repeat_message(
        self,
        repeatTime: int,
        userId: int,
        message_id: int,
        source_chat_id: int,
        group_id: str
    ):
        from bson import ObjectId
        gid = ObjectId(group_id) if isinstance(group_id, str) else group_id
        
        row = {
            "repeatTime": repeatTime,
            "userId": userId,
            "message_id": message_id,
            "source_chat_id": source_chat_id,
            "group_id": gid
        }
        result = await self.repeat_messages.insert_one(row)
        row["_id"] = result.inserted_id
        return row

    async def get_repeat_messages(self):
        cursor = self.repeat_messages.find({})
        return await cursor.to_list(length=None)

    async def delete_repeat_message(self, repeat_id: str):
        from bson import ObjectId
        rid = ObjectId(repeat_id) if isinstance(repeat_id, str) else repeat_id
        await self.repeat_messages.delete_one({"_id": rid})