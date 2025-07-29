from aiogram.types import Message


    
class TestingMessage(Message):
    # _testing_msg: Message

    async def reply(self, *args, **kwargs):
        try:
            res = await super().reply(*args, **kwargs)
            return res
        except Exception as ex:
            res = await super().answer(*args, **kwargs)
            return res
